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

        if "reference_parameters" not in st.session_state:
            st.session_state["reference_parameters"] = {}

        if "user_reference_parameters" not in st.session_state:
            st.session_state["user_reference_parameters"] = {}

        # Лог успешной загрузки
        self.logs_manager.add_log(
            module="ReferenceParameters",
            event="Эталонные параметры успешно загружены и инициализированы.",
            log_type="успех"
        )

    def render_refparameters_section(self):
        params = st.session_state.get("reference_parameters", {})
        user_params = st.session_state.get("user_reference_parameters", {})

        category = "Эталонные показатели"

        with st.expander(f"{category}", expanded=True):
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
                        step=0.1,
                        key=f"input_{param_name}"
                    )
                elif param_type == "int":
                    user_input = st.number_input(
                        f"{description} ({unit})",
                        value=int(current_val),
                        min_value=int(min_val),
                        max_value=int(max_val),
                        step=1,
                        key=f"input_{param_name}"
                    )
                else:
                    user_input = st.text_input(f"{description} ({unit})", value=str(current_val), key=f"input_{param_name}")

                st.session_state["user_reference_parameters"][param_name] = user_input

            # **Кнопка "Утвердить эталонные параметры"**
            if st.button("✅ Утвердить эталонные параметры", key="approve_ref_parameters"):
                st.session_state["reference_parameters"].update(st.session_state["user_reference_parameters"])
                self.logs_manager.add_log(
                    module="ReferenceParameters",
                    event="Эталонные параметры утверждены пользователем.",
                    log_type="успех"
                )
                st.sidebar.success("Эталонные параметры успешно утверждены!")

            # **Кнопка "Удалить эталонные параметры"**
            if st.button("❌ Удалить эталонные параметры", key="delete_ref_parameters"):
                st.session_state["reference_parameters"] = {}
                st.session_state["user_reference_parameters"] = {}
                self.logs_manager.add_log(
                    module="ReferenceParameters",
                    event="Эталонные параметры удалены.",
                    log_type="предупреждение"
                )
                st.sidebar.warning("Все эталонные параметры удалены.")
