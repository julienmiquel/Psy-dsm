"""
This module handles the customer selection page in the Streamlit application.
"""

import streamlit as st
from app.state import AppState
from app.database import db_service as store_service

st.set_page_config(layout="wide")

if 'app_state' not in st.session_state:
    st.session_state.app_state = AppState()
app_state = st.session_state.app_state

if not app_state.authenticated:
    st.error("You must be logged in to view this page.")
    st.stop()

st.title("Customer Selection")

characters = store_service.get_user_characters(app_state.user_id)
character_options = {
    char['character_name']: char['character_id'] for char in characters
}

if character_options:
    selected_character_name = st.selectbox(
        "Select a customer", list(character_options.keys())
    )

    if st.button("Load Customer"):
        app_state.character_id = character_options[selected_character_name]
        app_state.profile = store_service.get_character_profile(
            app_state.character_id
        )
        app_state.chc_profile = store_service.get_chc_profile(
            app_state.character_id
        )
        app_state.character_selected = True
        st.switch_page("pages/02_Customer_Dashboard.py")

if st.button("Create New Customer"):
    app_state.reset_character_data()
    app_state.character_selected = True
    st.switch_page("pages/02_Customer_Dashboard.py")
