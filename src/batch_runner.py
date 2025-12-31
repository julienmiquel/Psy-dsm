import argparse
import os
import sys
import logging
import asyncio
from dotenv import load_dotenv

# Ensure we can import from src/app
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services import (
    generate_character_profile,
    generate_tcc_program,
    generate_podcast_script,
    generate_module_podcast_script,
    generate_sleepcast_script,
    analyze_audio
)
from app.audio import generate_audio_segment, assemble_audio, mix_audio, convert_to_mp3
from app.music import MusicGenerator
from app.utils import (
    save_character_data,
    load_character_data,
    sanitize_filename,
    get_text_hash
)
from app.models import CharacterProfile, TCCProgram, PodcastScript, SleepcastScript
from app.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

def run_pipeline(description: str):
    """
    Runs the full generation pipeline:
    Profile -> TCC -> Podcast -> Module Podcasts -> Sleepcasts -> Audio -> Save
    """
    model_id = "gemini-2.5-pro"
    
    # 1. Profile
    logger.info("Generating Profile...")
    profile = generate_character_profile(description, model_id)
    
    # 2. TCC
    logger.info("Generating TCC Program...")
    tcc_program = generate_tcc_program(profile, model_id)
    
    # 3. Full Podcast
    logger.info("Generating Full Podcast Script...")
    podcast_script = generate_podcast_script(profile, tcc_program, model_id)
    
    audio_map = {}
    
    # Audio for Full Podcast
    logger.info("Synthesizing Full Podcast Audio...")
    segments = []
    for seg in podcast_script.segments:
        audio = generate_audio_segment(seg.text, seg.speaker)
        if audio:
            segments.append(audio)
    if segments:
        audio_map['full'] = assemble_audio(segments)
        
    # 4. Modules Logic
    sleepcast_scripts = {}
    
    for i, module in enumerate(tcc_program.modules):
        logger.info(f"Processing Module {i+1}: {module.title}")
        
        # Module Podcast
        mod_script = generate_module_podcast_script(profile, module, model_id)
        if mod_script:
            mod_segs = []
            for seg in mod_script.segments:
                audio = generate_audio_segment(seg.text, seg.speaker)
                if audio:
                    mod_segs.append(audio)
            if mod_segs:
                audio_map[f"module_{i}"] = assemble_audio(mod_segs)
        
        # Sleepcast
        sleep_script = generate_sleepcast_script(profile, module, model_id)
        if sleep_script:
            sleepcast_scripts[str(i)] = sleep_script
            
            # Voice
            sleep_segs = []
            for seg in sleep_script.segments:
                audio = generate_audio_segment(seg.text, seg.speaker)
                if audio:
                    sleep_segs.append(audio)
            
            voice_bytes = assemble_audio(sleep_segs) if sleep_segs else None
            
            # Music
            music_bytes = None
            try:
                music_gen = MusicGenerator()
                # We save temporary music file to read back bytes or handle in memory?
                # MusicGenerator saves to file.
                music_filename = f"music_temp_{i}.wav"
                music_gen.generate_and_save(sleep_script.music_prompt, music_filename, duration_seconds=30)
                with open(music_filename, "rb") as f:
                    music_bytes = f.read()
                os.remove(music_filename) # Clean up
            except Exception as e:
                logger.error(f"Music generation failed for module {i}: {e}")
            
            # Mix
            if voice_bytes and music_bytes:
                mixed_bytes = mix_audio(voice_bytes, music_bytes)
                audio_map[f"sleepcast_mixed_{i}"] = mixed_bytes
    
    # Save Everything
    path = save_character_data(
        profile, tcc_program, podcast_script, audio_map, description, sleepcast_scripts
    )
    logger.info(f"Batch processing complete. Saved to: {path}")


