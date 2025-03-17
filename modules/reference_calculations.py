import streamlit as st
import numpy as np
import pandas as pd
from utils.session_state_manager import SessionStateManager
from utils.logs_manager import LogsManager

class ReferenceCalculations:
    """
    Класс для выполнения расчетов эталонных значений.
    """

    def __init__(self, state_tracker, logs_manager):
        self.state_tracker = state_tracker
        self.logs_manager = logs_manager
        self.ref_table = None  # Таблица эталонных значений

        # Проверка типа шкалы перед инициализацией
        if "scale_type" not in st.session_state:
            st.session_state["scale_type"] = "Логарифмическая"  # Установлено по умолчанию
            self.logs_manager.add_log(
                module="ReferenceCalculations",
                event="Тип шкалы отсутствует, установлен 'Логарифмическая' (по умолчанию)",
                log_type="предупреждение"
            )

        # Инициализация хранилищ данных
        if "P_x_data" not in st.session_state:
            st.session_state["P_x_data"] = {}

        if "psd_table" not in st.session_state:
            st.session_state["psd_table"] = {}

        # Проверка и инициализация параметров x_range_min и target_x_max
        x_range_min = st.session_state["ref_vals"].get("x_range_min")
        target_x_max = st.session_state["ref_vals"].get("target_x_max")

        if x_range_min is None:
            st.warning("⚠ Параметр 'x_range_min' не задан. Проверьте эталонные значения.")
            self.logs_manager.add_log(module="ReferenceCalculations", event="Параметр 'x_range_min' отсутствует", log_type="предупреждение")

        if target_x_max is None:
            st.warning("⚠ Параметр 'target_x_max' не задан. Проверьте эталонные значения.")
            self.logs_manager.add_log(module="ReferenceCalculations", event="Параметр 'target_x_max' отсутствует", log_type="предупреждение")

    def generate_scale(self):
        """
        Генерация шкалы x_values в зависимости от типа шкалы.
        """
        try:
            # Очистка предыдущих значений шкалы
            st.session_state.pop("x_values", None)

            ref_vals = st.session_state.get("conf_ref_vals", {})
            if not isinstance(ref_vals, dict):
                st.error("Ошибка: conf_ref_vals имеет неверный формат.")
                self.logs_manager.add_log(module="reference_calculations", event="Ошибка: conf_ref_vals имеет неверный формат.", log_type="ошибка")
                return

            min_x = ref_vals.get("x_range_min")
            max_x = ref_vals.get("target_x_max")
            self.scale_type = st.session_state.get("scale_type", "Линейная")  # По умолчанию линейная шкала
            step_size = st.session_state.get("linear_step_size", None)

            if min_x is None or max_x is None:
                st.error("Ошибка: отсутствуют значения min_x или max_x.")
                self.logs_manager.add_log(module="reference_calculations", event="Ошибка: отсутствуют значения x_range_min или target_x_max.", log_type="ошибка")
                return

            if min_x >= max_x:
                st.error("Ошибка: x_range_min должно быть меньше target_x_max.")
                self.logs_manager.add_log(module="reference_calculations", event="Ошибка: x_range_min >= target_x_max.", log_type="ошибка")
                return

            # Проверка шага линейной шкалы
            if self.scale_type == "Линейная":
                if step_size is None or not isinstance(step_size, (int, float)) or step_size <= 0:
                    st.warning("⚠ Шаг линейной шкалы не задан или некорректен. Используется значение по умолчанию: 1.")
                    step_size = 1  # Устанавливаем значение по умолчанию
                    self.logs_manager.add_log(module="reference_calculations", event="Шаг линейной шкалы не был задан или некорректен. Установлено значение по умолчанию: 1.", log_type="предупреждение")

            # Генерация шкалы в зависимости от типа
            if self.scale_type == "Логарифмическая":
                x_values = np.logspace(np.log10(min_x), np.log10(max_x), num=50)
                self.logs_manager.add_log(module="reference_calculations", event=f"Сгенерирована логарифмическая шкала (min_x={min_x}, max_x={max_x}).", log_type="успех")

            elif self.scale_type == "Линейная":
                x_values = np.arange(min_x, max_x + step_size, step_size)
                self.logs_manager.add_log(module="reference_calculations", event=f"Сгенерирована линейная шкала (min_x={min_x}, max_x={max_x}, step_size={step_size}).", log_type="успех")

            else:
                st.error("Ошибка: неизвестный тип шкалы.")
                self.logs_manager.add_log(module="reference_calculations", event=f"Ошибка: неизвестный тип шкалы {self.scale_type}.", log_type="ошибка")
                return

            # Проверка, была ли шкала успешно сгенерирована
            if len(x_values) == 0:
                st.error("Ошибка: шкала x_values пустая.")
                self.logs_manager.add_log(module="reference_calculations", event="Ошибка: шкала x_values пустая.", log_type="ошибка")
                return

            # Сохранение шкалы в session_state
            st.session_state["x_values"] = x_values

            # Логирование успешного выполнения и информации о шкале
            st.success(f"Шкала {self.scale_type} успешно сгенерирована!")
            self.logs_manager.add_log(module="reference_calculations", event=f"Шкала x_values успешно сгенерирована. Тип: {self.scale_type}, Шаг: {step_size if self.scale_type == 'Линейная' else 'N/A'}.", log_type="успех")

        except Exception as e:
            self.logs_manager.add_log(module="reference_calculations", event=f"Ошибка при генерации шкалы: {str(e)}", log_type="ошибка")
            st.error(f"Ошибка при генерации шкалы: {e}")

    def calculate_p_x(self):
        """
        Расчет эталонных значений P(x).
        """
        try:
            # Очистка предыдущих данных P(x)
            st.session_state.pop("P_x_data", None)

            if "x_values" not in st.session_state:
                st.error("Ошибка: x_values не сгенерированы. Сначала выполните generate_scale().")
                self.logs_manager.add_log(module="reference_calculations", event="Ошибка: x_values не сгенерированы перед расчетом P(x).", log_type="ошибка")
                return

            x_values = st.session_state["x_values"]
            if len(x_values) == 0:
                st.error("Ошибка: x_values пуст, расчёт P(x) невозможен.")
                self.logs_manager.add_log(module="reference_calculations", event="Ошибка: x_values пуст.", log_type="ошибка")
                return

            ref_vals = st.session_state.get("conf_ref_vals", {})

            if not isinstance(ref_vals, dict):
                st.error("Ошибка: conf_ref_vals имеет неверный формат.")
                self.logs_manager.add_log(module="reference_calculations", event="Ошибка: conf_ref_vals имеет неверный формат.", log_type="ошибка")
                return

            x_max = ref_vals.get("target_x_max")
            x_50 = ref_vals.get("target_x_50")
            b = ref_vals.get("target_b")

            # Проверяем, заданы ли все необходимые параметры
            if None in (x_max, x_50, b):
                st.error("Ошибка: отсутствуют эталонные параметры для расчета P(x).")
                self.logs_manager.add_log(module="reference_calculations", event="Ошибка: отсутствуют x_max, x_50 или b перед расчетом P(x).", log_type="ошибка")
                return

            # Проверяем, что параметры являются числами
            if not all(isinstance(val, (int, float)) for val in [x_max, x_50, b]):
                st.error("Ошибка: x_max, x_50 и b должны быть числами.")
                self.logs_manager.add_log(module="reference_calculations", event="Ошибка: x_max, x_50 и b должны быть числами.", log_type="ошибка")
                return

            # Проверяем, что x_50 < x_max (иначе log(x_max / x_50) = 0, деление на 0)
            if x_50 >= x_max:
                st.error("Ошибка: target_x_50 должно быть меньше target_x_max.")
                self.logs_manager.add_log(module="reference_calculations", event="Ошибка: target_x_50 >= target_x_max.", log_type="ошибка")
                return

            # Расчет P(x) по заданной формуле
            p_x_values = []
            for x in x_values:
                if x > x_max:  # Пропускаем некорректные значения
                    continue
                try:
                    p_x = 1 / (1 + (np.log(x_max / x) / np.log(x_max / x_50)) ** b)
                    p_x_values.append((x, p_x * 100))
                except ZeroDivisionError:
                    self.logs_manager.add_log(module="reference_calculations", event=f"Ошибка деления на 0 при расчете P(x) для x={x}.", log_type="ошибка")

            # Проверка, что после фильтрации есть данные
            if len(p_x_values) == 0:
                st.error("Ошибка: после фильтрации не осталось допустимых значений P(x).")
                self.logs_manager.add_log(module="reference_calculations", event="Ошибка: после фильтрации пустая таблица P(x).", log_type="ошибка")
                return

            df = pd.DataFrame(p_x_values, columns=["Размер фрагмента (x), мм", "Эталонные P(x), %"])

            # Сохранение данных в session_state
            st.session_state["P_x_data"] = df

            # Логирование успешного выполнения расчета
            self.logs_manager.add_log(module="reference_calculations", event=f"Эталонные P(x) успешно рассчитаны. Количество значений: {len(df)}", log_type="успех")
            st.success(f"Эталонные P(x) успешно рассчитаны! Количество значений: {len(df)}")

        except Exception as e:
            self.logs_manager.add_log(module="reference_calculations", event=f"Ошибка при расчете P(x): {str(e)}", log_type="ошибка")
            st.error(f"Ошибка при расчете P(x): {e}")

    def update_psd_table(self):
        """
        Обновляет таблицу PSD в session_state.
        """
        try:
            # Очистка предыдущих данных таблицы PSD
            st.session_state.pop("psd_table", None)

            if "P_x_data" not in st.session_state or st.session_state["P_x_data"] is None:
                st.error("Ошибка: нет данных для обновления таблицы PSD.")
                self.logs_manager.add_log(module="reference_calculations", event="Ошибка: отсутствуют данные P_x_data для обновления PSD.", log_type="ошибка")
                return

            df = st.session_state["P_x_data"]

            # Проверяем, не пуст ли DataFrame
            if df.empty:
                st.error("Ошибка: данные в таблице PSD пусты.")
                self.logs_manager.add_log(module="reference_calculations", event="Ошибка: Таблица PSD пустая, обновление невозможно.", log_type="ошибка")
                return

            # Обновляем session_state
            st.session_state["psd_table"] = df

            # Вывод данных пользователю
            st.write("### Эталонная таблица PSD")
            st.dataframe(df)

            # Логирование успешного обновления таблицы
            self.logs_manager.add_log(module="reference_calculations", 
                                    event=f"Таблица PSD обновлена. Количество записей: {len(df)}.", 
                                    log_type="успех")

            # Вывод подтверждения пользователю
            st.success("Таблица PSD успешно обновлена!")

        except Exception as e:
            self.logs_manager.add_log(module="reference_calculations", event=f"Ошибка при обновлении PSD: {str(e)}", log_type="ошибка")
            st.error(f"Ошибка при обновлении PSD: {e}")

