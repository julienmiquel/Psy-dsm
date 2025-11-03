import streamlit as st
import os
import uuid
from google import genai
from app.models import CharacterProfile
from app.services import generate_character_profile, generate_tcc_program
from app.psychometry_chc_generate import generate_chc_profile
from app.chc_models import CHCModel
from app.dashboard import display_profile, display_chc_profile
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
    tab1, tab2 = st.tabs(["Generator", "User Profile"])

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
    st.sidebar.title("History")
    characters = store_service.get_user_characters(st.session_state['user_id'])
    for char in characters:
        if st.sidebar.button(char['character_name'], key=char['character_id']):
            st.session_state['character_id'] = char['character_id']
            st.session_state['profile'] = store_service.get_character_profile(char['character_id'])
            st.session_state['chc_profile'] = store_service.get_chc_profile(char['character_id'])
            if 'tcc_program' in st.session_state:
                del st.session_state["tcc_program"]
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
        st.rerun()