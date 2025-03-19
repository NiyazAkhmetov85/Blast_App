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

    def confirm_parameters(self):
        """
        Утверждает эталонные параметры, проверяя их корректность перед сохранением.
        """
        if not st.session_state.get("ref_vals"):
            st.warning("Нет данных для утверждения эталонных параметров.")
            self.logs_manager.add_log(module="ReferenceParameters", 
                                    event="Попытка утверждения пустых эталонных параметров.", 
                                    log_type="ошибка")
            return

        # Проверка x_range_min < target_x_max перед сохранением
        x_range_min = st.session_state["ref_vals"].get("x_range_min")
        target_x_max = st.session_state["ref_vals"].get("target_x_max")

        if x_range_min is not None and target_x_max is not None:
            if x_range_min >= target_x_max:
                st.warning("Минимальное значение x (x_range_min) должно быть меньше максимального (target_x_max).")
                self.logs_manager.add_log(module="ReferenceParameters", 
                                        event=f"Ошибка: x_range_min ({x_range_min}) >= target_x_max ({target_x_max})", 
                                        log_type="ошибка")

        # Проверка значений перед утверждением
        invalid_params = []  # Список для хранения ошибок

        for param in st.session_state["ref_vals"]:
            value = st.session_state["ref_vals"].get(param)
            if value is None:
                continue  # Пропускаем параметры без значений

            min_value = next((p["min_value"] for p in self.params if p["name"] == param), None)
            max_value = next((p["max_value"] for p in self.params if p["name"] == param), None)

            if min_value is not None and max_value is not None and not (min_value <= value <= max_value):
                invalid_params.append(f"{param}: {value} (допустимо: {min_value}-{max_value})")

        if invalid_params:
            st.warning("Некоторые параметры выходят за допустимые границы:\n" + "\n".join(invalid_params))
            self.logs_manager.add_log(
                module="ReferenceParameters",
                event=f"Ошибка: параметры выходят за границы: {', '.join(invalid_params)}",
                log_type="ошибка"
            )
            return  # Не сохраняем параметры, если есть ошибки

        # Сохранение утвержденных значений
        st.session_state["conf_ref_vals"] = st.session_state["ref_vals"].copy()
        self.logs_manager.add_log(module="ReferenceParameters", event="Эталонные параметры утверждены.", log_type="успех")
        st.success("Эталонные параметры сохранены!")
