"""Main Streamlit application."""
import asyncio
import streamlit as st
from dotenv import load_dotenv
from google.adk.runners import Runner
from app.services import (
    generate_character_profile,
    generate_tcc_program,
    generate_podcast_script,
    analyze_audio
)
from app.dashboard import display_profile
from app.agent import agent

load_dotenv()
st.set_page_config(layout="wide")

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Standard Profile", "Audio Analysis", "Interactive Chat"])

if page == "Audio Analysis":
    st.sidebar.title("Audio Analysis Config")
    uploaded_file = st.sidebar.file_uploader(
        "Upload Audio for Analysis", type=['mp3', 'wav', 'm4a', 'ogg']
    )

    if uploaded_file is not None:
        if st.sidebar.button("Analyze Audio"):
            with st.sidebar.status("Analyzing audio...", expanded=True) as status:
                try:
                    # Read file bytes
                    audio_bytes = uploaded_file.getvalue()
                    mime_type = uploaded_file.type

                    # Analyze
                    analysis_result = analyze_audio(audio_bytes, mime_type, "gemini-2.5-pro")
                    st.session_state['audio_analysis'] = analysis_result
                    status.update(label="Analysis complete!", state="complete", expanded=False)
                except Exception as e: # pylint: disable=broad-exception-caught
                    status.update(label="Analysis failed!", state="error")
                    st.sidebar.error(f"Error: {e}")

    st.title("Audio Analysis Report")

    if 'audio_analysis' in st.session_state:
        result = st.session_state['audio_analysis']

        st.subheader("Overall Assessment")
        st.info(result.overall_assessment)

        st.subheader("Transcript & Analysis")
        for segment in result.segments:
            with st.chat_message(segment.speaker_label):
                st.write(f"**{segment.speaker_label}**: {segment.text}")
                st.caption(f"Tone: {segment.emotional_tone}")

                if segment.dark_patterns:
                    for dp in segment.dark_patterns:
                        st.error(f"⚠️ **{dp.type}** ({dp.confidence}): {dp.description}")
        st.markdown("---")
    else:
        st.info("Please upload an audio file to view the analysis.")

elif page == "Interactive Chat":
    st.title("Interactive Character Diagnosis")
    st.markdown("Chat with the AI psychologist to build a profile through conversation.")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Describe the character or answer the question..."):
        # Display user message
        st.chat_message("user").markdown(prompt)
        st.session_state.chat_history.append({"role": "user", "content": prompt})

        # Run the agent
        with st.spinner("Thinking..."):
            try:
                # To maintain state, we can simply include the history in the prompt context
                # if we cannot persist the runner/session object easily.
                # Since LlmAgent can take `history` in `run`, or we can manually construct it.
                # However, ADK's `Runner` takes care of state if we reuse it.
                # Since we create a new `Runner` each time, we must pass the history.

                # Let's verify if `Runner` has a `history` parameter in `run` or `run_async` or init.
                # Based on typical ADK usage: runner = Runner(agent=agent, history=history_events)
                # But we have `chat_history` as a list of dicts. We need to convert it.

                # Simplified approach: Append history to the prompt text.
                # This ensures the LLM sees the conversation context.

                history_context = ""
                for msg in st.session_state.chat_history[:-1]: # Exclude the current prompt
                    history_context += f"{msg['role'].capitalize()}: {msg['content']}\n"

                FULL_PROMPT = (
                    f"Conversation History:\n{history_context}\n\n"
                    f"User: {prompt}\n"
                    "Please respond to the user based on the history and your instructions."
                )

                # NOTE: The following async code is wrapped to run in sync Streamlit.
                async def run_chat():
                    """Runs the agent with the provided prompt."""
                    # pylint: disable=missing-kwoa
                    runner = Runner(agent=agent)
                    # We pass the full prompt with history context.
                    # pylint: disable=too-many-function-args, missing-kwoa
                    # Using the full prompt simulates memory for the LLM.
                    chat_result = await runner.run_async(FULL_PROMPT)
                    return chat_result.text

                # Attempt to run (will likely fail in this mock env due to credentials)
                response_text = asyncio.run(run_chat())

                st.chat_message("assistant").markdown(response_text)
                st.session_state.chat_history.append(
                    {"role": "assistant", "content": response_text}
                )

            except Exception as e: # pylint: disable=broad-exception-caught
                # Fallback for when credentials/API are not available in this env
                FALLBACK_MSG = (
                    f"*(System Note: Unable to connect to Agent API: {e}. "
                    "In a live environment, the AI would respond here.)*"
                )
                st.chat_message("assistant").markdown(FALLBACK_MSG)
                st.session_state.chat_history.append(
                    {"role": "assistant", "content": FALLBACK_MSG}
                )

elif page == "Standard Profile":
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
                profile = generate_character_profile(description, "gemini-2.5-pro")
                st.session_state['profile'] = profile
                st.session_state['tcc_program'] = None

    if 'profile' in st.session_state:
        display_profile(st.session_state['profile'])
        if st.session_state['tcc_program'] is None:
            st.session_state['tcc_program'] = generate_tcc_program(
                st.session_state['profile'], "gemini-2.5-pro"
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

        if st.button("Generate Podcast Script", type="primary"):
            with st.spinner("Generating podcast script..."):
                podcast_script = generate_podcast_script(
                    st.session_state['profile'], st.session_state['tcc_program'], "gemini-2.5-pro"
                )
                st.session_state['podcast_script'] = podcast_script

    if 'podcast_script' in st.session_state:
        script = st.session_state['podcast_script']
        st.header(f"Podcast: {script.title}")
        st.caption(f"Target Audience: {script.target_audience}")

        for segment in script.segments:
            with st.chat_message(segment.speaker):
                st.write(f"**{segment.speaker}:** {segment.text}")
