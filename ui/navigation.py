import streamlit as st

from modules.data_initializer import DataInitializer
from utils.session_state_manager import SessionStateManager
from utils.logs_manager import LogsManager

from ui.data_input import DataInput
from ui.reference_values import RefValues
from ui.results_summary import ResultsSummary


# ✅ Инициализация менеджеров
session_manager = SessionStateManager()
logs_manager = LogsManager()
data_initializer = DataInitializer(session_manager, logs_manager)

# ✅ Первичная загрузка параметров (только при первом запуске)
if "parameters_loaded" not in st.session_state:
    data_initializer.load_default_parameters()
    st.session_state["parameters_loaded"] = True


# def reload_parameters():
#     """
#     Перезагрузка параметров с очисткой дублирующихся сообщений.
#     """
#     if "status_messages" not in st.session_state:
#         st.session_state["status_messages"] = []

#     # ✅ Повторная загрузка параметров
#     data_initializer.load_default_parameters()
#     st.sidebar.success("🔄 Параметры успешно перезагружены!")


def show_sidebar():
    """
    Отображение боковой панели с кнопками и логами.
    """
    # st.sidebar.button("🔄 Перезагрузить параметры", on_click=reload_parameters)


def navigation():
    """
    Функция, управляющая навигацией приложения.
    """
    # ✅ Отображение боковой панели
    show_sidebar()

    # ✅ Определение вкладок и их обработчиков
    data_input = DataInput(session_manager, logs_manager)
    reference_values = RefValues(session_manager, logs_manager)
    results_summary = ResultsSummary(session_manager, logs_manager)

    TAB_OPTIONS = {
        "📥 Импорт данных блока": data_input.show_import_block,
        "📋 Ввод параметров": data_input.show_input_form,
        "📊 Визуализация блока": data_input.show_visualization,
        "📜 Итоговые параметры": data_input.show_summary_screen,
        "📌 Эталонные значения": reference_values.show_reference_values,
        "📈 Итоговые расчеты": results_summary.show_results_summary
    }

    # ✅ Размещение вкладок
    selected_tab = st.sidebar.radio("Выберите раздел", list(TAB_OPTIONS.keys()))

    # ✅ Запуск соответствующего экрана
    TAB_OPTIONS[selected_tab]()
