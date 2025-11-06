"""
This module provides a local file system implementation of the database service.
It saves, retrieves, and updates profiles by reading/writing JSON files.
"""

import json
import os
from pathlib import Path

from app.models import CharacterProfile, TCCProgram
from app.chc_models import CHCModel
from app.user_models import UserProfile
from app import character_index_service as index_service

LOCAL_DB_PATH = Path("local_db")
PROFILES_PATH = LOCAL_DB_PATH / "profiles"
CHC_PROFILES_PATH = LOCAL_DB_PATH / "chc"
USERS_PATH = LOCAL_DB_PATH / "users"
TCC_PROGRAMS_PATH = LOCAL_DB_PATH / "tcc_programs"

def _init_db():
    """Creates the necessary directories for the local file store."""
    PROFILES_PATH.mkdir(parents=True, exist_ok=True)
    USERS_PATH.mkdir(parents=True, exist_ok=True)
    TCC_PROGRAMS_PATH.mkdir(parents=True, exist_ok=True)
    CHC_PROFILES_PATH.mkdir(parents=True, exist_ok=True)

def save_profile(profile: CharacterProfile, user_id: str):
    """Saves a character profile to the local file system."""
    _init_db()
    profile.user_id = user_id

    index_service.add_character_to_index(profile.character_id, profile.character_name)

    profile_data = profile.model_dump(exclude={"character_name"})
    profile_path = PROFILES_PATH / f"{profile.character_id}.json"
    with open(profile_path, "w", encoding="utf-8") as f:
        json.dump(profile_data, f, indent=2)
    
    index_service.add_profile_to_character(profile.character_id, "character", str(profile_path))

def save_chc_profile(profile: CHCModel, user_id: str):
    """Saves a CHC profile to the local file system."""
    _init_db()
    profile.user_id = user_id

    index_service.add_character_to_index(profile.character_id, profile.character_name)

    profile_data = profile.model_dump()
    profile_path = CHC_PROFILES_PATH / f"{profile.character_id}.json"
    
    os.makedirs(CHC_PROFILES_PATH, exist_ok=True)

    with open(profile_path, "w", encoding="utf-8") as f:
        json.dump(profile_data, f, indent=2)

    index_service.add_profile_to_character(profile.character_id, "chc", str(profile_path))

def update_profile_with_tcc_program(character_id: str, tcc_program: TCCProgram):
    """Saves a TCC program to a separate file."""
    _init_db()
    tcc_program_path = TCC_PROGRAMS_PATH / f"{character_id}.json"
    with open(tcc_program_path, "w", encoding="utf-8") as f:
        json.dump(tcc_program.model_dump(), f, indent=2)
    
    index_service.add_profile_to_character(character_id, "tcc", str(tcc_program_path))



def get_user_characters(user_id: str):
    """Retrieves all characters for a given user from the local file system."""
    _init_db()
    all_characters = index_service.get_all_characters_from_index()
    user_characters = []
    
    for char in all_characters:
        character_id = char["character_id"]
        character_data = index_service.get_character_data(character_id)
        if not character_data:
            continue

        profile_path_str = character_data["profiles"].get("character")
        if profile_path_str and Path(profile_path_str).exists():
            with open(profile_path_str, "r", encoding="utf-8") as f:
                profile_data = json.load(f)
            if profile_data.get("user_id") == user_id:
                user_characters.append(char)
                continue

        chc_profile_path_str = character_data["profiles"].get("chc")
        if chc_profile_path_str and Path(chc_profile_path_str).exists():
            with open(chc_profile_path_str, "r", encoding="utf-8") as f:
                chc_profile_data = json.load(f)
            if chc_profile_data.get("user_id") == user_id:
                user_characters.append(char)

    return user_characters

def get_character_profile(character_id: str):
    """Retrieves a CharacterProfile for a given character_id."""
    _init_db()
    character_data = index_service.get_character_data(character_id)
    if not character_data:
        return None

    profile_path_str = character_data["profiles"].get("character")
    if not profile_path_str or not Path(profile_path_str).exists():
        return None

    with open(profile_path_str, "r", encoding="utf-8") as f:
        profile_data = json.load(f)

    profile_data["character_name"] = character_data["pii"]["character_name"]

    tcc_path_str = character_data["profiles"].get("tcc")
    if tcc_path_str and Path(tcc_path_str).exists():
        with open(tcc_path_str, "r", encoding="utf-8") as f:
            tcc_program_data = json.load(f)
        profile_data["tcc_program"] = tcc_program_data

    return CharacterProfile(**profile_data)

def get_chc_profile(character_id: str):
    """Retrieves a CHCProfile for a given character_id."""
    _init_db()
    character_data = index_service.get_character_data(character_id)
    if not character_data:
        return None

    profile_path_str = character_data["profiles"].get("chc")
    if not profile_path_str or not Path(profile_path_str).exists():
        return None

    with open(profile_path_str, "r", encoding="utf-8") as f:
        profile_data = json.load(f)
    return CHCModel(**profile_data)

def save_user_profile(user_profile: UserProfile):
    """Saves a user profile to the local file system."""
    _init_db()
    profile_path = USERS_PATH / f"{user_profile.user_id}.json"
    with open(profile_path, "w", encoding="utf-8") as f:
        json.dump(user_profile.model_dump(), f, indent=2)

def get_user_profile(user_id: str):
    """Retrieves a user profile from the local file system."""
    _init_db()
    profile_path = USERS_PATH / f"{user_id}.json"
    if not profile_path.exists():
        return None

    with open(profile_path, "r", encoding="utf-8") as f:
        profile_data = json.load(f)
    return UserProfile(**profile_data)

def get_user_all_profiles(user_id: str) -> list:
    """Retrieves all profiles for a given user from the local file system."""
    _init_db()
    all_profiles = []
    
    all_characters_from_index = index_service.get_all_characters_from_index()

    for char_entry in all_characters_from_index:
        character_id = char_entry["character_id"]
        character_data = index_service.get_character_data(character_id)

        if not character_data:
            continue

        profile_path_str = character_data["profiles"].get("character")
        if profile_path_str and Path(profile_path_str).exists():
            with open(profile_path_str, "r", encoding="utf-8") as f:
                profile_data = json.load(f)
            if profile_data.get("user_id") == user_id:
                all_profiles.append({
                    "character_id": character_id,
                    "character_name": character_data["pii"]["character_name"],
                    "profile_type": "RIASEC",
                    "profile_datetime": profile_data.get("profile_datetime")
                })

        chc_profile_path_str = character_data["profiles"].get("chc")
        if chc_profile_path_str and Path(chc_profile_path_str).exists():
            with open(chc_profile_path_str, "r", encoding="utf-8") as f:
                chc_profile_data = json.load(f)
            if chc_profile_data.get("user_id") == user_id:
                all_profiles.append({
                    "character_id": character_id,
                    "character_name": chc_profile_data.get("character_name"),
                    "profile_type": "CHC",
                    "profile_datetime": chc_profile_data.get("profile_datetime")
                })
    
    all_profiles.sort(key=lambda x: x.get("profile_datetime", ""), reverse=True)
    return all_profiles
