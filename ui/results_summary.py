import streamlit as st

from modules.calculations import Calculations
from modules.psd_calculator import PSDCalculator
from modules.results_display import ResultsDisplay
from modules.psdvisualization import PSDVisualization

from utils.session_state_manager import SessionStateManager
from utils.logs_manager import LogsManager

class ResultsSummary:
    """
    Экран для отображения итоговых расчётов, таблицы PSD и визуализации результатов.
    """
    def __init__(self, session_manager: SessionStateManager, logs_manager: LogsManager):
        self.session_manager = session_manager
        self.logs_manager = logs_manager
        self.calculator = Calculations(session_manager, logs_manager)
        self.psd_calculator = PSDCalculator(session_manager, logs_manager)
        self.results_display = ResultsDisplay(session_manager, logs_manager)
        self.psdvisualization = PSDVisualization(session_manager, logs_manager)

    def show_results_summary(self):
        st.title("Итоговые расчёты параметров БВР")

                # Отображаем имя текущего блока
        block_name = st.session_state.get("block_name", "Неизвестный блок")

        if not block_name or block_name == "Неизвестный блок":
            st.warning("Блок не импортирован. Импортируйте блок на вкладке 'Импорт данных блока'.")
        else:
            st.info(f"Импортированный блок: **{block_name}**")

        # Кнопка запуска расчётов параметров БВР
        if st.button("Запустить расчеты БВР"):
            self.calculator.run_all_calculations()

        # Кнопка запуска расчётов PSD
        if st.button("Рассчитать Таблицу PSD и кумулятивную кривую"):
            self.psd_calculator.run_calculations()            
            self.psdvisualization.visualize_ref_psd_table()
            self.psdvisualization.visualize_ref_cumulative_curve()   

            # if "P_x_data" in st.session_state:
            #     st.write(st.session_state["P_x_data"].head())
