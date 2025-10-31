import streamlit as st
import os
from google import genai
from app.models import CharacterProfile
from app.services import generate_character_profile, generate_tcc_program
from app.dashboard import display_profile
from app import datastore_service

from dotenv import load_dotenv

load_dotenv()
st.set_page_config(layout="wide")

st.title("DSM-5 Character Profile Generator")

if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if not st.session_state['authenticated']:
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == os.environ.get("ADMIN_USERNAME") and password == os.environ.get("ADMIN_PASSWORD"):
            st.session_state['authenticated'] = True
            st.session_state['user_id'] = username
            st.rerun()
        else:
            st.error("Invalid username or password")
else:
    description = st.text_area("Character Description", height=200, placeholder="Enter a detailed description of the character you want to analyze.")

    if st.button("Generate Profile", type="primary"):
        if not description:
            st.error("Please enter a character description.")
        else:
            with st.spinner("Generating profile... This may take a moment."):
                profile = generate_character_profile(description, "gemini-2.5-pro", st.session_state['user_id'])
                st.session_state['profile'] = profile

    if 'profile' in st.session_state:
        display_profile(st.session_state['profile'])
        st.session_state['tcc_program'] = generate_tcc_program(st.session_state['profile'], "gemini-2.5-pro")

    if 'tcc_program' in st.session_state:
        st.header("Generated TCC Program")
        tcc_program = st.session_state['tcc_program']
        st.json(tcc_program.model_dump())

    st.sidebar.title("History")
    profiles = datastore_service.get_user_profiles(st.session_state['user_id'])
    for p in profiles:
        if st.sidebar.button(p.character_name, key=p.character_id):
            st.session_state['profile'] = p
            st.rerun()

    if st.sidebar.button("Clear Selection"):
        if "profile" in st.session_state:
            del st.session_state["profile"]
        if "tcc_program" in st.session_state:
            del st.session_state["tcc_program"]
        st.rerun()