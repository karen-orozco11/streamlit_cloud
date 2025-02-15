import streamlit as st
import requests

class AccountPage:
    def __init__(self, session_manager):
        self.session_manager = session_manager

    @staticmethod
    def remove_account(user_id):
        try:
            response = requests.post(f"http://aica-backend:8000/remove_account", json={"user_id": user_id})
            if response.status_code == 200:
                st.success("Your account has been successfully removed.")
                return True
            else:
                st.error("Failed to remove account. Please try again later.")
                return False
        except requests.exceptions.RequestException as e:
            st.error(f"An error occurred: {e}")
            return False

    def render(self):
        st.title("Account Settings")

        user_id = st.session_state.get('user_id')
        if not user_id:
            st.error("User not logged in.")
            return

        if st.button("Remove my account"):
            if st.confirm("Your account will be removed and all data will be erased."):
                if AccountPage.remove_account(user_id):
                    st.session_state.clear()  # Clear session state
                    st.experimental_rerun()  # Navigate to home page
