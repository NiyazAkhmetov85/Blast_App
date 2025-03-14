import streamlit as st
from utils.session_state_manager import SessionStateManager
from utils.logs_manager import LogsManager
from modules.data_initializer import DataInitializer
from ui.navigation import navigation

# ✅ Установка параметров страницы ДО отображения заголовка
st.set_page_config(page_title="Blast Optimization App", layout="wide")

# ✅ Инициализация логирования и состояния
logs_manager = LogsManager()
session_manager = SessionStateManager()
data_initializer = DataInitializer(session_manager, logs_manager)

# ✅ Отображение заголовка
st.title("Blast Optimization App")

# ✅ Отображение статусной строки
def show_status_bar():
    st.markdown("---")
    st.info(st.session_state["status_message"])
    st.sidebar.info(st.session_state["status_message"])

show_status_bar()

# ✅ Логируем запуск приложения
logs_manager.add_log(module="main", event="Приложение запущено", log_type="успех")
