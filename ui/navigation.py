import streamlit as st
# from ui.data_input import show_input_form
# from ui.reference_values import show_reference_values
# from ui.results_summary import show_results_summary
from modules.data_initializer import DataInitializer
from utils.session_state_manager import SessionStateManager
from utils.logs_manager import LogsManager


# ✅ Инициализация менеджеров
session_manager = SessionStateManager()
logs_manager = LogsManager()
data_initializer = DataInitializer(session_manager, logs_manager)

st.title("Blast Optimization App")  # Переносим заголовок в навигацию

# ✅ Определяем вкладки и их обработчики
# TAB_OPTIONS = {
#     "Ввод данных": show_input_form,
#     "Эталонные значения": show_reference_values,
#     "Результаты": show_results_summary,
# }

# ✅ Инициализация session_state
if "selected_tab" not in st.session_state:
    st.session_state["selected_tab"] = "Ввод данных"

if "status_message" not in st.session_state:
    st.session_state["status_message"] = "Готов к работе"

# 🎛 Боковая панель навигации
st.sidebar.title("Навигация")
selected_tab = st.sidebar.radio("Выберите раздел:", list(TAB_OPTIONS.keys()))

# ✅ Вызов отображения кнопок загрузки параметров
data_initializer.show_parameter_buttons()  # Добавляем кнопки в боковую панель

# 📌 Центральная область (отображение экрана)
TAB_OPTIONS[selected_tab]()  # Вызывает соответствующую функцию

# ✅ Статусная строка
def show_status_bar():
    st.markdown("---")
    st.info(st.session_state["status_message"])
    st.sidebar.info(st.session_state["status_message"])

show_status_bar()
