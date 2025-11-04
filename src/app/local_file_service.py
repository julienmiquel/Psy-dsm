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

    # Add character to index
    index_service.add_character_to_index(profile.character_id, profile.character_name)

    # Store non-PII data
    profile_data = profile.model_dump(exclude={"character_name"})
    profile_path = PROFILES_PATH / f"{profile.character_id}.json"
    with open(profile_path, "w") as f:
        json.dump(profile_data, f, indent=2)
    
    # Add profile to index
    index_service.add_profile_to_character(profile.character_id, "character", str(profile_path))

def save_chc_profile(profile: CHCModel, user_id: str):
    """Saves a CHC profile to the local file system."""
    _init_db()
    profile.user_id = user_id

    # Add character to index
    index_service.add_character_to_index(profile.character_id, profile.character_name)

    # Store CHC profile data
    profile_data = profile.model_dump()
    profile_path = CHC_PROFILES_PATH / f"{profile.character_id}.json"
    
    # Explicitly create the directory
    os.makedirs(CHC_PROFILES_PATH, exist_ok=True)

    with open(profile_path, "w") as f:
        json.dump(profile_data, f, indent=2)

    # Add profile to index
    index_service.add_profile_to_character(profile.character_id, "chc", str(profile_path))

def update_profile_with_tcc_program(character_id: str, tcc_program: TCCProgram):
    """Saves a TCC program to a separate file."""
    _init_db()
    tcc_program_path = TCC_PROGRAMS_PATH / f"{character_id}.json"
    with open(tcc_program_path, "w") as f:
        json.dump(tcc_program.model_dump(), f, indent=2)
    
    # Add profile to index
    index_service.add_profile_to_character(character_id, "tcc", str(tcc_program_path))



def get_user_characters(user_id: str):
    """Retrieves all characters for a given user from the local file system."""
    _init_db()
    all_characters = index_service.get_all_characters_from_index()
    user_characters = []
    
    # This is inefficient, but necessary with the current data model.
    # I need to read each profile to check the user_id.
    for char in all_characters:
        character_id = char["character_id"]
        character_data = index_service.get_character_data(character_id)
        if character_data:
            profile_path_str = character_data["profiles"].get("character")
            if profile_path_str:
                profile_path = Path(profile_path_str)
                if profile_path.exists():
                    with open(profile_path, "r") as f:
                        profile_data = json.load(f)
                    if profile_data.get("user_id") == user_id:
                        user_characters.append(char)
                        continue # Move to next character
            
            # If no character profile, check CHC profile
            chc_profile_path_str = character_data["profiles"].get("chc")
            if chc_profile_path_str:
                chc_profile_path = Path(chc_profile_path_str)
                if chc_profile_path.exists():
                    with open(chc_profile_path, "r") as f:
                        chc_profile_data = json.load(f)
                    if chc_profile_data.get("user_id") == user_id:
                        user_characters.append(char)

    return user_characters

def get_character_profile(character_id: str):
    """Retrieves a CharacterProfile for a given character_id."""
    _init_db()
    character_data = index_service.get_character_data(character_id)
    if character_data:
        profile_path_str = character_data["profiles"].get("character")
        if profile_path_str:
            profile_path = Path(profile_path_str)
            if profile_path.exists():
                with open(profile_path, "r") as f:
                    profile_data = json.load(f)
                
                profile_data["character_name"] = character_data["pii"]["character_name"]

                # Load TCC program
                tcc_path_str = character_data["profiles"].get("tcc")
                if tcc_path_str:
                    tcc_path = Path(tcc_path_str)
                    if tcc_path.exists():
                        with open(tcc_path, "r") as f:
                            tcc_program_data = json.load(f)
                        profile_data["tcc_program"] = tcc_program_data

                return CharacterProfile(**profile_data)
    return None

def get_chc_profile(character_id: str):
    """Retrieves a CHCProfile for a given character_id."""
    _init_db()
    character_data = index_service.get_character_data(character_id)
    if character_data:
        profile_path_str = character_data["profiles"].get("chc")
        if profile_path_str:
            profile_path = Path(profile_path_str)
            if profile_path.exists():
                with open(profile_path, "r") as f:
                    profile_data = json.load(f)
                return CHCModel(**profile_data)
    return None

def save_user_profile(user_profile: UserProfile):
    """Saves a user profile to the local file system."""
    _init_db()
    profile_path = USERS_PATH / f"{user_profile.user_id}.json"
    with open(profile_path, "w") as f:
        json.dump(user_profile.model_dump(), f, indent=2)

def get_user_profile(user_id: str):
    """Retrieves a user profile from the local file system."""
    _init_db()
    profile_path = USERS_PATH / f"{user_id}.json"
    if profile_path.exists():
        with open(profile_path, "r") as f:
            profile_data = json.load(f)
        return UserProfile(**profile_data)
    return None

def get_user_all_profiles(user_id: str) -> list:
    """Retrieves all profiles (Character and CHC) for a given user from the local file system."""
    _init_db()
    all_profiles = []
    
    all_characters_from_index = index_service.get_all_characters_from_index()

    for char_entry in all_characters_from_index:
        character_id = char_entry["character_id"]
        character_data = index_service.get_character_data(character_id)

        if character_data:
            # Check for CharacterProfile (RIASEC)
            profile_path_str = character_data["profiles"].get("character")
            if profile_path_str:
                profile_path = Path(profile_path_str)
                if profile_path.exists():
                    with open(profile_path, "r") as f:
                        profile_data = json.load(f)
                    if profile_data.get("user_id") == user_id:
                        all_profiles.append({
                            "character_id": character_id,
                            "character_name": character_data["pii"]["character_name"],
                            "profile_type": "RIASEC",
                            "profile_datetime": profile_data.get("profile_datetime")
                        })
            
            # Check for CHCProfile
            chc_profile_path_str = character_data["profiles"].get("chc")
            if chc_profile_path_str:
                chc_profile_path = Path(chc_profile_path_str)
                if chc_profile_path.exists():
                    with open(chc_profile_path, "r") as f:
                        chc_profile_data = json.load(f)
                    if chc_profile_data.get("user_id") == user_id:
                        all_profiles.append({
                            "character_id": character_id,
                            "character_name": chc_profile_data.get("character_name"), # CHCModel now has character_name
                            "profile_type": "CHC",
                            "profile_datetime": chc_profile_data.get("profile_datetime")
                        })
    
    # Sort by datetime
    all_profiles.sort(key=lambda x: x.get("profile_datetime", ""), reverse=True)
    return all_profiles


