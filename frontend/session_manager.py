import streamlit as st

class SessionManager:
    """Handles session state initialization and management."""
    def __init__(self):
        if 'current_page' not in st.session_state:
            st.session_state.current_page = 'home'
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []

    def set_page(self, page_name):
        st.session_state.current_page = page_name

    def add_to_chat_history(self, message):
        st.session_state.chat_history.append(message) 