import math
import json
import numpy as np
import pandas as pd
import streamlit as st
from scipy.special import gamma
from utils.logs_manager import LogsManager
from utils.session_state_manager import SessionStateManager


# Декоратор для обработки ошибок
def error_handler(func):
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception as e:
            LogsManager.add_log(module="calculations", event=f"Ошибка в {func.__name__}: {str(e)}", log_type="ошибка")
            st.error(f"Ошибка в {func.__name__}: {str(e)}")
    return wrapper

class Calculations:
    """
    Класс для выполнения расчетов параметров буровзрывных работ.
    """

    def __init__(self, session_manager: SessionStateManager, logs_manager: LogsManager):
        """
        Инициализация менеджера загрузки параметров.
        """
        self.session_manager = session_manager
        self.logs_manager = logs_manager
        self.results = {}

        self.params = st.session_state.get("user_parameters", {})

        if not st.session_state.get("reference_parameters"):
            st.warning("Утверждённые эталонные значения отсутствуют. Проверьте ввод данных.")
            self.logs_manager.add_log(module="calculations", event="Ошибка: отсутствуют эталонные значения.", log_type="ошибка")

        self._initialize_session_state()

    def _initialize_session_state(self):
        """
        Инициализирует ключи в session_state.
        """
        required_keys = ["reference_parameters", "calculation_results", "P_x_data"]
        for key in required_keys:
            if key not in st.session_state or st.session_state[key] is None:
                st.session_state[key] = {} if key == "calculation_results" else None

        self.logs_manager.add_log(module="calculations", event="Инициализация session_state завершена.", log_type="успех")

    # Блок 1: Расчет вспомогательных параметров
    @error_handler
    def calculate_rdi(self):
        """
        Расчет RDI (влияние плотности породы).
        """
        rho = self.params.get("rho")

        # Проверяем, есть ли значение и является ли оно числом
        if rho is None or not isinstance(rho, (int, float)):
            st.sidebar.warning("❌ Ошибка: Параметр rho отсутствует или имеет неверный формат.")
            self.logs_manager.add_log(module="calculations", event="Ошибка: некорректное значение rho.", log_type="ошибка")
            return

        # Выполняем расчет
        self.results["RDI"] = 0.025 * rho - 50

        # Готовим session_state
        if "calculation_results" not in st.session_state:
            st.session_state["calculation_results"] = {}

        # Очистка предыдущего значения RDI перед записью нового
        st.session_state["calculation_results"].pop("RDI", None)
        st.session_state["calculation_results"]["RDI"] = self.results["RDI"]

        # Логируем успешный расчет с указанием результата
        self.logs_manager.add_log(module="calculations", event=f"✅ Успешный расчет RDI: {self.results['RDI']:.2f}", log_type="успех")
        st.sidebar.success(f"✅ RDI успешно рассчитан: {self.results['RDI']:.2f}")

    @error_handler
    def calculate_hf(self):
        """
        Расчет HF (фактор твердости породы).
        """
        E = self.params.get("E")
        sigma_c = self.params.get("sigma_c")

        # Проверяем, есть ли значения и являются ли они числами
        if E is None or sigma_c is None or not isinstance(E, (int, float)) or not isinstance(sigma_c, (int, float)):
            st.warning("❌ Ошибка: Параметр E или sigma_c отсутствует или имеет неверный формат.")
            self.logs_manager.add_log(module="calculations", event="Ошибка: некорректное значение E или sigma_c.", log_type="ошибка")
            return

        # Выполняем расчет
        self.results["HF"] = E / 3 if E < 50 else sigma_c / 5

        # Готовим session_state
        if "calculation_results" not in st.session_state:
            st.session_state["calculation_results"] = {}

        # Очистка предыдущего значения HF перед записью нового
        st.session_state["calculation_results"].pop("HF", None)
        st.session_state["calculation_results"]["HF"] = self.results["HF"]

        # Логируем успешный расчет с указанием результата
        self.logs_manager.add_log(module="calculations", event=f"✅ Успешный расчет HF: {self.results['HF']:.2f}", log_type="успех")
        st.sidebar.success(f"✅ HF успешно рассчитан: {self.results['HF']:.2f}")

    @error_handler
    def calculate_a(self):
        """
        Расчет A (фактор породы).
        """
        RMD = self.params.get("RMD")
        RDI = self.results.get("RDI")
        HF = self.results.get("HF")

        # Проверяем, есть ли значения и являются ли они числами
        if None in (RMD, RDI, HF) or not all(isinstance(val, (int, float)) for val in [RMD, RDI, HF]):
            st.warning("❌ Ошибка: Параметр RMD, RDI или HF отсутствует или имеет неверный формат.")
            self.logs_manager.add_log(module="calculations", event="Ошибка: некорректные значения RMD, RDI или HF.", log_type="ошибка")
            return

        # Выполняем расчет
        self.results["A"] = 0.06 * (RMD + RDI + HF)

        # Готовим session_state
        if "calculation_results" not in st.session_state:
            st.session_state["calculation_results"] = {}

        # Очищаем только старое значение "A" перед записью
        st.session_state["calculation_results"].pop("A", None)
        st.session_state["calculation_results"]["A"] = self.results["A"]

        # Логируем успешный расчет с указанием результата
        self.logs_manager.add_log(module="calculations", event=f"✅ Успешный расчет A: {self.results['A']:.2f}", log_type="успех")
        st.sidebar.success(f"✅ A успешно рассчитан: {self.results['A']:.2f}")

    @error_handler
    def calculate_s_anfo(self):
        """
        Расчет s_ANFO (влияние энергии взрывчатого вещества).
        """
        energy_vv = self.params.get("energy_vv")

        # Проверяем, есть ли значение и является ли оно числом
        if energy_vv is None or not isinstance(energy_vv, (int, float)):
            st.warning("❌ Ошибка: Параметр energy_vv отсутствует или имеет неверный формат.")
            self.logs_manager.add_log(module="calculations", event="Ошибка: некорректное значение energy_vv.", log_type="ошибка")
            return

        energy_anfo = 4.2  # Фиксированное значение

        # Выполняем расчет
        self.results["s_ANFO"] = (energy_vv / energy_anfo) * 100

        # Готовим session_state
        if "calculation_results" not in st.session_state:
            st.session_state["calculation_results"] = {}

        # Очистка предыдущего значения перед записью нового
        st.session_state["calculation_results"].pop("s_ANFO", None)
        st.session_state["calculation_results"]["s_ANFO"] = self.results["s_ANFO"]

        # Логируем успешный расчет с указанием результата
        self.logs_manager.add_log(module="calculations", event=f"✅ Успешный расчет s_ANFO: {self.results['s_ANFO']:.2f}%", log_type="успех")
        st.sidebar.success(f"✅ s_ANFO успешно рассчитан: {self.results['s_ANFO']:.2f}%")

    @error_handler
    def calculate_q(self):
        """
        Расчет специфического заряда (q).
        """
        Q = self.params.get("Q")
        H = self.params.get("H")
        S = self.params.get("S")
        B = self.params.get("B")

        # Проверяем, есть ли значение и являются ли они числами
        if None in (Q, H, S, B):
            st.warning("❌ Ошибка: Отсутствует параметр Q, H, S или B, расчет q невозможен.")
            self.logs_manager.add_log(module="calculations", event="Ошибка: отсутствует один из параметров Q, H, S, B.", log_type="ошибка")
            return

        if not all(isinstance(val, (int, float)) for val in [Q, H, S, B]):
            st.warning("❌ Ошибка: Один из параметров Q, H, S, B имеет некорректный формат.")
            self.logs_manager.add_log(module="calculations", event="Ошибка: некорректный формат параметров Q, H, S, B.", log_type="ошибка")
            return

        if H == 0 or S == 0 or B == 0:
            st.error("❌ Ошибка: значения H, S или B не могут быть равны нулю.")
            self.logs_manager.add_log(module="calculations", event="Ошибка: значения H, S или B равны 0, деление невозможно.", log_type="ошибка")
            return

        # Выполняем расчет
        self.results["q"] = Q / (H * S * B)

        # Готовим session_state
        if "calculation_results" not in st.session_state:
            st.session_state["calculation_results"] = {}

        # Очистка предыдущего значения перед записью нового
        st.session_state["calculation_results"].pop("q", None)
        st.session_state["calculation_results"]["q"] = self.results["q"]

        # Логируем успешный расчет с указанием результата
        self.logs_manager.add_log(module="calculations", event=f"✅ Успешный расчет специфического заряда q: {self.results['q']:.4f}", log_type="успех")
        st.sidebar.success(f"✅ Специфический заряд q успешно рассчитан: {self.results['q']:.4f}")

    # Блок 2: Расчет ключевых параметров
    @error_handler
    def calculate_x_max(self):
        """
        Расчет максимального размера фрагмента (x_max).
        """
        in_situ_block_size = self.params.get("in_situ_block_size")
        S = self.params.get("S")
        B = self.params.get("B")

        # Проверяем, есть ли значение и являются ли они числами
        if None in (in_situ_block_size, S, B):
            st.warning("❌ Ошибка: Отсутствует параметр in_situ_block_size, S или B, расчет x_max невозможен.")
            self.logs_manager.add_log(module="calculations", event="Ошибка: отсутствует один из параметров in_situ_block_size, S, B.", log_type="ошибка")
            return

        if not all(isinstance(val, (int, float)) for val in [in_situ_block_size, S, B]):
            st.warning("❌ Ошибка: Один из параметров in_situ_block_size, S, B имеет некорректный формат.")
            self.logs_manager.add_log(module="calculations", event="Ошибка: некорректный формат параметров in_situ_block_size, S, B.", log_type="ошибка")
            return

        # Преобразование в мм
        S *= 1000  
        B *= 1000  

        # Выполняем расчет
        self.results["x_max"] = min(in_situ_block_size, S, B)

        # Готовим session_state
        if "calculation_results" not in st.session_state:
            st.session_state["calculation_results"] = {}

        # Очистка предыдущего значения перед записью нового
        st.session_state["calculation_results"].pop("x_max", None)
        st.session_state["calculation_results"]["x_max"] = self.results["x_max"]

        # Логируем успешный расчет с указанием результата
        self.logs_manager.add_log(module="calculations", event=f"✅ Успешный расчет x_max: {self.results['x_max']:.2f} мм", log_type="успех")
        st.sidebar.success(f"✅ Максимальный размер фрагмента x_max успешно рассчитан: {self.results['x_max']:.2f} мм")

    @error_handler
    def calculate_n(self):
        """
        Расчет коэффициента равномерности распределения (n).
        """
        x_max = self.results.get("x_max")
        x_50 = self.params.get("x_50")
        S = self.params.get("S")
        B = self.params.get("B")
        Ø_h = self.params.get("Ø_h", 0) / 1000  # Приведение к метрам
        SD = self.params.get("SD")
        L_b = self.params.get("L_b")
        L_c = self.params.get("L_c")
        L_tot = self.params.get("L_tot")
        H = self.params.get("H")

        # Проверка наличия всех необходимых параметров
        missing_params = [p for p in ["x_max", "x_50", "S", "B", "Ø_h", "SD", "L_b", "L_c", "L_tot", "H"]
                        if locals()[p] is None]
        
        if missing_params:
            st.warning(f"❌ Ошибка: Отсутствуют параметры: {', '.join(missing_params)}. Расчет n невозможен.")
            self.logs_manager.add_log(module="calculations", event=f"Ошибка: Отсутствуют параметры {missing_params}.", log_type="ошибка")
            return

        # Проверяем, являются ли параметры числами
        if not all(isinstance(locals()[p], (int, float)) for p in ["x_max", "x_50", "S", "B", "Ø_h", "SD", "L_b", "L_c", "L_tot", "H"]):
            st.warning("❌ Ошибка: Некоторые параметры имеют некорректный формат.")
            self.logs_manager.add_log(module="calculations", event="Ошибка: Некоторые параметры имеют некорректный формат.", log_type="ошибка")
            return

        # Проверка деления на 0
        if H == 0 or B == 0 or L_tot == 0:
            st.error("❌ Ошибка: H, B и L_tot должны быть больше 0.")
            self.logs_manager.add_log(module="calculations", event="Ошибка: H, B или L_tot равны 0.", log_type="ошибка")
            return

        # Выполняем расчет
        self.results["n"] = (
            2 * math.log(2) * math.log(x_max / x_50) *
            (2.2 - 0.014 * (B / Ø_h)) *
            (1 - SD / B) *
            math.sqrt((1 + S / B) / 2) *
            ((L_b - L_c) / L_tot + 0.1) ** 0.1 *
            (L_tot / H)
        )

        # Готовим session_state
        if "calculation_results" not in st.session_state:
            st.session_state["calculation_results"] = {}

        # Очистка предыдущего значения перед записью нового
        st.session_state["calculation_results"].pop("n", None)
        st.session_state["calculation_results"]["n"] = self.results["n"]

        # Логируем успешный расчет с указанием результата
        self.logs_manager.add_log(module="calculations", event=f"✅ Успешный расчет n: {self.results['n']:.4f}", log_type="успех")
        st.sidebar.success(f"✅ Коэффициент равномерности n успешно рассчитан: {self.results['n']:.4f}")

    @error_handler
    def calculate_b(self):
        """
        Расчет b (параметра формы кривой).
        """
        x_max = self.results.get("x_max")
        x_50 = self.params.get("x_50")
        n = self.results.get("n")

        # Проверка наличия всех необходимых параметров
        missing_params = [p for p in ["x_max", "x_50", "n"] if locals()[p] is None]

        if missing_params:
            st.warning(f"❌ Ошибка: Отсутствуют параметры: {', '.join(missing_params)}. Расчет b невозможен.")
            self.logs_manager.add_log(module="calculations", event=f"Ошибка: Отсутствуют параметры {missing_params}.", log_type="ошибка")
            return

        # Проверяем, являются ли параметры числами
        if not all(isinstance(locals()[p], (int, float)) for p in ["x_max", "x_50", "n"]):
            st.warning("❌ Ошибка: Некоторые параметры имеют некорректный формат.")
            self.logs_manager.add_log(module="calculations", event="Ошибка: Некоторые параметры имеют некорректный формат.", log_type="ошибка")
            return

        # Проверка деления на 0
        if x_50 <= 0:
            st.error("❌ Ошибка: x_50 должен быть больше 0.")
            self.logs_manager.add_log(module="calculations", event="Ошибка: x_50 <= 0.", log_type="ошибка")
            return

        # Выполняем расчет
        self.results["b"] = 2 * math.log(2) * math.log(x_max / x_50) * n

        # Готовим session_state
        if "calculation_results" not in st.session_state:
            st.session_state["calculation_results"] = {}

        # Очистка предыдущего значения перед записью нового
        st.session_state["calculation_results"].pop("b", None)
        st.session_state["calculation_results"]["b"] = self.results["b"]

        # Логируем успешный расчет с указанием результата
        self.logs_manager.add_log(module="calculations", event=f"✅ Успешный расчет b: {self.results['b']:.4f}", log_type="успех")
        st.sidebar.success(f"✅ Параметр формы кривой b успешно рассчитан: {self.results['b']:.4f}")

    @error_handler
    def calculate_g_n(self):
        """
        Расчет показателя g(n).
        """
        n = self.results.get("n")

        # Проверяем наличие параметра n
        if n is None:
            st.warning("❌ Ошибка: Отсутствует параметр n, расчет g(n) невозможен.")
            self.logs_manager.add_log(module="calculations", event="Ошибка: Параметр n отсутствует.", log_type="ошибка")
            return

        # Проверяем, является ли параметр числом
        if not isinstance(n, (int, float)):
            st.warning("❌ Ошибка: Параметр n имеет некорректный формат.")
            self.logs_manager.add_log(module="calculations", event="Ошибка: Параметр n имеет некорректный формат.", log_type="ошибка")
            return

        # Проверяем, что n > 0
        if n <= 0:
            st.error("❌ Ошибка: Параметр n должен быть больше 0.")
            self.logs_manager.add_log(module="calculations", event="Ошибка: n <= 0.", log_type="ошибка")
            return

        try:
            ln_2 = math.log(2)
            gamma_value = math.gamma(1 + 1 / n)
            self.results["g_n"] = (ln_2 ** (1 / n)) / gamma_value
        except ZeroDivisionError:
            st.error("❌ Ошибка: Деление на 0 при расчете g(n).")
            self.logs_manager.add_log(module="calculations", event="Ошибка: Деление на 0 при расчете g(n).", log_type="ошибка")
            return

        # Готовим session_state
        if "calculation_results" not in st.session_state:
            st.session_state["calculation_results"] = {}

        # Очистка предыдущего значения перед записью нового
        st.session_state["calculation_results"].pop("g_n", None)
        st.session_state["calculation_results"]["g_n"] = self.results["g_n"]

        # Логируем успешный расчет с указанием результата
        self.logs_manager.add_log(module="calculations", event=f"✅ Успешный расчет g(n): {self.results['g_n']:.4f}", log_type="успех")
        st.sidebar.success(f"✅ Показатель g(n) успешно рассчитан: {self.results['g_n']:.4f}")

    @error_handler
    def calculate_x_50(self):
        """
        Расчет медианного размера фрагмента (x_50).
        """
        g_n = self.results.get("g_n")
        A = self.results.get("A")
        Q = self.params.get("Q")
        s_ANFO = self.params.get("s_ANFO")
        q = self.params.get("q")

        # Проверка наличия всех параметров
        if None in (g_n, A, Q, s_ANFO, q):
            st.warning("❌ Ошибка: Отсутствуют входные параметры для расчета x_50.")
            self.logs_manager.add_log(module="calculations", event="Ошибка: отсутствуют входные параметры для x_50.", log_type="ошибка")
            return

        # Проверка, что все параметры являются числами
        if not all(isinstance(val, (int, float)) for val in [g_n, A, Q, s_ANFO, q]):
            st.warning("❌ Ошибка: Один из параметров для расчета x_50 имеет неверный формат.")
            self.logs_manager.add_log(module="calculations", event="Ошибка: Некорректный формат параметров x_50.", log_type="ошибка")
            return

        # Проверка корректности значений (избегаем деления на 0)
        if q <= 0 or s_ANFO <= 0:
            st.error("❌ Ошибка: q и s_ANFO должны быть больше 0.")
            self.logs_manager.add_log(module="calculations", event="Ошибка: q или s_ANFO <= 0.", log_type="ошибка")
            return

        try:
            # Выполняем расчет x_50
            self.results["x_50"] = (g_n * A * Q ** (1 / 6) * (115 / s_ANFO) ** (19 / 30) / q ** 0.8)
        except ZeroDivisionError:
            st.error("❌ Ошибка: Деление на 0 при расчете x_50.")
            self.logs_manager.add_log(module="calculations", event="Ошибка: Деление на 0 при расчете x_50.", log_type="ошибка")
            return

        # Готовим session_state
        if "calculation_results" not in st.session_state:
            st.session_state["calculation_results"] = {}

        # Очистка предыдущего значения перед записью нового
        st.session_state["calculation_results"].pop("x_50", None)
        st.session_state["calculation_results"]["x_50"] = self.results["x_50"]

        # Логируем успешный расчет с указанием результата
        self.logs_manager.add_log(module="calculations", event=f"✅ Успешный расчет x_50: {self.results['x_50']:.4f}", log_type="успех")
        st.sidebar.success(f"✅ Медианный размер фрагмента (x_50) успешно рассчитан: {self.results['x_50']:.4f}")

