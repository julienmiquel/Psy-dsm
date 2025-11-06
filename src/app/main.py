import streamlit as st
import os
import uuid
from google import genai
from app.models import CharacterProfile
from app.services import generate_character_profile, generate_hexa3d_profile, generate_tcc_program, analyze_profile_comparison, combine_character_profiles, generate_detailed_session
from app.psychometry_chc_generate import generate_chc_profile
from app.chc_models import CHCModel
from app.dashboard import display_profile, display_chc_profile, display_comparison
from app.database import db_service as store_service
from app.crm import crm_page


from dotenv import load_dotenv
load_dotenv()
st.set_page_config(layout="wide")

st.title("DSM-5 Character Profile Generator")

DEBUG = os.environ.get("DEBUG", "false").lower() == "true"
DEBUG = True

if DEBUG :
    st.warning("Debug mode is ON. Make sure not to use real PII data.")
    st.session_state['authenticated'] = True
    st.session_state['user_id'] = "admin"

if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if not st.session_state['authenticated']:
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == os.environ.get("ADMIN_USERNAME", "admin") and password == os.environ.get("ADMIN_PASSWORD", "h4gcv8PpV2@EKb@"):
            st.session_state['authenticated'] = True
            st.session_state['user_id'] = username
            st.rerun()
        else:
            st.error("Invalid username or password")
