import streamlit as st
import json
import os
from utils.logs_manager import LogsManager

class DataInitializer:
    """
    Класс для загрузки параметров из JSON-файла и их инициализации в session_state.
    """

    def __init__(self, session_manager, logs_manager):
        """
        Инициализация менеджера загрузки параметров.
        """
        self.session_manager = session_manager
        self.logs_manager = logs_manager

        # Путь к файлу параметров
        self.default_file = "config/full_parameter_list.json"

        # Проверяем инициализирован ли session_state
        if "parameters" not in st.session_state:
            st.session_state["parameters"] = {}

        # Загружаем параметры при старте
        self.load_default_parameters()

    def load_default_parameters(self):
        """
        Загружает параметры из файла по умолчанию в session_state.
        """
        try:
            if not os.path.exists(self.default_file):
                with st.sidebar:
                    st.error(f"Файл параметров {self.default_file} не найден!")
                self.logs_manager.add_log("data_initializer", "Файл параметров не найден", "ошибка")
                return

            with open(self.default_file, "r", encoding="utf-8") as file:
                data = json.load(file)

            # Проверяем наличие ключа "parameters"
            if "parameters" not in data or not isinstance(data["parameters"], list):
                with st.sidebar:
                    st.error(f"Файл {self.default_file} не содержит корректные параметры!")
                self.logs_manager.add_log("data_initializer", "Файл параметров пуст или некорректен", "ошибка")
                return

            # Загружаем параметры в session_state
            st.session_state["parameters"] = {param["name"]: param for param in data["parameters"]}
            st.sidebar.success("Параметры успешно загружены!")
            self.logs_manager.add_log("data_initializer", f"Загружены {len(st.session_state['parameters'])} параметров", "успех")

        except Exception as e:
            with st.sidebar:
                st.error(f"Ошибка загрузки параметров: {e}")
            self.logs_manager.add_log("data_initializer", f"Ошибка загрузки: {e}", "ошибка")

    def reload_parameters(self):
        """
        Позволяет пользователю загрузить параметры заново через кнопку.
        """
        if st.sidebar.button("Перезагрузить параметры"):
            self.load_default_parameters()
