"""
This module handles the profile generation page in the Streamlit application.
"""

import streamlit as st
import uuid
from app.state import AppState
from app.services import (
    generate_character_profile,
    generate_hexa3d_profile,
    generate_tcc_program,
)
from app.psychometry_chc_generate import generate_chc_profile
from app.database import db_service as store_service

st.set_page_config(layout="wide")

if 'app_state' not in st.session_state:
    st.session_state.app_state = AppState()
app_state = st.session_state.app_state

if not app_state.authenticated:
    st.error("You must be logged in to view this page.")
    st.stop()

st.title("Generate New Profile")

description = st.text_area(
    "Character Description",
    height=200,
    placeholder="Enter a detailed description...",
)
assessment_type = st.radio(
    "Select Assessment Type", ("RIASEC", "Hexa3D", "CHC")
)

if st.button("Generate Profile", type="primary"):
    if not description:
        st.error("Please enter a character description.")
    else:
        with st.spinner("Generating profile..."):
            if assessment_type == "RIASEC":
                profile = generate_character_profile(
                    description, "gemini-1.5-pro", app_state.user_id
                )
                store_service.save_profile(profile, app_state.user_id)
                app_state.profile = profile
                app_state.chc_profile = None
                with st.spinner("Generating TCC program..."):
                    tcc_program = generate_tcc_program(
                        app_state.profile, "gemini-1.5-pro"
                    )
                    app_state.tcc_program = tcc_program
                    store_service.update_profile_with_tcc_program(
                        app_state.profile.character_id, tcc_program
                    )
            elif assessment_type == "Hexa3D":
                profile = generate_hexa3d_profile(
                    description, "gemini-1.5-pro", app_state.user_id
                )
                store_service.save_profile(profile, app_state.user_id)
                app_state.profile = profile
                app_state.chc_profile = None
            else:
                chc_profile = generate_chc_profile(
                    description, "gemini-1.5-pro", app_state.user_id
                )
                chc_profile.character_id = str(uuid.uuid4())
                store_service.save_chc_profile(
                    chc_profile, app_state.user_id
                )
                app_state.chc_profile = chc_profile
                app_state.profile = None

            st.success("Profile generated successfully!")
            st.switch_page("pages/02_Customer_Dashboard.py")

if st.button("Back to Dashboard"):
    st.switch_page("pages/02_Customer_Dashboard.py")
