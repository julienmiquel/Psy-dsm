import json
import os
from pathlib import Path
from app.models import CharacterProfile, TCCProgram
from app.chc_models import CHCModel
from app.user_models import UserProfile

LOCAL_DB_PATH = Path("local_db")
PROFILES_PATH = LOCAL_DB_PATH / "profiles"
CHC_PROFILES_PATH = LOCAL_DB_PATH / "chc"
PII_PATH = LOCAL_DB_PATH / "pii"
USERS_PATH = LOCAL_DB_PATH / "users"
TCC_PROGRAMS_PATH = LOCAL_DB_PATH / "tcc_programs"

def _init_db():
    """Creates the necessary directories for the local file store."""
    PROFILES_PATH.mkdir(parents=True, exist_ok=True)
    PII_PATH.mkdir(parents=True, exist_ok=True)
    USERS_PATH.mkdir(parents=True, exist_ok=True)
    TCC_PROGRAMS_PATH.mkdir(parents=True, exist_ok=True)
    CHC_PROFILES_PATH.mkdir(parents=True, exist_ok=True)

def save_profile(profile: CharacterProfile, user_id: str):
    """Saves a character profile to the local file system, separating PII."""
    _init_db()
    profile.user_id = user_id

    # Store non-PII data
    profile_data = profile.model_dump(exclude={"character_name"})
    profile_path = PROFILES_PATH / f"{profile.character_id}.json"
    with open(profile_path, "w") as f:
        json.dump(profile_data, f, indent=2)

    # Store PII in a separate file
    pii_data = {"character_name": profile.character_name}
    pii_path = PII_PATH / f"{profile.character_id}.json"
    with open(pii_path, "w") as f:
        json.dump(pii_data, f, indent=2)

def save_chc_profile(profile: CHCModel, user_id: str):
    """Saves a CHC profile to the local file system."""
    _init_db()

    # Store CHC profile data
    profile.user_id = user_id
    profile_data = profile.model_dump()
    profile_path = CHC_PROFILES_PATH / f"{profile.character_id}.json"
    with open(profile_path, "w") as f:
        json.dump(profile_data, f, indent=2)

def update_profile_with_tcc_program(character_id: str, tcc_program: TCCProgram):
    """Saves a TCC program to a separate file."""
    _init_db()
    tcc_program_path = TCC_PROGRAMS_PATH / f"{character_id}.json"
    with open(tcc_program_path, "w") as f:
        json.dump(tcc_program.model_dump(), f, indent=2)

def get_user_profiles(user_id: str):
    """Retrieves all profiles for a given user from the local file system."""
    _init_db()
    profiles = []
    for profile_path in PROFILES_PATH.glob("*.json"):
        with open(profile_path, "r") as f:
            profile_data = json.load(f)
        
        if profile_data.get("user_id") == user_id:
            # Fetch and re-attach PII
            pii_path = PII_PATH / f"{profile_data['character_id']}.json"
            if pii_path.exists():
                with open(pii_path, "r") as f:
                    pii_data = json.load(f)
                profile_data["character_name"] = pii_data.get("character_name")

            profiles.append(CharacterProfile(**profile_data))
            
    return profiles

def get_user_characters(user_id: str):
    """Retrieves all characters for a given user from the local file system."""
    _init_db()
    characters = {}
    
    # From CharacterProfiles
    for profile_path in PROFILES_PATH.glob("*.json"):
        with open(profile_path, "r") as f:
            data = json.load(f)
        
        if data.get("user_id") == user_id:
            character_id = data.get("character_id")
            if character_id and character_id not in characters:
                pii_path = PII_PATH / f"{character_id}.json"
                if pii_path.exists():
                    with open(pii_path, "r") as f_pii:
                        pii_data = json.load(f_pii)
                    character_name = pii_data.get("character_name")
                    if character_name:
                        characters[character_id] = {"character_id": character_id, "character_name": character_name}

    # From CHCProfiles
    for profile_path in CHC_PROFILES_PATH.glob("*.json"):
        with open(profile_path, "r") as f:
            data = json.load(f)
        
        if data.get("user_id") == user_id:
            character_id = data.get("character_id")
            character_name = data.get("character_name")
            if character_id and character_name and character_id not in characters:
                characters[character_id] = {"character_id": character_id, "character_name": character_name}

    return list(characters.values())

def get_character_profile(character_id: str):
    """Retrieves a CharacterProfile for a given character_id."""
    _init_db()
    profile_path = PROFILES_PATH / f"{character_id}.json"
    if profile_path.exists():
        with open(profile_path, "r") as f:
            profile_data = json.load(f)
        pii_path = PII_PATH / f"{character_id}.json"
        if pii_path.exists():
            with open(pii_path, "r") as f:
                pii_data = json.load(f)
            profile_data["character_name"] = pii_data.get("character_name")
        
        # Load TCC program
        tcc_program_path = TCC_PROGRAMS_PATH / f"{character_id}.json"
        if tcc_program_path.exists():
            with open(tcc_program_path, "r") as f:
                tcc_program_data = json.load(f)
            profile_data["tcc_program"] = tcc_program_data

        return CharacterProfile(**profile_data)
    return None

def get_chc_profile(character_id: str):
    """Retrieves a CHCProfile for a given character_id."""
    _init_db()
    profile_path = PROFILES_PATH / f"chc_{character_id}.json"
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

def get_user_chc_profiles(user_id: str):
    """Retrieves all profiles for a given user from the local file system."""
    _init_db()
    profiles = []
    for profile_path in CHC_PROFILES_PATH.glob("*.json"):
        with open(profile_path, "r") as f:
            profile_data = json.load(f)
        
        if profile_data.get("user_id") == user_id:
            # Fetch and re-attach PII
            pii_path = PII_PATH / f"{profile_data['character_id']}.json"
            if pii_path.exists():
                with open(pii_path, "r") as f:
                    pii_data = json.load(f)
                profile_data["character_name"] = pii_data.get("character_name")

            profiles.append(CharacterProfile(**profile_data))
            
    return profiles
