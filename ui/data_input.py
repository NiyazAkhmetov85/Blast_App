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
        block_name = st.session_state.get("block_name", "Неизвестный блок")

        if not block_name or block_name == "Неизвестный блок":
            st.warning("Блок не импортирован. Импортируйте блок на вкладке 'Импорт данных блока'.")
        else:
            st.info(f"Импортированный блок: **{block_name}**")

        # Добавляем кнопку для отображения всех параметров session_state
        if st.button("Показать параметры session_state"):
            self.show_all_session_state()

        # Отображаем параметры блока
        self.input_form.render_parameters_section()  

        # Выбор типа сетки
        self.input_form.render_grid_type_selection()  

        # Кнопки управления параметрами
        self.input_form.render_control_buttons()

    def show_all_session_state(self):
        """Вывод всех параметров session_state"""
        st.subheader("Содержимое session_state")
        for key, value in st.session_state.items():
            st.write(f"**{key}**: {value}")


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

        # Кнопка запуска генерации сетки скважин
        if st.button("Запустить генерацию сетки скважин"):
            self.grid_generator.generate_grid()
        
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
    
        # Проверка наличия параметров
        if "user_parameters" in st.session_state and st.session_state["user_parameters"]:
            st.subheader("Утвержденные параметры блока")
    
            # Обход параметров: поддержка как вложенных, так и простых структур
            parameters = st.session_state["user_parameters"]
            if isinstance(parameters, dict):
                for group, params in parameters.items():
                    if isinstance(params, dict):
                        st.write(f"**{group}:**")
                        for param, value in params.items():
                            if isinstance(value, dict) and "value" in value and "description" in value:
                                st.write(f"- {param}: `{value['value']}` ({value['description']})")
                            else:
                                st.write(f"- {param}: `{value}`")
                    else:
                        st.write(f"- {group}: `{params}`")  # Если структура плоская
            else:
                st.warning("⚠ Ошибка: `user_parameters` имеет некорректный формат!")
    
        else:
            st.warning("⚠ Нет утвержденных параметров для отображения.")
    


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
