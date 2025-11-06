"""
Main Streamlit application for the DSM-5 Character Profile Generator.

This module handles the user interface, state management, and interaction
with the backend services for character profile generation and analysis.
"""

import os
import uuid
import streamlit as st
from dotenv import load_dotenv

from app.models import CharacterProfile
from app.services import (
    generate_character_profile,
    generate_hexa3d_profile,
    generate_tcc_program,
    analyze_profile_comparison,
    combine_character_profiles,
    generate_detailed_session,
)
from app.psychometry_chc_generate import generate_chc_profile
from app.dashboard import display_profile, display_chc_profile, display_comparison
from app.database import db_service as store_service
from app.crm import crm_page
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
    if app_state.user_id:
        all_profiles = store_service.get_user_all_profiles(app_state.user_id)
    else:
        all_profiles = []

    if not app_state.character_selected:
        st.title("Welcome")
        
        characters = store_service.get_user_characters(app_state.user_id)
        character_options = {
            char['character_name']: char['character_id'] for char in characters
        }

        if character_options:
            selected_character_name = st.selectbox(
                "Select a character", list(character_options.keys())
            )

            if st.button("Load Character"):
                app_state.character_id = character_options[selected_character_name]
                app_state.profile = store_service.get_character_profile(
                    app_state.character_id
                )
                app_state.chc_profile = store_service.get_chc_profile(
                    app_state.character_id
                )
                app_state.character_selected = True
                st.rerun()

        if st.button("Create New Character"):
            app_state.reset_character_data()
            app_state.character_selected = True
            st.rerun()

    elif app_state.combining:
        st.header("Combine Profiles")
        char_name = app_state.combine_character_name
        st.subheader(f"Character: {char_name}")

        profiles_to_combine = [
            p for p in all_profiles
            if p['character_name'] == char_name and p['profile_type'] == "RIASEC"
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
                    app_state.combining = False
                    st.rerun()

        if st.button("Back"):
            app_state.combining = False
            st.rerun()

    else:
        tabs = ["Generator", "User Profile"]
        if app_state.comparison_ready:
            tabs.append("Comparison")

        tab_objs = st.tabs(tabs)
        tab1, tab2 = tab_objs[0], tab_objs[1]
        if len(tab_objs) > 2:
            comparison_tab = tab_objs[2]
            with comparison_tab:
                display_comparison(
                    app_state.compare_profile1, app_state.compare_profile2
                )

                if st.button("Analyze Comparison with Gemini"):
                    with st.spinner("Analyzing comparison..."):
                        profile1 = app_state.compare_profile1
                        profile2 = app_state.compare_profile2
                        if isinstance(profile1, CharacterProfile) and isinstance(
                            profile2, CharacterProfile
                        ):
                            analysis = analyze_profile_comparison(
                                profile1, profile2, "gemini-2.5-pro"
                            )
                            app_state.comparison_analysis = analysis
                        else:
                            st.error(
                                "Comparison analysis only supports two RIASEC profiles."
                            )

                if app_state.comparison_analysis and app_state.comparison_ready:
                    st.subheader("Gemini Analysis")
                    st.markdown(app_state.comparison_analysis)

        with tab1:
            description = st.text_area(
                "Character Description",
                height=200,
                placeholder="Enter a detailed description...",
            )
            assessment_type = st.radio(
                "Select Assessment Type", ("RIASEC", "Hexa3D")
            )
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Generate Profile", type="primary"):
                    if not description:
                        st.error("Please enter a character description.")
                    else:
                        with st.spinner("Generating profile..."):
                            if assessment_type == "RIASEC":
                                profile = generate_character_profile(
                                    description, "gemini-2.5-pro", app_state.user_id
                                )
                            else:
                                profile = generate_hexa3d_profile(
                                    description, "gemini-2.5-pro", app_state.user_id
                                )
                            app_state.profile = profile
                            app_state.chc_profile = None
                            app_state.tcc_program = None

            with col2:
                if st.button("Generate CHC Profile"):
                    if not description:
                        st.error("Please enter a character description.")
                    else:
                        with st.spinner("Generating CHC profile..."):
                            chc_profile = generate_chc_profile(
                                description, "gemini-2.5-pro", app_state.user_id
                            )
                            chc_profile.character_id = str(uuid.uuid4())
                            store_service.save_chc_profile(
                                chc_profile, app_state.user_id
                            )
                            app_state.chc_profile = chc_profile
                            app_state.profile = None
                            app_state.tcc_program = None

            if app_state.profile is not None:
                display_profile(app_state.profile)
                if app_state.profile.tcc_program:
                    app_state.tcc_program = app_state.profile.tcc_program
                else:
                    with st.spinner("Generating TCC program..."):
                        tcc_program = generate_tcc_program(
                            app_state.profile, "gemini-2.5-pro"
                        )
                        app_state.tcc_program = tcc_program
                        store_service.update_profile_with_tcc_program(
                            app_state.profile.character_id, tcc_program
                        )

            if app_state.chc_profile is not None:
                display_chc_profile(app_state.chc_profile)

            if app_state.tcc_program is not None:
                st.header("Generated TCC Program")
                tcc_program = app_state.tcc_program
                
                st.subheader(tcc_program.title)
                st.write(f"**Global Objective:** {tcc_program.global_objective}")
                
                for i, module in enumerate(tcc_program.modules):
                    st.markdown(f"### Module {i+1}: {module.title}")
                    st.write(f"**Objective:** {module.objective}")
                    st.write(f"**Session Range:** {module.session_range}")

                    st.markdown("#### Activities:")
                    for j, activity in enumerate(module.activities):
                        st.markdown(f"**- {activity.title}**")
                        
                        key = f"gen-session-{i}-{j}"
                        if st.button(f"Detailed Session for '{activity.title}'", key=key):
                            with st.spinner(f"Generating session..."):
                                profile = app_state.profile
                                if profile:
                                    session_details = generate_detailed_session(
                                        profile, module, activity
                                    )
                                    app_state.detailed_sessions[f"{i}-{j}"] = session_details
                                else:
                                    st.error("A character profile is needed.")

                        if f"{i}-{j}" in app_state.detailed_sessions:
                            with st.expander("View Detailed Session Plan"):
                                st.markdown(
                                    app_state.detailed_sessions[f"{i}-{j}"],
                                    unsafe_allow_html=True,
                                )

                        for detail in activity.details:
                            st.markdown(f"  - {detail}")
                    st.markdown("---")
                with st.expander("View Raw TCC Program JSON"):
                    st.json(tcc_program.model_dump())

        with tab2:
            crm_page()


if app_state.user_id:
    if st.sidebar.button("Back to Character Selection"):
        app_state.back_to_character_selection()
        st.rerun()

    st.sidebar.title("History")
    
    characters_history = {}
    for p in all_profiles:
        char_name = p['character_name']
        if char_name not in characters_history:
            characters_history[char_name] = {
                "name": p['character_name'], "profiles": []
            }
        characters_history[char_name]['profiles'].append(p)

    for char_name, char_data in characters_history.items():
        st.sidebar.markdown(f"**{char_data['name']}**")

        col1, col2 = st.sidebar.columns([3,1])
        with col1:
            for profile_entry in char_data['profiles']:
                text = f"({profile_entry['profile_type']}) - {profile_entry['profile_datetime']}"
                if st.button(text, key=f"view-{profile_entry['character_id']}"):
                    app_state.character_id = profile_entry['character_id']
                    app_state.reset_character_data()

                    if profile_entry['profile_type'] == "RIASEC":
                        app_state.profile = store_service.get_character_profile(
                            profile_entry['character_id']
                        )
                    elif profile_entry['profile_type'] == "CHC":
                        app_state.chc_profile = store_service.get_chc_profile(
                            profile_entry['character_id']
                        )

                    if app_state.profile and app_state.profile.tcc_program:
                        app_state.tcc_program = app_state.profile.tcc_program

                    st.rerun()
        with col2:
            if st.button("Compare", key=f"compare-{char_name}"):
                app_state.comparing = True
                app_state.compare_character_name = char_name
                st.rerun()
            if st.button("Combine", key=f"combine-{char_name}"):
                app_state.combining = True
                app_state.combine_character_name = char_name
                st.rerun()

    if st.sidebar.button("Clear Selection"):
        app_state.back_to_character_selection()
        st.rerun()
