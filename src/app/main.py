import streamlit as st
import os
from google import genai
from app.models import CharacterProfile
from app.services import generate_character_profile, generate_tcc_program
from app.dashboard import display_profile

from dotenv import load_dotenv

load_dotenv()
st.set_page_config(layout="wide")

st.title("DSM-5 Character Profile Generator")

description = st.text_area("Character Description", height=200, placeholder="Enter a detailed description of the character you want to analyze.")

if st.button("Generate Profile", type="primary"):
    if not description:
        st.error("Please enter a character description.")
    else:
        with st.spinner("Generating profile... This may take a moment."):
            # try:
                profile = generate_character_profile(description, "gemini-2.5-pro")
                st.session_state['profile'] = profile



if 'profile' in st.session_state:
    display_profile(st.session_state['profile'])
    st.session_state['tcc_program'] = generate_tcc_program(st.session_state['profile'], "gemini-2.5-pro")

if 'tcc_program' in st.session_state:
    st.header("Generated TCC Program")
    tcc_program = st.session_state['tcc_program']
    st.json(tcc_program.model_dump())