import streamlit as st
import requests
from config import BACKEND_URL

class EmailCheckPage:
    def __init__(self, session_manager):
        self.session_manager = session_manager

    def render(self):
        st.markdown("<div class='header-section'><h1>AI Career Adviser</h1></div>", unsafe_allow_html=True)
        
        st.markdown("<div class='content-section'>", unsafe_allow_html=True)
        
        # Add email input field
        email = st.text_input("Enter your email address")
        
        # Add check button
        if st.button("Check Email"):
            if email:
                try:
                    response = requests.post(
                        f"{BACKEND_URL}/check_user",
                        json={"email": email}
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        if result.get("onboarded"):
                            st.success("Email found! Please check your inbox for the login link.")
                        else:
                            st.warning("Email not found. Please complete the onboarding process.")
                            # Redirect to onboarding page
                            self.session_manager.set_page('onboarding')
                    else:
                        st.error("Error checking email. Please try again.")
                        
                except requests.exceptions.RequestException as e:
                    st.error(f"Connection error. Please try again later.")
                    st.error(f"Debug info: {str(e)}")
            else:
                st.warning("Please enter an email address")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='footer-section'>© AI Career Adviser at aicareeradviser.us, 2025</div>", unsafe_allow_html=True) 