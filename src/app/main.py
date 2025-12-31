"""Main Streamlit application."""
import streamlit as st
import os
from dotenv import load_dotenv
from app.services import (
    generate_character_profile,
    generate_tcc_program,
    generate_podcast_script,
    generate_podcast_script,
    generate_module_podcast_script,
    generate_sleepcast_script,
    analyze_audio
)
from app.music import MusicGenerator
from app.music import MusicGenerator
from app.audio import generate_audio_segment, assemble_audio, mix_audio
from app.dashboard import display_profile
from app.utils import (
    save_character_data,
    get_saved_characters,
    get_character_versions,
    load_character_data,
    sanitize_filename
)
from app.logging_config import setup_logging
import logging

setup_logging()
logger = logging.getLogger(__name__)

def autosave_data():
    """Helper to autosave current session state to disk."""
    if 'profile' in st.session_state and st.session_state['profile']:
        logger.info("Autosaving data...")
        # Collect audio
        audio_map = {}
        if 'audio_full' in st.session_state:
            audio_map['full'] = st.session_state['audio_full']
        
        # Collect module audio and sleepcast scripts
        sleepcast_scripts = {}
        
        for key in st.session_state:
            # Module Podcast Audio
            if key.startswith("audio_mod_"):
                suffix = key.replace("audio_mod_", "module_")
                audio_map[suffix] = st.session_state[key]
            
            # Sleepcast Final Audio (Mixed)
            if key.startswith("mixed_sleep_"):
                 suffix = key.replace("mixed_sleep_", "sleepcast_mixed_")
                 audio_map[suffix] = st.session_state[key]

            # Sleepcast Scripts
            if key.startswith("sleepcast_") and not key.startswith("sleepcast_mixed_"):
                 # key is like sleepcast_0
                 idx = key.replace("sleepcast_", "")
                 if idx.isdigit():
                     val = st.session_state[key]
                     if val: # Check if not None
                        sleepcast_scripts[idx] = val

            # Module Scripts
            if key.startswith("module_podcast_"):
                # key is module_podcast_0
                idx = key.replace("module_podcast_", "")
                if idx.isdigit():
                    val = st.session_state[key]
                    if val:
                        # For saving, we can just use the index as key for the dict
                        # But wait, utils.py expects module_scripts dict
                        if 'module_scripts' not in locals():
                             module_scripts = {}
                        module_scripts[idx] = val

        saved_path = save_character_data(
            st.session_state['profile'],
            st.session_state.get('tcc_program'),
            st.session_state.get('podcast_script'),
            audio_map,
            description=st.session_state.get('description', ""),
            sleepcast_scripts=sleepcast_scripts,
            overwrite_dir=st.session_state.get('save_dir'),
            module_scripts=module_scripts if 'module_scripts' in locals() else None
        )
        # Store for future overwrites
        st.session_state['save_dir'] = saved_path
        logger.info(f"Autosave complete: {saved_path}")

load_dotenv()
st.set_page_config(layout="wide")


# --- LOAD CHARACTER SECTION ---
st.sidebar.title("Load Character")
saved_chars_map = get_saved_characters()
saved_char_labels = [""] + list(saved_chars_map.keys())

