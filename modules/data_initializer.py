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

        # ✅ Инициализация ключей session_state
        st.session_state.setdefault("parameters", {})
        st.session_state.setdefault("parameters_loaded", False)
        st.session_state.setdefault("user_parameters", {})

        # ✅ Загрузка параметров только при первом запуске
        if not st.session_state["parameters_loaded"]:
            self.load_default_parameters()

    @st.cache_data(show_spinner=False)
    def _load_json_from_file(self, file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def load_default_parameters(self):
        """
        Загружает параметры из файла по умолчанию в session_state.
        """
        try:
            if not os.path.exists(self.default_file):
                st.sidebar.error(f"Файл параметров {self.default_file} не найден!")
                self.logs_manager.add_log("data_initializer", "Файл параметров не найден", "ошибка")
                return

            data = self._load_json_from_file(self.default_file)

            if "parameters" not in data or not isinstance(data["parameters"], list):
                st.sidebar.error("Файл параметров некорректен или пуст.")
                self.logs_manager.add_log("data_initializer", "Формат параметров некорректен", "ошибка")
                return

            st.session_state["parameters"] = {param["name"]: param for param in data["parameters"]}
            st.session_state["parameters_loaded"] = True

            st.sidebar.success("✅ Параметры успешно загружены.")
            self.logs_manager.add_log("data_initializer", f"Загружено {len(data['parameters'])} параметров", "успех")

        except Exception as e:
            st.sidebar.error(f"Ошибка загрузки параметров: {e}")
            self.logs_manager.add_log("data_initializer", f"Ошибка загрузки: {e}", "ошибка")

    def reload_parameters(self):
        """
        Принудительно перезагружает параметры.
        """
        st.session_state["parameters"] = {}
        st.session_state["parameters_loaded"] = False
        self.load_default_parameters()
