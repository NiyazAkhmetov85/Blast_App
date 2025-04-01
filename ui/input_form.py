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
                                value=float(current_val) if current_val is not None else 0.0,
                                min_value=float(min_val) if min_val is not None else None,
                                max_value=float(max_val) if max_val is not None else None,
                                step=0.1
                            )
                            user_params[param_name] = float(user_input)
                        elif param_type == "int":
                            user_input = st.number_input(
                                f"{description}, {unit}",
                                value=int(current_val) if current_val is not None else 0,
                                min_value=int(min_val) if min_val is not None else None,
                                max_value=int(max_val) if max_val is not None else None,
                                step=1
                            )
                            user_params[param_name] = int(user_input)
                        else:
                            user_input = st.text_input(f"{description}, {unit}", value=str(current_val))
                            user_params[param_name] = user_input  # Оставляем строку без изменений
    
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
        Выбор типа сетки (треугольная/квадратная).
        """
            st.subheader("Выберите тип сетки скважин")
        
            # Защита: убеждаемся, что ключ инициализирован
            if "user_parameters" not in st.session_state:
                st.session_state["user_parameters"] = {}
        
            # Получаем текущее значение или устанавливаем по умолчанию
            grid_type_default = st.session_state["user_parameters"].get("grid_type", "triangular")
        
            # Радиокнопка с явным указанием value и уникальным key
            new_grid_type = st.radio(
                label="Тип сетки",
                options=["triangular", "square"],
                format_func=lambda x: "Квадратная" if x == "square" else "Треугольная",
                key="grid_type_selection",  # уникальный ключ — обязательно
                value=grid_type_default     # задаём текущее состояние
            )
        
            # Обновляем, только если значение изменилось
            if new_grid_type != st.session_state["user_parameters"].get("grid_type"):
                st.session_state["user_parameters"]["grid_type"] = new_grid_type
                self.logs_manager.add_log(
                    module="input_form",
                    event=f"Тип сетки изменён пользователем: {'Квадратная' if new_grid_type == 'square' else 'Треугольная'}",
                    log_type="info"
                )

    
    # def render_grid_type_selection(self):
    #     """
    #     Выбор типа сетки (треугольная/квадратная).
    #     """
    #     st.subheader("Выберите тип сетки скважин")
    
    #     # Проверяем, установлен ли grid_type в session_state
    #     grid_type_default = st.session_state["user_parameters"].get("grid_type", "triangular")
    
    #     # Выбор типа сетки пользователем
    #     new_grid_type = st.radio(
    #         label="Тип сетки",
    #         options=["triangular", "square"],
    #         format_func=lambda x: "Квадратная" if x == "square" else "Треугольная",
    #         key="grid_type_selection",  # важно: нужен уникальный key для правильной работы
    #         value=grid_type_default     # 👈 вместо index
    #     )
    #     # new_grid_type = st.radio(
    #     #     label="Тип сетки",
    #     #     options=["triangular","square"],
    #     #     index=0 if grid_type_default == "square" else 1,
    #     #     format_func=lambda x: "Квадратная" if x == "square" else "Треугольная"
    #     # )
    
    #     # Обновляем состояние, если значение изменилось
    #     if new_grid_type != st.session_state["user_parameters"].get("grid_type"):
    #         st.session_state["user_parameters"]["grid_type"] = new_grid_type
    #         self.logs_manager.add_log(
    #             module="input_form",
    #             event=f"Тип сетки изменён пользователем: {'Квадратная' if new_grid_type == 'square' else 'Треугольная'}",
    #             log_type="info"
    #         )

    def render_control_buttons(self):
        """
        Отображение кнопки управления параметрами с проверкой изменений.
        """
        st.subheader("Управление параметрами")
    
        if st.button("Утвердить параметры"):
            # Сохранение выбора типа сетки
            selected_grid_type = st.session_state["user_parameters"].get("grid_type", "square")
            st.session_state["user_parameters"]["grid_type"] = selected_grid_type
    
            self.logs_manager.add_log(
                module="input_form",
                event=f"Параметры утверждены, тип сетки: {'Квадратная' if selected_grid_type == 'square' else 'Треугольная'}",
                log_type="success"
            )
    
            # Статусное сообщение
            st.sidebar.success(f"✅ Параметры сохранены. Выбран тип сетки: {'Квадратная' if selected_grid_type == 'square' else 'Треугольная'}")
            st.sidebar.success(st.session_state["status_message"])
