import streamlit as st

class SessionStateManager:
    """
    Управляет параметрами `st.session_state`
    """

    def __init__(self):
        """Инициализация параметров при старте."""
        self._initialize_session_state()     

    def _initialize_session_state(self):
        """Создаёт все ключи `st.session_state`, если они отсутствуют."""
        default_values = {
            "parameters": {},  
            "default_parameters": {},  
            "user_parameters": {},
            "last_action": None,  
            "block_contour": None,  
            "block_name": "Неизвестный блок",  
            "block_geometry": None,  
            "grid_data": None,  
            "grid_metrics": None,  
            "grid_updated": False,  
            "P_x_data": None,  
            "calculation_results": {},  
            "conf_ref_vals": {},  
            "ref_vals": {},  
            "x_values": None,  
            "scale_type": "Линейная",  
            "linear_step_size": 1.0,  
            "show_psd": False,  
            "show_curve": False,  
            "logs": [],  
            "config": {"theme": "dark", "language": "en"},  
            "user_data": {"user_id": None, "username": "", "preferences": []},  
            "current_step": None,
            "parameter_source": None,
            "status_message": "", 
        }

        for key, value in default_values.items():
            if key not in st.session_state:
                st.session_state[key] = value

        
    def update_status(self, message: str, level: str = "info"):
        """
        Обновляет статусное сообщение.
        
        :param message: Строка с текстом статуса.
        """
        st.session_state["status_message"] = message
       
if __name__ == "__main__":
    manager = SessionStateManager()

