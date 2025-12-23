"""
Main application module for the DSM-5 Character Profile Generator.
This Streamlit app allows users to input character descriptions and generate
clinical profiles and TCC programs using AI.
"""

from dotenv import load_dotenv
import streamlit as st

from app.services import generate_character_profile, generate_tcc_program
from app.dashboard import display_profile

load_dotenv()
st.set_page_config(layout="wide")

st.title("DSM-5 Character Profile Generator")

description = st.text_area(
    "Character Description",
    height=200,
    placeholder="Enter a detailed description of the character you want to analyze."
)

if st.button("Generate Profile", type="primary"):
    if not description:
        st.error("Please enter a character description.")
    else:
        with st.spinner("Generating profile... This may take a moment."):
            # try:
            profile = generate_character_profile(description, "gemini-2.5-pro")
            st.session_state['profile'] = profile
            st.session_state['tcc_program'] = None


if 'profile' in st.session_state:
    display_profile(st.session_state['profile'])
    if st.session_state.get('tcc_program') is None:
        st.session_state['tcc_program'] = generate_tcc_program(
            st.session_state['profile'],
            "gemini-2.5-pro"
        )

if 'tcc_program' in st.session_state and st.session_state['tcc_program']:
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
