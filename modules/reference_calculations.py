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

        # Устанавливаем логарифмическую шкалу по умолчанию
        st.session_state.setdefault("scale_type", "Логарифмическая")
        st.session_state.setdefault("P_x_data", {})
        st.session_state.setdefault("psd_table", {})

    def generate_scale(self):
        """
        Генерация логарифмической шкалы x_values.
        """
        try:
            st.session_state.pop("x_values", None)
            
            params = st.session_state.get("parameters", {})
            if not params:
                st.error("Ошибка: параметры не загружены.")
                self.logs_manager.add_log("reference_calculations", "Ошибка: параметры отсутствуют в session_state.", "ошибка")
                return

            min_x = params.get("x_range_min", {}).get("default_value")
            max_x = params.get("target_x_max", {}).get("default_value")
            
            if min_x is None or max_x is None or min_x >= max_x:
                st.error("Ошибка: некорректные значения x_range_min или target_x_max.")
                self.logs_manager.add_log("reference_calculations", "Ошибка: некорректные значения x_range_min или target_x_max.", "ошибка")
                return

            x_values = np.logspace(np.log10(min_x), np.log10(max_x), num=50)
            st.session_state["x_values"] = x_values

            st.success("Логарифмическая шкала успешно сгенерирована!")
            self.logs_manager.add_log("reference_calculations", "Шкала успешно сгенерирована.", "успех")
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
            df = df.sort_values(by="Размер фрагмента (x), мм", ascending=False)  # Сортировка от максимума к минимуму

            st.session_state["P_x_data"] = df
            
            st.success("Расчеты выполнены успешно!")
            self.logs_manager.add_log("reference_calculations", "Расчеты выполнены успешно.", "успех")

            st.subheader("Результаты расчетов")
            st.dataframe(df)
        except Exception as e:
            st.error(f"Ошибка выполнения расчетов: {e}")
            self.logs_manager.add_log("reference_calculations", f"Ошибка выполнения расчетов: {e}", "ошибка")

    def render_ui(self):
        """
        Отображение UI.
        """
        st.sidebar.header("Настройки расчета")
        if st.sidebar.button("Запустить расчеты"):
            self.run_calculations()
