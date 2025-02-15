import streamlit as st
import time
import logging

from views.chat_page import ChatPage
from views.home_page import HomePage
from views.onboarding_page import OnboardingPage
from views.email_check_page import EmailCheckPage
from views.resume_page import ResumePage
from views.account_page import AccountPage
from components.sidebar import render_sidebar

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

class UIComponents:
    """Handles UI rendering and interactions."""
    def __init__(self, session_manager, chat_handler):
        self.session_manager = session_manager
        self.chat_handler = chat_handler
        self.pages = {
            'home': HomePage(session_manager),
            'chat': ChatPage(session_manager, chat_handler),
            'onboarding': OnboardingPage(session_manager),
            'email_check': EmailCheckPage(session_manager),
            'resume': ResumePage(session_manager),
            'account': AccountPage(session_manager)
        }
        logger.info("UIComponents initialized with pages: %s", list(self.pages.keys()))

    def render_page(self, page_name):
        """Render the specified page"""
        logger.info("Rendering page: %s", page_name)
        
        # Render sidebar first
        logger.info("Rendering sidebar")
        render_sidebar()
        
        # Then render the main page
        if page_name in self.pages:
            logger.info("Rendering main page: %s", page_name)
            self.pages[page_name].render()
            logger.info("Page %s rendered successfully", page_name)
        else:
            logger.error("Page %s not found", page_name)
            st.error(f"Page {page_name} not found")