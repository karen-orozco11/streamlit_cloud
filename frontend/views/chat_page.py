import streamlit as st
import logging
import uuid

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]  # Ensure logs are sent to stdout
)
logger = logging.getLogger(__name__)

class ChatPage:
    def __init__(self, session_manager, chat_handler):
        self.session_manager = session_manager
        self.chat_handler = chat_handler
        self.initialize_chat_history()

    def initialize_chat_history(self):
        if 'chat_history' not in st.session_state or not st.session_state.chat_history:
            logger.info("Adding greeting to chat history")
            st.session_state.chat_history = ["**Adviser:** What career advancement could I help you with?"]

    def render(self):
        logger.info("ChatPage render() called")
        # Load external CSS
        with open("styles.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
        logger.info("CSS loaded")

        # Header section with title
        st.markdown("<div class='header-section'><br><h1>AI Career Adviser</h1></div>", unsafe_allow_html=True)
        logger.info("Header section rendered")

        # Debug: Print current chat history
        logger.info(f"Current chat history: {st.session_state.chat_history}")

        # Conversation display section
        with st.container():  # Use st.container as context
            st.markdown("<div class='conversation-section'>", unsafe_allow_html=True)  # Open div
            chat_placeholder = st.empty()  # Placeholder *inside* the div
            formatted_messages = "<br>".join(
                f'<div class="{"user-text" if msg.startswith("**You:**") else "adviser-text"}">'
                f'{msg.replace("**", "<strong>").replace("**", "</strong>", 1)}</div>'
                for msg in st.session_state.chat_history
            )
            chat_placeholder.markdown(formatted_messages, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)  # Close div

        # User input section
        user_input = st.text_input("Chat Input", placeholder="Type your message here...", key="chat_input", value="")
        send_button = st.button("Send")

        # Footer section - Corrected
        footer_html = "<div class='footer-section'>© AI Career Adviser at aicareeradviser.us, 2025</div>"
        st.markdown(footer_html, unsafe_allow_html=True)  # Single markdown call
        logger.info("Footer section rendered")

        # Handle send button click
        if send_button and user_input:
            logger.info(f"Processing user input: {user_input}")
            user_message = f"**You:** {user_input}"
            st.session_state.chat_history.append(user_message)

            with st.spinner("Thinking..."):
                logger.info("Getting AI response")
                user_id = st.session_state.get('user_id')
                conversation_id = st.session_state.get('conversation_id')
                ai_response = self.chat_handler.send_question(user_id, conversation_id, user_input)
                ai_message = f"**Adviser:** {ai_response}"
                st.session_state.chat_history.append(ai_message)
                logger.info("AI response added to chat history")

            # TODO: Clear input box after send
            # st.session_state.chat_input = ""
            st.rerun()  # Force Streamlit to rerun
