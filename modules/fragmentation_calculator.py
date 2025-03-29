import streamlit as st
import pandas as pd
import numpy as np
from modules.calculations import Calculations
from utils.logs_manager import LogsManager
from utils.session_state_manager import SessionStateManager

class FragmentationCalculator:
    """
    Класс для расчёта фракционного состава взорванной горной массы (БВР).
    """
    def __init__(self, session_manager: SessionStateManager):
        self.session_manager = session_manager
        self.logs_manager = LogsManager(session_manager)
        self.calc = Calculations(session_manager, self.logs_manager)

        # ✅ Проверяем входные данные
        required_keys = ["user_parameters", "reference_parameters", "grid_data"]
        missing_keys = [key for key in required_keys if key not in st.session_state or not st.session_state[key]]

        if missing_keys:
            st.error(f"❌ Ошибка: отсутствуют входные данные: {', '.join(missing_keys)}")
            self.logs_manager.add_log("fragmentation_calculator", f"Ошибка: отсутствуют данные: {', '.join(missing_keys)}", "ошибка")
            return

        # ✅ Создаем `calculation_results`, если его нет
        if "calculation_results" not in st.session_state:
            st.session_state["calculation_results"] = {}

        self.logs_manager.add_log("fragmentation_calculator", "FragmentationCalculator успешно инициализирован.", "успех")

    def run_calculations(self):
        """
        Запускает последовательное выполнение всех расчетов БВР.
        """
        # self.session_manager.set_state("current_step", "Запуск расчетов БВР")
        st.session_state["status_message"] = "Запуск расчетов БВР..."

        try:
            # ✅ Прогресс-бар
            progress_bar = st.progress(0)
            calculation_steps = [
                self.calc.calculate_rdi,
                self.calc.calculate_hf,
                self.calc.calculate_a,
                self.calc.calculate_s_anfo,
                self.calc.calculate_q,
                self.calc.calculate_x_max,
                self.calc.calculate_n,
                self.calc.calculate_b,
                self.calc.calculate_g_n,
                self.calc.calculate_x_50,
            ]

            # ✅ Запуск расчетов
            for i, step in enumerate(calculation_steps, 1):
                step_name = step.__name__
                self.logs_manager.add_log("fragmentation_calculator", f"Выполняется: {step_name}", "информация")
                step()
                progress_bar.progress(i / len(calculation_steps))

            # # ✅ Сохранение расчетов
            # self.save_to_session_state()

            self.logs_manager.add_log("fragmentation_calculator", "✅ Все расчеты БВР успешно выполнены.", "успех")
            st.sidebar.success("✅ Все расчеты БВР успешно выполнены и сохранены.")

        except Exception as e:
            self.logs_manager.add_log("fragmentation_calculator", f"Ошибка при расчетах БВР: {str(e)}", "ошибка")
            st.sidebar.error(f"❌ Ошибка при выполнении расчетов БВР: {e}")

        finally:
            self.session_manager.set_state("current_step", None)
            st.session_state["status_message"] = "Готов к работе"

    # def save_to_session_state(self):
    #     """
    #     Сохраняет расчётные параметры БВР в session_state.
    #     """
    #     if "calculation_results" not in st.session_state:
    #         st.session_state["calculation_results"] = {}

    #     # Сохраняем параметры, если они существуют
    #     for param in ["x_max", "x_50", "b"]:
    #         if param in st.session_state:
    #             st.session_state["calculation_results"][param] = st.session_state[param]

    #     if not st.session_state["calculation_results"]:
    #         st.warning("⚠ Расчеты выполнены, но результатов нет. Проверьте входные данные.")
    #         self.logs_manager.add_log("fragmentation_calculator", "Предупреждение: calculation_results пуст после расчетов.", "предупреждение")
