import streamlit as st
from ui.data_input import DataInput
from modules.data_initializer import DataInitializer
from utils.session_state_manager import SessionStateManager

# ✅ Инициализация менеджеров
# ✅ Создаём экземпляр DataInitializer
logs_manager = LogsManager()
session_manager = SessionStateManager()
data_initializer = DataInitializer(session_manager, logs_manager)

# ✅ Создаём экземпляр DataInitializer
data_initializer = DataInitializer(session_manager)

# ✅ Первичная загрузка параметров (только при первом запуске)
if "parameters_loaded" not in st.session_state:
    data_initializer.load_default_parameters()
    st.session_state["parameters_loaded"] = True

def reload_parameters():
    """
    Перезагрузка параметров.
    """
    data_initializer.reload_parameters()

def show_sidebar():
    """
    Отображение боковой панели с кнопкой управления параметрами.
    """
    with st.sidebar:
        st.button("Перезагрузить параметры", on_click=reload_parameters)

def navigation():
    """
    Функция, управляющая навигацией приложения.
    """
    # ✅ Отображение боковой панели
    show_sidebar()

    # ✅ Инициализация классов экранов
    data_input = DataInput(session_manager)

    # ✅ Определение вкладок и их обработчиков
    TAB_OPTIONS = {
        "📥 Ввод данных": data_input.show_import_block,
        "📋 Ввод параметров": data_input.show_input_form,
        "📊 Визуализация блока": data_input.show_visualization,
        "📜 Итоговые параметры": data_input.show_summary_screen,
    }

    # ✅ Размещение вкладок
    selected_tab = st.sidebar.radio("Выберите раздел", list(TAB_OPTIONS.keys()))

    # ✅ Запуск соответствующего экрана
    TAB_OPTIONS[selected_tab]()
