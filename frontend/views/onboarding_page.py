import streamlit as st
import requests
from PyPDF2 import PdfReader
from docx import Document

class OnboardingPage:
    def __init__(self, session_manager):
        self.session_manager = session_manager

    def render(self):
        st.markdown("<div class='header-section'><h1>AI Career Adviser</h1></div>", unsafe_allow_html=True)
        
        st.markdown("<div class='content-section'>", unsafe_allow_html=True)
        with st.form("user_info"):
            name = st.text_input("Name")
            dream_role = st.selectbox("Your Dream Role", ["Data Scientist", "Technical Project Manager"])
            resume = st.file_uploader("Upload your Resume", type=["pdf", "docx"])
            
            submitted = st.form_submit_button("Next")
            if submitted:
                if name and dream_role and resume:
                    try:
                        file_type = resume.name.split('.')[-1]
                        resume_text = self.extract_text_from_file(resume, file_type)
                        response = requests.post("http://aica-backend:8000/onboard", json={
                            "email": st.session_state.email,
                            "name": name,
                            "dream_role": dream_role,
                            "resume": resume_text
                        })
                        if response.status_code == 200:
                            self.session_manager.set_page('email_check')
                        else:
                            st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
                    except Exception as e:
                        st.error(f"An error occurred: {e}")
                else:
                    st.warning("Please fill out all fields and upload your resume.")
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='footer-section'>© AI Career Adviser at aicareeradviser.us, 2025</div>", unsafe_allow_html=True)

    def extract_text_from_file(self, file, file_type):
        if file_type == "pdf":
            reader = PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            return text
        elif file_type == "docx":
            doc = Document(file)
            return "\n".join([para.text for para in doc.paragraphs])
        else:
            raise ValueError("Unsupported file type") 