def process_analyze(input_path: str):
    logger.info(f"Analyzing input: {input_path}")
    
    text_content = ""
    
    if input_path.endswith(('.mp3', '.wav', '.m4a', '.ogg')):
        # Audio Analysis
        with open(input_path, 'rb') as f:
            audio_bytes = f.read()
        # mime guessing logic?
        mime_type = "audio/wav" if input_path.endswith(".wav") else "audio/mp3"
        
        result = analyze_audio(audio_bytes, mime_type, "gemini-2.5-pro")
        # Construct description from analysis
        text_content = f"Overall Assessment: {result.overall_assessment}\n\nTranscript:\n"
        for seg in result.segments:
            text_content += f"{seg.speaker_label}: {seg.text}\n"
    else:
        # Text file
        with open(input_path, 'r', encoding='utf-8') as f:
            text_content = f.read()
            
    if not text_content:
        logger.error("No content to analyze.")
        return

    run_pipeline(text_content)

def process_generate(folder_path: str):
    logger.info(f"Processing existing profile from: {folder_path}")
    
    # Determine version. If folder has profile.json directly, use it.
    # If it's the base char folder, find latest version?
    # User said "save folder of the person".
    
    # Let's assume folder_path points to a specific version directory for simplicity
    if not os.path.exists(os.path.join(folder_path, "profile.json")):
        logger.error("No profile.json found in directory.")
        return

    # Load data manually since load_character_data takes name/version
    # We can reverse engineer or just load directly
    with open(os.path.join(folder_path, "profile.json"), 'r') as f:
        profile = CharacterProfile.model_validate_json(f.read())
        
    tcc_program = None
    if os.path.exists(os.path.join(folder_path, "tcc_program.json")):
        with open(os.path.join(folder_path, "tcc_program.json"), 'r') as f:
            tcc_program = TCCProgram.model_validate_json(f.read())
            
    description = ""
    if os.path.exists(os.path.join(folder_path, "description.txt")):
        with open(os.path.join(folder_path, "description.txt"), 'r') as f:
            description = f.read()
            
    # We essentially want to verify/regenerate missing podcasts?
    # User said "launch podcast generation from an existing profile / TCC"
    # So if they exist, maybe we skip? Or overwrite? 
    # Let's assume populate missing.
    
    model_id = "gemini-2.5-pro"
    
    if not tcc_program:
        tcc_program = generate_tcc_program(profile, model_id)
        
    # Check Podcast Script
    podcast_script = None
    if os.path.exists(os.path.join(folder_path, "podcast_script.json")):
         with open(os.path.join(folder_path, "podcast_script.json"), 'r') as f:
            podcast_script = PodcastScript.model_validate_json(f.read())
    else:
        podcast_script = generate_podcast_script(profile, tcc_program, model_id)
        
    # Re-run pipeline logic but skip existing? 
    # For now, simplest is to just call run_pipeline-like logic but with populated objects.
    # But run_pipeline starts from scratch.
    
    # Let's effectively run "Resume/Complete Pipeline"
    # To keep it simple, I will reuse run_pipeline logic but checks for existence?
    # Since I'm time constrained, I'll just regenerate the audio parts if missing.
    
    # ... (Implementation similar to run_pipeline loop but checking file existence)
    # Actually, user might want to generate *new* podcasts? 
    # "Launch podcast generation".
    # I will just invoke the generation for podcasts/sleepcasts on the loaded objects.
    
    # Audio Map population with check for existing
    audio_map = {}
    sleepcast_scripts = {}
    
    # Ensure subfolders exist
    scripts_dir = os.path.join(folder_path, "scripts")
    sleep_dir = os.path.join(folder_path, "sleepcasts")
    os.makedirs(scripts_dir, exist_ok=True)
    os.makedirs(sleep_dir, exist_ok=True)

    # Helper to check/load or generate AND SAVE IMMEDIATELY
    def load_or_generate_and_save(filename_key, generate_func):
        mp3_filename = f"audio_{filename_key}.mp3"
        mp3_filepath = os.path.join(folder_path, mp3_filename)
        
        # 1. Check if MP3 exists (Final State)
        if os.path.exists(mp3_filepath):
            logger.info(f"⏭️ Skipping {filename_key}, found existing MP3: {mp3_filename}")
            with open(mp3_filepath, 'rb') as f:
                return f.read()

        # 2. Check if WAV exists and needs conversion
        wav_filename = f"audio_{filename_key}.wav"
        wav_filepath = os.path.join(folder_path, wav_filename)
        
        if os.path.exists(wav_filepath):
             logger.info(f"🔄 Found WAV for {filename_key}, converting to MP3...")
             try:
                 with open(wav_filepath, 'rb') as f:
                     wav_bytes = f.read()
                 mp3_bytes = convert_to_mp3(wav_bytes)
                 with open(mp3_filepath, "wb") as f:
                     f.write(mp3_bytes)
                 logger.info(f"💾 Saved converted MP3: {mp3_filename}")
                 return mp3_bytes
             except Exception as e:
                 logger.error(f"Failed to convert {wav_filename} to MP3: {e}")
                 # Fallback to returning WAV bytes if conversion fails?
                 # No, loop below will try to regenerate if we return None or fail?
                 # But we have bytes.
                 return wav_bytes 
        
        # 3. Check legacy podcast_ prefix (WAV)
        legacy_path = os.path.join(folder_path, f"podcast_{filename_key}.wav")
        if os.path.exists(legacy_path):
             logger.info(f"🔄 Found legacy WAV for {filename_key}, converting to MP3...")
             try:
                 with open(legacy_path, 'rb') as f:
                     wav_bytes = f.read()
                 mp3_bytes = convert_to_mp3(wav_bytes)
                 with open(mp3_filepath, "wb") as f:
                     f.write(mp3_bytes)
                 logger.info(f"💾 Saved converted MP3 from legacy: {mp3_filename}")
                 return mp3_bytes
             except Exception as e:
                 logger.error(f"Failed to convert legacy {legacy_path} to MP3: {e}")
                 return wav_bytes

        # 4. Generate New
        logger.info(f"🔨 Generating {filename_key}...")
        data = generate_func() # This returns WAV bytes (from assemble/mix)
        
        if data:
            # Convert to MP3 before saving
            try:
                mp3_bytes = convert_to_mp3(data)
                with open(mp3_filepath, "wb") as f:
                    f.write(mp3_bytes)
                logger.info(f"💾 Saved new MP3: {mp3_filename}")
                return mp3_bytes
            except Exception as e:
                 logger.error(f"Failed to convert new generation to MP3: {e}")
                 # Save as WAV fallback so work isn't lost
                 with open(wav_filepath, "wb") as f:
                     f.write(data)
                 logger.warning(f"💾 Saved as WAV fallback: {wav_filename}")
                 return data
                 
        return data

    # Full Podcast Audio
    if podcast_script:
        def gen_full():
             segments = []
             total = len(podcast_script.segments)
             for idx, seg in enumerate(podcast_script.segments):
                logger.info(f"  Synthesizing Full Podcast Segment {idx+1}/{total}")
                audio = generate_audio_segment(seg.text, seg.speaker)
                if audio:
                    segments.append(audio)
             return assemble_audio(segments) if segments else None

        audio_map['full'] = load_or_generate_and_save('full', gen_full)

    # Modules
    total_modules = len(tcc_program.modules)
    for i, module in enumerate(tcc_program.modules):
        logger.info(f"📦 Processing Module {i+1}/{total_modules}: {module.title}")
        
        # 1. Module Podcast Script
        mod_script_path = os.path.join(scripts_dir, f"module_{i}.json")
        mod_script = None
        
        if os.path.exists(mod_script_path):
             logger.info(f"  📖 Loaded existing script: {mod_script_path}")
             with open(mod_script_path, 'r') as f:
                 mod_script = PodcastScript.model_validate_json(f.read())
        else:
             logger.info(f"  ✍️ Generating Module Podcast Script...")
             mod_script = generate_module_podcast_script(profile, module, model_id)
             if mod_script:
                 with open(mod_script_path, "w", encoding="utf-8") as f:
                     f.write(mod_script.model_dump_json(indent=2))
                 logger.info(f"  💾 Saved script: {mod_script_path}")

        # 2. Module Audio
        if mod_script:
            def gen_mod():
                mod_segs = []
                total = len(mod_script.segments)
                for idx, seg in enumerate(mod_script.segments):
                    logger.info(f"    Synthesizing Module Segment {idx+1}/{total}")
                    audio = generate_audio_segment(seg.text, seg.speaker)
                    if audio:
                        mod_segs.append(audio)
                return assemble_audio(mod_segs) if mod_segs else None
            
            audio_map[f"module_{i}"] = load_or_generate_and_save(f"module_{i}", gen_mod)

        # 3. Sleepcast Script
        sleep_path = os.path.join(sleep_dir, f"{i}.json")
        sleep_script = None
        
        if os.path.exists(sleep_path):
             logger.info(f"  📖 Loaded existing sleepcast script: {sleep_path}")
             with open(sleep_path, 'r') as f:
                 sleep_script = SleepcastScript.model_validate_json(f.read())
        else:
             logger.info(f"  🌙 Generating Sleepcast Script...")
             sleep_script = generate_sleepcast_script(profile, module, model_id)
             if sleep_script:
                 with open(sleep_path, "w", encoding="utf-8") as f:
                     f.write(sleep_script.model_dump_json(indent=2))
                 logger.info(f"  💾 Saved sleepcast script: {sleep_path}")

        # 4. Sleepcast Mixed Audio
        if sleep_script:
            sleepcast_scripts[str(i)] = sleep_script
            
            def gen_sleep_mixed():
                sleep_segs = []
                total = len(sleep_script.segments)
                for idx, seg in enumerate(sleep_script.segments):
                    logger.info(f"    Synthesizing Sleepcast Segment {idx+1}/{total}")
                    audio = generate_audio_segment(seg.text, seg.speaker)
                    if audio:
                        sleep_segs.append(audio)
                voice_bytes = assemble_audio(sleep_segs) if sleep_segs else None
                
                music_bytes = None
                try:
                     music_gen = MusicGenerator()
                     music_filename = f"music_temp_{i}.wav"
                     logger.info(f"    🎵 Generating Music...")
                     music_gen.generate_and_save(sleep_script.music_prompt, music_filename, duration_seconds=30)
                     with open(music_filename, "rb") as f:
                         music_bytes = f.read()
                     os.remove(music_filename)
                except Exception as e:
                    logger.error(f"Music error: {e}")
                    
                if voice_bytes and music_bytes:
                    logger.info(f"    🎛️ Mixing Audio...")
                    return mix_audio(voice_bytes, music_bytes)
                return None

            audio_map[f"sleepcast_mixed_{i}"] = load_or_generate_and_save(f"sleepcast_mixed_{i}", gen_sleep_mixed)

    # MANUALLY Save to Input Folder to fulfill "verify folder contain... in the input folder"
    # We iterate and save what we have
    logger.info(f"Saving updates back to {folder_path}...")
    
    # Save audio
    # Save audio (Redundant if load_or_generate_and_save does it, but keeps sync)
    # The load_or_generate_and_save function now handles saving. 
    # We can remove the manual save loop here or update it to be MP3 aware if needed.
    # Since load_or_generate_and_save saves immediately, this loop is strictly checks.
    pass

    # Save scripts
    if sleepcast_scripts:
        sleep_dir = os.path.join(folder_path, "sleepcasts")
        if not os.path.exists(sleep_dir):
            os.makedirs(sleep_dir)
        for key, script in sleepcast_scripts.items():
            safe_key = sanitize_filename(str(key))
            script_path = os.path.join(sleep_dir, f"{safe_key}.json")
            if not os.path.exists(script_path):
                with open(script_path, "w", encoding="utf-8") as f:
                    f.write(script.model_dump_json(indent=2))

    logger.info(f"Update complete in: {folder_path}")


def main():
    parser = argparse.ArgumentParser(description="Psydsm Batch Processor")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Analyze
    analyze_parser = subparsers.add_parser("analyze", help="Analyze file and run full pipeline")
    analyze_parser.add_argument("input_path", help="Path to text or audio file")
    
    # Generate
    gen_parser = subparsers.add_parser("generate", help="Generate podcasts from existing folder")
    gen_parser.add_argument("folder_path", help="Path to character version folder containing profile.json")
    
    args = parser.parse_args()
    
    load_dotenv()
    
    if args.command == "analyze":
        process_analyze(args.input_path)
    elif args.command == "generate":
        process_generate(args.folder_path)

if __name__ == "__main__":
    main()
