"""
This module handles the customer dashboard page in the Streamlit application.
"""

import streamlit as st
from app.state import AppState
from app.dashboard import display_profile, display_chc_profile
from app.database import db_service as store_service
from app.services import generate_detailed_session

st.set_page_config(layout="wide")

if 'app_state' not in st.session_state:
    st.session_state.app_state = AppState()
app_state = st.session_state.app_state

if not app_state.authenticated:
    st.error("You must be logged in to view this page.")
    st.stop()

if not app_state.character_selected:
    st.warning("No character selected.")
    st.switch_page("pages/01_Customer_Selection.py")

st.title("Customer Dashboard")

# Display current profile
if app_state.profile:
    display_profile(app_state.profile)
    if app_state.profile.tcc_program:
        app_state.tcc_program = app_state.profile.tcc_program
elif app_state.chc_profile:
    display_chc_profile(app_state.chc_profile)
else:
    st.info("No profile loaded or generated for this customer yet.")

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

# Actions
st.header("Actions")
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("Generate New Profile"):
        st.switch_page("pages/03_Generate_Profile.py")
with col2:
    if st.button("Compare Profiles"):
        st.switch_page("pages/04_Compare_Profiles.py")
with col3:
    if st.button("Combine Profiles"):
        st.switch_page("pages/05_Combine_Profiles.py")

# History Sidebar
st.sidebar.title("History")
if app_state.user_id:
    all_profiles = store_service.get_user_all_profiles(app_state.user_id)
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
        for profile_entry in char_data['profiles']:
            text = f"({profile_entry['profile_type']}) - {profile_entry['profile_datetime']}"
            if st.sidebar.button(text, key=f"view-{profile_entry['character_id']}"):
                app_state.character_id = profile_entry['character_id']
                if profile_entry['profile_type'] == "RIASEC":
                    app_state.profile = store_service.get_character_profile(
                        profile_entry['character_id']
                    )
                    if app_state.profile and app_state.profile.tcc_program:
                        app_state.tcc_program = app_state.profile.tcc_program
                    app_state.chc_profile = None
                elif profile_entry['profile_type'] == "CHC":
                    app_state.chc_profile = store_service.get_chc_profile(
                        profile_entry['character_id']
                    )
                    app_state.profile = None
                st.rerun()

if st.sidebar.button("Back to Customer Selection"):
    app_state.back_to_character_selection()
    st.switch_page("pages/01_Customer_Selection.py")