if saved_chars_map:
    selected_label = st.sidebar.selectbox("Select Character", saved_char_labels)
    if selected_label:
        selected_char_folder = saved_chars_map[selected_label]
        versions = get_character_versions(selected_char_folder)
        if versions:
            # Format timestamps for display if desired, here just raw
            selected_version = st.sidebar.selectbox("Select Version", versions)
            
            if st.sidebar.button("📂 Load Version"):
                logger.info(f"Loading version {selected_version} for {selected_label}")
                data = load_character_data(selected_char_folder, selected_version)
                if data:
                    # Clear current state effectively by overwriting
                    st.session_state['description'] = data.get('description', "")
                    st.session_state['profile'] = data.get('profile')
                    st.session_state['tcc_program'] = data.get('tcc_program')
                    st.session_state['podcast_script'] = data.get('podcast_script')
                    
                    # Restore audio
                    # Clear existing audio keys first to avoid ghosts? 
                    # Streamlit session state is persistent, so maybe good idea.
                    # But simpler just to overwrite what we have.
                    audio_map = data.get('audio_map', {})
                    if 'full' in audio_map:
                        st.session_state['audio_full'] = audio_map['full']
                    
                    # Restore module audio
                    for key, val in audio_map.items():
                        if key.startswith("module_"):
                            # Map back to audio_mod_X
                            # We need to know the index X. 
                            # If we saved as podcast_module_{i}.wav, key is module_{i}
                            # So we put it in session state as audio_mod_{i}
                            idx_str = key.replace("module_", "")
                            st.session_state[f"audio_mod_{idx_str}"] = val
                    
                    # Restore module scripts
                    mod_scripts = data.get('module_scripts', {})
                    for idx, script in mod_scripts.items():
                        st.session_state[f"module_podcast_{idx}"] = script
                        
                    # Restore sleepcast scripts
                    sleep_scripts = data.get('sleepcast_scripts', {})
                    for idx, script in sleep_scripts.items():
                        st.session_state[f"sleepcast_{idx}"] = script
                    
                    # Store loaded dir as current save target?
                    # Yes, if we load, we probably want to update that version unless we explicitly save new.
                    # But overwriting a LOADED history version might be dangerous.
                    # Usually "Save" implies update.
                    # Let's set it.
                    st.session_state['save_dir'] = os.path.join("output", selected_char_folder, selected_version)

                    st.sidebar.success(f"Loaded {selected_label} ({selected_version})")
                    st.rerun()
                else:
                    st.sidebar.error("Failed to load data.")
        else:
            st.sidebar.info("No saved versions found.")
else:
    st.sidebar.info("No saved characters found.")

st.sidebar.markdown("---")

st.sidebar.title("Audio Analysis")
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
                logger.info("Starting audio analysis...")
                analysis_result = analyze_audio(audio_bytes, mime_type, "gemini-2.5-pro")
                st.session_state['audio_analysis'] = analysis_result
                logger.info("Audio analysis complete.")
                status.update(label="Analysis complete!", state="complete", expanded=False)
            except Exception as e: # pylint: disable=broad-exception-caught
                status.update(label="Analysis failed!", state="error")
                st.sidebar.error(f"Error: {e}")

if st.sidebar.button("💾 Save All to Disk"):
    logger.info("User clicked Save All to Disk")
    if 'profile' in st.session_state and st.session_state['profile']:
        # Collect audio data
        audio_map = {}
        if 'audio_full' in st.session_state:
            audio_map['full'] = st.session_state['audio_full']
        
        # Check for module audios
        # We need to scan keys or reconstructed based on what we know exists
        # Inspecting session state keys is easier if we just iterate
        for key in st.session_state:
            if key.startswith("audio_mod_"):
                suffix = key.replace("audio_mod_", "module_")
                audio_map[suffix] = st.session_state[key]
        
        saved_path = save_character_data(
            st.session_state['profile'],
            st.session_state.get('tcc_program'),
            st.session_state.get('podcast_script'),
            audio_map,
            description=st.session_state.get('description', ""),
            overwrite_dir=st.session_state.get('save_dir')
        )
        st.session_state['save_dir'] = saved_path
        st.sidebar.success(f"Saved to: {saved_path}")
    else:
        st.sidebar.warning("No profile to save yet.")

st.title("DSM-5 Character Profile Generator")

if 'audio_analysis' in st.session_state:
    result = st.session_state['audio_analysis']
    st.header("Audio Analysis Report")

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


description = st.text_area(
    "Character Description",
    value=st.session_state.get('description', ""),
    height=200,
    placeholder="Enter a detailed description of the character you want to analyze."
)
# Update session state on change (or just read from variable when saving)
st.session_state['description'] = description

if st.button("Generate Profile", type="primary"):
    if not description:
        st.error("Please enter a character description.")
    else:
        with st.spinner("Generating profile... This may take a moment."):
            logger.info("Generating profile for new description...")
            profile = generate_character_profile(description, "gemini-2.5-pro")
            st.session_state['profile'] = profile
            logger.info(f"Profile generated: {profile.character_name}")
            st.session_state['tcc_program'] = None
            # Reset save dir for new profile
            st.session_state['save_dir'] = None
            autosave_data()

