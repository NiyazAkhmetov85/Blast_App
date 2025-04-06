
import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px

from utils.session_state_manager import SessionStateManager
from utils.logs_manager import LogsManager

class PSDVisualization:
    """
    Класс для визуализации таблицы распределения фрагментов (PSD) и 
    эталонной кумулятивной кривой распределения.
    """

    def __init__(self, session_manager: SessionStateManager, logs_manager: LogsManager):
        self.session_manager = session_manager
        self.logs_manager = logs_manager

    def visualize_psd_table(self):
        """
        Визуализация таблицы PSD (Particle Size Distribution).
        """
        try:
            # Извлекаем таблицу PSD из session_state
            psd_table = st.session_state.get("psd_table_calculated")
            P_x_calculated = st.session_state.get("P_x_calculated")

            # Проверяем, существует ли таблица и не является ли она пустой
            if not isinstance(psd_table, pd.DataFrame) or psd_table.empty:
                st.sidebar.warning("Нет данных для визуализации PSD.")
                self.logs_manager.add_log(
                    "psdvisualization",
                    "Попытка визуализации PSD с отсутствующими или пустыми данными.",
                    "предупреждение"
                )
                return

            # Отображаем таблицу PSD с помощью Streamlit
            st.subheader("Таблица распределения размеров частиц (PSD)")
            st.dataframe(psd_table, use_container_width=True)

            # Лог успешного отображения таблицы
            self.logs_manager.add_log(
                "psdvisualization",
                "Таблица PSD успешно визуализирована.",
                "успех"
            )

        except Exception as e:
            st.sidebar.error(f"Ошибка визуализации таблицы PSD: {e}")
            self.logs_manager.add_log(
                "psdvisualization",
                f"Ошибка визуализации таблицы PSD: {e}",
                "ошибка"
            )

    def visualize_cumulative_curve(self):
        """
        Визуализация эталонной кумулятивной кривой распределения.
        """
        try:
            # Извлекаем данные для кумулятивной кривой из session_state
            df = st.session_state.get("P_x_calculated")

            # Проверяем, существует ли DataFrame и не является ли он пустым
            if not isinstance(df, pd.DataFrame) or df.empty:
                st.sidebar.warning("Нет данных для построения графика.")
                self.logs_manager.add_log(
                    "psdvisualization",
                    "Попытка построения кумулятивной кривой с отсутствующими или пустыми данными.",
                    "предупреждение"
                )
                return

            # Построение графика с использованием Plotly
            fig = px.line(
                df,
                x="Размер фрагмента (x), мм",
                y="Эталонные P(x), %",
                title="Эталонная кумулятивная кривая распределения",
                labels={
                    "Размер фрагмента (x), мм": "Размер фрагмента (мм)",
                    "Эталонные P(x), %": "Кумулятивное распределение (%)"
                }
            )
            fig.update_traces(mode='lines+markers')
            st.plotly_chart(fig)

            # Лог успешного построения графика
            self.logs_manager.add_log(
                "psdvisualization",
                "Кумулятивная кривая успешно визуализирована.",
                "успех"
            )

        except Exception as e:
            st.sidebar.error(f"Ошибка визуализации кумулятивной кривой: {e}")
            self.logs_manager.add_log(
                "psdvisualization",
                f"Ошибка визуализации кумулятивной кривой: {e}",
                "ошибка"
            )

