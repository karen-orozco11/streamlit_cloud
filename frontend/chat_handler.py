import requests
import streamlit as st
from config import BACKEND_URL

class ChatHandler:
    """Handles chat interactions and API requests."""
    def __init__(self, session_manager):
        self.session_manager = session_manager
        self.base_url = BACKEND_URL

    def validate_session(self, session_id):
        try:
            response = requests.post(
                f"{self.base_url}/validate_session",
                json={"session_id": session_id},
                timeout=30
            )
            if response.status_code == 200:
                return response.json()
            else:
                st.error("Error validating session.")
                return {"valid": False}
        except requests.exceptions.RequestException as e:
            st.error(f"An error occurred: {e}")
            return {"valid": False}

    def send_question(self, question, user_id, conversation_id):
        try:
            response = requests.post(
                f"{self.base_url}/ask",
                headers={
                    "user_id": user_id,
                    "conversation_id": conversation_id
                },
                json={"question": question},
                timeout=30
            )
            return response.json()["answer"]
        except requests.exceptions.JSONDecodeError:
            return "Error: Received a non-JSON response from the server."
        except requests.exceptions.RequestException as e:
            st.error(f"Error sending question: {e}")
            return "Sorry, I'm having trouble connecting to the server." 