else:
    if st.session_state.get('user_id'):
        all_profiles = store_service.get_user_all_profiles(st.session_state['user_id'])
    else:
        all_profiles = []
    if 'character_selected' not in st.session_state:
        st.session_state['character_selected'] = False

    if not st.session_state['character_selected']:
        st.title("Welcome")
        
        characters = store_service.get_user_characters(st.session_state['user_id'])
        character_options = {char['character_name']: char['character_id'] for char in characters}

        if character_options:
            selected_character_name = st.selectbox("Select a character", list(character_options.keys()))

            if st.button("Load Character"):
                character_id = character_options[selected_character_name]
                st.session_state['character_id'] = character_id
                st.session_state['profile'] = store_service.get_character_profile(character_id)
                st.session_state['chc_profile'] = store_service.get_chc_profile(character_id)
                st.session_state['character_selected'] = True
                st.rerun()

        if st.button("Create New Character"):
            # Reset session state for new character
            if "profile" in st.session_state:
                del st.session_state["profile"]
            if "chc_profile" in st.session_state:
                del st.session_state["chc_profile"]
            if "tcc_program" in st.session_state:
                del st.session_state["tcc_program"]
            if "character_id" in st.session_state:
                del st.session_state["character_id"]
            st.session_state['character_selected'] = True
            st.rerun()

    elif 'combining' in st.session_state and st.session_state['combining']:
        st.header("Combine Profiles")
        char_name = st.session_state['combine_character_name']
        st.subheader(f"Character: {char_name}")

        profiles_to_combine = [p for p in all_profiles if p['character_name'] == char_name and p['profile_type'] == "RIASEC"]
        
        selected_profiles_info = []
        for p in profiles_to_combine:
            label = f"{p['profile_type']} - {p['profile_datetime']}"
            if st.checkbox(label, key=f"combine-cb-{p['character_id']}"):
                selected_profiles_info.append(p)

        if st.button("Merge Selected Profiles"):
            if len(selected_profiles_info) < 2:
                st.error("Please select at least two profiles to merge.")
            else:
                with st.spinner("Merging profiles..."):
                    selected_profiles = [store_service.get_character_profile(p['character_id']) for p in selected_profiles_info]
                    merged_profile = combine_character_profiles(selected_profiles, st.session_state['user_id'])
                    store_service.save_profile(merged_profile, st.session_state['user_id'])
                    st.session_state['profile'] = merged_profile
                    st.session_state['combining'] = False
                    st.rerun()

        if st.button("Back"):
            del st.session_state['combining']
            st.rerun()

    else:
        tabs = ["Generator", "User Profile"]
        if 'comparison_ready' in st.session_state and st.session_state.get('comparison_ready', False):
            tabs.append("Comparison")

        tab_objs = st.tabs(tabs)
        tab1 = tab_objs[0]
        tab2 = tab_objs[1]
        if len(tab_objs) > 2:
            comparison_tab = tab_objs[2]
            with comparison_tab:
                display_comparison(st.session_state['compare_profile1'], st.session_state['compare_profile2'])

                if st.button("Analyze Comparison with Gemini"):
                    with st.spinner("Analyzing comparison..."):
                        profile1 = st.session_state['compare_profile1']
                        profile2 = st.session_state['compare_profile2']
                        if isinstance(profile1, CharacterProfile) and isinstance(profile2, CharacterProfile):
                            analysis = analyze_profile_comparison(
                                profile1,
                                profile2,
                                "gemini-2.5-pro"
                            )
                            st.session_state['comparison_analysis'] = analysis
                        else:
                            st.error("Comparison analysis only supports two RIASEC profiles.")

                if 'comparison_analysis' in st.session_state and 'comparison_ready' in st.session_state and st.session_state['comparison_ready']:
                    st.subheader("Gemini Analysis")
                    st.markdown(st.session_state['comparison_analysis'])

        with tab1:
            description = st.text_area("Character Description", height=200, placeholder="Enter a detailed description of the character you want to analyze.")
            assessment_type = st.radio("Select Assessment Type", ("RIASEC", "Hexa3D"))
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Generate Profile", type="primary"):
                    if not description:
                        st.error("Please enter a character description.")
                    else:
                        with st.spinner("Generating profile... This may take a moment."):
                            if assessment_type == "RIASEC":
                                profile = generate_character_profile(description, "gemini-2.5-pro", st.session_state['user_id'])
                            else:
                                profile = generate_hexa3d_profile(description, "gemini-2.5-pro", st.session_state['user_id'])
                            st.session_state['profile'] = profile
                            if 'chc_profile' in st.session_state:
                                del st.session_state['chc_profile']
                            if 'tcc_program' in st.session_state:
                                del st.session_state["tcc_program"]

            with col2:
                if st.button("Generate CHC Profile"):
                    if not description:
                        st.error("Please enter a character description.")
                    else:
                        with st.spinner("Generating CHC profile... This may take a moment."):
                            chc_profile = generate_chc_profile(description, "gemini-2.5-pro", st.session_state['user_id'])
                            chc_profile.character_id = str(uuid.uuid4())
                            store_service.save_chc_profile(chc_profile, st.session_state['user_id'])
                            st.session_state['chc_profile'] = chc_profile
                            if 'profile' in st.session_state:
                                del st.session_state['profile']
                            if 'tcc_program' in st.session_state:
                                del st.session_state["tcc_program"]

            if 'profile' in st.session_state and st.session_state['profile'] is not None:
                display_profile(st.session_state['profile'])
                if st.session_state['profile'].tcc_program:
                    st.session_state['tcc_program'] = st.session_state['profile'].tcc_program
                else:
                    with st.spinner("Generating TCC program... This may take a moment."):
                        tcc_program = generate_tcc_program(st.session_state['profile'], "gemini-2.5-pro")
                        st.session_state['tcc_program'] = tcc_program
                        store_service.update_profile_with_tcc_program(st.session_state['profile'].character_id, tcc_program)

            if 'chc_profile' in st.session_state and st.session_state['chc_profile'] is not None:
                display_chc_profile(st.session_state['chc_profile'])

            if 'tcc_program' in st.session_state and st.session_state['tcc_program'] is not None:
                st.header("Generated TCC Program")
                tcc_program = st.session_state['tcc_program']
                
                st.subheader(tcc_program.title)
                st.write(f"**Global Objective:** {tcc_program.global_objective}")
                
                for i, module in enumerate(tcc_program.modules):
                    st.markdown(f"### Module {i+1}: {module.title}")
                    st.write(f"**Objective:** {module.objective}")
                    st.write(f"**Session Range:** {module.session_range}")

                    st.markdown("#### Activities:")
                    for j, activity in enumerate(module.activities):
                        st.markdown(f"**- {activity.title}**")
                        
                        if st.button(f"Generate Detailed Session for '{activity.title}'", key=f"gen-session-{i}-{j}"):
                            with st.spinner(f"Generating session for '{activity.title}'..."):
                                profile = st.session_state.get('profile')
                                if profile:
                                    session_details = generate_detailed_session(profile, module, activity)
                                    if 'detailed_sessions' not in st.session_state:
                                        st.session_state['detailed_sessions'] = {}
                                    st.session_state['detailed_sessions'][f"{i}-{j}"] = session_details
                                else:
                                    st.error("A full character profile is needed to generate session details.")

                        if 'detailed_sessions' in st.session_state and f"{i}-{j}" in st.session_state['detailed_sessions']:
                            with st.expander("View Detailed Session Plan"):
                                st.markdown(st.session_state['detailed_sessions'][f"{i}-{j}"], unsafe_allow_html=True)

                        for detail in activity.details:
                            st.markdown(f"  - {detail}")
                    st.markdown("---")
                with st.expander("View Raw TCC Program JSON"):
                    st.json(tcc_program.model_dump())

        with tab2:
            crm_page()


