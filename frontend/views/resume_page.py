import streamlit as st
import requests

class ResumePage:
    def __init__(self, session_manager):
        self.session_manager = session_manager

    @staticmethod
    def fetch_resume_and_skills(user_id):
        try:
            headers = {'user_id': user_id}
            response = requests.post("http://aica-backend:8000/get_resume", headers=headers)
            if response.status_code == 200:
                return response.json()
            else:
                st.error("Failed to fetch resume and skills.")
                return None
        except requests.exceptions.RequestException as e:
            st.error(f"An error occurred: {e}")
            return None

    def render(self):
        st.title("Your Resume")

        user_id = st.session_state.get('user_id')
        if not user_id:
            st.error("User not logged in.")
            return

        data = ResumePage.fetch_resume_and_skills(user_id)
        if data:
            st.subheader("Resume")
            st.text(data.get("resume", "No resume available."))

            st.subheader("Skills")
            skills = data.get("skills", [])
            if skills:
                st.write(", ".join(skills))
            else:
                st.write("No skills available.") 