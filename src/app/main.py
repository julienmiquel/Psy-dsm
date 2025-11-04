import streamlit as st
import os
import uuid
from google import genai
from app.models import CharacterProfile
from app.services import generate_character_profile, generate_tcc_program
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

    else:
        if 'comparing' in st.session_state and st.session_state['comparing']:
            st.header("Profile Comparison")

            char_id = st.session_state['compare_character_id']
            profiles = [p for p in all_profiles if p['character_id'] == char_id]

            profile_options = {f"{p['profile_type']} - {p['profile_datetime']}": p for p in profiles}

            col1, col2 = st.columns(2)
            with col1:
                selection1 = st.selectbox("Select Profile 1", list(profile_options.keys()), key="comp_select1")
            with col2:
                selection2 = st.selectbox("Select Profile 2", list(profile_options.keys()), key="comp_select2", index=min(1, len(profile_options)-1))

            if st.button("Compare Profiles"):
                profile_info1 = profile_options[selection1]
                profile_info2 = profile_options[selection2]

                # Load profiles
                if profile_info1['profile_type'] == "RIASEC":
                    st.session_state['compare_profile1'] = store_service.get_character_profile(profile_info1['character_id'])
                else:
                    st.session_state['compare_profile1'] = store_service.get_chc_profile(profile_info1['character_id'])

                if profile_info2['profile_type'] == "RIASEC":
                    st.session_state['compare_profile2'] = store_service.get_character_profile(profile_info2['character_id'])
                else:
                    st.session_state['compare_profile2'] = store_service.get_chc_profile(profile_info2['character_id'])

                st.session_state['comparison_ready'] = True

            if st.button("Back to Generator"):
                del st.session_state['comparing']
                if 'comparison_ready' in st.session_state:
                    del st.session_state['comparison_ready']
                st.rerun()

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

        with tab1:
            description = st.text_area("Character Description", height=200, placeholder="Enter a detailed description of the character you want to analyze.")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Generate Profile", type="primary"):
                    if not description:
                        st.error("Please enter a character description.")
                    else:
                        with st.spinner("Generating profile... This may take a moment."):
                            profile = generate_character_profile(description, "gemini-2.5-pro", st.session_state['user_id'])
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
                    for activity in module.activities:
                        st.markdown(f"**- {activity.title}**")
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
    all_profiles = store_service.get_user_all_profiles(st.session_state['user_id'])
    
    # Group profiles by character
    characters_history = {}
    for p in all_profiles:
        char_id = p['character_id']
        if char_id not in characters_history:
            characters_history[char_id] = {
                "name": p['character_name'],
                "profiles": []
            }
        characters_history[char_id]['profiles'].append(p)

    for char_id, char_data in characters_history.items():
        st.sidebar.markdown(f"**{char_data['name']}**")

        col1, col2 = st.sidebar.columns([3,1])
        with col1:
            for profile_entry in char_data['profiles']:
                display_text = f"({profile_entry['profile_type']}) - {profile_entry['profile_datetime']}"
                if st.button(display_text, key=f"view-{char_id}-{profile_entry['profile_type']}-{profile_entry['profile_datetime']}"):
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
            if st.button("Compare", key=f"compare-{char_id}"):
                st.session_state['comparing'] = True
                st.session_state['compare_character_id'] = char_id
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