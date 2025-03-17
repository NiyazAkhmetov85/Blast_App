import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from modules.data_processing import DataProcessing  # Модуль обработки данных
from modules.visualization import Visualization  # Модуль визуализации
from utils.session_state_manager import SessionStateManager
from utils.logs_manager import LogsManager

# Создание экземпляров классов
session_manager = SessionStateManager()
logs_manager = LogsManager()
processor = DataProcessing(session_manager, logs_manager)
visualizer = Visualization(session_manager, logs_manager)

st.title("Импорт и визуализация контура блока")

# Выбор файла для загрузки
uploaded_file = st.file_uploader("Загрузите файл с контуром блока", type=["csv", "txt", "str"])

if uploaded_file is not None:
    # Загружаем данные
    processor.load_block_contour(uploaded_file)
    df = st.session_state.get("block_contour", None)
    
    if df is not None and not df.empty:
        # Отображаем загруженные данные
        st.subheader("Просмотр загруженных данных")
        st.write(df)
        
        # Визуализация контура блока
        st.subheader("Визуализация контура блока")
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.plot(df["X"], df["Y"], marker='o', linestyle='-', color='b', label="Контур блока")
        ax.fill(df["X"], df["Y"], alpha=0.2)
        ax.set_xlabel("Координата X")
        ax.set_ylabel("Координата Y")
        ax.set_title("Контур загруженного блока")
        ax.legend()
        st.pyplot(fig)
    else:
        st.error("Ошибка при обработке файла. Проверьте формат данных.")

# Кнопки для дополнительных визуализаций
st.subheader("Дополнительные визуализации")
if st.button("Показать контур блока"):
    visualizer.plot_block_contour()

if st.button("Показать сетку скважин"):
    visualizer.plot_drill_grid()

if st.button("Показать комбинированную визуализацию"):
    visualizer.plot_combined()

if st.button("Очистить визуализацию"):
    visualizer.clear_visualization()
