import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils.session_state_manager import SessionStateManager
from utils.logs_manager import LogsManager

class PSDVisualization:
    """
    Класс для визуализации таблицы PSD (Particle Size Distribution) и
    кумулятивной кривой распределения рассчитанных значений.
    """

    def __init__(self, session_manager: SessionStateManager, logs_manager: LogsManager):
        self.session_manager = session_manager
        self.logs_manager = logs_manager

    def visualize_calculated_psd_table(self):
        """
        Визуализация таблицы PSD (Particle Size Distribution) с рассчитанными значениями.
        """
        try:
            # Извлекаем таблицу PSD из session_state
            psd_table = st.session_state.get("psd_table_calculated")

            # Проверяем, существует ли таблица и не является ли она пустой
            if not isinstance(psd_table, pd.DataFrame) or psd_table.empty:
                st.sidebar.warning("Нет данных для визуализации PSD.")
                self.logs_manager.add_log(
                    "psd_visualization",
                    "Попытка визуализации PSD с отсутствующими или пустыми данными.",
                    "предупреждение"
                )
                return

            # Отображаем таблицу PSD с помощью Streamlit
            st.subheader("Таблица распределения размеров частиц (PSD - Рассчитанные значения)")
            st.dataframe(psd_table, use_container_width=True)

            # Лог успешного отображения таблицы
            self.logs_manager.add_log(
                "psd_visualization",
                "Таблица PSD успешно визуализирована.",
                "успех"
            )

        except Exception as e:
            st.sidebar.error(f"Ошибка визуализации таблицы PSD: {e}")
            self.logs_manager.add_log(
                "psd_visualization",
                f"Ошибка визуализации таблицы PSD: {e}",
                "ошибка"
            )

    def visualize_calculated_cumulative_curve(self):
        """
        Визуализация кумулятивной кривой распределения рассчитанных значений P(x).
        """
        try:
            # Извлекаем данные для кумулятивной кривой из session_state
            df = st.session_state.get("P_x_calculated")

            # Проверяем, существует ли DataFrame и не является ли он пустым
            if not isinstance(df, pd.DataFrame) or df.empty:
                st.sidebar.warning("Нет данных для построения графика.")
                self.logs_manager.add_log(
                    "psd_visualization",
                    "Попытка построения кумулятивной кривой с отсутствующими или пустыми данными.",
                    "предупреждение"
                )
                return

            # Построение графика с использованием Plotly
            fig = px.line(
                df,
                x="Размер фрагмента (x), мм",
                y="P(x) рассчитанные, %",
                title="Кумулятивная кривая распределения (Рассчитанные значения)",
                labels={
                    "Размер фрагмента (x), мм": "Размер фрагмента (мм)",
                    "P(x) рассчитанные, %": "Кумулятивное распределение (%)"
                }
            )
            fig.update_traces(mode='lines+markers')
            st.plotly_chart(fig)

            # Лог успешного построения графика
            self.logs_manager.add_log(
                "psd_visualization",
                "Кумулятивная кривая успешно визуализирована.",
                "успех"
            )

        except Exception as e:
            st.sidebar.error(f"Ошибка визуализации кумулятивной кривой: {e}")
            self.logs_manager.add_log(
                "psd_visualization",
                f"Ошибка визуализации кумулятивной кривой: {e}",
                "ошибка"
            )


    def visualize_dual_cumulative_curves(self):
        """
        Визуализация эталонной и рассчитанной кумулятивных кривых распределения.
        """
        try:
            df_reference = st.session_state.get("P_x_data")
            df_calculated = st.session_state.get("P_x_calculated")
            
            if df_reference is None or df_reference.empty:
                st.sidebar.warning("Нет данных для построения эталонной кривой.")
                return
            
            if df_calculated is None or df_calculated.empty:
                st.sidebar.warning("Нет данных для построения рассчитанной кривой.")
                return
    
            fig = go.Figure()
    
            # Эталонная кривая (красного цвета)
            fig.add_trace(go.Scatter(x=df_reference["Размер фрагмента (x), мм"], 
                                     y=df_reference["Эталонные P(x), %"], 
                                     mode='lines+markers', 
                                     name='Эталонная кривая', 
                                     line=dict(color='red')))
    
            # Рассчитанная кривая (синего цвета)
            fig.add_trace(go.Scatter(x=df_calculated["Размер фрагмента (x), мм"], 
                                     y=df_calculated["Рассчитанные P(x), %"], 
                                     mode='lines+markers', 
                                     name='Рассчитанная кривая', 
                                     line=dict(color='blue')))
    
            fig.update_layout(title="Сравнение эталонной и рассчитанной кумулятивных кривых распределения",
                              xaxis_title="Размер фрагмента (мм)",
                              yaxis_title="Кумулятивное распределение (%)")
    
            st.plotly_chart(fig)
        except Exception as e:
            st.sidebar.error(f"Ошибка визуализации кривых: {e}")
            self.logs_manager.add_log("psd_visualization", f"Ошибка визуализации кривых: {e}", "ошибка")
