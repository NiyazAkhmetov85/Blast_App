import streamlit as st
import pandas as pd
import numpy as np
from utils.logs_manager import LogsManager
from utils.session_state_manager import SessionStateManager

class DataProcessing:
    """
    Класс для загрузки и обработки данных контура блока.
    """
    def __init__(self, session_manager: SessionStateManager, logs_manager: LogsManager):
        """
        Инициализация менеджера загрузки параметров.
        """
        self.session_manager = session_manager
        self.logs_manager = logs_manager
        self.block_contour = None  # Контур блока загружается позже
        self.block_name = None  # Контур блока загружается позже
        self.block_geometry = None  # Контур блока загружается позже

    def load_block_contour(self, uploaded_file):
        """
        Загружает и обрабатывает контур блока из файла (.csv, .txt, .str).
        Обеспечивает числовой формат координат.
        """
        if uploaded_file is None:
            st.sidebar.warning("Выберите файл с контуром блока.")
            return

        file_extension = uploaded_file.name.split(".")[-1].lower()

        data = []
        try:
            if file_extension in ["csv", "txt"]:
                df = pd.read_csv(uploaded_file, delimiter=",", header=0)
                df = df.iloc[:, :2]
                df.columns = ["X", "Y"]

            elif file_extension == "str":
                lines = uploaded_file.getvalue().decode("utf-8").splitlines()[1:]  # пропускаем первую строку

                for line in lines:
                    values = line.strip().split(",")

                    if len(values) < 3 or "END" in line or all(v.strip() in ["0", "0.000", ""] for v in values[1:3]):
                        continue

                    try:
                        x = float(values[1].strip())
                        y = float(values[2].strip())
                        data.append([x, y])
                    except ValueError:
                        continue

                df = pd.DataFrame(data, columns=["X", "Y"])

            else:
                st.sidebar.warning("Неподдерживаемый формат файла. Разрешены только .csv, .txt и .str")
                return

            # Приведение к числовому формату и удаление строк с ошибками
            df["X"] = pd.to_numeric(df["X"], errors='coerce')
            df["Y"] = pd.to_numeric(df["Y"], errors='coerce')
            df.dropna(inplace=True)

            # Проверка количества точек
            if len(df) < 3:
                st.sidebar.error("Ошибка: Контур блока должен содержать минимум 3 точки.")
                self.logs_manager.add_log("DataProcessing", "Ошибка: Контур блока содержит менее 3 точек.", "ошибка")
                return

            # Сохраняем DataFrame
            self.block_contour = df
            self.block_name = uploaded_file.name

            st.session_state["block_contour"] = df
            st.session_state["block_name"] = uploaded_file.name

            st.sidebar.success(f"Файл {uploaded_file.name} успешно загружен!")
            self.logs_manager.add_log("DataProcessing", f"Успешно загружен контур блока: {uploaded_file.name}", "успех")

        except Exception as e:
            self.logs_manager.add_log("DataProcessing", f"Ошибка загрузки контура блока: {str(e)}", "ошибка")
            st.sidebar.error(f"Ошибка при загрузке: {e}")

    def calculate_block_geometry(self):
        """
        Выполняет расчёт геометрических параметров блока.
        """
        try:
            # Очистка предыдущих данных перед расчётом
            st.session_state["block_geometry"] = None

            # Проверяем, загружен ли контур блока
            if "block_contour" not in st.session_state or st.session_state["block_contour"] is None:
                st.sidebar.warning("Сначала загрузите контур блока.")
                self.logs_manager.add_log("DataProcessing", "Ошибка: Контур блока отсутствует.", "ошибка")
                return

            df = st.session_state["block_contour"]
            if df.empty:
                st.sidebar.error("Ошибка: Загруженный контур блока пуст.")
                self.logs_manager.add_log("DataProcessing", "Ошибка: Загруженный контур блока пуст.", "ошибка")
                return

            # Проверяем наличие параметра H (высота уступа)
            H = st.session_state["user_parameters"].get("H")

            # Если H отсутствует в user_parameters, берём из default_parameters (резервное значение)
            if H is None:
                H = st.session_state["default_parameters"].get("H")
                if H is None:
                    st.sidebar.warning("Ошибка: Необходимо задать параметр H перед расчётами.")
                    self.logs_manager.add_log("DataProcessing", "Ошибка: Параметр H отсутствует.", "ошибка")
                    return

            # Проверяем, что H корректное число и больше 0
            if not isinstance(H, (int, float)) or H <= 0:
                st.sidebar.error("Ошибка: Параметр H должен быть числом больше 0.")
                self.logs_manager.add_log("DataProcessing", f"Ошибка: Некорректное значение H ({H})", "ошибка")
                return

            self.logs_manager.add_log("DataProcessing", f"Начат расчёт геометрии блока с H={H}", "информация")

            # Вычисление площади блока (методом многоугольника)
            x, y = df["X"].values, df["Y"].values
            area = 0.5 * np.abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1)))

            # Вычисление объёма блока
            volume = area * H

            # Сохраняем данные в объект класса
            self.block_geometry = {"area": area, "volume": volume}

            # Сохранение результата в session_state
            st.session_state["block_geometry"] = {"area": area, "volume": volume}

            # Логирование успешного расчёта
            self.logs_manager.add_log("DataProcessing", f"Расчёт завершён: площадь = {area:.2f} м², объём = {volume:.2f} м³", "успех")
            st.sidebar.success(f"Расчёт геометрии блока выполнен! Площадь: {area:.2f} м², Объём: {volume:.2f} м³")

        except Exception as e:
            self.logs_manager.add_log("DataProcessing", f"Ошибка расчёта геометрии: {str(e)}", "ошибка")
            st.sidebar.error(f"Ошибка при расчёте: {e}")

    def clear_block_data(self):
        """
        Очищает данные импортированного блока, включая контур, имя и сетку скважин.
        """
        # Очистка данных в session_state
        st.session_state.pop("block_contour", None)
        st.session_state.pop("block_name", None)
        st.session_state.pop("grid_data", None)

        # Логирование очистки
        self.logs_manager.add_log("data_processing", "Данные блока и сетка скважин удалены.", "информация")
        st.sidebar.warning("Все данные блока и сетки удалены.")