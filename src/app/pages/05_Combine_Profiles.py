"""
This module handles the profile combination page in the Streamlit application.
"""

import streamlit as st
from app.state import AppState
from app.services import combine_character_profiles
from app.database import db_service as store_service

st.set_page_config(layout="wide")

if 'app_state' not in st.session_state:
    st.session_state.app_state = AppState()
app_state = st.session_state.app_state

if not app_state.authenticated:
    st.error("You must be logged in to view this page.")
    st.stop()

st.title("Combine Profiles")

if not app_state.character_id:
    st.warning("Please select a character first.")
    st.switch_page("pages/01_Customer_Selection.py")

all_profiles = store_service.get_user_all_profiles(app_state.user_id)
profiles_to_combine = [
    p for p in all_profiles
    if p['character_name'] == app_state.profile.character_name
    and p['profile_type'] == "RIASEC"
]

selected_profiles_info = []
for p in profiles_to_combine:
    profile_label = f"{p['profile_type']} - {p['profile_datetime']}"
    if st.checkbox(profile_label, key=f"combine-cb-{p['character_id']}"):
        selected_profiles_info.append(p)

if st.button("Merge Selected Profiles"):
    if len(selected_profiles_info) < 2:
        st.error("Please select at least two profiles to merge.")
    else:
        with st.spinner("Merging profiles..."):
            selected_profiles = [
                store_service.get_character_profile(p['character_id'])
                for p in selected_profiles_info
            ]
            merged_profile = combine_character_profiles(
                selected_profiles, app_state.user_id
            )
            store_service.save_profile(merged_profile, app_state.user_id)
            app_state.profile = merged_profile
            st.success("Profiles merged successfully!")
            st.switch_page("pages/02_Customer_Dashboard.py")

if st.button("Back to Dashboard"):
    st.switch_page("pages/02_Customer_Dashboard.py")
