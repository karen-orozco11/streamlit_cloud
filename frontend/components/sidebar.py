import streamlit as st
from views.chat_page import ChatPage
from views.resume_page import ResumePage
from views.account_page import AccountPage
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def render_sidebar():
    logger.info("Rendering sidebar")
    with st.sidebar:
        st.markdown("""
            <div style='padding: 15px;'>
                <h3>Main Menu</h3>
            </div>
        """, unsafe_allow_html=True)
        
        # Use buttons for navigation
        if st.button("Home"):
            logger.info("Home button clicked")
            st.session_state.current_page = 'home'
            st.rerun()
        if st.button("Chat"):
            logger.info("Chat button clicked")
            st.session_state.current_page = 'chat'
            st.rerun()
        if st.button("Show Resume"):
            logger.info("Show Resume button clicked")
            st.session_state.current_page = 'resume'
            st.rerun()
        if st.button("Account Settings"):
            logger.info("Account Settings button clicked")
            st.session_state.current_page = 'account'
            st.rerun()
        if st.button("Logout"):
            logger.info("Logout button clicked")
            st.session_state.current_page = 'logout'
            st.rerun()
        # Future functionality will be added here 