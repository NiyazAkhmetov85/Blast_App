import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from utils.logs_manager import LogsManager

class ResultsDisplay:
    def __init__(self):
        """Инициализация модуля отображения результатов."""
        self.logs_manager = LogsManager()

        # Проверяем и загружаем имя блока
        self.block_name = st.session_state.get("block_name", "Неизвестный блок")
        if self.block_name == "Неизвестный блок":
            st.warning("⚠ Имя блока не загружено. Проверьте импорт блока.")
            self.logs_manager.add_log(module="results_display", event="Предупреждение: Имя блока не загружено.", log_type="предупреждение")

        # Проверяем наличие P_x_data
        if "P_x_data" not in st.session_state or st.session_state["P_x_data"] is None:
            st.warning("⚠ Данные P(x) отсутствуют. Проверьте расчеты.")
            self.logs_manager.add_log(module="results_display", event="Предупреждение: P_x_data отсутствует.", log_type="предупреждение")

        # Логируем успешную инициализацию
        self.logs_manager.add_log(module="results_display", event="Модуль отображения результатов инициализирован.", log_type="успех")

    def display_psd_table(self):
        """Отображение таблицы PSD с расчетными и эталонными значениями."""
        self.state_tracker.set_state("current_step", "Отображение таблицы PSD")

        try:
            # Проверяем, есть ли данные в session_state
            if "P_x_data" not in st.session_state or st.session_state["P_x_data"] is None:
                st.warning("❌ Данные PSD отсутствуют. Пожалуйста, загрузите данные.")
                self.logs_manager.add_log(module="results_display", event="Предупреждение: Данные PSD отсутствуют", log_type="предупреждение")
                return

            df = st.session_state["P_x_data"].copy()

            # Проверка структуры данных
            required_columns = {"Размер фрагмента (x), мм", "Эталонные P(x), %", "Рассчитанные P(x), %"}
            if not required_columns.issubset(df.columns):
                st.error("❌ Ошибка: Некорректная структура данных PSD.")
                self.logs_manager.add_log(module="results_display", event="Ошибка: некорректная структура данных PSD", log_type="ошибка")
                return

            # Проверка, не пуст ли DataFrame
            if df.empty:
                st.warning("⚠ Таблица PSD пуста. Проверьте корректность расчетов.")
                self.logs_manager.add_log(module="results_display", event="Предупреждение: Таблица PSD пуста", log_type="предупреждение")
                return

            # Проверка значений P(x)
            if (df["Рассчитанные P(x), %"] < 0).any() or (df["Рассчитанные P(x), %"] > 100).any():
                st.warning("⚠ Найдены некорректные значения в расчетных P(x). Значения должны быть в диапазоне [0, 100]%.")
                self.logs_manager.add_log(module="results_display", event="Предупреждение: Некорректные значения в P(x)", log_type="предупреждение")

            # Сортируем по убыванию размера фрагментов
            df_sorted = df.sort_values(by="Размер фрагмента (x), мм", ascending=False)

            # Вывод информации о блоке и эталонных значениях
            x_min = st.session_state.get("x_range_min", "N/A")
            x_max = st.session_state.get("target_x_max", "N/A")
            x_50 = st.session_state.get("target_x_50", "N/A")

            st.write(f"### 📊 Таблица PSD - {self.block_name}")
            st.write(f"**Эталонные показатели:** x_min: {x_min}, x_max: {x_max}, X_50: {x_50}")

            # Вывод таблицы с форматированием
            st.dataframe(df_sorted.style.format({
                "Размер фрагмента (x), мм": "{:.2f}",
                "Эталонные P(x), %": "{:.2f}",
                "Рассчитанные P(x), %": "{:.2f}"
            }))

            # Логирование успешного отображения
            self.logs_manager.add_log(module="results_display", event="✅ Таблица PSD успешно отображена", log_type="успех")

        except Exception as e:
            self.logs_manager.add_log(module="results_display", event=f"Ошибка отображения таблицы PSD: {str(e)}", log_type="ошибка")
            st.error(f"❌ Ошибка отображения таблицы PSD: {e}")

        finally:
            self.state_tracker.set_state("current_step", None)

    def display_cumulative_curve(self):
        """Отображение кумулятивной кривой с обозначением x_min, x_max, X_50."""
        self.state_tracker.set_state("current_step", "Отображение кумулятивной кривой")

        try:
            # Проверяем, есть ли данные в session_state
            if "P_x_data" not in st.session_state or st.session_state["P_x_data"] is None:
                st.warning("❌ Данные для кумулятивной кривой отсутствуют. Пожалуйста, загрузите данные.")
                self.logs_manager.add_log(module="results_display", event="Предупреждение: Данные для кумулятивной кривой отсутствуют", log_type="предупреждение")
                return

            df = st.session_state["P_x_data"].copy()

            # Проверка структуры данных
            required_columns = {"Размер фрагмента (x), мм", "Эталонные P(x), %", "Рассчитанные P(x), %"}
            if not required_columns.issubset(df.columns):
                st.error("❌ Ошибка: Некорректная структура данных PSD.")
                self.logs_manager.add_log(module="results_display", event="Ошибка: некорректная структура данных PSD", log_type="ошибка")
                return

            # Проверка, не пуст ли DataFrame
            if df.empty:
                st.warning("⚠ Данные для построения кумулятивной кривой отсутствуют.")
                self.logs_manager.add_log(module="results_display", event="Предупреждение: Пустой DataFrame для кумулятивной кривой", log_type="предупреждение")
                return

            # Проверка значений P(x)
            if (df["Рассчитанные P(x), %"] < 0).any() or (df["Рассчитанные P(x), %"] > 100).any():
                st.warning("⚠ Найдены некорректные значения в расчетных P(x). Значения должны быть в диапазоне [0, 100]%.")
                self.logs_manager.add_log(module="results_display", event="Предупреждение: Некорректные значения в P(x)", log_type="предупреждение")

            # Получение эталонных параметров
            x_min = st.session_state.get("x_range_min", None)
            x_max = st.session_state.get("target_x_max", None)
            x_50 = st.session_state.get("target_x_50", None)

            # Создание графика
            plt.figure(figsize=(8, 6))
            plt.plot(df["Размер фрагмента (x), мм"], df["Эталонные P(x), %"], label="Эталонные P(x)", linestyle="-", marker="o", color="blue")
            plt.plot(df["Размер фрагмента (x), мм"], df["Рассчитанные P(x), %"], label="Рассчитанные P(x)", linestyle="--", marker="s", color="red")

            # Добавление вертикальных линий для x_min, x_max, x_50 (если заданы)
            if x_min is not None:
                plt.axvline(x=x_min, color='green', linestyle=':', label='x_min')
            if x_max is not None:
                plt.axvline(x=x_max, color='purple', linestyle=':', label='x_max')
            if x_50 is not None:
                plt.axvline(x=x_50, color='orange', linestyle=':', label='X_50')

            plt.xlabel("Размер фрагмента, мм")
            plt.ylabel("Вероятность прохождения, %")
            plt.title(f"📈 Кумулятивная кривая - {self.block_name}")
            plt.legend()
            plt.grid(True, linestyle="--", linewidth=0.5)
            st.pyplot(plt)  # Отображение графика
            plt.close()  # Закрытие фигуры после отрисовки (избегает утечки памяти)

            # Логирование успешного отображения
            self.logs_manager.add_log(module="results_display", event="✅ Кумулятивная кривая успешно отображена", log_type="успех")

        except Exception as e:
            self.logs_manager.add_log(module="results_display", event=f"Ошибка отображения кумулятивной кривой: {str(e)}", log_type="ошибка")
            st.error(f"❌ Ошибка отображения кумулятивной кривой: {e}")

        finally:
            self.state_tracker.set_state("current_step", None)



# Streamlit UI 
if __name__ == "__main__":
    if "show_psd" not in st.session_state:
        st.session_state["show_psd"] = False
    if "show_curve" not in st.session_state:
        st.session_state["show_curve"] = False
    if "show_summary" not in st.session_state:
        st.session_state["show_summary"] = False
    
    state_tracker = st.session_state.get("state_tracker", None)
    if state_tracker is None:
        st.error("Ошибка: state_tracker не инициализирован.")
    else:
        results_display = ResultsDisplay(state_tracker)

        # Кнопка для отображения таблицы PSD
        if st.button("📊 Показать таблицу PSD"):
            st.session_state["show_psd"] = not st.session_state["show_psd"]
        if st.session_state["show_psd"]:
            results_display.display_psd_table()

        # Кнопка для отображения кумулятивной кривой
        if st.button("📈 Показать кумулятивную кривую"):
            st.session_state["show_curve"] = not st.session_state["show_curve"]
        if st.session_state["show_curve"]:
            results_display.display_cumulative_curve()
