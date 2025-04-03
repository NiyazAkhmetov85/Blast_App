import streamlit as st
import pandas as pd
import numpy as np

from utils.logs_manager import LogsManager
from utils.session_state_manager import SessionStateManager

class PSDCalculator:
    """
    Класс для расчета P(x) (рассчитанные) и формирования PSD-таблицы.
    """
    def __init__(self, session_manager: SessionStateManager, logs_manager: LogsManager):
        self.session_manager = session_manager
        self.logs_manager = logs_manager

    def run_calculations(self):
        """
        Запускает расчёты P(x) рассчитанные и обновляет таблицу PSD.
        """
        self.calculate_p_x_calculated()
        self.generate_psd_table()

    def calculate_p_x_calculated(self):
        """
        Рассчитывает P(x) рассчитанные на основе параметров БВР.
        """
        try:
            x_values = st.session_state.get("x_values", [])
            if not x_values:
                st.sidebar.error("Ошибка: x_values не найдены.")
                return

            params = st.session_state.get("calculation_results", {})
            x_max = params.get("x_max", 1000)
            x_50 = params.get("x_50", 200)
            b = params.get("b", 3.5)

            p_x_calculated = [(x, (1 / (1 + (np.log(x_max / x) / np.log(x_max / x_50)) ** b)) * 100) for x in x_values if x <= x_max]

            df = pd.DataFrame(p_x_calculated, columns=["Размер фрагмента (x), мм", "P(x) рассчитанные, %"])
            st.session_state["P_x_calculated"] = df
            st.sidebar.success("P(x) рассчитанные успешно вычислены.")
            self.logs_manager.add_log("psd_calculator", "P(x) рассчитанные успешно вычислены.", "успех")

        except Exception as e:
            st.sidebar.error(f"Ошибка при расчете P(x) рассчитанные: {e}")
            self.logs_manager.add_log("psd_calculator", f"Ошибка при расчете P(x) рассчитанные: {e}", "ошибка")

    def generate_psd_table(self):
        """
        Формирует итоговую таблицу PSD.
        """
        try:
            df_reference = st.session_state.get("P_x_data")
            df_calculated = st.session_state.get("P_x_calculated")
    
            if df_reference is None or df_calculated is None:
                raise ValueError("Отсутствуют необходимые данные в st.session_state.")
    
            if df_reference.empty or df_calculated.empty:
                raise ValueError("Один из DataFrame пустой.")
    
            if "Размер фрагмента (x), мм" not in df_reference.columns or "Размер фрагмента (x), мм" not in df_calculated.columns:
                raise ValueError("Отсутствует столбец 'Размер фрагмента (x), мм' в одном из DataFrame.")
    
            df_psd = pd.merge(df_reference, df_calculated, on="Размер фрагмента (x), мм", how="outer").fillna(0)
            st.session_state["psd_table"] = df_psd
            st.sidebar.success("✅ Итоговая PSD-таблица успешно сформирована.")
            self.logs_manager.add_log("psd_calculator", "✅ Итоговая PSD-таблица успешно сформирована.", "успех")
    
        except Exception as e:
            st.sidebar.error(f"Ошибка при создании PSD-таблицы: {e}")
            self.logs_manager.add_log("psd_calculator", f"❌ Ошибка при создании PSD-таблицы: {e}", "ошибка")

    # def generate_psd_table(self):
    #     """
    #     Формирует итоговую таблицу PSD.
    #     """
    #     try:
    #         df_reference = st.session_state.get("P_x_data")
    #         df_calculated = st.session_state.get("P_x_calculated")
    #         df_psd = pd.merge(df_reference, df_calculated, on="Размер фрагмента (x), мм", how="outer").fillna(0)
    #         st.session_state["psd_table"] = df_psd
    #         st.sidebar.success("✅ Итоговая PSD-таблица успешно сформирована.")
    #         self.logs_manager.add_log("psd_calculator", "✅ Итоговая PSD-таблица успешно сформирована.", "успех")
    
    #     except Exception as e:
    #         st.sidebar.error(f"Ошибка при создании PSD-таблицы: {e}")
    #         self.logs_manager.add_log("psd_calculator", f"❌ Ошибка при создании PSD-таблицы: {e}", "ошибка")

