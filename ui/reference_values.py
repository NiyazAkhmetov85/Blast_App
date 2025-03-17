import streamlit as st
from modules.reference_parameters import ReferenceParameters
from modules.reference_calculations import ReferenceCalculations
from utils.session_state_manager import SessionStateManager
from utils.logs_manager import LogsManager

def show_reference_values():
    """
    Экран для работы с эталонными значениями БВР.
    """
    st.header("Эталонные значения БВР")

    session_manager = SessionStateManager()
    logs_manager = LogsManager()
    
    # ✅ Загружаем эталонные параметры и расчеты
    reference_params = ReferenceParameters(session_manager, logs_manager)
    reference_calculations = ReferenceCalculations(session_manager, logs_manager)

    # ✅ Отображаем имя текущего блока
    block_name = session_manager.get_state("current_block", "Не задан")
    st.info(f"Текущий блок: **{block_name}**")

    # ✅ Отображаем параметры
    render_reference_parameters(reference_params)

    # ✅ Настройка шкалы значений
    st.subheader("📏 Тип шкалы")
    scale_type = st.radio("Выберите тип шкалы:", ["Логарифмическая", "Линейная"], index=0)

    # ✅ Если линейная шкала – запрашиваем шаг
    step_size = None
    if scale_type == "Линейная":
        step_size = st.number_input("Введите шаг для линейной шкалы:", min_value=0.1, max_value=10.0, value=1.0, step=0.1)

    if st.button("🔄 Генерировать шкалу"):
        reference_calculations.generate_scale(scale_type, step_size)
        logs_manager.add_log("reference_values", f"Генерирована шкала: {scale_type}, шаг: {step_size}", "успех")
        st.success(f"✅ Шкала {scale_type} успешно создана!")

    # ✅ Кнопки управления расчетами
    st.subheader("📊 Расчет эталонных значений")
    if st.button("📈 Рассчитать эталонные параметры"):
        reference_calculations.calculate_p_x()
        reference_calculations.update_psd_table()
        logs_manager.add_log("reference_values", "Выполнен пересчет эталонных значений", "успех")
        st.success("✅ Эталонные значения пересчитаны!")

    if st.button("✅ Утвердить параметры"):
        reference_params.confirm_parameters()
        logs_manager.add_log("reference_values", "Параметры утверждены", "успех")
        st.success("✅ Параметры утверждены!")

def render_reference_parameters(reference_params):
    """
    Отображает эталонные параметры и позволяет их редактировать.
    """
    st.subheader("📝 Эталонные параметры")

    # ✅ Загружаем параметры
    ref_values = reference_params.get_reference_values()

    if not ref_values:
        st.warning("⚠ Эталонные значения не загружены.")
        return

    # ✅ Отображаем параметры с возможностью редактирования
    updated_values = {}
    for category, params in ref_values.items():
        with st.expander(f"📌 {category}", expanded=False):
            for param, value in params.items():
                updated_values[f"{category}_{param}"] = st.number_input(
                    f"{param}", value=value, key=f"ref_{category}_{param}"
                )

    # ✅ Кнопка сохранения изменений
    if st.button("💾 Сохранить изменения"):
        save_changes(reference_params, updated_values)

def save_changes(reference_params, updated_values):
    """
    Сохраняет изменения в эталонных значениях.
    """
    updated_dict = {}
    for key, value in updated_values.items():
        category, param = key.split("_", 1)
        if category not in updated_dict:
            updated_dict[category] = {}
        updated_dict[category][param] = value

    reference_params.set_reference_values(updated_dict)
    st.success("✅ Эталонные значения обновлены!")
