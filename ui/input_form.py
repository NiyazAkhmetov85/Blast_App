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
        if "user_parameters" not in st.session_state:
            st.session_state["user_parameters"] = copy.deepcopy(st.session_state.get("parameters", {}))
            self.logs_manager.add_log("input_form", "Пользовательские параметры инициализированы значениями по умолчанию.")
        else:
            self.logs_manager.add_log("input_form", "Пользовательские параметры загружены из сессии.")

        self.parameters = st.session_state["user_parameters"]

    def _render_parameters_section(self):
        st.subheader("Ввод параметров блока")

        for group_name in [
            "Геометрические параметры блока",
            "Физико-механические свойства породы",
            "Параметры буровзрывных работ",
            "Локальная система координат (ЛСК)"
        ]:
            if group_name in self.parameters:
                editable = group_name != "Локальная система координат (ЛСК)"
                self._render_group(
                    group_name=group_name,
                    group_parameters=self.parameters[group_name],
                    editable=editable
                )

    def _render_group(self, group_name: str, group_parameters: list, editable: bool = True):
        """
        Отображение группы параметров с проверкой корректности self.parameters.
        """
        if "user_parameters" not in st.session_state:
            st.session_state["user_parameters"] = {}

        if not self.parameters or group_name not in self.parameters:
            st.sidebar.warning(f"Группа параметров '{group_name}' не найдена.")
            self.logs_manager.add_log(
                "input_form",
                f"Группа параметров '{group_name}' не найдена.",
                "error"
            )
            return

        with st.expander(f"Группа: {group_name}"):
            for param_details in group_parameters:
                param = param_details.get("name", "unknown_param")
                description = param_details.get("description", "")
                default_value = param_details.get("default_value", None)
                min_value = param_details.get("min_value", None)
                max_value = param_details.get("max_value", None)
                param_type = param_details.get("type", "float")  # Исправлено!
                unit = param_details.get("unit", "")              # Исправлено!

                st.markdown(f"**{description}**")
                st.caption(f"Единица измерения: {unit}")
                current_value = st.session_state["user_parameters"].get(param, default_value)

                # Отображение поля ввода с учетом типа данных
                if editable:
                    if param_type == "int":
                        new_value = st.number_input(
                            f"{param}", 
                            min_value=min_value, max_value=max_value,
                            value=int(current_value) if current_value is not None else int(default_value)
                        )
                    elif param_type == "float":
                        new_value = st.number_input(
                            f"{param}", 
                            min_value=min_value, max_value=max_value,
                            value=float(current_value) if current_value is not None else float(default_value)
                        )
                    else:
                        new_value = st.text_input(
                            f"{param}", 
                            value=str(current_value) if current_value else str(default_value)
                        )

                    # Проверки допустимых значений
                    if min_value is not None and new_value < min_value:
                        st.sidebar.warning(f"{param} меньше минимально допустимого {min_value}. Исправьте значение.")
                        self.logs_manager.add_log("input_form", f"{param} ниже допустимого ({new_value} < {min_value})", "error")
                        new_value = min_value

                    if max_value is not None and new_value > max_value:
                        st.sidebar.warning(f"{param} больше максимально допустимого {max_value}. Исправьте значение.")
                        self.logs_manager.add_log("input_form", f"{param} больше максимально допустимого", "error")
                        new_value = current_value

                    # Сохраняем параметр, если значение изменилось
                    if new_value != current_value:
                        st.session_state["user_parameters"][param] = new_value
                        self.logs_manager.add_log("input_form", f"{param} изменён пользователем", "info")
                else:
                    # Если не editable, просто показываем текущее значение
                    st.write(f"{param}: {current_value}")
    
    def _render_grid_type_selection(self):
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

        if st.button("Вернуть параметры по умолчанию"):
            # Перебираем параметры по умолчанию и перезаписываем ими user_parameters
            for group_name, group_params in st.session_state["parameters"].items():
                for param_name, param_details in group_params.items():
                    default_value = param_details["default_value"]
                    st.session_state["user_parameters"][group_name][param_name] = default_value
                    form_key = f"{group_name}_{param_name}"
                    if form_key in st.session_state:
                        st.session_state[form_key] = default_value  # обновляем отображаемые формы ввода
                        

    # def show_all_session_state(self):
    #     """Вывод всех параметров session_state для отладки."""
    #     st.subheader("Содержимое session_state")
    #     st.json(st.session_state)

                
            # Статусное сообщение
            st.session_state["status_message"] = "Параметры возвращены к значениям по умолчанию."
            st.sidebar.success(st.session_state["status_message"])
# Завершен 14.03.2025
