import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from utils.logs_manager import LogsManager
from utils.session_state_manager import SessionStateManager

class Visualization:
    def __init__(self, session_manager: SessionStateManager, logs_manager: LogsManager):
        self.session_manager = session_manager
        self.logs_manager = logs_manager

    def plot_block_contour(self):
        contour = st.session_state.get("block_contour")
        block_name = st.session_state.get("block_name", "Не задан")

        if contour is None or contour.empty:
            st.sidebar.warning("Контур блока не загружен.")
            self.logs_manager.add_log("visualization", "Контур блока не загружен или пуст.", "warning")
            return

        fig, ax = plt.subplots(figsize=(8, 6))

        # Строим контур блока (без нормализации или смещения)
        ax.plot(contour["X"], contour["Y"], marker='o', linestyle='-', color='b', label="Контур блока")
        ax.fill(contour["X"], contour["Y"], alpha=0.2)

        # Настройка подписей и названий
        ax.set_xlabel("Координата X")
        ax.set_ylabel("Координата Y")
        ax.set_title(f"Контур блока ({block_name})")
        ax.legend()

        # Отображаем в Streamlit
        st.pyplot(fig)
        plt.close()

        # Логирование
        st.sidebar.success(f"Отображён контур блока '{block_name}'.")
        self.logs_manager.add_log("visualization", f"Отображён контур блока '{block_name}'.")

    def plot_drill_grid(self):
        """
        Визуализация сетки скважин.
        """
        try:
            # Проверяем, загружена ли сетка скважин
            if "grid_data" not in st.session_state or st.session_state["grid_data"] is None:
                st.sidebar.warning("Сетка скважин не загружена.")
                self.logs_manager.add_log(module="visualization", event="Ошибка: Сетка скважин не загружена.", log_type="ошибка")
                return

            # Проверяем, была ли обновлена сетка
            if not st.session_state.get("grid_updated", False):
                st.sidebar.warning("⚠ Сетка скважин не обновлена. Сначала выполните генерацию сетки.")
                return

            grid_data = st.session_state["grid_data"]
            block_name = st.session_state.get("block_name", "Безымянный блок")

            # Проверяем, содержит ли DataFrame координаты X и Y
            if grid_data.empty or "X" not in grid_data.columns or "Y" not in grid_data.columns:
                st.sidebar.warning("Ошибка: Сетка скважин пустая или имеет неверный формат.")
                self.logs_manager.add_log(module="visualization", event="Ошибка: Сетка скважин пустая или некорректная.", log_type="ошибка")
                return

            # Проверка, если сетка пуста, но обновлена (дополнительная защита)
            if grid_data.empty:
                st.sidebar.warning("Ошибка: Сетка скважин не содержит точек.")
                self.logs_manager.add_log(module="visualization", event="Ошибка: Сетка скважин не содержит точек.", log_type="ошибка")
                return

            # Визуализация сетки скважин
            plt.figure(figsize=(8, 6))
            plt.scatter(grid_data["X"], grid_data["Y"], c='r', marker='o', label="Скважины")
            plt.xlabel("X координата")
            plt.ylabel("Y координата")
            plt.title(f"Сетка скважин ({block_name})")
            plt.legend()

            # Отображение графика
            st.pyplot(plt)
            plt.close()  # Закрываем фигуру после отображения, чтобы избежать утечек памяти

            # Логируем успешное построение графика
            self.logs_manager.add_log(module="visualization", event=f"Сетка скважин для блока '{block_name}' успешно отображена", log_type="успех")

        except Exception as e:
            self.logs_manager.add_log(module="visualization", event=f"Ошибка при отображении сетки скважин: {str(e)}", log_type="ошибка")
            st.sidebar.errorst(f"Ошибка при построении сетки скважин: {e}")

    def plot_combined(self):
        contour = st.session_state.get("block_contour")
        grid_data = st.session_state.get("grid_data")
        block_name = st.session_state.get("block_name", "Не задан")

        if contour is None or grid_data is None:
            st.sidebar.warning("Загрузите контур и сгенерируйте сетку.")
            self.logs_manager.add_log("visualization", "Нет данных для комбинированной визуализации.", "warning")
            return

        plt.figure(figsize=(8, 6))
        plt.plot(contour["X"], contour["Y"], linewidth=2, label="Контур блока")
        plt.fill(contour["X"], contour["Y"], alpha=0.2)
        plt.scatter(grid_data["X"], grid_data["Y"], marker='o', label="Скважины")
        plt.xlabel("X координата")
        plt.ylabel("Y координата")
        plt.title(f"Контур блока и сетка скважин ({block_name})")
        plt.legend()
        st.pyplot(plt)
        plt.close()

        st.sidebar.success("Комбинированная визуализация успешно отображена.")
        self.logs_manager.add_log("visualization", "Комбинированная визуализация успешно отображена.")

    def clear_visualization(self):
        keys = ["grid_updated", "grid_data", "block_contour", "grid_metrics"]
        for key in keys:
            st.session_state.pop(key, None)
        st.sidebar.success("Визуализации очищены.")

# Пример использования в data_input.py или navigation.py
if __name__ == "__main__":
    session_manager = SessionStateManager()
    logs_manager = LogsManager()
    viz = Visualization(session_manager, logs_manager)

    st.header("Визуализация буровзрывных работ")

    if st.button("Показать контур блока"):
        viz.plot_block_contour()

    if st.button("Показать сетку скважин"):
        viz.plot_drill_grid()

    if st.button("Показать комбинированную визуализацию"):
        viz.plot_combined()

    if st.button("Очистить визуализацию"):
        viz.clear_visualization()