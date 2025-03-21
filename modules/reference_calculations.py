import streamlit as st
import numpy as np
import pandas as pd
from utils.session_state_manager import SessionStateManager
from utils.logs_manager import LogsManager

class ReferenceCalculations:
    """
    Класс для выполнения расчетов эталонных значений.
    """
    def __init__(self, session_manager: SessionStateManager, logs_manager: LogsManager):
        self.session_manager = session_manager
        self.logs_manager = logs_manager
        self.ref_table = None  # Таблица эталонных значений

        # Проверка типа шкалы перед инициализацией
        if "scale_type" not in st.session_state:
            st.session_state["scale_type"] = "Логарифмическая"  # Установлено по умолчанию


        # Инициализация хранилищ данных
        if "P_x_data" not in st.session_state:
            st.session_state["P_x_data"] = {}

        if "psd_table" not in st.session_state:
            st.session_state["psd_table"] = {}

    def render_scale_type_selection(self):
        """
        Выбор типа шкалы (логарифмическая/линейная) с возможностью задания шага для линейной шкалы.
        """
        st.subheader("Выберите тип шкалы")
    
        # Проверяем, установлен ли scale_type в session_state
        # scale_type_default = st.session_state.get("scale_type", "Логарифмическая")
       
    
        # Выбор типа шкалы пользователем
        new_scale_type = st.radio(
            label="Тип шкалы",
            options=["Линейная","Логарифмическая"],
            index=0 if scale_type_default == "Логарифмическая" else 1
        )
    
        # Если выбрана линейная шкала – отображаем ввод шага
        if new_scale_type == "Линейная":
            step_size_default = st.session_state.get("linear_step_size", 1.0)
            new_step_size = st.number_input(
                label="Шаг для линейной шкалы",
                min_value=0.1,
                max_value=10.0,
                value=step_size_default,
                step=0.1
            )
            # Обновляем шаг в session_state
            st.session_state["linear_step_size"] = new_step_size
    
        # Обновляем тип шкалы в session_state
        if new_scale_type != st.session_state.get("scale_type"):
            st.session_state["scale_type"] = new_scale_type
            self.logs_manager.add_log(
                module="reference_calculations",
                event=f"Тип шкалы изменён пользователем: {new_scale_type}",
                log_type="info"
            )

    
    def generate_scale(self):
        """
        Генерация шкалы x_values в зависимости от типа шкалы.
        """
        try:
            # Очистка предыдущих значений шкалы
            st.session_state.pop("x_values", None)
    
            # Проверка наличия параметров
            params = st.session_state.get("parameters", {})
            if not params:
                st.error("Ошибка: параметры не загружены.")
                self.logs_manager.add_log("reference_calculations", "Ошибка: параметры отсутствуют в session_state.", "ошибка")
                return
    
            # Получение значений min_x и max_x
            min_x = params.get("x_range_min", {}).get("default_value")
            max_x = params.get("target_x_max", {}).get("default_value")
            step_size = st.session_state.get("linear_step_size", 1.0)  # Значение по умолчанию
            scale_type = st.session_state.get("scale_type", "Линейная")  # Значение по умолчанию
    
            # Проверка корректности значений
            if min_x is None or max_x is None:
                st.error("Ошибка: отсутствуют значения x_range_min или target_x_max.")
                self.logs_manager.add_log("reference_calculations", "Ошибка: отсутствуют x_range_min или target_x_max.", "ошибка")
                return
    
            if min_x >= max_x:
                st.error("Ошибка: x_range_min должно быть меньше target_x_max.")
                self.logs_manager.add_log("reference_calculations", "Ошибка: x_range_min >= target_x_max.", "ошибка")
                return
    
            if scale_type == "Линейная" and (not isinstance(step_size, (int, float)) or step_size <= 0):
                st.warning("⚠ Некорректный шаг линейной шкалы. Используется значение по умолчанию: 1.0")
                step_size = 1.0
                self.logs_manager.add_log("reference_calculations", "Шаг линейной шкалы был некорректен, установлено значение 1.0.", "предупреждение")
    
            # Генерация шкалы
            if scale_type == "Логарифмическая":
                x_values = np.logspace(np.log10(min_x), np.log10(max_x), num=50)
                self.logs_manager.add_log("reference_calculations", f"Сгенерирована логарифмическая шкала (min_x={min_x}, max_x={max_x}).", "успех")
    
            elif scale_type == "Линейная":
                x_values = np.arange(min_x, max_x + step_size, step_size)
                self.logs_manager.add_log("reference_calculations", f"Сгенерирована линейная шкала (min_x={min_x}, max_x={max_x}, step_size={step_size}).", "успех")
    
            else:
                st.error("Ошибка: неизвестный тип шкалы.")
                self.logs_manager.add_log("reference_calculations", f"Ошибка: неизвестный тип шкалы {scale_type}.", "ошибка")
                return
    
            # Проверка, что шкала успешно создана
            if len(x_values) == 0:
                st.error("Ошибка: шкала x_values пустая.")
                self.logs_manager.add_log("reference_calculations", "Ошибка: шкала x_values пустая.", "ошибка")
                return
    
            # Сохранение шкалы в session_state
            st.session_state["x_values"] = x_values
    
            # Логирование успешного выполнения
            st.success(f"Шкала {scale_type} успешно сгенерирована!")
            self.logs_manager.add_log("reference_calculations", f"Шкала успешно создана. Тип: {scale_type}, Шаг: {step_size if scale_type == 'Линейная' else 'N/A'}.", "успех")
    
        except Exception as e:
            self.logs_manager.add_log("reference_calculations", f"Ошибка при генерации шкалы: {str(e)}", "ошибка")
            st.error(f"Ошибка при генерации шкалы: {e}")


    def calculate_p_x(self):
        """
        Расчет эталонных значений P(x) на основе загруженных параметров.
        """
        try:
            # Очистка предыдущих данных P(x)
            # st.session_state.pop("P_x_data", None)
            if "P_x_data" in st.session_state:
                st.session_state["P_x_data"] = None

    
            # Проверка наличия шкалы x_values
            x_values = st.session_state.get("x_values")
            # if not x_values or len(x_values) == 0:
            if x_values is None or x_values.size == 0:

                st.error("Ошибка: шкала x_values отсутствует. Сначала выполните generate_scale().")
                self.logs_manager.add_log("reference_calculations", "Ошибка: x_values отсутствуют перед расчетом P(x).", "ошибка")
                return
    
            # Проверка наличия параметров в session_state
            params = st.session_state.get("parameters", {})
            if not params:
                st.error("Ошибка: параметры не загружены.")
                self.logs_manager.add_log("reference_calculations", "Ошибка: параметры отсутствуют в session_state.", "ошибка")
                return
    
            # Получаем необходимые параметры
            x_max = params.get("target_x_max", {}).get("default_value")
            x_50 = params.get("target_x_50", {}).get("default_value")
            b = params.get("target_b", {}).get("default_value")
    
            # Проверка, что параметры не пустые
            if None in (x_max, x_50, b):
                st.error("Ошибка: отсутствуют обязательные параметры target_x_max, target_x_50 или target_b.")
                self.logs_manager.add_log("reference_calculations", "Ошибка: отсутствуют x_max, x_50 или b перед расчетом P(x).", "ошибка")
                return
    
            # Проверяем, что параметры являются числами
            if not all(isinstance(val, (int, float)) for val in [x_max, x_50, b]):
                st.error("Ошибка: target_x_max, target_x_50 и target_b должны быть числами.")
                self.logs_manager.add_log("reference_calculations", "Ошибка: target_x_max, target_x_50 и target_b должны быть числами.", "ошибка")
                return
    
            # Проверяем, что x_50 < x_max
            if x_50 >= x_max:
                st.error("Ошибка: target_x_50 должно быть меньше target_x_max.")
                self.logs_manager.add_log("reference_calculations", "Ошибка: target_x_50 >= target_x_max.", "ошибка")
                return
    
            # Расчет P(x) по формуле
            p_x_values = []
            for x in x_values:
                if x > x_max:  # Пропускаем некорректные значения
                    continue
                try:
                    p_x = 1 / (1 + (np.log(x_max / x) / np.log(x_max / x_50)) ** b)
                    p_x_values.append((x, p_x * 100))
                except ZeroDivisionError:
                    self.logs_manager.add_log("reference_calculations", f"Ошибка деления на 0 при расчете P(x) для x={x}.", "ошибка")
    
            # Проверяем, что после фильтрации остались значения
            if len(p_x_values) == 0:
                st.error("Ошибка: после фильтрации не осталось допустимых значений P(x).")
                self.logs_manager.add_log("reference_calculations", "Ошибка: после фильтрации пустая таблица P(x).", "ошибка")
                return
    
            # Создаем DataFrame
            df = pd.DataFrame(p_x_values, columns=["Размер фрагмента (x), мм", "Эталонные P(x), %"])
    
            # Сохраняем данные в session_state
            st.session_state["P_x_data"] = df
    
            # Логируем успешный расчет
            self.logs_manager.add_log("reference_calculations", f"Эталонные P(x) успешно рассчитаны. Количество значений: {len(df)}", "успех")
            st.success(f"Эталонные P(x) успешно рассчитаны! Количество значений: {len(df)}")
    
        except Exception as e:
            self.logs_manager.add_log("reference_calculations", f"Ошибка при расчете P(x): {str(e)}", "ошибка")
            st.error(f"Ошибка при расчете P(x): {e}")

    def update_psd_table(self):
        """
        Обновляет таблицу PSD в session_state.
        """
        try:
            # Очистка предыдущих данных таблицы PSD
            st.session_state.pop("psd_table", None)
    
            # Проверяем наличие данных P_x_data
            df = st.session_state.get("P_x_data")
    
            if df is None or df.empty:
                st.error("Ошибка: нет данных для обновления таблицы PSD.")
                self.logs_manager.add_log("reference_calculations", "Ошибка: отсутствуют данные P_x_data для обновления PSD.", "ошибка")
                return
    
            # Проверяем, содержатся ли необходимые колонки
            required_columns = {"Размер фрагмента (x), мм", "Эталонные P(x), %"}
            if not required_columns.issubset(df.columns):
                st.error("Ошибка: данные P_x_data имеют неверный формат.")
                self.logs_manager.add_log("reference_calculations", "Ошибка: неверный формат данных P_x_data при обновлении PSD.", "ошибка")
                return
    
            # Сортировка данных по убыванию размера фрагментов (от большего к меньшему)
            df_sorted = df.sort_values(by="Размер фрагмента (x), мм", ascending=False).reset_index(drop=True)
    
            # Сохраняем в session_state
            st.session_state["psd_table"] = df_sorted
    
            # Проверка перед выводом
            st.write("### Проверка данных перед выводом")
            st.write(df_sorted)
    
            # Вывод данных пользователю
            st.write("### Эталонная таблица PSD")
            st.dataframe(st.session_state["psd_table"])  # Используем данные из session_state
    
            # Логирование успешного обновления таблицы
            self.logs_manager.add_log(
                "reference_calculations",
                f"Таблица PSD обновлена. Количество записей: {len(df_sorted)}.",
                "успех"
            )
    
            # Вывод подтверждения пользователю
            st.success("✅ Таблица PSD успешно обновлена!")
    
        except Exception as e:
            self.logs_manager.add_log("reference_calculations", f"Ошибка при обновлении PSD: {str(e)}", "ошибка")
            st.error(f"Ошибка при обновлении PSD: {e}")

