import streamlit as st
from modules.fragmentation_calculator import FragmentationCalculator
from modules.psd_calculator import PSDCalculator
from modules.results_display import ResultsDisplay
from utils.session_state_manager import SessionStateManager
from utils.logs_manager import LogsManager

class ResultsSummary:
    """
    Экран для отображения итоговых расчётов, PSD-таблицы и визуализации результатов.
    """
    def __init__(self, session_manager: SessionStateManager, logs_manager: LogsManager):
        self.session_manager = session_manager
        self.logs_manager = logs_manager
        self.calculator = FragmentationCalculator(session_manager)
        self.psd_calculator = PSDCalculator(session_manager)
        self.results_display = ResultsDisplay()

    def show_results_summary(self):
        """
        Интерфейс итоговых расчётов и визуализации.
        """
        st.header("📊 Итоговые расчёты и визуализация")

        block_name = self.session_manager.get_state("current_block", "Не задан")
        st.info(f"🔹 Текущий блок: **{block_name}**")

        # Кнопка для запуска расчётов
        if st.button("▶ Запустить расчёты"):
            with st.spinner("⏳ Выполняются расчёты..."):
                self.calculator.run_calculations()  # Расчёт параметров БВР
                self.psd_calculator.run_calculations()  # Формирование PSD-таблицы
                self.logs_manager.add_log("results_summary", "✅ Все расчёты успешно выполнены", "успех")
            st.success("✅ Все расчёты успешно выполнены!")

        # Блок визуализации
        st.subheader("📊 Визуализация результатов")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("📊 Показать таблицу PSD"):
                self.results_display.display_psd_table()

        with col2:
            if st.button("📈 Показать кумулятивную кривую"):
                self.results_display.display_cumulative_curve()

        with col3:
            if st.button("📋 Показать параметры блока"):
                self.results_display.display_summary_table()

        # Блок очистки данных
        st.subheader("🗑 Очистка визуализации")

        col4, col5 = st.columns(2)

        with col4:
            if st.button("🗑 Очистить таблицу"):
                self.session_manager.set_state("psd_table", None)
                st.warning("⚠ Таблица PSD очищена.")

        with col5:
            if st.button("🗑 Очистить график"):
                self.session_manager.set_state("cumulative_curve", None)
                st.warning("⚠ График кумулятивной кривой очищен.")
