import streamlit as st
from utils.logs_manager import LogsManager
from utils.session_state_manager import SessionStateManager
import copy 

class InputForm:
    def __init__(self, session_manager: SessionStateManager, logs_manager: LogsManager):
        """
        Инициализация формы ввода данных.
        """
        self.session_manager = session_manager
        self.logs_manager = logs_manager

        # Инициализация пользовательских параметров
        if "parameters" not in st.session_state:
            st.session_state["parameters"] = {}
            self.logs_manager.add_log("input_form", "⚠️ Параметры не загружены при инициализации", "warning")


    def render_parameters_section(self):
        params = st.session_state.get("parameters", {})
        user_params = st.session_state.get("user_parameters", {})
    
        # Группировка параметров по категориям, сохраняя порядок из конфигурации
        categories_order = [
            "Геометрические параметры блока",
            "Физико-механические свойства породы",
            "Параметры буровзрывных работ",
            "ЛСК"
        ]
    
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
    
                    # Получаем сохраненное значение пользователя, если оно есть, иначе - по умолчанию
                    current_val = user_params.get(param_name, default_value)
    
                    # Группа ЛСК - только для чтения
                    if category == "ЛСК":
                        st.write(f"**{param_name} ({unit})**: {current_val}")
                    else:
                        # Проверка типа параметра для отображения корректного поля ввода
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
    
                        # Сохраняем пользовательское значение обратно в session_state
                        user_params[param_name] = user_input
    
        # Сохраняем обновленные параметры
        st.session_state["user_parameters"] = user_params




    def _render_group(self, group_name, group_parameters, editable=True):
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
    
                # Обновляем st.session_state["parameters"]
                if editable:
                    st.session_state["parameters"][param_key]["default_value"] = new_value    
    
    def render_grid_type_selection(self):
        """
        Выбор типа сетки (квадратная/треугольная).
        """
        st.subheader("Выберите тип сетки скважин")

        grid_type_default = "square"  # Значение по умолчанию

        # Проверяем наличие grid_type в user_parameters
        if "grid_type" not in st.session_state["user_parameters"]:
            st.session_state["user_parameters"]["grid_type"] = grid_type_default = "square"
            st.sidebar.warning("Тип сетки не был указан. Установлено значение по умолчанию: Квадратная.")
            self.logs_manager.add_log(
                module="data_input",
                event="Тип сетки задан по умолчанию - Квадратная",
                log_type="warning"
            )
        else:
            grid_type_default = st.session_state["user_parameters"]["grid_type"]

        # Выбор типа сетки пользователем
        st.session_state["user_parameters"]["grid_type"] = st.radio(
            label="Тип сетки",
            options=["square", "triangular"],
            index=0 if grid_type_default == "square" else 1,
            format_func=lambda x: "Квадратная" if x == "square" else "Треугольная"
        )

    def render_control_buttons(self):
        """
        Отображение кнопок управления параметрами с проверкой изменений.
        """
        st.subheader("Управление параметрами")
        col1, col2 = st.columns(2)

        if st.button("Утвердить параметры"):
            # Перебираем все группы и параметры
            for group_name, group_params in st.session_state["parameters"].items():
                for param_name, param_details in group_params.items():
                    # Получаем значение из формы ввода
                    form_key = f"{group_name}_{param_name}"
                    if form_key in st.session_state:
                        input_value = st.session_state[form_key]
                        # Сохраняем в user_parameters
                        st.session_state["user_parameters"][group_name][param_name] = input_value
            
            # Статусное сообщение
            st.session_state["status_message"] = "Параметры утверждены."
            st.sidebar.success(st.session_state["status_message"])
