import numpy as np
import pandas as pd
import streamlit as st

from utils.session_state_manager import SessionStateManager
from utils.logs_manager import LogsManager

from modules.reference_parameters import ReferenceParameters
from modules.reference_calculations import ReferenceCalculations
from modules.reference_visualization import RefVisualization

class RefValues:
    def __init__(self, session_manager: SessionStateManager, logs_manager: LogsManager):
        self.session_manager = session_manager
        self.logs_manager = logs_manager
        self.reference_parameters = ReferenceParameters(session_manager, logs_manager)
        self.reference_calculations = ReferenceCalculations(session_manager, logs_manager)
        self.reference_visualization = RefVisualization(session_manager, logs_manager)

    def show_reference_values(self):
        """
        Экран для работы с эталонными значениями БВР.
        """
        st.header("Эталонные значения БВР")
    
        # Отображаем имя текущего блока
        block_name = st.session_state.get("block_name", "Неизвестный блок")

        if not block_name or block_name == "Неизвестный блок":
            st.warning("Блок не импортирован. Импортируйте блок на вкладке 'Импорт данных блока'.")
        else:
            st.info(f"Импортированный блок: **{block_name}**")
    
        # Отображаем эталонные показатели
        self.reference_parameters.render_refparameters_section()

        # Отображаем интерфейс для запуска расчетов
        self.render_calculations_ui()

    def render_calculations_ui(self):
        """
        Интерфейс для запуска расчетов эталонных значений (PSD) с автоматической визуализацией.
        """
        st.subheader("Запуск расчетов эталонных значений (PSD)")
    
        # Кнопка для запуска расчетов
        if st.button("Запустить расчеты"):
            try:
                # Выполняем расчеты
                self.reference_calculations.run_calculations()
                st.sidebar.success("Расчеты успешно выполнены!")

                # Автоматическая визуализация результатов
                self.reference_visualization.visualize_psd_table()
                self.reference_visualization.visualize_cumulative_curve()
            except Exception as e:
                st.sidebar.error(f"Ошибка при выполнении расчетов: {e}")
