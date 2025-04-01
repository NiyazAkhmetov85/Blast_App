import streamlit as st

# ✅ Первая команда в Streamlit-приложении
st.set_page_config(page_title="Blast Optimization App", layout="wide")

# ✅ Устанавливаем масштабирование приложения на 80%
st.markdown(
    """
    <style>
        body {
            zoom: 80%;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ✅ Импорты менеджеров и загрузчиков
from utils.session_state_manager import SessionStateManager
from utils.logs_manager import LogsManager
from modules.data_initializer import DataInitializer

# ✅ Создание экземпляров менеджеров
session_manager = SessionStateManager()
logs_manager = LogsManager()
data_initializer = DataInitializer(session_manager, logs_manager)

# ✅ Инициализация параметров при первом запуске
if "parameters" not in st.session_state or "user_parameters" not in st.session_state:
    data_initializer.load_default_parameters()
    logs_manager.add_log("main", "Параметры инициализированы при старте", "информация")

# ✅ Однократное приветствие (опционально)
if "app_initialized" not in st.session_state:
    st.info("👋 Добро пожаловать в приложение *Blast Optimization App*.\n\nВыберите вкладку слева для начала работы.")
    st.session_state["app_initialized"] = True

# ✅ Заголовок приложения
st.title("Blast Optimization App")

# ✅ Импорт навигации (после инициализации)
from ui.navigation import navigation

# ✅ Запуск системы навигации
navigation()

# ✅ Отображение статусной строки
def show_status_bar():
    st.markdown("---")
    if "status_message" in st.session_state:
        st.sidebar.info(st.session_state["status_message"])

show_status_bar()

# ✅ Логируем запуск приложения
logs_manager.add_log(module="main", event="Приложение запущено", log_type="успех")
