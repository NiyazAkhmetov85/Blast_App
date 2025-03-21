import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from utils.logs_manager import LogsManager
from utils.session_state_manager import SessionStateManager

class Visualization:
    def __init__(self, session_manager: SessionStateManager, logs_manager: LogsManager):
        self.session_manager = session_manager
        self.logs_manager = logs_manager

    def plot_drill_grid(self):
        """
        Визуализация сетки скважин с ID и линиями соединения.
        """
        try:
            if "grid_data" not in st.session_state or st.session_state["grid_data"] is None:
                st.sidebar.warning("Сетка скважин не загружена.")
                self.logs_manager.add_log("visualization", "Ошибка: Сетка скважин не загружена.", "ошибка")
                return

            if not st.session_state.get("grid_updated", False):
                st.sidebar.warning("⚠ Сетка скважин не обновлена. Сначала выполните генерацию сетки.")
                return

            grid_data = st.session_state["grid_data"]
            block_name = st.session_state.get("block_name", "Безымянный блок")

            if grid_data.empty or "X" not in grid_data.columns or "Y" not in grid_data.columns:
                st.sidebar.warning("Ошибка: Сетка скважин пустая или некорректная.")
                self.logs_manager.add_log("visualization", "Ошибка: Сетка скважин пустая или некорректная.", "ошибка")
                return

            # Определяем шаг сетки (по X и Y одинаковый)
            x_min, x_max = grid_data["X"].min(), grid_data["X"].max()
            y_min, y_max = grid_data["Y"].min(), grid_data["Y"].max()
            step_x = (x_max - x_min) / (len(grid_data["X"].unique()) - 1)
            step_y = (y_max - y_min) / (len(grid_data["Y"].unique()) - 1)
            step = min(step_x, step_y)  # Делаем шаг одинаковым

            # Визуализация сетки скважин
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.scatter(grid_data["X"], grid_data["Y"], c='r', marker='o', label="Скважины")

            # Добавление подписей ID скважин
            for i, row in grid_data.iterrows():
                ax.text(row["X"], row["Y"], str(row["ID"]), fontsize=9, ha='center', va='center', color='black')

            # Добавление соединительных линий между скважинами
            ax.plot(grid_data["X"], grid_data["Y"], linestyle='-', color='gray', alpha=0.5, label="Связи между скважинами")

            ax.set_xlabel("X координата")
            ax.set_ylabel("Y координата")
            ax.set_title(f"Сетка скважин ({block_name})")
            ax.legend()

            # Отображение графика
            st.pyplot(fig)
            plt.close()

            self.logs_manager.add_log("visualization", f"Сетка скважин для блока '{block_name}' успешно отображена", "успех")

        except Exception as e:
            self.logs_manager.add_log("visualization", f"Ошибка при отображении сетки скважин: {str(e)}", "ошибка")
            st.sidebar.error(f"Ошибка при построении сетки скважин: {e}")
