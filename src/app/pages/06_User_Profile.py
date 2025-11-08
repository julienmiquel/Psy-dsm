"""
This module defines the User Profile page for the Streamlit application.
"""

import streamlit as st
from app.database import db_service
from app.user_models import UserProfile
from app.state import AppState

st.set_page_config(layout="wide")

if 'app_state' not in st.session_state:
    st.session_state.app_state = AppState()
app_state = st.session_state.app_state

if not app_state.authenticated:
    st.error("You must be logged in to view this page.")
    st.stop()

st.title("User Profile")

user_id = st.session_state.get("user_id")
if not user_id:
    st.warning("You need to be logged in to view this page.")
    st.stop()

user_profile = db_service.get_user_profile(user_id)
if not user_profile:
    user_profile = UserProfile(user_id=user_id)

with st.form("user_profile_form"):
    st.write("Edit your profile:")
    name = st.text_input("Name", value=user_profile.name)
    surname = st.text_input("Surname", value=user_profile.surname)
    email = st.text_input("Email", value=user_profile.email)

    submitted = st.form_submit_button("Save")
    if submitted:
        user_profile.name = name
        user_profile.surname = surname
        user_profile.email = email
        db_service.save_user_profile(user_profile)
        st.success("Profile saved!")

st.write("---")
st.write("Current Profile:")
st.write(f"**Name:** {user_profile.name}")
st.write(f"**Surname:** {user_profile.surname}")
st.write(f"**Email:** {user_profile.email}")

if st.button("Back to Dashboard"):
    st.switch_page("pages/02_Customer_Dashboard.py")
