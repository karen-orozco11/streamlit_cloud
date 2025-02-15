import streamlit as st
import requests

class HomePage:
    def __init__(self, session_manager):
        self.session_manager = session_manager

    def render(self):
        st.markdown("<div class='header-section'><h1>AI Career Adviser</h1></div>", unsafe_allow_html=True)
        
        st.markdown("<div class='content-section'>", unsafe_allow_html=True)
        email = st.text_input("User Email")
        if st.button("Next") and email:
            st.session_state.email = email
            try:
                response = requests.post("http://aica-backend:8000/check_user", json={"email": email})
                if response.status_code == 200:
                    onboarded = response.json().get("onboarded", False)
                    if onboarded:
                        self.session_manager.set_page('email_check')
                    else:
                        self.session_manager.set_page('onboarding')
                else:
                    st.error("Error checking user status.")
            except Exception as e:
                st.error(f"An error occurred: {e}")
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='footer-section'>© AI Career Adviser at aicareeradviser.us, 2025</div>", unsafe_allow_html=True) 