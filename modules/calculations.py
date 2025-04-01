import math
import json
import numpy as np
import pandas as pd
import streamlit as st
from scipy.special import gamma
from utils.logs_manager import LogsManager
from utils.session_state_manager import SessionStateManager



def error_handler(func):
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception as e:
            self.logs_manager.add_log(module="calculations", event=f"Ошибка в {func.__name__}: {str(e)}", log_type="ошибка")
            st.error(f"Ошибка в {func.__name__}: {str(e)}")
    return wrapper



class Calculations:
    """
    Класс для выполнения расчетов параметров буровзрывных работ.
    """

    def __init__(self, session_manager: SessionStateManager, logs_manager: LogsManager):
        self.session_manager = session_manager
        self.logs_manager = logs_manager
        self.results = {}
        self.params = st.session_state.get("user_parameters", {})

        if "calculation_results" not in st.session_state:
            st.session_state["calculation_results"] = {}

    @error_handler
    def calculate_rdi(self):
        """
        Расчет RDI (влияние плотности породы).
        """
        rho = self.params.get("rho")

        if rho is None or not isinstance(rho, (int, float)):
            st.sidebar.warning("❌ Ошибка: Параметр rho отсутствует или имеет неверный формат.")
            self.logs_manager.add_log(module="calculations", event="Ошибка: некорректное значение rho.", log_type="ошибка")
            return

        self.results["RDI"] = 0.025 * rho - 50
        st.session_state["calculation_results"]["RDI"] = self.results["RDI"]

        self.logs_manager.add_log(module="calculations", event=f"✅ Успешный расчет RDI: {self.results['RDI']:.2f}", log_type="успех")
        st.sidebar.success(f"✅ RDI успешно рассчитан: {self.results['RDI']:.2f}")


    
    @error_handler
    def calculate_hf(self):
        """
        Расчет HF (фактор твердости породы).
        """
        E = self.params.get("E")
        sigma_c = self.params.get("sigma_c")

        if E is None or sigma_c is None or not isinstance(E, (int, float)) or not isinstance(sigma_c, (int, float)):
            st.warning("❌ Ошибка: Параметр E или sigma_c отсутствует или имеет неверный формат.")
            self.logs_manager.add_log(module="calculations", event="Ошибка: некорректное значение E или sigma_c.", log_type="ошибка")
            return

        self.results["HF"] = E / 3 if E < 50 else sigma_c / 5
        st.session_state["calculation_results"]["HF"] = self.results["HF"]

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

        if None in (RMD, RDI, HF) or not all(isinstance(val, (int, float)) for val in [RMD, RDI, HF]):
            st.warning("❌ Ошибка: Параметр RMD, RDI или HF отсутствует или имеет неверный формат.")
            self.logs_manager.add_log(module="calculations", event="Ошибка: некорректные значения RMD, RDI или HF.", log_type="ошибка")
            return

        self.results["A"] = 0.06 * (RMD + RDI + HF)
        st.session_state["calculation_results"]["A"] = self.results["A"]

        self.logs_manager.add_log(module="calculations", event=f"✅ Успешный расчет A: {self.results['A']:.2f}", log_type="успех")
        st.sidebar.success(f"✅ A успешно рассчитан: {self.results['A']:.2f}")


    
    @error_handler
    def calculate_s_anfo(self):
        """
        Расчет s_ANFO (влияние энергии взрывчатого вещества).
        """
        energy_vv = self.params.get("energy_vv")

        if energy_vv is None or not isinstance(energy_vv, (int, float)):
            st.warning("❌ Ошибка: Параметр energy_vv отсутствует или имеет неверный формат.")
            self.logs_manager.add_log(module="calculations", event="Ошибка: некорректное значение energy_vv.", log_type="ошибка")
            return

        energy_anfo = 4.2  # Фиксированное значение
        self.results["s_ANFO"] = (energy_vv / energy_anfo) * 100
        st.session_state["calculation_results"]["s_ANFO"] = self.results["s_ANFO"]

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

        if None in (Q, H, S, B) or not all(isinstance(val, (int, float)) for val in [Q, H, S, B]):
            st.warning("❌ Ошибка: Параметры Q, H, S или B отсутствуют или имеют неверный формат.")
            self.logs_manager.add_log(module="calculations", event="Ошибка: некорректные значения Q, H, S или B.", log_type="ошибка")
            return

        if H == 0 or S == 0 or B == 0:
            st.error("❌ Ошибка: значения H, S или B не могут быть равны нулю.")
            self.logs_manager.add_log(module="calculations", event="Ошибка: значения H, S или B равны 0.", log_type="ошибка")
            return

        self.results["q"] = Q / (H * S * B)

        if "calculation_results" not in st.session_state:
            st.session_state["calculation_results"] = {}

        st.session_state["calculation_results"]["q"] = self.results["q"]

        self.logs_manager.add_log(module="calculations", event=f"✅ Успешный расчет q: {self.results['q']:.4f}", log_type="успех")
        st.sidebar.success(f"✅ Специфический заряд q успешно рассчитан: {self.results['q']:.4f}")


    
    @error_handler
    def calculate_x_max(self):
        """
        Расчет максимального размера фрагмента (x_max).
        """
        in_situ_block_size = self.params.get("in_situ_block_size")
        S = self.params.get("S")
        B = self.params.get("B")

        if None in (in_situ_block_size, S, B) or not all(isinstance(val, (int, float)) for val in [in_situ_block_size, S, B]):
            st.warning("❌ Ошибка: Параметры in_situ_block_size, S или B отсутствуют или имеют неверный формат.")
            self.logs_manager.add_log(module="calculations", event="Ошибка: некорректные значения in_situ_block_size, S или B.", log_type="ошибка")
            return

        S *= 1000  # Преобразование S в мм
        B *= 1000  # Преобразование B в мм

        # self.results["x_max"] = min(in_situ_block_size, S, B)

        # if "calculation_results" not in st.session_state:
        #     st.session_state["calculation_results"] = {}

        # st.session_state["calculation_results"]["x_max"] = self.results["x_max"]

        # self.logs_manager.add_log(module="calculations", event=f"✅ Успешный расчет x_max: {self.results['x_max']:.2f} мм", log_type="успех")
        # st.sidebar.success(f"✅ Максимальный размер фрагмента x_max успешно рассчитан: {self.results['x_max']:.2f} мм")

        self.results["x_max"] = float(min(in_situ_block_size, S, B))
        
        if "calculation_results" not in st.session_state:
            st.session_state["calculation_results"] = {}
        
        st.session_state["calculation_results"]["x_max"] = self.results["x_max"]
        
        self.logs_manager.add_log(
            module="calculations", 
            event=f"✅ Успешный расчет x_max: {self.results['x_max']:.2f} мм", 
            log_type="успех"
        )
        st.sidebar.success(
            f"✅ Максимальный размер фрагмента x_max успешно рассчитан: {self.results['x_max']:.2f} мм"
        )

    
  
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

        missing_params = [p for p in ["x_max", "x_50", "S", "B", "Ø_h", "SD", "L_b", "L_c", "L_tot", "H"] if locals()[p] is None]
        
        if missing_params:
            st.warning(f"❌ Ошибка: Отсутствуют параметры: {', '.join(missing_params)}.")
            self.logs_manager.add_log(module="calculations", event=f"Ошибка: Отсутствуют параметры {missing_params}.", log_type="ошибка")
            return

        if not all(isinstance(locals()[p], (int, float)) for p in ["x_max", "x_50", "S", "B", "Ø_h", "SD", "L_b", "L_c", "L_tot", "H"]):
            st.warning("❌ Ошибка: Некоторые параметры имеют некорректный формат.")
            self.logs_manager.add_log(module="calculations", event="Ошибка: Некоторые параметры имеют некорректный формат.", log_type="ошибка")
            return

        if H == 0 or B == 0 or L_tot == 0:
            st.error("❌ Ошибка: H, B и L_tot должны быть больше 0.")
            self.logs_manager.add_log(module="calculations", event="Ошибка: H, B или L_tot равны 0.", log_type="ошибка")
            return

        self.results["n"] = (
            2 * math.log(2) * math.log(x_max / x_50) *
            (2.2 - 0.014 * (B / Ø_h)) *
            (1 - SD / B) *
            math.sqrt((1 + S / B) / 2) *
            ((L_b - L_c) / L_tot + 0.1) ** 0.1 *
            (L_tot / H)
        )

        if "calculation_results" not in st.session_state:
            st.session_state["calculation_results"] = {}

        st.session_state["calculation_results"]["n"] = self.results["n"]

        self.logs_manager.add_log(module="calculations", event=f"✅ Успешный расчет n: {self.results['n']:.4f}", log_type="успех")
        st.sidebar.success(f"✅ Коэффициент равномерности n успешно рассчитан: {self.results['n']:.4f}")


    
    @error_handler
    def calculate_g_n(self):
        """
        Расчет показателя g(n).
        """
        n = self.results.get("n")

        if n is None or not isinstance(n, (int, float)) or n <= 0:
            st.warning("❌ Ошибка: Параметр n отсутствует или некорректен.")
            self.logs_manager.add_log(module="calculations", event="Ошибка: Некорректный параметр n.", log_type="ошибка")
            return

        try:
            ln_2 = math.log(2)
            gamma_value = math.gamma(1 + 1 / n)
            self.results["g_n"] = (ln_2 ** (1 / n)) / gamma_value
        except ZeroDivisionError:
            st.error("❌ Ошибка: Деление на 0 при расчете g(n).")
            self.logs_manager.add_log(module="calculations", event="Ошибка: Деление на 0 при расчете g(n).", log_type="ошибка")
            return

        # Сохранение результата в st.session_state
        st.session_state["calculation_results"]["g_n"] = self.results["g_n"]

        self.logs_manager.add_log(module="calculations", event=f"✅ Успешный расчет g(n): {self.results['g_n']:.4f}", log_type="успех")
        st.sidebar.success(f"✅ Показатель g(n) успешно рассчитан: {self.results['g_n']:.4f}")

    
    
    @error_handler
    def calculate_x_50(self):
        """
        Расчет медианного размера фрагмента (x_50).
        """
        A = self.results.get("A")
        Q = self.params.get("Q")
        s_ANFO = self.results.get("s_ANFO")
        q = self.results.get("q")
    
        if None in (A, Q, s_ANFO, q):
            st.warning("❌ Ошибка: Отсутствуют входные параметры для расчета x_50.")
            self.logs_manager.add_log("calculations", "Ошибка: отсутствуют входные параметры для x_50.", "ошибка")
            return
    
        if q <= 0 or s_ANFO <= 0:
            st.error("❌ Ошибка: q и s_ANFO должны быть больше 0.")
            self.logs_manager.add_log("calculations", "Ошибка: q или s_ANFO <= 0.", "ошибка")
            return
    
        try:
            self.results["x_50"] = A * Q**(1/6) * (115 / s_ANFO)**0.633 / q**0.8
        except ZeroDivisionError:
            st.error("❌ Ошибка: Деление на 0 при расчете x_50.")
            self.logs_manager.add_log("calculations", "Ошибка: Деление на 0 при расчете x_50.", "ошибка")
            return
    
        st.session_state["calculation_results"]["x_50"] = self.results["x_50"]
    
        self.logs_manager.add_log("calculations", f"✅ Успешный расчет x_50: {self.results['x_50']:.4f}", "успех")
        st.sidebar.success(f"✅ Медианный размер фрагмента (x_50) успешно рассчитан: {self.results['x_50']:.4f}")


    
    @error_handler
    def calculate_b(self):
        """
        Расчет b (параметра формы кривой).
        """
        try:
            x_max = float(self.results["x_max"])
            x_50 = float(self.results["x_50"])
            n = float(self.results["n"])
        except (TypeError, ValueError, KeyError):
            st.error("❌ Ошибка: один из параметров (x_max, x_50, n) имеет неверный формат или отсутствует.")
            self.logs_manager.add_log(
                module="calculations",
                event="Ошибка: Некорректный формат или отсутствие параметров (x_max, x_50, n).",
                log_type="ошибка"
            )
            return
    
        # Проверка деления на 0
        if x_50 <= 0:
            st.error("❌ Ошибка: x_50 должен быть больше 0.")
            self.logs_manager.add_log(
                module="calculations",
                event="Ошибка: x_50 <= 0.",
                log_type="ошибка"
            )
            return
    
        # Выполняем расчет
        self.results["b"] = 2 * math.log(2) * math.log(x_max / x_50) * n
    
        # Сохранение результата в st.session_state
        st.session_state["calculation_results"]["b"] = self.results["b"]
        
        # Логируем результат
        self.logs_manager.add_log(
            module="calculations",
            event=f"✅ Успешный расчет b: {self.results['b']:.4f}",
            log_type="успех"
        )
        st.sidebar.success(f"✅ Параметр формы кривой b успешно рассчитан: {self.results['b']:.4f}")



    @error_handler
    def calculate_n_iterative(self, tolerance=0.05, max_iterations=5):
        """
        Итерационный расчет коэффициента n и x_50 с использованием эталонного x_50.
        """
        x_50_ref = st.session_state.get("reference_parameters", {}).get("target_x_50")
    
        if x_50_ref is None or not isinstance(x_50_ref, (int, float)):
            st.error("❌ Ошибка: отсутствует эталонное значение x_50.")
            self.logs_manager.add_log("calculations", "Ошибка: отсутствует эталонное значение x_50.", "ошибка")
            return
    
        S = self.params.get("S")
        B = self.params.get("B")
        Ø_h = self.params.get("Ø_h", 0) / 1000
        SD = self.params.get("SD")
        L_b = self.params.get("L_b")
        L_c = self.params.get("L_c")
        L_tot = self.params.get("L_tot")
        H = self.params.get("H")
        x_max = self.results.get("x_max")
    
        required_params = [S, B, Ø_h, SD, L_b, L_c, L_tot, H, x_max]
        if any(p is None for p in required_params):
            st.error("❌ Ошибка: отсутствуют необходимые исходные параметры.")
            self.logs_manager.add_log("calculations", "Ошибка: не все исходные параметры доступны.", "ошибка")
            return
    
        n = None
        x_50_current = x_50_ref
    
        for iteration in range(1, max_iterations + 1):
            n = (
                2 * math.log(2) * math.log(x_max / x_50_current) *
                (2.2 - 0.014 * (B / Ø_h)) *
                (1 - SD / B) *
                math.sqrt((1 + S / B) / 2) *
                ((L_b - L_c) / L_tot + 0.1) ** 0.1 *
                (L_tot / H)
            )
    
            self.results["n"] = n
            self.calculate_g_n()  # Гарантируем перерасчёт g_n
    
            g_n = self.results.get("g_n")
            if g_n is None:
                st.error("Ошибка: g_n не рассчитан. Итерации остановлены.")
                return
    
            self.calculate_x_50()
            x_50_new = self.results.get("x_50")
    
            if x_50_new is None:
                st.error("Ошибка: x_50 не рассчитан. Итерации остановлены.")
                return
    
            st.write(f"Итерация {iteration}: n = {n:.4f}, x_50 = {x_50_new:.4f}")
    
            if abs(x_50_new - x_50_current) / x_50_current <= tolerance:
                st.success(f"✅ Итерации завершены с достаточной точностью за {iteration} шагов.")
                break
    
            x_50_current = x_50_new
        else:
            st.warning("⚠️ Достигнуто максимальное число итераций без достаточной сходимости.")
    
        st.session_state["calculation_results"]["n"] = n
        st.session_state["calculation_results"]["x_50"] = x_50_current
    
        self.logs_manager.add_log(
            module="calculations",
            event=f"✅ Итерационный расчет n завершён: n={n:.4f}, x_50={x_50_current:.4f}",
            log_type="успех"
        )



    @error_handler
    def run_all_calculations(self):
        """
        Запуск всех расчетов БВР последовательно с учетом итерационного подхода для n и x_50.
        """
    
        try:
            progress_bar = st.progress(0)
            calculation_steps = [
                self.calculate_rdi,
                self.calculate_hf,
                self.calculate_a,
                self.calculate_s_anfo,
                self.calculate_q,
                self.calculate_x_max,
                self.calculate_n_iterative,  # Итерационный расчёт n и x_50
                # self.calculate_g_n,           # Перерасчёт g_n после итераций
                self.calculate_b,
            ]
    
            for i, step in enumerate(calculation_steps, 1):
                step_name = step.__name__
                self.logs_manager.add_log("calculations", f"Выполняется: {step_name}", "информация")
                step()
                progress_bar.progress(i / len(calculation_steps))
    
            self.logs_manager.add_log("calculations", "✅ Все расчеты БВР успешно выполнены.", "успех")
            st.sidebar.success("✅ Все расчеты БВР успешно выполнены и сохранены.")


            # 1. Итоговые параметры БВР
            block_name = st.session_state.get("block_name", "Без названия")
            st.subheader(f"Итоговые параметры БВР {block_name}")
            
            parameter_info = {
                "x_50": {"name": "Медианный размер фрагмента", "unit": "мм", "order": 1},
                "x_max": {"name": "Максимальный размер фрагмента", "unit": "мм", "order": 2},
                "b": {"name": "Показатель формы кривой", "unit": "-", "order": 3},
                "n": {"name": "Коэффициент равномерности", "unit": "-", "order": 4},
                "g_n": {"name": "Показатель g(n)", "unit": "-", "order": 5},
                "RDI": {"name": "Индекс плотности породы", "unit": "-", "order": 6},
                "HF": {"name": "Фактор твёрдости породы", "unit": "-", "order": 7},
                "A": {"name": "Индекс взрываемости породы", "unit": "-", "order": 8},
                "s_ANFO": {"name": "Относительная энергия ВВ", "unit": "%", "order": 9},
                "q": {"name": "Специфический заряд", "unit": "кг/м³", "order": 10},
            }
            
            results_data = []
            for key, value in st.session_state.get("calculation_results", {}).items():
                meta = parameter_info.get(key, {"name": key, "unit": "", "order": 99})
                results_data.append({
                    "Параметр": f"{meta['name']}, {key}",
                    "Значение": round(value, 4),
                    "Ед. изм.": meta["unit"],
                    "Порядок": meta["order"]
                })
            
            results_df = pd.DataFrame(results_data).sort_values("Порядок")
            st.dataframe(results_df[["Параметр", "Значение", "Ед. изм."]], use_container_width=True, hide_index=True)



        #     # 2. Исходные параметры БВР
        #     block_name = st.session_state.get("block_name", "Блок")
        #     st.subheader(f"Исходные параметры — {block_name}")
            
        #     # Получение параметров из session_state
        #     params_all = st.session_state.get("user_parameters", {})
        #     reference_all = st.session_state.get("reference_parameters", {})
        #     param_definitions = st.session_state.get("parameters", {})
            
        #     # Словарь для хранения категорий и их параметров
        #     categorized_params = {}
            
        #     # Объединённый список всех параметров
        #     combined_params = {**params_all, **reference_all}
            
        #     for key, value in combined_params.items():
        #         param_meta = param_definitions.get(key, {})
        #         description = param_meta.get("description", key)
        #         unit = param_meta.get("unit", "")
        #         category = param_meta.get("category", "Прочие параметры")
            
        #         # Безопасное округление
        #         try:
        #             numeric_value = round(float(value), 4)
        #         except (ValueError, TypeError):
        #             numeric_value = value
            
        #         row = (f"{description} ({key}), {block_name}", numeric_value, unit)
            
        #         # Сохраняем в нужную категорию
        #         if category not in categorized_params:
        #             categorized_params[category] = []
        #         categorized_params[category].append(row)
            
        #     # Отображаем таблицы по категориям
        #     for category_name, rows in categorized_params.items():
        #         if not rows:
        #             continue
        #         st.markdown(f"**{category_name}**")
        #         df = pd.DataFrame(rows, columns=["Параметр", "Значение", "Ед. изм."])
        #         st.dataframe(df, use_container_width=True, hide_index=True)

           
  
        except Exception as e:
            self.logs_manager.add_log("calculations", f"Ошибка при расчетах БВР: {str(e)}", "ошибка")
            st.sidebar.error(f"❌ Ошибка при выполнении расчетов БВР: {e}")
