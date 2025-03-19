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
            
        # Лог успешной загрузки параметров
            self.logs_manager.add_log(module="ReferenceParameters", event="Эталонные параметры успешно загружены и инициализированы.", log_type="успех")

    # def _initialize_session_state(self):
    #     """
    #     Инициализирует необходимые ключи в session_state.
    #     """
    #     required_keys = ["parameters", "ref_vals", "conf_ref_vals", "default_parameters"]

    #     # Очищаем старые данные перед инициализацией
    #     for key in required_keys:
    #         st.session_state.pop(key, None)
    #         if key not in st.session_state:
    #             st.session_state[key] = {}

    #     self.logs_manager.add_log(module="ReferenceParameters", event="Инициализация session_state завершена.", log_type="успех")
    def render_refparameters_section(self):
        params = st.session_state.get("parameters", {})
        user_params = st.session_state.get("user_parameters", {})
    
        # Группировка параметров по категориям, сохраняя порядок из конфигурации
        categories_order = [
            "Эталонные показатели"
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
    
                # Обновляем st.session_state["parameters"]
                if editable:
                    st.session_state["parameters"][param_key]["default_value"] = new_value    


    
    def _load_reference_parameters(self):
        """
        Загружает только параметры категории 'Эталонные показатели' с проверкой корректности.
        """
        # Гарантируем наличие default_parameters в session_state
        st.session_state.setdefault("default_parameters", {})

        default_params = st.session_state["default_parameters"]

        # Проверяем, есть ли в default_parameters нужная категория
        if "Эталонные показатели" not in default_params:
            default_params["Эталонные показатели"] = []  # Инициализация пустого списка
            self.logs_manager.add_log(module="ReferenceParameters", event="Эталонные параметры отсутствовали. Создан пустой список.", log_type="предупреждение")
            st.warning("Эталонные показатели не найдены. Создан пустой список.")
            return

        ref_params = default_params["Эталонные показатели"]

        # Проверяем, что параметры действительно являются списком
        if not isinstance(ref_params, list):
            self.logs_manager.add_log(
                module="ReferenceParameters",
                event=f"Ошибка загрузки: Эталонные параметры имеют неверный формат ({type(ref_params)}).",
                log_type="ошибка"
            )
            st.error(f"Ошибка: Эталонные параметры повреждены. Ожидается список значений, получен {type(ref_params)}.")
            return

        # Очистка перед загрузкой новых данных
        self.params = []

        # Присваиваем загруженные параметры
        self.params = ref_params
        self.logs_manager.add_log(module="ReferenceParameters", event="Эталонные параметры успешно загружены.", log_type="успех")

    def render_reference_parameters(self):
        """
        Отображает параметры эталонных показателей с вводом значений и проверкой границ.
        """
        if not self.params:
            st.warning("Эталонные параметры отсутствуют.")
            self.logs_manager.add_log(module="ReferenceParameters", event="Попытка отобразить пустые эталонные параметры.", log_type="предупреждение")
            return

        with st.expander("Эталонные показатели", expanded=True):
            for param in self.params:
                name = param.get("name")
                description = param.get("description", "Без описания")
                unit = param.get("unit", "")
                default_value = param.get("default_value")
                min_value = param.get("min_value")
                max_value = param.get("max_value")
                param_type = param.get("type")

                # Проверяем границы min/max перед использованием
                if min_value is None or max_value is None:
                    self.logs_manager.add_log(
                        module="ReferenceParameters",
                        event=f"Отсутствуют границы для параметра {name}. Пропускаем.",
                        log_type="ошибка"
                    )
                    continue  # Пропускаем параметр без границ

                # Инициализируем значение в session_state
                if name not in st.session_state["ref_vals"]:
                    st.session_state["ref_vals"][name] = default_value

                value = None  # Для контроля корректности ввода

                if param_type in ["float", "int"]:
                    value = st.number_input(
                        f"{description} ({unit})", 
                        min_value=min_value, 
                        max_value=max_value, 
                        value=st.session_state["ref_vals"].get(name, default_value), 
                        step=0.1 if param_type == "float" else 1,
                        key=name
                    )
                elif param_type == "bool":
                    value = st.checkbox(f"{description}", value=bool(default_value), key=name)
                elif param_type == "str":
                    value = st.text_input(f"{description}", value=str(default_value), key=name)
                else:
                    self.logs_manager.add_log(
                        module="ReferenceParameters",
                        event=f"Неизвестный тип параметра '{param_type}' для {name}.",
                        log_type="ошибка"
                    )
                    continue  # Пропускаем неизвестные параметры

                # Проверка границ значений
                if value is not None and (value < min_value or value > max_value):
                    st.warning(f"{description}: введенное значение ({value}) выходит за допустимые границы ({min_value} - {max_value})!")
                    self.logs_manager.add_log(
                        module="ReferenceParameters",
                        event=f"Параметр {name} выходит за границы ({value} не в {min_value}-{max_value})",
                        log_type="предупреждение"
                    )

                # Обновляем session_state
                st.session_state["ref_vals"][name] = value

            self.logs_manager.add_log(module="ReferenceParameters", event="Эталонные параметры успешно обновлены.", log_type="успех")
