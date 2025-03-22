import numpy as np
import pandas as pd
import streamlit as st
from utils.session_state_manager import SessionStateManager
from utils.logs_manager import LogsManager
from modules.reference_parameters import ReferenceParameters
from modules.reference_calculations import ReferenceCalculations

class RefValues:
    def __init__(self, session_manager: SessionStateManager, logs_manager: LogsManager):
        self.session_manager = session_manager
        self.logs_manager = logs_manager
        self.reference_parameters = ReferenceParameters(session_manager, logs_manager)
        self.reference_calculations = ReferenceCalculations(session_manager, logs_manager)

    def show_reference_values(self):
        """
        Экран для работы с эталонными значениями БВР.
        """
        st.header("📌 Эталонные значения БВР")
    
        # ✅ Отображаем имя текущего блока
        block_name = st.session_state.get("block_name", "Неизвестный блок")

        if not block_name or block_name == "Неизвестный блок":
            st.warning("Блок не импортирован. Импортируйте блок на вкладке 'Импорт данных блока'.")
        else:
            st.info(f"Импортированный блок: **{block_name}**")
    
        # ✅ Отображаем эталонные показатели
        self.reference_parameters.render_refparameters_section()

        self.reference_calculations.render_ui()

      
        # # ✅ Кнопка утвердить параметры
        # if st.button("✅ Утвердить параметры"):
        #     self.logs_manager.add_log("reference_values", "Эталонные параметры утверждены пользователем.", "успех")
        #     st.success("✅ Параметры утверждены!")
    
        # # ✅ Генерация шкалы вручную
        # if st.button("🔄 Генерировать шкалу"):
        #     self.reference_calculations.generate_scale()
    
        #     # ✅ Проверяем и отображаем сгенерированные x_values
        #     x_values = self.session_manager.get("x_values", None)
        #     if x_values is not None and isinstance(x_values, (list, np.ndarray)) and len(x_values) > 0:
        #         df_x_values = pd.DataFrame(sorted(x_values, reverse=True), columns=["Размер фрагмента (x), мм"])
        #         st.subheader("🔍 Сгенерированная шкала x_values")
        #         st.dataframe(df_x_values)
        #     else:
        #         st.warning("⚠ Шкала x_values не была создана или пустая.")
    
        # # ✅ Расчет эталонных P(x) (только по кнопке)
        # if st.button("📈 Рассчитать эталонные P(x)"):
        #     self.reference_calculations.calculate_p_x()
    
        #     # ✅ Просмотр таблицы PSD и её утверждение (только если P(x) уже рассчитан)
        #     P_x_data = self.session_manager.get("P_x_data", None)
        #     if P_x_data is not None:
        #         st.subheader("📊 Итоговые эталонные значения P(x)")
        #         st.dataframe(P_x_data)
        
        #         if st.button("✅ Утвердить шкалу и P(x)"):
        #             self.reference_calculations.update_psd_table()
        #             st.success("✅ Шкала и эталонные значения утверждены!")
        #             self.logs_manager.add_log("reference_values", "Шкала и эталонные значения утверждены пользователем.", "успех")
        #     else:
        #         st.warning("⚠ Таблица P(x) не была рассчитана. Сначала нажмите '📈 Рассчитать эталонные P(x)'.")
