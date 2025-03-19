import streamlit as st
from utils.session_state_manager import SessionStateManager
from utils.logs_manager import LogsManager

def show_reference_values():
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
