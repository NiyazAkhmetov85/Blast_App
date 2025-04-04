import numpy as np
import pandas as pd
import streamlit as st
from utils.session_state_manager import SessionStateManager
from utils.logs_manager import LogsManager
from modules.reference_parameters import ReferenceParameters
from modules.reference_calculations import ReferenceCalculations

class RefValues:
    def __init__(self, session_manager: SessionStateManager, logs_manager: LogsManager):
        self.session_manager = session_manager
        self.logs_manager = logs_manager
        self.reference_parameters = ReferenceParameters(session_manager, logs_manager)
        self.reference_calculations = ReferenceCalculations(session_manager, logs_manager)

    def show_reference_values(self):
        """
        Экран для работы с эталонными значениями БВР.
        """
        st.header("Эталонные значения БВР")
    
        # ✅ Отображаем имя текущего блока
        block_name = st.session_state.get("block_name", "Неизвестный блок")

        if not block_name or block_name == "Неизвестный блок":
            st.warning("Блок не импортирован. Импортируйте блок на вкладке 'Импорт данных блока'.")
        else:
            st.info(f"Импортированный блок: **{block_name}**")
    
        # ✅ Отображаем эталонные показатели
        self.reference_parameters.render_refparameters_section()

        self.reference_calculations.render_ui()
