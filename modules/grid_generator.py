import streamlit as st
import pandas as pd
import numpy as np
from shapely.geometry import Polygon, Point
from utils.logs_manager import LogsManager
from utils.session_state_manager import SessionStateManager


class GridGenerator:
    """
    Генерация сетки скважин на основе параметров и контура блока.
    """

    def __init__(self, session_manager: SessionStateManager, logs_manager: LogsManager):
        """Инициализация параметров и контура блока."""
        self.session_manager = session_manager
        self.logs_manager = logs_manager

        self.block_contour = st.session_state.get("block_contour")
        self.params = st.session_state.get("user_parameters", {})

        self.grid_data = None
        self.block_polygon = None

        if self.block_contour is not None:
            self.block_polygon = Polygon(self.block_contour[["X", "Y"]].values)
        else:
            self.logs_manager.add_log("grid_generator", "Отсутствует контур блока.", "error")
            st.sidebar.error("Отсутствует контур блока. Загрузите контур блока перед генерацией сетки.")

    def generate_grid(self):
        """
        Генерирует сетку скважин внутри блока, соблюдая ограничения `edge_distance`.
        """

        # Проверка наличия блока
        if self.block_contour is None or self.block_contour.empty:
            st.sidebar.warning("Ошибка: Контур блока отсутствует или пуст. Загрузите контур перед генерацией сетки.")
            self.logs_manager.add_log("GridGenerator", "Ошибка: Контур блока отсутствует или пуст.", "ошибка")
            return

        # Создание полигона блока
        self.block_polygon = Polygon(self.block_contour[["X", "Y"]].values)

        # Получение параметров
        edge_distance = self.params.get("edge_distance", 1)
        S = self.params.get("S", 2)
        B = self.params.get("B", 2)
        H = self.params.get("H", 15)  
        grid_type = self.params.get("grid_type", "square")

        # Проверка корректности параметров
        min_x, min_y, max_x, max_y = self.block_polygon.bounds

        if edge_distance < 0 or S <= 0 or B <= 0:
            st.sidebar.error("Ошибка: Параметры сетки должны быть положительными.")
            self.logs_manager.add_log("GridGenerator", "Ошибка: некорректные параметры сетки (отрицательные или нулевые значения).", "ошибка")
            return

        # Сдвигаем границы блока на edge_distance внутрь
        min_x += edge_distance
        min_y += edge_distance
        max_x -= edge_distance
        max_y -= edge_distance

        # Проверяем, что после сдвига остаётся достаточно места
        if min_x >= max_x or min_y >= max_y:
            st.sidebar.error("Ошибка: edge_distance слишком велик – область для сетки исчезает.")
            self.logs_manager.add_log("GridGenerator", "Ошибка: edge_distance слишком велик.", "ошибка")
            return

        grid_points = []
        x_coords = np.arange(min_x, max_x + S, S)
        y_coords = np.arange(min_y, max_y + B, B)

        if grid_type == "square":
            for x in x_coords:
                for y in y_coords:
                    point = Point(x, y)
                    if self.block_polygon.contains(point):
                        grid_points.append((x, y))

        elif grid_type == "triangular":
            for j, y in enumerate(y_coords):
                offset = (S / 2) if j % 2 else 0  
                for x in x_coords:
                    point = Point(x + offset, y)
                    if self.block_polygon.contains(point):
                        grid_points.append((x + offset, y))

        if not grid_points:
            st.sidebar.warning("Ошибка: Сетка пустая, измените параметры.")
            self.logs_manager.add_log("GridGenerator", "Ошибка: Сетка пустая после генерации.", "ошибка")
            return

        # Сохраняем данные
        self.grid_data = pd.DataFrame(grid_points, columns=["X", "Y"])
        self.grid_data["H"] = H  

        if not self.grid_data.empty:
            st.session_state["grid_data"] = self.grid_data.copy()
            self.logs_manager.add_log("GridGenerator", f"Сетка успешно сгенерирована. Количество скважин: {len(self.grid_data)}", "успех")
            st.sidebar.success(f"Сетка успешно сгенерирована! Количество скважин: {len(self.grid_data)}")

    def calculate_grid_metrics(self):
        """Расчёт основных метрик сетки."""

        if self.grid_data is None:
            self.logs_manager.add_log("grid_generator", "Метрики не могут быть рассчитаны - сетка не сгенерирована.", "error")
            st.sidebar.error("Метрики не могут быть рассчитаны - сетка не сгенерирована.")
            return

        area = self.block_polygon.area
        num_holes = len(self.grid_data)
        total_length = self.grid_data["H"].sum()

        metrics = {
            "area": area,
            "num_holes": num_holes,
            "total_length": total_length
        }

        st.session_state["grid_metrics"] = metrics

        self.logs_manager.add_log("grid_generator", "Метрики сетки успешно рассчитаны.")
        st.sidebar.success("Метрики сетки успешно рассчитаны.")
# Завершен 14.03.2025