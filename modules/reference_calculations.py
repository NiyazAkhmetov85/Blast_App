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
        st.session_state.setdefault("scale_type", "Логарифмическая")
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
                st.error("Ошибка: параметры не загружены.")
                self.logs_manager.add_log("reference_calculations", "Ошибка: параметры отсутствуют в session_state.", "ошибка")
                return

            max_x = params.get("target_x_max", 1000)  # Исправлено: теперь max_x всегда число
            max_x = self.round_to_nearest_100(max_x)
            x_values = [x for x in self.STANDARD_X_VALUES if x <= max_x]
            st.session_state["x_values"] = x_values

            self.logs_manager.add_log("reference_calculations", f"Шкала успешно сгенерирована до {max_x} мм.", "успех")
        except Exception as e:
            st.error(f"Ошибка генерации шкалы: {e}")
            self.logs_manager.add_log("reference_calculations", f"Ошибка генерации шкалы: {e}", "ошибка")

    def run_calculations(self):
        """
        Запуск всех расчетов и отображение результатов.
        """
        try:
            self.generate_scale()
            
            if "x_values" not in st.session_state:
                return
            
            x_values = st.session_state["x_values"]
            P_x_data = np.cumsum(np.random.rand(len(x_values)))  # Заглушка для расчетов
            P_x_data /= P_x_data[-1]  # Нормализация

            df = pd.DataFrame({"Размер фрагмента (x), мм": x_values, "Эталонные P(x), %": P_x_data * 100})
            df = df.sort_values(by="Размер фрагмента (x), мм", ascending=True)  # Сортировка от минимума к максимуму

            st.session_state["P_x_data"] = df
            self.logs_manager.add_log("reference_calculations", "Расчеты выполнены успешно.", "успех")

            self.update_psd_table()
            self.visualize_cumulative_curve()
        except Exception as e:
            st.error(f"Ошибка выполнения расчетов: {e}")
            self.logs_manager.add_log("reference_calculations", f"Ошибка выполнения расчетов: {e}", "ошибка")

    def update_psd_table(self):
        """
        Обновляет таблицу PSD в session_state.
        """
        try:
            df = st.session_state.get("P_x_data")
            if df is None or df.empty:
                st.error("Ошибка: нет данных для обновления таблицы PSD.")
                self.logs_manager.add_log("reference_calculations", "Ошибка: отсутствуют данные P_x_data для обновления PSD.", "ошибка")
                return

            df_sorted = df.sort_values(by="Размер фрагмента (x), мм", ascending=True).reset_index(drop=True)
            st.session_state["psd_table"] = df_sorted

            st.success("✅ Таблица PSD успешно обновлена!")
            self.logs_manager.add_log("reference_calculations", "Таблица PSD обновлена.", "успех")
            st.subheader("Результаты расчетов")
            st.dataframe(df_sorted)
        except Exception as e:
            st.error(f"Ошибка обновления PSD: {e}")
            self.logs_manager.add_log("reference_calculations", f"Ошибка обновления PSD: {e}", "ошибка")

    def visualize_cumulative_curve(self):
        """
        Визуализация эталонной кумулятивной кривой распределения.
        """
        try:
            df = st.session_state.get("P_x_data")
            if df is None or df.empty:
                st.warning("Нет данных для построения графика.")
                return

            fig = px.line(df, x="Размер фрагмента (x), мм", y="Эталонные P(x), %",
                          title="Эталонная кумулятивная кривая распределения",
                          labels={"Размер фрагмента (x), мм": "Размер фрагмента (мм)", "Эталонные P(x), %": "Кумулятивное распределение (%)"})
            fig.update_traces(mode='lines+markers')
            st.plotly_chart(fig)
        except Exception as e:
            st.error(f"Ошибка визуализации кривой: {e}")
            self.logs_manager.add_log("reference_calculations", f"Ошибка визуализации кривой: {e}", "ошибка")

    def render_ui(self):
        """
        Отображение UI.
        """
        if st.button("Запустить расчеты"):
            self.run_calculations()