if 'profile' in st.session_state:
    display_profile(st.session_state['profile'])
    if st.session_state['tcc_program'] is None:
        logger.info("Generating TCC program...")
        st.session_state['tcc_program'] = generate_tcc_program(
            st.session_state['profile'], "gemini-2.5-pro"
        )
        logger.info("TCC program generated.")
        autosave_data()

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
        
        # Module-specific podcast generation
        mod_key = f"module_podcast_{i}"
        audio_key = f"audio_mod_{i}"
        
        if audio_key in st.session_state:
             st.success("Podcast Ready!")
             st.audio(st.session_state[audio_key], format="audio/wav")
             
             # Optional: Allow viewing script if it exists
             if mod_key in st.session_state:
                 mod_script = st.session_state[mod_key]
                 if mod_script:
                     with st.expander(f"View Script: {mod_script.title}"):
                        for segment in mod_script.segments:
                            with st.chat_message(segment.speaker):
                                st.write(f"**{segment.speaker}:** {segment.text}")
        
        elif mod_key in st.session_state:
             # Script exists but no audio
             mod_script = st.session_state[mod_key]
             if mod_script:
                 st.info(f"Script Generated: {mod_script.title}")
                 with st.expander(f"View Script", expanded=False):
                    for segment in mod_script.segments:
                        with st.chat_message(segment.speaker):
                            st.write(f"**{segment.speaker}:** {segment.text}")

        # Otherwise show Generate button (only if no script)
        if mod_key not in st.session_state:
            if st.button(f"Generate Podcast for Module {i+1}", key=f"btn_mod_{i}"):
             logger.info(f"Generating podcast for Module {i+1}")
             with st.spinner(f"Generating podcast for Module {i+1}..."):
                try:
                    mod_script = generate_module_podcast_script(
                        st.session_state['profile'], module, "gemini-2.5-pro"
                    )
                    st.session_state[mod_key] = mod_script
                    if not mod_script:
                         st.error("Generation returned empty. Please check logs.")
                    autosave_data()
                except Exception as e:
                    st.error(f"An error occurred: {e}")
        
        if mod_key in st.session_state:
            mod_script = st.session_state[mod_key]
            if mod_script:
                with st.expander(f"🎧 Podcast: {mod_script.title}", expanded=True):
                    st.caption(f"Target Audience: {mod_script.target_audience}")
                
                    # Audio Generation for Module Podcast
                    if st.button("▶️ Generate Audio", key=f"btn_audio_mod_{i}"):
                        with st.spinner("Generating audio..."):
                            audio_segments = []
                            for seg in mod_script.segments:
                                logger.info(f"Generating audio for segment {mod_script.segments.index(seg) + 1} / {len(mod_script.segments)} : {seg.text}") 
                                st.write(f"Generating audio for segment {mod_script.segments.index(seg) + 1} / {len(mod_script.segments)} : {seg.text}")
                                segment_audio = generate_audio_segment(seg.text, seg.speaker)
                                if segment_audio:
                                    audio_segments.append(segment_audio)
                            st.session_state[f"audio_mod_{i}"] = assemble_audio(audio_segments)
                            autosave_data()

                    if f"audio_mod_{i}" in st.session_state:
                        st.audio(st.session_state[f"audio_mod_{i}"], format="audio/wav")

                    for segment in mod_script.segments:
                        with st.chat_message(segment.speaker):
                            st.write(f"**{segment.speaker}:** {segment.text}")
        
        # --- Sleepcast Section ---
        st.markdown("#### 🌙 Sleepcast")
        sleep_key = f"sleepcast_{i}"
        
        if st.button(f"Generate Sleepcast for Module {i+1}", key=f"btn_sleep_{i}"):
             logger.info(f"Generating sleepcast for Module {i+1}")
             with st.spinner(f"Generating sleepcast for Module {i+1}..."):
                 try:
                     sleep_script = generate_sleepcast_script(
                         st.session_state['profile'], module, "gemini-2.5-pro"
                     )
                     st.session_state[sleep_key] = sleep_script
                     if not sleep_script:
                         st.error("Sleepcast generation returned empty.")
                     autosave_data()
                 except Exception as e:
                     st.error(f"Error generating sleepcast: {e}")
        
        if sleep_key in st.session_state:
            sleep_script = st.session_state[sleep_key]
            if sleep_script:
                with st.expander(f"🌙 Sleepcast: {sleep_script.title}", expanded=True):
                    st.info(f"🎵 **Suggested Music Prompt:** {sleep_script.music_prompt}")
                    
                with st.expander(f"🌙 Sleepcast: {sleep_script.title}", expanded=True):
                    st.info(f"🎵 **Suggested Music Prompt:** {sleep_script.music_prompt}")
                    
                    if st.button("▶️ Generate & Play Sleepcast", key=f"btn_sleep_mix_{i}"):
                         # 1. Generate Voice (if not already done)
                         if f"audio_sleep_{i}" not in st.session_state:
                             with st.spinner("Generating voice track..."):
                                audio_segments = []
                                for seg in sleep_script.segments:
                                    st.write(f"Synthesizing segment {sleep_script.segments.index(seg) + 1}/{len(sleep_script.segments)}...")
                                    logger.info(f"Generating audio for segment {sleep_script.segments.index(seg) + 1} / {len(sleep_script.segments)} : {seg.text}") 
                                    segment_audio = generate_audio_segment(seg.text, seg.speaker) 
                                    if segment_audio:
                                        audio_segments.append(segment_audio)
                                st.session_state[f"audio_sleep_{i}"] = assemble_audio(audio_segments)
                         
                         # 2. Generate Music (if not already done)
                         if f"music_file_{i}" not in st.session_state:
                             with st.spinner("Composing background music (Lyria)..."):
                                 try:
                                     music_gen = MusicGenerator()
                                     music_path = f"output/music_{i}_{sanitize_filename(module.title)}.wav"
                                     os.makedirs("output", exist_ok=True)
                                     
                                     music_gen.generate_and_save(
                                         prompt=sleep_script.music_prompt,
                                         output_path=music_path,
                                         duration_seconds=30 
                                     )
                                     st.session_state[f"music_file_{i}"] = music_path
                                 except Exception as e:
                                     st.error(f"Music generation failed: {e}")

                         # 3. Mix Audio
                         if f"audio_sleep_{i}" in st.session_state and f"music_file_{i}" in st.session_state:
                             with st.spinner("Mixing audio tracks..."):
                                 voice_bytes = st.session_state[f"audio_sleep_{i}"]
                                 with open(st.session_state[f"music_file_{i}"], 'rb') as f:
                                     music_bytes = f.read()
                                 
                                 mixed_bytes = mix_audio(voice_bytes, music_bytes, music_volume=0.2)
                                 st.session_state[f"mixed_sleep_{i}"] = mixed_bytes
                                 st.session_state[f"show_player_{i}"] = True
                                 autosave_data()

                    # Display Final Player if ready
                    if st.session_state.get(f"show_player_{i}") and f"mixed_sleep_{i}" in st.session_state:
                        st.success("Sleepcast Ready!")
                        st.audio(st.session_state[f"mixed_sleep_{i}"], format="audio/wav")
                        
                        # Option to download
                        st.download_button(
                            label="Download Sleepcast",
                            data=st.session_state[f"mixed_sleep_{i}"],
                            file_name=f"sleepcast_{sanitize_filename(module.title)}.wav",
                            mime="audio/wav",
                            key=f"dl_sleep_{i}"
                        )

                    st.markdown("---")
                    with st.expander("Show Script"):
                        for segment in sleep_script.segments:
                            st.write(f"*{segment.speaker}:* {segment.text}")

        st.markdown("---")

    st.header("Full Program Podcast")
    if st.button("Generate Podcast Script for Full Program", type="primary"):
        logger.info("Generating full program podcast script")
        with st.spinner("Generating podcast script..."):
            podcast_script = generate_podcast_script(
                st.session_state['profile'], st.session_state['tcc_program'], "gemini-2.5-pro"
            )
            st.session_state['podcast_script'] = podcast_script
            autosave_data()

if 'podcast_script' in st.session_state and st.session_state['podcast_script']:
    script = st.session_state['podcast_script']
    st.header(f"Podcast: {script.title}")
    st.caption(f"Target Audience: {script.target_audience}")

    # Audio Generation for Full Podcast
    if st.button("▶️ Generate Audio for Full Podcast", key="btn_audio_full"):
        with st.spinner("Generating audio..."):
            audio_segments = []
            for seg in script.segments:
                segment_audio = generate_audio_segment(seg.text, seg.speaker)
                if segment_audio:
                    audio_segments.append(segment_audio)
            st.session_state["audio_full"] = assemble_audio(audio_segments)
            autosave_data()

    if "audio_full" in st.session_state:
        st.audio(st.session_state["audio_full"], format="audio/wav")

    for segment in script.segments:
        with st.chat_message(segment.speaker):
            st.write(f"**{segment.speaker}:** {segment.text}")
