import streamlit as st
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

        # Кнопка для запуска загрузки файла
        if st.button("Импортировать контур блока"):
            st.session_state["show_file_uploader"] = True  

        # Отображаем загрузчик файла ТОЛЬКО после нажатия кнопки
        if st.session_state.get("show_file_uploader", False):
            uploaded_file = st.file_uploader("Выберите файл с контуром блока", type=["str", "csv", "txt"])
            
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
        block_name = st.session_state.get("block_name")
    
        if not block_name or block_name == "Неизвестный блок":
            st.warning("Блок не импортирован. Импортируйте блок на вкладке 'Импорт данных блока'.")
        else:
            st.info(f"Импортированный блок: **{block_name}**")

        self.input_form.render_parameters_section()  # Отображаем параметры

        st.subheader("Выбор типа сетки")
        self.input_form._render_grid_type_selection()  # Отображаем выбор сетки

        st.subheader("Управление параметрами")
        self.input_form.render_control_buttons()  # Отображаем кнопки управления параметрами

    def show_visualization(self):
        """
        Экран для визуализации блока, сетки и метрик.
        """
        st.header("Визуализация блока и сетки")
        
        # Отображаем информацию о загруженном блоке и выбранном типе сетки
        st.text(f"Импортированный блок: {st.session_state.get('block_name', 'Неизвестный')}")
        st.text(f"Тип сетки: {st.session_state.get('user_parameters', {}).get('grid_type', 'Не указано')}")

        # Кнопка запуска расчёта метрик сетки
        if st.button("Запустить расчет метрик"):
            self.grid_generator.calculate_grid_metrics()

        # Кнопки визуализации
        if st.button("Визуализировать контур блока"):
            self.visualizer.plot_block_contour()

        if st.button("Визуализировать сетку скважин"):
            self.visualizer.plot_drill_grid()

        if st.button("Комбинированная визуализация"):
            self.visualizer.plot_combined()

        # Кнопка очистки визуализации
        if st.button("Очистить визуализацию"):
            self.visualizer.clear_visualization()

    def show_summary_screen(self):
        """
        Экран итогового обзора перед переходом к следующим разделам.
        """
        st.title("Итоговый обзор блока")

        # Отображение имени импортированного блока
        block_name = st.session_state.get("block_name", "Не импортирован")
        st.subheader(f"Импортированный блок: {block_name}")

        # Отображение утвержденных параметров блока
        if "user_parameters" in st.session_state:
            st.subheader("Утвержденные параметры блока")
            for group, params in st.session_state["user_parameters"].items():
                st.write(f"**{group}:**")
                for param, value in params.items():
                    st.write(f"- {param}: `{value}`")

        # Отображение рассчитанных метрик сетки
        if "grid_data" in st.session_state and not st.session_state["grid_data"].empty:
            st.subheader("Рассчитанные метрики сетки")
            grid_data = st.session_state["grid_data"]
            st.write(f"- **Количество скважин:** {len(grid_data)}")

            # Если в session_state есть расчетные метрики, отображаем их
            if "block_geometry" in st.session_state:
                st.write("**Геометрия блока:**")
                for key, value in st.session_state["block_geometry"].items():
                    st.write(f"- {key}: `{value}`")

        # Визуализация блока и сетки
        if "block_contour" in st.session_state and "grid_data" in st.session_state:
            st.subheader("Визуализация блока и сетки")
            self.visualizer.display_combined_visualization()

        # Кнопка для перехода к следующим разделам
        st.markdown("---")
        if st.button("Перейти к следующим разделам"):
            st.session_state["current_screen"] = "results_summary"
            logs_manager.add_log("summary_screen", "Пользователь завершил проверку и перешел к расчетам.", "информация")
            st.experimental_rerun()

# Пример использования
if __name__ == "__main__":
    session_manager = SessionStateManager()
    logs_manager = LogsManager()
    data_input = DataInput(session_manager, logs_manager)
    st.sidebar.title("Меню")
    option = st.sidebar.radio("Выберите экран", ["Импорт блока", "Ввод параметров", "Визуализация", "Итоговый обзор"])
    if option == "Импорт блока":
        data_input.show_import_block()
    elif option == "Ввод параметров":
        data_input.show_input_form()
    elif option == "Визуализация":
        data_input.show_visualization()
    elif option == "Итоговый обзор":
        data_input.show_summary_screen()
