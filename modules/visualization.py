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

            x_min, x_max = grid_data["X"].min(), grid_data["X"].max()
            y_min, y_max = grid_data["Y"].min(), grid_data["Y"].max()
            step_x = (x_max - x_min) / (len(grid_data["X"].unique()) - 1)
            step_y = (y_max - y_min) / (len(grid_data["Y"].unique()) - 1)
            step = min(step_x, step_y)

            fig, ax = plt.subplots(figsize=(8, 6))
            ax.scatter(grid_data["X"], grid_data["Y"], c='r', marker='o', label="Скважины")

            for i, row in grid_data.iterrows():
                ax.text(row["X"], row["Y"], str(row["ID"]), fontsize=9, ha='center', va='center', color='black')

            ax.plot(grid_data["X"], grid_data["Y"], linestyle='-', color='gray', alpha=0.5, label="Связи между скважинами")

            ax.set_xlabel("X координата")
            ax.set_ylabel("Y координата")
            ax.set_title(f"Сетка скважин ({block_name})")
            ax.legend()

            st.pyplot(fig)
            plt.close()

            self.logs_manager.add_log("visualization", f"Сетка скважин для блока '{block_name}' успешно отображена", "успех")

        except Exception as e:
            self.logs_manager.add_log("visualization", f"Ошибка при отображении сетки скважин: {str(e)}", "ошибка")
            st.sidebar.error(f"Ошибка при построении сетки скважин: {e}")

    def plot_block_contour(self):
        contour = st.session_state.get("block_contour")
        block_name = st.session_state.get("block_name", "Не задан")

        if contour is None or contour.empty:
            st.sidebar.warning("Контур блока не загружен.")
            self.logs_manager.add_log("visualization", "Контур блока не загружен или пуст.", "warning")
            return

        fig, ax = plt.subplots(figsize=(8, 6))
        ax.plot(contour["X"], contour["Y"], marker='o', linestyle='-', color='b', label="Контур блока")
        ax.fill(contour["X"], contour["Y"], alpha=0.2)

        ax.set_xlabel("Координата X")
        ax.set_ylabel("Координата Y")
        ax.set_title(f"Контур блока ({block_name})")
        ax.legend()

        st.pyplot(fig)
        plt.close()

        st.sidebar.success(f"Отображён контур блока '{block_name}'.")
        self.logs_manager.add_log("visualization", f"Отображён контур блока '{block_name}'.")

    def plot_combined(self):
        contour = st.session_state.get("block_contour")
        grid_data = st.session_state.get("grid_data")
        block_name = st.session_state.get("block_name", "Не задан")

        if contour is None or grid_data is None:
            st.sidebar.warning("Загрузите контур и сгенерируйте сетку.")
            self.logs_manager.add_log("visualization", "Нет данных для комбинированной визуализации.", "warning")
            return

        fig, ax = plt.subplots(figsize=(8, 6))
        ax.plot(contour["X"], contour["Y"], linewidth=2, label="Контур блока")
        ax.fill(contour["X"], contour["Y"], alpha=0.2)
        ax.scatter(grid_data["X"], grid_data["Y"], marker='o', c='r', label="Скважины")
        ax.plot(grid_data["X"], grid_data["Y"], linestyle='-', color='gray', alpha=0.5, label="Связи между скважинами")

        for i, row in grid_data.iterrows():
            ax.text(row["X"], row["Y"], str(row["ID"]), fontsize=9, ha='center', va='center', color='black')

        ax.set_xlabel("X координата")
        ax.set_ylabel("Y координата")
        ax.set_title(f"Контур блока и сетка скважин ({block_name})")
        ax.legend()

        st.pyplot(fig)
        plt.close()

        st.sidebar.success("Комбинированная визуализация успешно отображена.")
        self.logs_manager.add_log("visualization", "Комбинированная визуализация успешно отображена.")

    def clear_visualization(self):
        keys = ["grid_updated", "grid_data", "block_contour", "grid_metrics"]
        for key in keys:
            st.session_state.pop(key, None)
        st.sidebar.success("Визуализации очищены.")