#     @error_handler
#     def calculate_p_x(self):
#         """
#         Рассчитывает P(x) и добавляет в DataFrame.
#         """
#         try:
#             # Очистка предыдущих расчетов P(x)
#             if "P_x_data" in st.session_state:
#                 st.session_state.pop("P_x_data")

#             # Проверяем, есть ли эталонные значения
#             if "P_x_data" not in st.session_state or st.session_state["P_x_data"] is None:
#                 st.error("❌ Ошибка: отсутствуют эталонные значения P(x).")
#                 self.logs_manager.add_log(module="calculations", event="Ошибка: P_x_data не найден.", log_type="ошибка")
#                 return

#             # Получаем необходимые параметры
#             ref_vals = st.session_state.get("conf_ref_vals", {})
#             max_x = ref_vals.get("target_x_max")
#             x_50_calc = self.results.get("x_50")
#             b_calc = self.results.get("b")

#             # Проверяем наличие всех параметров
#             if None in (max_x, x_50_calc, b_calc):
#                 st.warning("❌ Ошибка: Некоторые расчетные параметры отсутствуют.")
#                 self.logs_manager.add_log(module="calculations", event="Ошибка: отсутствуют target_x_max, x_50 или b.", log_type="ошибка")
#                 return

#             # Проверяем корректность параметров
#             if not isinstance(b_calc, (int, float)) or b_calc == 0:
#                 st.error("❌ Ошибка: b_calc должен быть числом и не равным 0.")
#                 self.logs_manager.add_log(module="calculations", event="Ошибка: b_calc некорректен (0 или не число).", log_type="ошибка")
#                 return

