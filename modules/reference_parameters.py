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

        # Инициализация пользовательских параметров
        if "parameters" not in st.session_state:
            st.session_state["parameters"] = {}
            self.logs_manager.add_log(module="ReferenceParameters", event="Эталонные параметры успешно загружены и инициализированы.", log_type="успех")

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
    
                    if category == "ЛСК":
                        st.write(f"**{param_name} ({unit})**: {current_val}")
                    else:
                        if param_type == "float":
                            user_input = st.number_input(
                                f"{description}, {unit}",
                                value=float(current_val),
                                min_value=float(min_val),
                                max_value=float(max_val),
                                step=0.1
                            )
                        elif param_type == "int":
                            user_input = st.number_input(
                                f"{description}, {unit}",
                                value=int(current_val),
                                min_value=int(min_val),
                                max_value=int(max_val),
                                step=1
                            )
                        else:
                            user_input = st.text_input(f"{description}, {unit}", value=str(current_val))
    
                        user_params[param_name] = user_input

        # **Кнопка "Утвердить эталонные параметры"**
        if st.button("✅ Утвердить эталонные параметры", key="approve_ref_parameters"):
            st.session_state["reference_parameters"] = user_params.copy()
            self.logs_manager.add_log(
                module="ReferenceParameters",
                event="Эталонные параметры утверждены пользователем.",
                log_type="успех"
            )
            st.sidebar.success("Эталонные параметры успешно утверждены!")

        # **Кнопка "Удалить эталонные параметры"**
        if st.button("❌ Удалить эталонные параметры", key="delete_ref_parameters"):
            st.session_state["reference_parameters"] = {}
            st.session_state["user_parameters"] = {}
            self.logs_manager.add_log(
                module="ReferenceParameters",
                event="Эталонные параметры удалены.",
                log_type="предупреждение"
            )
            st.sidebar.warning("Все эталонные параметры удалены.")

    def _render_refgroup(self, group_name, group_parameters, editable=True):
        """
        Отображает параметры в указанной группе.
        """
        with st.expander(group_name, expanded=False):
            for param_key, param in group_parameters.items():
                if param_key not in st.session_state["parameters"]:
                    st.warning(f"⚠️ Параметр '{param_key}' отсутствует.")
                    continue
    
                param_value = st.session_state["parameters"][param_key].get("default_value", None)
                param_type = st.session_state["parameters"][param_key].get("type", "float")
                min_value = st.session_state["parameters"][param_key].get("min_value", None)
                max_value = st.session_state["parameters"][param_key].get("max_value", None)
                unit = st.session_state["parameters"][param_key].get("unit", "")
    
                label = f"{param['description']} ({unit})" if unit else param['description']
    
                if param_type == "float":
                    new_value = st.number_input(
                        label=label,
                        value=float(param_value) if param_value is not None else 0.0,
                        min_value=float(min_value) if min_value is not None else None,
                        max_value=float(max_value) if max_value is not None else None,
                        step=0.1,
                        disabled=not editable
                    )
                elif param_type == "int":
                    new_value = st.number_input(
                        label=label,
                        value=int(param_value) if param_value is not None else 0,
                        min_value=int(min_value) if min_value is not None else None,
                        max_value=int(max_value) if max_value is not None else None,
                        step=1,
                        disabled=not editable
                    )
                elif param_type == "str":
                    new_value = st.text_input(
                        label=label,
                        value=str(param_value) if param_value is not None else "",
                        disabled=not editable
                    )
                else:
                    st.error(f"❌ Неизвестный тип параметра: {param_type}")
    
                if editable:
                    st.session_state["parameters"][param_key]["default_value"] = new_value
