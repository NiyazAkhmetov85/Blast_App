import streamlit as st
import pandas as pd
import math
import json
import numpy as np
from modules.data_processing import DataProcessing
from modules.grid_generator import GridGenerator
from modules.visualization import Visualization
from ui.input_form import InputForm
from utils.session_state_manager import SessionStateManager
from utils.logs_manager import LogsManager

class DataInput:
    def __init__(self, session_manager: SessionStateManager, logs_manager: LogsManager):
        self.session_manager = session_manager
        self.logs_manager = logs_manager
        self.data_processor = DataProcessing(session_manager, logs_manager)
        self.grid_generator = GridGenerator(session_manager, logs_manager)
        self.visualizer = Visualization(session_manager, logs_manager)
        self.input_form = InputForm(session_manager, logs_manager)

    def show_import_block(self):
        """
        Экран для импорта и начальной визуализации блока.
        """
        st.header("Импорт данных блока")
    
        # 🔹 Загрузчик файла (доступен сразу, без кнопки)
        uploaded_file = st.file_uploader("Выберите файл с контуром блока", type=["str", "csv", "txt"])
    
        # 🔹 Если файл загружен, выполняем обработку          
        if uploaded_file is not None:
            self.data_processor.load_block_contour(uploaded_file)
            st.session_state["show_file_uploader"] = False  # Скрываем загрузчик после загрузки

                # Отображение загруженного DataFrame
            if "block_contour" in st.session_state and not st.session_state["block_contour"].empty:
                df = st.session_state["block_contour"]
                st.subheader("Просмотр загруженных данных")
                st.write(df)
            

        # Кнопка визуализации блока
        if st.button("Визуализировать импортированный блок") and "block_contour" in st.session_state:
            self.visualizer.plot_block_contour()

        # Кнопка очистки данных блока
        if st.button("Очистить визуализацию и удалить импортированный блок"):
            self.data_processor.clear_block_data()
            self.visualizer.clear_visualization()
            st.session_state.pop("block_name", None)
            st.session_state.pop("block_contour", None)

    def show_input_form(self):
        """
        Экран для ввода параметров и выбора сетки скважин.
        """
        st.header("Ввод параметров и выбор сетки")

        # Проверяем наличие имени блока
        block_name = st.session_state.get("block_name", "Неизвестный блок")

        if not block_name or block_name == "Неизвестный блок":
            st.warning("Блок не импортирован. Импортируйте блок на вкладке 'Импорт данных блока'.")
        else:
            st.info(f"Импортированный блок: **{block_name}**")


        # Отображаем параметры блока
        self.input_form.render_parameters_section()  

        # Выбор типа сетки
        self.input_form.render_grid_type_selection()  

        # Кнопки управления параметрами
        self.input_form.render_control_buttons()


    def show_visualization(self):
        """
        Экран для визуализации блока, сетки и метрик.
        """
        st.header("Визуализация блока и сетки скважин")
        
        # Проверяем наличие имени блока
        block_name = st.session_state.get("block_name", "Неизвестный блок")

        if not block_name or block_name == "Неизвестный блок":
            st.warning("Блок не импортирован. Импортируйте блок на вкладке 'Импорт данных блока'.")
        else:
            st.info(f"Импортированный блок: **{block_name}**")

        st.info(f"Тип сетки: {st.session_state.get('user_parameters', {}).get('grid_type', 'Не указано')}")

        # Кнопка запуска генерации сетки скважин и расчёта параметров сетки
        if st.button("Запустить генерацию сетки скважин и расчет параметров сетки"):
            self.grid_generator.generate_grid()
            self.grid_generator.calculate_grid_metrics()
            st.subheader("Расчитанные координаты скважин")
            if st.session_state.get("grid_generated", False):
                st.dataframe(self.grid_generator.grid_data, width=600)
            
            if st.session_state.get("grid_metrics"):
                st.dataframe(st.session_state["grid_metrics"], width=600)
                
        # Кнопка запуска комбинированной визуализации
        if st.button("Комбинированная визуализация"):
            self.visualizer.plot_combined()

        # Кнопка очистки визуализации
        if st.button("Очистить визуализацию"):
            self.visualizer.clear_visualization()


    def show_summary_screen(self):
        """
        Экран итогового обзора перед переходом к следующим разделам.
        """
        st.title("Исходные параметры блока")
    
        # Проверяем наличие имени блока
        block_name = st.session_state.get("block_name", "Неизвестный блок")
    
        if not block_name or block_name == "Неизвестный блок":
            st.warning("Блок не импортирован. Импортируйте блок на вкладке 'Импорт данных блока'.")
        else:
            st.info(f"Импортированный блок: **{block_name}**")

            # 2. Исходные параметры БВР
            st.subheader("Исходные параметры блока")
            
            # Получение данных
            params_all = st.session_state.get("user_parameters", {})
            reference_all = st.session_state.get("reference_parameters", {})
            param_definitions = st.session_state.get("parameters", {})
            
            # Объединяем параметры
            combined_params = {**params_all, **reference_all}
            categorized_params = {}
            
            for key, value in combined_params.items():
                meta = param_definitions.get(key, {})
                description = meta.get("description", key)
                unit = meta.get("unit", "")
                category = meta.get("category", "Прочие параметры")
            
                # Безопасное округление
                try:
                    numeric_value = round(float(value), 4)
                except (ValueError, TypeError):
                    numeric_value = str(value)
            
                row = (f"{description} ({key})", numeric_value, unit)
                
                if category not in categorized_params:
                    categorized_params[category] = []
                categorized_params[category].append(row)
            
            # Отображение таблиц по категориям
            for category_name, rows in categorized_params.items():
                if not rows:
                    continue
                st.markdown(f"**{category_name}**")
                df = pd.DataFrame(rows, columns=["Параметр", "Значение", "Ед. изм."])
                
                # Визуально зафиксируем ширину через markdown (альтернатива .style)
                st.markdown(
                    df.to_html(index=False, escape=False),
                    unsafe_allow_html=True
                )