#             df = st.session_state["P_x_data"].copy()

#             # Проверяем, что в данных есть x_values
#             if "Размер фрагмента (x), мм" not in df.columns:
#                 st.error("❌ Ошибка: Отсутствуют данные о размерах фрагментов.")
#                 self.logs_manager.add_log(module="calculations", event="Ошибка: в P_x_data отсутствует 'Размер фрагмента (x), мм'.", log_type="ошибка")
#                 return

#             x_values = df["Размер фрагмента (x), мм"].values

#             if len(x_values) == 0:
#                 st.error("❌ Ошибка: x_values пуст, расчет невозможен.")
#                 self.logs_manager.add_log(module="calculations", event="Ошибка: x_values пустой массив.", log_type="ошибка")
#                 return

#             # Рассчитываем P_x, добавляем защиту от деления на 0
#             try:
#                 p_x_calc = 1 / (1 + (np.log(max_x / x_values) / np.log(max_x / x_50_calc)) ** b_calc)
#             except ZeroDivisionError:
#                 st.error("❌ Ошибка: Деление на 0 при расчете P(x).")
#                 self.logs_manager.add_log(module="calculations", event="Ошибка: Деление на 0 при расчете P(x).", log_type="ошибка")
#                 return

#             df["Рассчитанные P(x), %"] = p_x_calc * 100

