import streamlit as st

class EmailCheckPage:
    def __init__(self, session_manager):
        self.session_manager = session_manager

    def render(self):
        st.markdown("<div class='header-section'><h1>AI Career Adviser</h1></div>", unsafe_allow_html=True)
        
        st.markdown("<div class='content-section'>", unsafe_allow_html=True)
        st.write("Please check your email to click to login.")
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='footer-section'>© AI Career Adviser at aicareeradviser.us, 2025</div>", unsafe_allow_html=True) 