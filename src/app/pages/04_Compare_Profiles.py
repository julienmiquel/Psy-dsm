"""
This module handles the profile comparison page in the Streamlit application.
"""

import streamlit as st
from app.state import AppState
from app.models import CharacterProfile
from app.services import analyze_profile_comparison
from app.dashboard import display_comparison
from app.database import db_service as store_service

st.set_page_config(layout="wide")

if 'app_state' not in st.session_state:
    st.session_state.app_state = AppState()
app_state = st.session_state.app_state

if not app_state.authenticated:
    st.error("You must be logged in to view this page.")
    st.stop()

st.title("Compare Profiles")

if not app_state.character_id:
    st.warning("Please select a character first.")
    st.switch_page("pages/01_Customer_Selection.py")

all_profiles = store_service.get_user_all_profiles(app_state.user_id)
character_profiles = [
    p for p in all_profiles
    if p['character_name'] == app_state.profile.character_name
    and p['profile_type'] == "RIASEC"
]

profile_options = {
    f"{p['profile_type']} - {p['profile_datetime']}": p['character_id']
    for p in character_profiles
}

if len(profile_options) < 2:
    st.warning("You need at least two RIASEC profiles for the same character to compare.")
else:
    col1, col2 = st.columns(2)
    with col1:
        selected_profile1_label = st.selectbox(
            "Select Profile 1", list(profile_options.keys())
        )
        profile1_id = profile_options[selected_profile1_label]
        app_state.compare_profile1 = store_service.get_character_profile(profile1_id)

    with col2:
        selected_profile2_label = st.selectbox(
            "Select Profile 2", list(profile_options.keys())
        )
        profile2_id = profile_options[selected_profile2_label]
        app_state.compare_profile2 = store_service.get_character_profile(profile2_id)

    if app_state.compare_profile1 and app_state.compare_profile2:
        display_comparison(app_state.compare_profile1, app_state.compare_profile2)

        if st.button("Analyze Comparison with Gemini"):
            with st.spinner("Analyzing comparison..."):
                analysis = analyze_profile_comparison(
                    app_state.compare_profile1, app_state.compare_profile2, "gemini-1.5-pro"
                )
                app_state.comparison_analysis = analysis

        if app_state.comparison_analysis:
            st.subheader("Gemini Analysis")
            st.markdown(app_state.comparison_analysis)

if st.button("Back to Dashboard"):
    st.switch_page("pages/02_Customer_Dashboard.py")