#             # Обновление session_state
#             st.session_state["P_x_data"] = df
#             if "calculation_results" not in st.session_state:
#                 st.session_state["calculation_results"] = {}

#             st.session_state["calculation_results"]["P_x_data"] = df

#             # Логирование успешного расчета
#             self.logs_manager.add_log(module="calculations", event=f"✅ Рассчитанные значения P(x) добавлены. Количество значений: {len(df)}", log_type="успех")
#             st.success(f"✅ Рассчитанные P(x) успешно добавлены! Количество значений: {len(df)}")

#         except Exception as e:
#             self.logs_manager.add_log(module="calculations", event=f"Ошибка расчета P(x): {str(e)}", log_type="ошибка")
#             st.error(f"❌ Ошибка при расчете P(x): {e}")

# if __name__ == "__main__":
#     state_tracker = SessionStateManager()
#     logs_manager = LogsManager()
#     calc = Calculations(state_tracker, logs_manager)

#     try:
#         # Выполняем все расчеты с логированием и защитой от ошибок
#         calc.calculate_rdi()
#         calc.calculate_hf()
#         calc.calculate_a()
#         calc.calculate_s_anfo()
#         calc.calculate_q()
#         calc.calculate_x_max()
#         calc.calculate_n()
#         calc.calculate_b()
#         calc.calculate_g_n()
#         calc.calculate_x_50()
#         calc.calculate_p_x()

#         # Сохранение результатов
#         calc.save_to_session_state()
#         st.success("✅ Все расчеты успешно выполнены и сохранены!")

#     except Exception as e:
#         logs_manager.add_log(module="calculations", event=f"❌ Ошибка выполнения расчетов: {str(e)}", log_type="ошибка")
#         st.error(f"❌ Ошибка выполнения расчетов: {e}")
