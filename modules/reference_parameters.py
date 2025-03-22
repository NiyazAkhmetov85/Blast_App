import streamlit as st
from utils.session_state_manager import SessionStateManager
from utils.logs_manager import LogsManager

class ReferenceParameters:
    """
    Класс для инициализации и управления эталонными параметрами.
    """

    def __init__(self, session_manager: SessionStateManager, logs_manager: LogsManager):
        self.session_manager = session_manager
        self.logs_manager = logs_manager

        if "parameters" not in st.session_state:
            st.session_state["parameters"] = {}

        if "user_parameters" not in st.session_state:
            st.session_state["user_parameters"] = {}

        # Лог успешной загрузки
        self.logs_manager.add_log(
            module="ReferenceParameters",
            event="Эталонные параметры успешно загружены и инициализированы.",
            log_type="успех"
        )

    def render_refparameters_section(self):
        params = st.session_state.get("parameters", {})
        user_params = st.session_state.get("user_parameters", {})

        categories_order = ["Эталонные показатели"]

        for category in categories_order:
            with st.expander(f"{category}", expanded=False):
                category_params = [p for p in params.values() if p["category"] == category]

                for param in category_params:
                    param_name = param["name"]
                    default_value = param["default_value"]
                    min_val = param["min_value"]
                    max_val = param["max_value"]
                    description = param["description"]
                    unit = param["unit"]
                    param_type = param["type"]

                    current_val = user_params.get(param_name, default_value)

                    if param_type == "float":
                        user_input = st.number_input(
                            f"{description} ({unit})",
                            value=float(current_val),
                            min_value=float(min_val),
                            max_value=float(max_val),
                            step=0.1
                        )
                    elif param_type == "int":
                        user_input = st.number_input(
                            f"{description} ({unit})",
                            value=int(current_val),
                            min_value=int(min_val),
                            max_value=int(max_val),
                            step=1
                        )
                    else:
                        user_input = st.text_input(f"{description} ({unit})", value=str(current_val))

                    # Исправленный отступ
                    st.session_state["user_parameters"][param_name] = user_input

        # **Добавление кнопки "Утвердить параметры"**
        if st.button("✅ Утвердить параметры"):
            st.session_state["parameters"].update(st.session_state["user_parameters"])
            self.logs_manager.add_log(
                module="ReferenceParameters",
                event="Параметры утверждены пользователем.",
                log_type="успех"
            )
            st.sidebar.success("Параметры успешно утверждены!")

        # **Добавление кнопки "Удалить утвержденные параметры"**
        if st.button("❌ Удалить утвержденные параметры"):
            st.session_state["parameters"] = {}
            st.session_state["user_parameters"] = {}
            self.logs_manager.add_log(
                module="ReferenceParameters",
                event="Утвержденные параметры удалены.",
                log_type="предупреждение"
            )
            st.sidebar.warning("Все утвержденные параметры удалены.")
