import streamlit as st
import json
import os
from utils.logs_manager import LogsManager
from utils.session_state_manager import SessionStateManager

class DataInitializer:
    def __init__(self, session_manager: SessionStateManager, logs_manager: LogsManager):
        self.session_manager = session_manager
        self.logs_manager = logs_manager
        self.default_file = "config/full_parameter_list.json"

        # ✅ Корректно инициализируем ключи в session_state
        if "parameters" not in st.session_state:
            st.session_state["parameters"] = {}

        if "parameters_loaded" not in st.session_state:  # Добавляем проверку
            st.session_state["parameters_loaded"] = False

        # Загружаем параметры только если они ещё не загружены
        if not st.session_state["parameters_loaded"]:
            self.load_default_parameters()

    def load_default_parameters(self):
        """
        Загружает параметры из файла по умолчанию в session_state.
        """
        try:
            if not os.path.exists(self.default_file):
                st.sidebar.error(f"Файл параметров {self.default_file} не найден!")
                self.logs_manager.add_log("data_initializer", "Файл параметров не найден", "ошибка")
                return

            with open(self.default_file, "r", encoding="utf-8") as file:
                data = json.load(file)

            # Проверяем наличие ключа "parameters"
            if "parameters" not in data or not isinstance(data["parameters"], list):
                st.sidebar.error(f"Файл {self.default_file} не содержит корректные параметры!")
                self.logs_manager.add_log("data_initializer", "Файл параметров пуст или некорректен", "ошибка")
                return

            # Загружаем параметры только если они не загружены
            if not st.session_state["parameters"]:
                st.session_state["parameters"] = {param["name"]: param for param in data["parameters"]}

                # Сообщение о загрузке параметров показываем только один раз
                if not st.session_state["parameters_loaded"]:
                    st.sidebar.success("Параметры успешно загружены!")
                    self.logs_manager.add_log("data_initializer", f"Загружены {len(st.session_state['parameters'])} параметров", "успех")
                    st.session_state["parameters_loaded"] = True  # Устанавливаем флаг

        except Exception as e:
            st.sidebar.error(f"Ошибка загрузки параметров: {e}")
            self.logs_manager.add_log("data_initializer", f"Ошибка загрузки: {e}", "ошибка")

    def reload_parameters(self):
        """
        Позволяет пользователю загрузить параметры заново через кнопку.
        """
        st.session_state["parameters"] = {}  # Очистка перед загрузкой
        st.session_state["parameters_loaded"] = False  # Сбрасываем флаг
        self.load_default_parameters()
