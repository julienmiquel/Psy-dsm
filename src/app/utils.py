"""
Utility functions for the application.
"""
import os
import re
import json
import logging
import datetime
import base64
import hashlib
from typing import List, Optional, Dict, Any
from app.models import CharacterProfile, TCCProgram, PodcastScript, SleepcastScript
from app.audio import convert_to_mp3

logger = logging.getLogger(__name__)

def sanitize_filename(name: str) -> str:
    """
    Sanitizes a string to be used as a valid filename.
    Replaces non-alphanumeric characters with underscores.
    """
    # Remove accents/diacritics (optional, but good for compatibility)
    # For simplicity, just keep alphanumeric, spaces, dashes, underscores
    s = re.sub(r'[^a-zA-Z0-9_\- ]', '', name)
    # Replace spaces with underscores
    s = s.replace(' ', '_')
    # Limit length
    return s[:50]

def get_text_hash(text: str) -> str:
    """Returns the MD5 hash of the given text."""
    return hashlib.md5(text.encode("utf-8")).hexdigest()

def save_character_data(
    profile: Optional[CharacterProfile],
    tcc_program: Optional[TCCProgram],
    podcast_script: Optional[PodcastScript],
    audio_data_map: dict,
    description: str = "",
    sleepcast_scripts: Optional[Dict[str, SleepcastScript]] = None,
    overwrite_dir: Optional[str] = None,
    module_scripts: Optional[Dict[str, PodcastScript]] = None
) -> str:
    """
    Saves character data (profile, TCC, audio) to a dedicated directory.
    Uses hash of description if available for folder stability.
    
    Args:
        profile: The character profile.
        tcc_program: The generated TCC program.
        podcast_script: The generated podcast script (full).
        audio_data_map: A dictionary mapping identifiers to audio bytes.
        audio_data_map: A dictionary mapping identifiers to audio bytes.
        description: The original character description text.
        sleepcast_scripts: Dictionary of module index to SleepcastScript.
        module_scripts: Dictionary of module index to PodcastScript.
        
    Returns:
        str: The path to the saved directory.
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    base_dir = "output"
    
    if overwrite_dir and os.path.exists(overwrite_dir):
        save_dir = overwrite_dir
    else:
        # Determine directory structure
        if description:
            # Use Hash folder for consistency/autosave
            desc_hash = get_text_hash(description)
            # Structure: output/{HASH}/{Timestamp}/
            save_dir = os.path.join(base_dir, desc_hash, timestamp)
        elif profile and profile.character_name:
            # Fallback to Name based if no description provided
            char_name = sanitize_filename(profile.character_name)
            save_dir = os.path.join(base_dir, char_name, timestamp)
        else:
            # Fallback
            save_dir = os.path.join(base_dir, "Unknown", timestamp)

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        
    # Save Description
    if description:
        with open(os.path.join(save_dir, "description.txt"), "w", encoding="utf-8") as f:
            f.write(description)

    # Save Profile
    if profile:
        with open(os.path.join(save_dir, "profile.json"), "w", encoding="utf-8") as f:
            f.write(profile.model_dump_json(indent=2))
        
    # Save TCC Program
    if tcc_program:
        with open(os.path.join(save_dir, "tcc_program.json"), "w", encoding="utf-8") as f:
            f.write(tcc_program.model_dump_json(indent=2))

    # Save Podcast Script (Full)
    if podcast_script:
        with open(os.path.join(save_dir, "podcast_script.json"), "w", encoding="utf-8") as f:
            f.write(podcast_script.model_dump_json(indent=2))

    # Save Sleepcast Scripts
    if sleepcast_scripts:
        sleep_dir = os.path.join(save_dir, "sleepcasts")
        if not os.path.exists(sleep_dir):
            os.makedirs(sleep_dir)
        for key, script in sleepcast_scripts.items():
            # key is likely "sleepcast_0" or just "0"
            safe_key = sanitize_filename(str(key))
            with open(os.path.join(sleep_dir, f"{safe_key}.json"), "w", encoding="utf-8") as f:
                f.write(script.model_dump_json(indent=2))

    # Save Module Scripts
    if module_scripts:
        scripts_dir = os.path.join(save_dir, "scripts")
        if not os.path.exists(scripts_dir):
            os.makedirs(scripts_dir)
        for key, script in module_scripts.items():
            # key is likely "0", "1", etc.
            # We want to save as "module_{key}.json" to match batch runner format?
            # Batch runner saves as: script_path = os.path.join(scripts_dir, f"module_{i}.json")
            # So if key is '0', filename should be 'module_0.json'
            safe_key = sanitize_filename(str(key))
            filename = f"module_{safe_key}.json"
            with open(os.path.join(scripts_dir, filename), "w", encoding="utf-8") as f:
                f.write(script.model_dump_json(indent=2))

    # Save Audio Files
    for key, audio_bytes in audio_data_map.items():
        if audio_bytes:
            # Convert to MP3
            try:
                mp3_bytes = convert_to_mp3(audio_bytes)
                filename = f"audio_{key}.mp3"
                filepath = os.path.join(save_dir, filename)
                with open(filepath, "wb") as f:
                    f.write(mp3_bytes)
            except Exception as e:
                logger.error(f"Failed to save audio {key} as MP3: {e}")
                # Fallback? Or just log. User requested "All audio files must be generated in mp3"
                # If conversion fails, maybe save as WAV as backup to not lose data?
                # But request says "All ... mp3". Let's stick to error logging and maybe simple write for debug.
                # Actually, better to save WAV as backup if MP3 fails so data isn't lost.
                filename = f"audio_{key}.wav"
                filepath = os.path.join(save_dir, filename)
                with open(filepath, "wb") as f:
                    f.write(audio_bytes)

    
    logger.info(f"Saved data to {save_dir}")
    return os.path.abspath(save_dir)

def get_saved_characters(base_dir: str = "output") -> Dict[str, str]:
    """
    Returns a dictionary of {character_name_or_label: hash_folder_name} for display.
    Scans the latest version in each folder to find the name.
    """
    if not os.path.exists(base_dir):
        return {}
        
    results = {}
    
    for d in os.listdir(base_dir):
        # d is likely a hash or name
        path = os.path.join(base_dir, d)
        if os.path.isdir(path):
            # Find latest version inside
            versions = sorted([v for v in os.listdir(path) if os.path.isdir(os.path.join(path, v))], reverse=True)
            if versions:
                latest_v = versions[0]
                # Check for profile.json or name metadata
                profile_path = os.path.join(path, latest_v, "profile.json")
                if os.path.exists(profile_path):
                    try:
                        # Quick read of name
                        with open(profile_path, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            char_name = data.get("character_name", d)
                            results[f"{char_name} ({d[:6]}...)"] = d
                    except:
                        results[d] = d
                else:
                    results[d] = d
            else:
                # No versions, maybe empty folder
                pass
                
    return results

def get_character_versions(character_name: str, base_dir: str = "output") -> List[str]:
    """Returns a sorted list of versions (timestamps) for a character."""
    char_dir = os.path.join(base_dir, character_name)
    if not os.path.exists(char_dir):
        return []
    versions = [d for d in os.listdir(char_dir) if os.path.isdir(os.path.join(char_dir, d))]
    # Sort reverse to get latest first
    return sorted(versions, reverse=True)

def load_character_data(character_name: str, version: str, base_dir: str = "output") -> dict:
    """
    Loads all data for a specific character version.
    Returns a dictionary containing the loaded objects and raw data.
    """
    version_dir = os.path.join(base_dir, character_name, version)
    if not os.path.exists(version_dir):
        return {}
    
    data = {}
    
    # Load Description
    desc_path = os.path.join(version_dir, "description.txt")
    if os.path.exists(desc_path):
        with open(desc_path, "r", encoding="utf-8") as f:
            data['description'] = f.read()

    # Load Profile
    prof_path = os.path.join(version_dir, "profile.json")
    if os.path.exists(prof_path):
        with open(prof_path, "r", encoding="utf-8") as f:
            data['profile'] = CharacterProfile.model_validate_json(f.read())
            
    # Load TCC Program
    tcc_path = os.path.join(version_dir, "tcc_program.json")
    if os.path.exists(tcc_path):
        with open(tcc_path, "r", encoding="utf-8") as f:
            data['tcc_program'] = TCCProgram.model_validate_json(f.read())
            
    # Load Podcast Script
    script_path = os.path.join(version_dir, "podcast_script.json")
    if os.path.exists(script_path):
        with open(script_path, "r", encoding="utf-8") as f:
            data['podcast_script'] = PodcastScript.model_validate_json(f.read())

    # Load Module Scripts
    module_scripts = {}
    scripts_dir = os.path.join(version_dir, "scripts")
    if os.path.exists(scripts_dir):
        for filename in os.listdir(scripts_dir):
            if filename.startswith("module_") and filename.endswith(".json"):
                 # Extract key: module_0.json -> 0
                 key = filename.replace("module_", "").replace(".json", "")
                 with open(os.path.join(scripts_dir, filename), "r", encoding="utf-8") as f:
                     try:
                        module_scripts[key] = PodcastScript.model_validate_json(f.read())
                     except Exception as e:
                        logger.error(f"Failed to load module script {filename}: {e}")
    data['module_scripts'] = module_scripts

    # Load Sleepcast Scripts
    sleepcast_scripts = {}
    sleep_dir = os.path.join(version_dir, "sleepcasts")
    if os.path.exists(sleep_dir):
         for filename in os.listdir(sleep_dir):
             if filename.endswith(".json"):
                 key = filename.replace(".json", "")
                 with open(os.path.join(sleep_dir, filename), "r", encoding="utf-8") as f:
                     try:
                        sleepcast_scripts[key] = SleepcastScript.model_validate_json(f.read())
                     except Exception as e:
                        logger.error(f"Failed to load sleepcast script {filename}: {e}")
    data['sleepcast_scripts'] = sleepcast_scripts
            
    # Load Audio Files
    # Scan directory for .wav files starting with audio_ or podcast_
    audio_map = {}
    # Load Audio Files
    # Scan directory for .mp3 (prefer) or .wav files
    audio_map = {}
    for filename in os.listdir(version_dir):
        if filename.endswith(".mp3") or filename.endswith(".wav"):
             if filename.startswith("audio_"):
                 key = filename.replace("audio_", "").replace(".mp3", "").replace(".wav", "")
                 # If we already loaded this key (e.g. mp3 loaded, now seeing wav), skip or prioritize?
                 # If we see mp3 first, keep it. 
                 if key in audio_map and filename.endswith(".wav"):
                     continue # Prefer MP3
                     
                 audio_map[key] = None # Flag existence? No, load bytes.
             elif filename.startswith("podcast_"):
                  key = filename.replace("podcast_", "").replace(".mp3", "").replace(".wav", "")
             else:
                  continue
             
             with open(os.path.join(version_dir, filename), "rb") as f:
                audio_map[key] = f.read()
    data['audio_map'] = audio_map
    
    return data

def save_base64_audio(base64_data: str, output_path: str) -> None:
    """
    Decodes base64 audio data and saves it to a file.
    """
    try:
        decoded_data = base64.b64decode(base64_data)
        with open(output_path, "wb") as f:
            f.write(decoded_data)
        logger.info(f"Saved base64 audio to {output_path}")
    except Exception as e:
        logger.error(f"Failed to save base64 audio: {e}")
