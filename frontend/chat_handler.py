import requests
import streamlit as st

class ChatHandler:
    """Handles chat interactions and API requests."""
    def __init__(self, session_manager):
        self.session_manager = session_manager

    def validate_session(self, session_id):
        try:
            response = requests.post(
                "http://aica-backend:8000/validate_session",
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

    def send_question(self, user_id, conversation_id, question):
        try:
            headers = {
                "user_id": user_id,
                "conversation_id": conversation_id
            }
            response = requests.post(
                "http://aica-backend:8000/ask",
                json={"question": question},
                headers=headers,
                timeout=30
            )
            response_data = response.json()
            if "answer" in response_data:
                return response_data['answer']
            else:
                return "Sorry, I couldn't understand that."
        except requests.exceptions.JSONDecodeError:
            return "Error: Received a non-JSON response from the server."
        except requests.exceptions.RequestException as e:
            return f"An error occurred: {e}" 