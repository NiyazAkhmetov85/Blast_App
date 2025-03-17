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

        # Гарантируем числовой тип данных в DataFrame
        contour["X"] = pd.to_numeric(contour["X"], errors='coerce')
        contour["Y"] = pd.to_numeric(contour["Y"], errors='coerce')

        # Удаляем возможные NaN-значения после преобразования
        contour = contour.dropna()

        x = contour["X"] - contour["X"].min()
        y = contour["Y"] - contour["Y"].min()

        # Проверяем и замыкаем контур, если не замкнут
        if x.iloc[0] != x.iloc[-1] or y.iloc[0] != y.iloc[-1]:
            x = pd.concat([x, pd.Series(x.iloc[0])])
            y = pd.concat([y, pd.Series(y.iloc[0])])

        # Создание и отображение графика
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.scatter(x, y, c="red", label="Точки контура")
        ax.plot(x, y, 'b-', linewidth=2, label="Контур блока")
        ax.fill(x, y, color='blue', alpha=0.2, label="Область блока")

        ax.set_xlabel("Координата X")
        ax.set_ylabel("Координата Y")
        ax.set_title(f"Карта блока ({st.session_state.get('block_name', 'Не задан')})")
        ax.legend()

        ax.set_aspect('equal', adjustable='datalim')

        # Отображение в Streamlit
        st.pyplot(fig)

        # Логирование
        st.sidebar.success(f"Отображён контур блока '{st.session_state['block_name']}'.")
        self.logs_manager.add_log("visualization", f"Отображён контур блока '{st.session_state['block_name']}'.")







    # def plot_block_contour(self):
    #     contour = st.session_state.get("block_contour")
    #     block_name = st.session_state.get("block_name", "Не задан")

    #     if contour is None or contour.empty:
    #         st.sidebar.warning("Контур блока не загружен.")
    #         self.logs_manager.add_log("visualization", "Контур блока не загружен или пуст.", "warning")
    #         return

    #     plt.figure(figsize=(8, 6))
    #     plt.plot(contour["X"], contour["Y"], 'b-', linewidth=2, label="Контур блока")
    #     plt.fill(contour["X"], contour["Y"], alpha=0.2)
    #     plt.xlabel("X координата")
    #     plt.ylabel("Y координата")
    #     plt.title(f"Контур блока ({block_name})")
    #     plt.legend()
    #     st.pyplot(plt)
    #     plt.close()

    #     st.sidebar.success(f"Отображён контур блока '{block_name}'.")
    #     self.logs_manager.add_log("visualization", f"Отображён контур блока '{block_name}'.")

    def plot_drill_grid(self):
        grid_data = st.session_state.get("grid_data")

        if grid_data is None or grid_data.empty:
            st.sidebar.warning("Сетка скважин не загружена или пуста.")
            self.logs_manager.add_log("visualization", "Сетка скважин не загружена или пуста", "warning")
            return

        plt.figure(figsize=(8, 6))
        plt.scatter(grid_data["X"], grid_data["Y"], marker='o')
        plt.xlabel("X координата")
        plt.ylabel("Y координата")
        plt.title("Сетка скважин")
        st.pyplot(plt)
        plt.close()

        st.sidebar.success("Сетка скважин отображена.")
        self.logs_manager.add_log("visualization", "Сетка скважин отображена.")

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
# Завершен 14.03.2025
