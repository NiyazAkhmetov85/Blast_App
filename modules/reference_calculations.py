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
            
            params = st.session_state.get("reference_parameters", {})
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

            self.logs_manager.add_log("reference_calculations", "Логарифмическая шкала успешно сгенерирована.", "успех")
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
            self.logs_manager.add_log("reference_calculations", "Расчеты выполнены успешно.", "успех")

            self.update_psd_table()
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

            df_sorted = df.sort_values(by="Размер фрагмента (x), мм", ascending=False).reset_index(drop=True)
            st.session_state["psd_table"] = df_sorted

            st.success("✅ Таблица PSD успешно обновлена!")
            self.logs_manager.add_log("reference_calculations", "Таблица PSD обновлена.", "успех")
            st.subheader("Результаты расчетов")
            st.dataframe(df_sorted)
        except Exception as e:
            st.error(f"Ошибка обновления PSD: {e}")
            self.logs_manager.add_log("reference_calculations", f"Ошибка обновления PSD: {e}", "ошибка")

    def render_ui(self):
        """
        Отображение UI.
        """
        # st.sidebar.header("Настройки расчета")
        if st.button("Запустить расчеты"):
            self.run_calculations()
