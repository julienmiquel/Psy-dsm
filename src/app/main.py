import streamlit as st
from google import genai
from .models import CharacterProfile
from .services import generate_character_profile
from .agent import agent as adk_agent
from google.adk.runners import Runner

def setup_gemini_client():
    """Sets up the Gemini client from Streamlit secrets."""
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
        return genai.Client(api_key=api_key)
    except Exception as e:
        st.error(f"Could not initialize Gemini client. Check your API key. Error: {e}")
        return None

def display_profile(profile: CharacterProfile):
    """Renders the character profile in the UI."""
    profile_dict = profile.model_dump()

    st.header("Generated Clinical Profile")
    st.subheader(f"Character: {profile_dict.get('character_name', 'N/A')}")
    st.caption(f"Profile Date: {profile_dict.get('profile_date', 'N/A')}")

    st.markdown("---")

    st.subheader("Overall Assessment:")
    summary = profile_dict.get('overall_assessment_summary', 'No summary provided.')
    st.write(summary)

    # Display Holland Code Assessment
    holland_assessment = profile_dict.get('holland_code_assessment')
    if holland_assessment:
        st.subheader("Holland Code (RIASEC) Assessment:")
        st.write(f"**Top Themes:** {', '.join(holland_assessment.get('top_themes', []))}")
        st.write(f"**Summary:** {holland_assessment.get('summary', 'No summary provided.')}")
        for score in holland_assessment.get('riasec_scores', []):
            st.markdown(f"- **{score.get('theme')}**: {score.get('score')}/10 - {score.get('description')}")

    diagnoses = profile_dict.get('diagnoses', [])
    if not diagnoses:
        st.info("No formal diagnoses were assigned.")
    else:
        st.subheader("Diagnostic Impressions:")
        for dx in diagnoses:
            with st.expander(f"{dx.get('disorder_name', 'N/A')} ({dx.get('dsm_code', 'N/A')})"):
                st.write(f"**Category:** {dx.get('dsm_category', 'N/A')}")

                specifiers = dx.get('specifiers', [])
                if specifiers:
                    st.write("**Specifiers:**")
                    for s in specifiers:
                        st.markdown(f"- {s.get('specifier_type')}: {s.get('value')}")

                st.write("**Criteria Met (Justification):**")
                criteria = dx.get('criteria_met', [])
                if criteria:
                    for c in criteria:
                        st.markdown(f"- {c}")
                else:
                    st.markdown("- None listed.")

                st.write("**Functional Impairment:**")
                impairment = dx.get('functional_impairment', 'Not specified.')
                st.write(impairment)

                note = dx.get('diagnostic_note')
                if note:
                    st.write("**Notes:**")
                    st.write(note)

def standard_ui(client):
    """Renders the standard UI."""
    st.text_area("Character Description", key="description", height=200)
    if st.button("Generate Profile"):
        description = st.session_state.description
        if not description:
            st.error("Please enter a character description.")
            return

        with st.spinner("Generating profile..."):
            try:
                profile = generate_character_profile(description, client)
                st.session_state.profile = profile
            except Exception as err:
                st.error(str(err))

    if "profile" in st.session_state and st.session_state.profile:
        display_profile(st.session_state.profile)

def chat_ui():
    """Renders the chat UI."""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Chat with the agent"):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.spinner("Agent is thinking..."):
            try:
                runner = Runner(agent=adk_agent)
                response = runner.run(prompt)
                if isinstance(response, CharacterProfile):
                    st.session_state.profile = response
                    display_profile(response)
                else:
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
                    with st.chat_message("assistant"):
                        st.markdown(response)
            except Exception as err:
                st.error(str(err))

def main():
    """Main Streamlit application."""
    st.title("DSM-5 Character Profile Generator")

    client = setup_gemini_client()
    if not client:
        return

    chat_mode = st.checkbox("Toggle Chat Mode")

    if chat_mode:
        chat_ui()
    else:
        standard_ui(client)

if __name__ == "__main__":
    main()
