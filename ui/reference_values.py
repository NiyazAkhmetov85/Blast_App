import streamlit as st
from utils.session_state_manager import SessionStateManager
from utils.logs_manager import LogsManager
from modules.reference_parameters import ReferenceParameters

class RefValues:
    def __init__(self, session_manager: SessionStateManager, logs_manager: LogsManager):
        self.session_manager = session_manager
        self.logs_manager = logs_manager


    def show_reference_values(self):
        """
        Экран для работы с эталонными значениями БВР.
        """
        st.header("📌 Эталонные значения БВР")
    
        session_manager = SessionStateManager()
        logs_manager = LogsManager()
        
        # ✅ Отображаем имя текущего блока
        # Проверяем наличие имени блока
        block_name = st.session_state.get("block_name", "Неизвестный блок")
    
        if not block_name or block_name == "Неизвестный блок":
            st.warning("Блок не импортирован. Импортируйте блок на вкладке 'Импорт данных блока'.")
        else:
            st.info(f"Импортированный блок: **{block_name}**")

        # ✅ Создаем объект ReferenceParameters и рендерим параметры
        ref_params = ReferenceParameters(self.session_manager, self.logs_manager)
        ref_params.render_refparameters_section()
