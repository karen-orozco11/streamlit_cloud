import streamlit as st
import uuid
import requests

# Set page configuration to collapse the sidebar by default
st.set_page_config(
    page_title="AI Career Adviser",
    page_icon=":robot:",
    layout="wide",
    initial_sidebar_state="collapsed"  # Collapse the sidebar by default
)

# Import other necessary modules
import time
import logging
from views.chat_page import ChatPage
from views.home_page import HomePage
from views.onboarding_page import OnboardingPage
from views.email_check_page import EmailCheckPage
from views.resume_page import ResumePage
from views.account_page import AccountPage
from components.sidebar import render_sidebar

from session_manager import SessionManager
from chat_handler import ChatHandler
from ui_components import UIComponents

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]  # This handler prints to the console
)
logger = logging.getLogger(__name__)

def main():
    logger.info("Application started")  # Test log message to console
    session_manager = SessionManager()
    chat_handler = ChatHandler(session_manager)
    ui_components = UIComponents(session_manager, chat_handler)
    
    # URL parameter check
    query_params = st.query_params
    if 'sessionid' in query_params and st.session_state.current_page != 'chat':
        session_id = query_params['sessionid']
        validation_response = chat_handler.validate_session(session_id)
        if validation_response['valid']:
            st.session_state['user_id'] = validation_response['user_id']  # Store user_id in session state
            logger.info(f"Current page: {st.session_state.current_page}")
            
            if not st.session_state.current_page or st.session_state.current_page == 'home':
                session_manager.set_page('chat')
            
            # Check if a conversation_id already exists
            if 'conversation_id' not in st.session_state:
                # Generate and store a new conversation_id
                st.session_state['conversation_id'] = str(uuid.uuid4())
                logger.info(f"Generated new Conversation ID: {st.session_state['conversation_id']}")
            else:
                logger.info(f"Using existing Conversation ID: {st.session_state['conversation_id']}")

    # Render the current page
    ui_components.render_page(st.session_state.current_page)

def handle_user_input(chat_handler, user_input):
    user_id = st.session_state['user_id']
    conversation_id = st.session_state['conversation_id']
    answer = chat_handler.send_question(user_input, user_id, conversation_id)
    st.session_state.chat_history.append(f"**Adviser:** {answer}")

if __name__ == "__main__":
    main() 