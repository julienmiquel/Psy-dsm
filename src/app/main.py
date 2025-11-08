"""
Main Streamlit application for the DSM-5 Character Profile Generator.

This module handles the user authentication.
"""

import os
import streamlit as st
from dotenv import load_dotenv

from app.state import AppState

load_dotenv()
st.set_page_config(layout="wide")

# Initialize the AppState in the session state if it doesn't exist
if 'app_state' not in st.session_state:
    st.session_state.app_state = AppState()
app_state = st.session_state.app_state

st.title("DSM-5 Character Profile Generator")

DEBUG = os.environ.get("DEBUG", "false").lower() == "true"

if DEBUG:
    st.warning("Debug mode is ON. Make sure not to use real PII data.")
    app_state.authenticated = True
    app_state.user_id = "admin"

if not app_state.authenticated:
    st.header("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        admin_user = os.environ.get("ADMIN_USERNAME", "admin")
        admin_pass = os.environ.get("ADMIN_PASSWORD", "h4gcv8PpV2@EKb@")
        if username == admin_user and password == admin_pass:
            app_state.authenticated = True
            app_state.user_id = username
            st.rerun()
        else:
            st.error("Invalid username or password")
else:
    st.success("Login successful!")
    st.write("Redirecting to customer selection...")
    st.switch_page("pages/01_Customer_Selection.py")
