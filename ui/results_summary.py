import streamlit as st
from modules.fragmentation_calculator import FragmentationCalculator
from modules.results_display import ResultsDisplay
from utils.session_state_manager import SessionStateManager
from utils.logs_manager import LogsManager


class ResultsSummary:
    def __init__(self, session_manager: SessionStateManager, logs_manager: LogsManager):
        self.session_manager = session_manager
        self.logs_manager = logs_manager
        self.calculator = FragmentationCalculator(session_manager)
        self.results_display = ResultsDisplay()  

    def show_results_summary(self):
        """
        Экран для работы с расчетными данными и визуализацией.
        """
        st.header("Итоговые расчеты и визуализация")
    
        block_name = self.session_manager.get_state("current_block", "Не задан")
        st.info(f"🔹 Текущий блок: **{block_name}**")
    
        # Кнопка для запуска расчетов
        if st.button("▶ Запустить расчеты"):
            with st.spinner("⏳ Выполняются расчеты..."):
                self.calculator.run_calculations()
                self.logs_manager.add_log("results_summary", "✅ Расчеты успешно выполнены", "успех")
            st.success("✅ Расчеты выполнены!")
    
        # Раздел с кнопками визуализации
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
    
        # Раздел с кнопками очистки
        st.subheader("🗑 Очистка визуализации")
    
        col4, col5 = st.columns(2)
    
        with col4:
            if st.button("🗑 Очистить таблицу"):
                self.session_manager.set_state("psd_table", None)
                st.warning("⚠ Таблица PSD очищена.")
    
        with col5:  # ✅ Исправлен отступ
            if st.button("🗑 Очистить график"):
                self.session_manager.set_state("cumulative_curve", None)
                st.warning("⚠ График кумулятивной кривой очищен.")
