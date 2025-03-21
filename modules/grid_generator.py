import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from shapely.geometry import Polygon, Point
from shapely.ops import unary_union
from utils.logs_manager import LogsManager
from utils.session_state_manager import SessionStateManager

class GridGenerator:
    """
    Генерация сетки скважин на основе параметров и контура блока.
    """
    def __init__(self, session_manager: SessionStateManager, logs_manager: LogsManager):
        self.session_manager = session_manager
        self.logs_manager = logs_manager
        self.block_contour = st.session_state.get("block_contour")
        self.params = st.session_state.get("user_parameters", {})
        self.grid_data = None
        self.block_polygon = None

        if self.block_contour is not None:
            self.block_polygon = Polygon(self.block_contour[["X", "Y"]].values)

    def generate_grid(self):
        if self.block_contour is None or self.block_contour.empty:
            st.sidebar.warning("Ошибка: Контур блока отсутствует или пуст. Загрузите контур перед генерацией сетки.")
            self.logs_manager.add_log("GridGenerator", "Ошибка: Контур блока отсутствует или пуст.", "ошибка")
            return

        self.block_polygon = Polygon(self.block_contour[["X", "Y"]].values)
        edge_distance = self.params.get("edge_distance", 1)
        S = self.params.get("S", 2)
        B = self.params.get("B", 2)
        H = self.params.get("H", 15)
        grid_type = self.params.get("grid_type", "square")

        if edge_distance < 0 or S <= 0 or B <= 0:
            st.sidebar.error("Ошибка: Параметры сетки должны быть положительными.")
            return

        # Буферизация полигона для точного учета edge_distance
        adjusted_polygon = self.block_polygon.buffer(-edge_distance)
        if adjusted_polygon.is_empty:
            st.sidebar.error("Ошибка: edge_distance слишком велик – область для сетки исчезает.")
            return

        min_x, min_y, max_x, max_y = adjusted_polygon.bounds
        grid_points = []
        x_coords = np.arange(min_x, max_x + S, S)
        y_coords = np.arange(min_y, max_y + B, B)

        if grid_type == "square":
            for x in x_coords:
                for y in y_coords:
                    point = Point(x, y)
                    if adjusted_polygon.contains(point):
                        grid_points.append((x, y))

        elif grid_type == "triangular":
            for j, y in enumerate(y_coords):
                offset = (S / 2) if j % 2 else 0  
                for x in x_coords:
                    point = Point(x + offset, y)
                    if adjusted_polygon.contains(point):
                        grid_points.append((x + offset, y))

        if not grid_points:
            st.sidebar.warning("Ошибка: Сетка пустая, измените параметры.")
            return

        self.grid_data = pd.DataFrame(grid_points, columns=["X", "Y"])
        self.grid_data.insert(0, "ID", range(1, len(self.grid_data) + 1))
        self.grid_data["H"] = H
        
        # Пронумеруем скважины, начиная с 1
        self.grid_data["ID"] = range(1, len(self.grid_data) + 1)
        
        # Переставим колонки так, чтобы ID был первым
        self.grid_data = self.grid_data[["ID", "X", "Y", "H"]]

        st.session_state["grid_data"] = self.grid_data.copy()
        st.session_state["grid_generated"] = True
        st.session_state["grid_updated"] = True 

        self.logs_manager.add_log("GridGenerator", f"Сетка успешно сгенерирована. Количество скважин: {len(self.grid_data)}", "успех")
        st.sidebar.success(f"✅ Сетка успешно сгенерирована! Количество скважин: {len(self.grid_data)}")

    def calculate_grid_metrics(self):
        if not st.session_state.get("grid_generated", False):
            return

        grid_data = st.session_state.get("grid_data")
        if grid_data is None or grid_data.empty:
            return

        area = self.block_polygon.area
        num_holes = len(grid_data)
        total_length = grid_data["H"].sum()

        metrics = {
            "Площадь блока (м²)": area,
            "Количество скважин": num_holes,
            "Общая длина скважин (м)": total_length
        }

        st.session_state["grid_metrics"] = metrics
        st.sidebar.success("Метрики успешно рассчитаны.")

    def visualize_grid(self):
        if self.grid_data is None or self.grid_data.empty:
            st.sidebar.warning("Нет данных для визуализации.")
            return

        fig = px.scatter(self.grid_data, x="X", y="Y", text="ID", title="Сетка скважин")
        fig.update_traces(textposition='top center')
        st.plotly_chart(fig)
