import streamlit as st

# Устанавливаем настройки страницы
st.set_page_config(page_title="Blast Optimization App", layout="wide")


# ✅ Отображение заголовка
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
