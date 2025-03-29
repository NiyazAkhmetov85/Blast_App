import streamlit as st
from modules.fragmentation_calculator import FragmentationCalculator
from modules.psd_calculator import PSDCalculator
from modules.results_display import ResultsDisplay
from utils.session_state_manager import SessionStateManager
from utils.logs_manager import LogsManager

class ResultsSummary:
    """
    Экран для отображения итоговых расчётов, таблицы PSD и визуализации результатов.
    """
    def __init__(self, session_manager: SessionStateManager, logs_manager: LogsManager):
        self.session_manager = session_manager
        self.logs_manager = logs_manager
        self.calculator = FragmentationCalculator(session_manager)
        self.psd_calculator = PSDCalculator(session_manager)
        self.results_display = ResultsDisplay()

    def show_results_summary(self):
        """
        Интерфейс итоговых расчётов, PSD-таблицы и визуализации кумулятивной кривой.
        """
        st.header("Итоговые расчёты и визуализация")

        # Проверяем наличие имени блока
        block_name = st.session_state.get("block_name", "Неизвестный блок")

        if not block_name or block_name == "Неизвестный блок":
            st.warning("Блок не импортирован. Импортируйте блок на вкладке 'Импорт данных блока'.")
        else:
            st.info(f"Импортированный блок: **{block_name}**")


        # Кнопка для запуска расчётов
        if st.button("Запустить расчёты"):
            with st.spinner("Выполняются расчёты..."):
                self.calculator.run_calculations()  # Расчёт параметров БВР
    #             self.psd_calculator.run_calculations()  # Формирование PSD-таблицы


    #     # Блок визуализации
    #     st.subheader("Визуализация результатов")

    #     col1, col2 = st.columns(2)

    #     with col1:
    #         if st.button("Показать таблицу PSD"):
    #             self.display_psd_table()

    #     with col2:
    #         if st.button("Показать кумулятивную кривую"):
    #             self.display_cumulative_curve()

    #     # Блок очистки данных
    #     st.subheader("Очистка визуализации")

    #     col3, col4 = st.columns(2)

    #     with col3:
    #         if st.button("Очистить таблицу"):
    #             self.session_manager.set_state("psd_table", None)
    #             st.warning("Таблица PSD очищена.")

    #     with col4:
    #         if st.button("Очистить график"):
    #             self.session_manager.set_state("cumulative_curve", None)
    #             st.warning("График кумулятивной кривой очищен.")

    # def display_psd_table(self):
    #     """
    #     Отображение итоговой PSD-таблицы с x_values, P(x) эталонные и P(x) расчётные.
    #     """
    #     df_psd = st.session_state.get("psd_table")

    #     if df_psd is None or df_psd.empty:
    #         st.warning("PSD-таблица отсутствует.")
    #         return

    #     st.subheader("Итоговая таблица PSD")
    #     st.dataframe(df_psd)

    # def display_cumulative_curve(self):
    #     """
    #     Визуализация кумулятивной кривой распределения фрагментов.
    #     """
    #     df_psd = st.session_state.get("psd_table")

    #     if df_psd is None or df_psd.empty:
    #         st.warning("Нет данных для построения графика.")
    #         return

    #     import plotly.express as px

    #     fig = px.line(
    #         df_psd,
    #         x="Размер фрагмента (x), мм",
    #         y=["Эталонные P(x), %", "P(x) рассчитанные, %"],
    #         title="Кумулятивная кривая распределения фрагментов",
    #         labels={"value": "Кумулятивное распределение (%)", "variable": "Тип"},
    #         markers=True
    #     )
    #     st.plotly_chart(fig)
