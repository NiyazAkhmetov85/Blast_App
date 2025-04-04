import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px

from utils.session_state_manager import SessionStateManager
from utils.logs_manager import LogsManager

class ReferenceCalculations:
    """
    Класс для выполнения расчетов эталонных значений.
    """
    STANDARD_X_VALUES = [
        0.07, 0.25, 1, 2, 4, 8, 12, 16, 20, 25, 32, 40, 50, 60, 90, 125, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500
    ]

    def __init__(self, session_manager: SessionStateManager, logs_manager: LogsManager):
        self.session_manager = session_manager
        self.logs_manager = logs_manager
        self.ref_table = None  # Таблица эталонных значений

        # Устанавливаем стандартные параметры
        st.session_state.setdefault("P_x_data", {})
        st.session_state.setdefault("psd_table", {})

    def round_to_nearest_100(self, value):
        """
        Округление значения до ближайшего кратного 100.
        """
        return min(round(value / 100) * 100, 1000)  # Ограничиваем x_max 1000 мм

    def generate_scale(self):
        """
        Генерация шкалы x_values по стандартным значениям.
        """
        try:
            st.session_state.pop("x_values", None)
            params = st.session_state.get("reference_parameters", {})
            if not params:
                st.sidebar.error("Ошибка: параметры не загружены.")
                self.logs_manager.add_log("reference_calculations", "Ошибка: параметры отсутствуют в session_state.", "ошибка")
                return

            max_x = params.get("target_x_max", 1000)  # Теперь max_x всегда число
            max_x = self.round_to_nearest_100(max_x)
            x_values = [x for x in self.STANDARD_X_VALUES if x <= max_x]
            st.session_state["x_values"] = x_values

            self.logs_manager.add_log("reference_calculations", f"Шкала успешно сгенерирована до {max_x} мм.", "успех")
        except Exception as e:
            st.sidebar.error(f"Ошибка генерации шкалы: {e}")
            self.logs_manager.add_log("reference_calculations", f"Ошибка генерации шкалы: {e}", "ошибка")

    def run_calculations(self):
        """
        Запуск всех расчетов и отображение результатов.
        """
        try:
            # Генерация шкалы
            self.generate_scale()

            if "x_values" not in st.session_state:
                return

            x_values = st.session_state["x_values"]
            
            # Получаем эталонные параметры для расчёта P(x)
            params = st.session_state.get("reference_parameters", {})
            x_max_ref = params.get("target_x_max", 1000)
            x_50 = params.get("target_x_50")
            b = params.get("target_b")
            
            # Проверяем, что параметры корректны
            if any(val is None or not isinstance(val, (int, float)) for val in [x_max_ref, x_50, b]):
                st.sidebar.error("Ошибка: параметры должны быть числами и не должны быть пустыми.")
                self.logs_manager.add_log("reference_calculations", "Некорректные параметры: target_x_max, target_x_50, target_b.", "ошибка")
                return

            # Расчет P(x) по формуле для каждого x из x_values
            p_x_values = []
            for x in x_values:
                if x > x_max_ref:  # Пропускаем значения, превышающие заданный x_max
                    continue
                try:
                    num = np.log(x_max_ref / x)
                    den = np.log(x_max_ref / x_50)
                    if den == 0:  # Пропуск деления на 0
                        continue
                    p_x = 1 / (1 + (num / den) ** b)
                    p_x_values.append((x, p_x * 100))  # Переводим в проценты
                except Exception as calc_e:
                    self.logs_manager.add_log("reference_calculations", f"Ошибка при расчете P(x) для x={x}: {calc_e}", "ошибка")

            if len(p_x_values) == 0:
                st.sidebar.error("Ошибка: после расчета не осталось допустимых значений P(x).")
                self.logs_manager.add_log("reference_calculations", "Пустой расчет P(x) после фильтрации.", "ошибка")
                return

            # Создаем DataFrame
            df = pd.DataFrame(p_x_values, columns=["Размер фрагмента (x), мм", "Эталонные P(x), %"])
            df = df.sort_values(by="Размер фрагмента (x), мм", ascending=True)

            st.session_state["P_x_data"] = df
            self.logs_manager.add_log("reference_calculations", "Расчеты эталонных P(x) выполнены успешно.", "успех")

            self.update_psd_table()
        except Exception as e:
            st.sidebar.error(f"Ошибка выполнения расчетов: {e}")
            self.logs_manager.add_log("reference_calculations", f"Ошибка выполнения расчетов: {e}", "ошибка")

    def update_psd_table(self):
        """
        Обновляет таблицу PSD в session_state.
        """
        try:
            df = st.session_state.get("P_x_data")
            if not isinstance(df, pd.DataFrame) or df.empty:
                st.sidebar.error("Ошибка: нет данных для обновления таблицы PSD.")
                self.logs_manager.add_log("reference_calculations", "Ошибка: отсутствуют данные P_x_data для обновления PSD.", "ошибка")
                return

            df_sorted = df.sort_values(by="Размер фрагмента (x), мм", ascending=True).reset_index(drop=True)
            st.session_state["psd_table"] = df_sorted

            st.sidebar.success("Таблица PSD успешно обновлена!")
            self.logs_manager.add_log("reference_calculations", "Таблица PSD обновлена.", "успех")

            st.subheader("Результаты расчетов")
            st.text("Таблица распределения фрагментов (PSD)")
            st.dataframe(df_sorted)
        except Exception as e:
            st.sidebar.error(f"Ошибка обновления PSD: {e}")
            self.logs_manager.add_log("reference_calculations", f"Ошибка обновления PSD: {e}", "ошибка")   

    def visualize_cumulative_curve(self):
        """
        Визуализация эталонной кумулятивной кривой распределения.
        """
        try:
            df = st.session_state.get("P_x_data")
            if not isinstance(df, pd.DataFrame) or df.empty:
                st.sidebar.warning("Нет данных для построения графика.")
                return

            fig = px.line(df, x="Размер фрагмента (x), мм", y="Эталонные P(x), %",
                          title="Эталонная кумулятивная кривая распределения",
                          labels={"Размер фрагмента (x), мм": "Размер фрагмента (мм)", "Эталонные P(x), %": "Кумулятивное распределение (%)"})
            fig.update_traces(mode='lines+markers')
            st.plotly_chart(fig)
        except Exception as e:
            st.sidebar.error(f"Ошибка визуализации кривой: {e}")
            self.logs_manager.add_log("reference_calculations", f"Ошибка визуализации кривой: {e}", "ошибка")
