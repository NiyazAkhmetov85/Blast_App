import streamlit as st

from modules.data_initializer import DataInitializer
from utils.session_state_manager import SessionStateManager
from utils.logs_manager import LogsManager

from ui.data_input import DataInput
from ui.reference_values import ReferenceParameters
from ui.results_summary import ReferenceCalculations

# ✅ Инициализация менеджеров
session_manager = SessionStateManager()
logs_manager = LogsManager()
data_initializer = DataInitializer(session_manager, logs_manager)

# ✅ Первичная загрузка параметров (только при первом запуске)
if "parameters_loaded" not in st.session_state:
    data_initializer.load_default_parameters()
    st.session_state["parameters_loaded"] = True

def reload_parameters():
    """
    Перезагрузка параметров с очисткой дублирующихся сообщений.
    """
    # Очистка старых сообщений
    if "status_messages" not in st.session_state:
        st.session_state["status_messages"] = []

    # Перезагрузка параметров
    data_initializer.reload_parameters()

    # # Добавляем сообщение о перезагрузке, если оно не было добавлено ранее
    # message = "Параметры успешно перезагружены!"
    # if message not in st.session_state["status_messages"]:
    #     st.session_state["status_messages"].append(message)

def show_sidebar():
    """
    Отображение боковой панели с кнопками и сообщениями.
    """
    st.sidebar.button("Перезагрузить параметры", on_click=reload_parameters)

    # # Контейнер для сообщений в боковой панели
    # message_container = st.sidebar.empty()
    # with message_container:
    #     for msg in st.session_state.get("status_messages", []):
    #         st.sidebar.success(msg)

def navigation():
    """
    Функция, управляющая навигацией приложения.
    """
    # ✅ Отображение боковой панели
    show_sidebar()

    # ✅ Определение вкладок и их обработчиков
    data_input = DataInput(session_manager, logs_manager)

    TAB_OPTIONS = {
        "📥 Импорт данных блока": data_input.show_import_block,
        "📋 Ввод параметров": data_input.show_input_form,
        "📊 Визуализация блока": data_input.show_visualization,
        "📜 Итоговые параметры": data_input.show_summary_screen,
        "📌 Эталонные значения": RefValues.show_reference_values,
        "📈 Итоговые расчеты": show_results_summary
    }

    # ✅ Размещение вкладок
    selected_tab = st.sidebar.radio("Выберите раздел", list(TAB_OPTIONS.keys()))

    # ✅ Запуск соответствующего экрана
    TAB_OPTIONS[selected_tab]()
