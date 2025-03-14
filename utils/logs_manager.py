import json
import os
import streamlit as st
from datetime import datetime

class LogsManager:
    """
    Класс для управления логами приложения.
    """
    
    def __init__(self, log_file="config/logs.json", max_logs=1000):
        """
        Инициализация менеджера логов.
        """
        self.log_file = log_file
        self.max_logs = max_logs

        if "logs" not in st.session_state:
            st.session_state["logs"] = []

        self.load_logs_from_file()

    def add_log(self, module, event, log_type="info"):
        """
        Добавляет лог в session_state и записывает его в файл.
        """
        log_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # Добавляем временную метку
            "module": module,
            "event": event,
            "log_type": log_type
        }

        st.session_state["logs"].append(log_entry)

        # Ограничиваем количество логов
        if len(st.session_state["logs"]) > self.max_logs:
            st.session_state["logs"] = st.session_state["logs"][-self.max_logs:]

        self.save_logs_to_file()

    def save_logs_to_file(self):
        """
        Сохраняет логи в файл `logs.json`.
        """
        try:
            os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
            with open(self.log_file, "w", encoding="utf-8") as log_file:
                json.dump(st.session_state["logs"], log_file, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Ошибка при сохранении логов: {e}")