if 'user_id' in st.session_state:
    if st.sidebar.button("Back to Character Selection"):
        st.session_state['character_selected'] = False
        if 'comparing' in st.session_state:
            del st.session_state['comparing']
        if 'comparison_ready' in st.session_state:
            del st.session_state['comparison_ready']
        st.rerun()

    st.sidebar.title("History")
    
    # Group profiles by character name
    characters_history = {}
    for p in all_profiles:
        char_name = p['character_name']
        if char_name not in characters_history:
            characters_history[char_name] = {
                "name": p['character_name'],
                "profiles": []
            }
        characters_history[char_name]['profiles'].append(p)

    for char_name, char_data in characters_history.items():
        st.sidebar.markdown(f"**{char_data['name']}**")

        col1, col2 = st.sidebar.columns([3,1])
        with col1:
            for profile_entry in char_data['profiles']:
                display_text = f"({profile_entry['profile_type']}) - {profile_entry['profile_datetime']}"
                if st.button(display_text, key=f"view-{profile_entry['character_id']}"):
                    st.session_state['character_id'] = profile_entry['character_id']

                    # Clear existing profiles
                    if 'profile' in st.session_state: del st.session_state['profile']
                    if 'chc_profile' in st.session_state: del st.session_state['chc_profile']
                    if 'tcc_program' in st.session_state: del st.session_state['tcc_program']

                    if profile_entry['profile_type'] == "RIASEC":
                        st.session_state['profile'] = store_service.get_character_profile(profile_entry['character_id'])
                    elif profile_entry['profile_type'] == "CHC":
                        st.session_state['chc_profile'] = store_service.get_chc_profile(profile_entry['character_id'])

                    if 'profile' in st.session_state and st.session_state['profile'] is not None:
                        if st.session_state['profile'].tcc_program:
                            st.session_state['tcc_program'] = st.session_state['profile'].tcc_program

                    st.rerun()
        with col2:
            if st.button("Compare", key=f"compare-{char_name}"):
                st.session_state['comparing'] = True
                st.session_state['compare_character_name'] = char_name
                st.rerun()
            if st.button("Combine", key=f"combine-{char_name}"):
                st.session_state['combining'] = True
                st.session_state['combine_character_name'] = char_name
                st.rerun()

    if st.sidebar.button("Clear Selection"):
        if "profile" in st.session_state:
            del st.session_state["profile"]
        if "chc_profile" in st.session_state:
            del st.session_state["chc_profile"]
        if "tcc_program" in st.session_state:
            del st.session_state["tcc_program"]
        if "character_id" in st.session_state:
            del st.session_state["character_id"]
        if 'comparing' in st.session_state:
            del st.session_state['comparing']
        if 'comparison_ready' in st.session_state:
            del st.session_state['comparison_ready']
        st.rerun()