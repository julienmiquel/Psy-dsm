from google.cloud import datastore
from google.cloud.datastore.query import PropertyFilter

from app.models import CharacterProfile, TCCProgram
from app.chc_models import CHCModel
from app.user_models import UserProfile
import os

def get_datastore_client():
    """Initializes and returns a Datastore client."""
    db_name = "db-fs-std" #"fs-native" #"db-fs-std"
    return datastore.Client(project=os.getenv("GOOGLE_CLOUD_PROJECT"), database=db_name) 

def save_profile(profile: CharacterProfile, user_id: str):
    """Saves a character profile to Datastore, separating PII."""
    client = get_datastore_client()

    # Create a key for the main profile entity
    profile_key = client.key("CharacterProfile", profile.character_id)
    profile_entity = datastore.Entity(key=profile_key)

    # Store non-PII data
    profile.user_id = user_id
    profile_data = profile.model_dump(exclude={"character_name"})
    profile_entity.update(profile_data)
    client.put(profile_entity)

    # Store PII in a separate entity
    pii_key = client.key("PII", profile.character_id)
    pii_entity = datastore.Entity(key=pii_key)
    pii_entity.update({
        "character_name": profile.character_name
    })
    client.put(pii_entity)

def save_chc_profile(profile: CHCModel, user_id: str):
    """Saves a CHC profile to Datastore."""
    client = get_datastore_client()

    # Create a key for the CHC profile entity
    profile_key = client.key("CHCProfile", profile.character_id)
    profile_entity = datastore.Entity(key=profile_key)

    # Store CHC profile data
    profile.user_id = user_id
    profile_data = profile.model_dump()
    profile_entity.update(profile_data)
    client.put(profile_entity)

def update_profile_with_tcc_program(character_id: str, tcc_program: TCCProgram):
    """Updates an existing CharacterProfile entity with the TCC program data."""
    client = get_datastore_client()
    profile_key = client.key("CharacterProfile", character_id)
    profile_entity = client.get(profile_key)

    if profile_entity:
        profile_entity["tcc_program"] = tcc_program.model_dump_json()
        client.put(profile_entity)
    else:
        print(f"CharacterProfile with ID {character_id} not found.")

def get_user_profiles(user_id: str):
    """Retrieves all profiles for a given user."""
    client = get_datastore_client()
    query = client.query(kind="CharacterProfile")
    query.add_filter(filter=PropertyFilter("user_id", "=", user_id))

    profiles = []
    for entity in query.fetch():
        profile_data = dict(entity)

        # Fetch and re-attach PII
        pii_key = client.key("PII", entity.key.name)
        pii_entity = client.get(pii_key)
        if pii_entity:
            profile_data["character_name"] = pii_entity.get("character_name")

        profiles.append(CharacterProfile(**profile_data))

    return profiles

def get_user_characters(user_id: str):
    """Retrieves all characters for a given user.""" 
    client = get_datastore_client()
    characters = {}
    
    # Query CharacterProfiles
    query_char = client.query(kind="CharacterProfile")
    query_char.add_filter(filter=PropertyFilter("user_id", "=", user_id))
    for entity in query_char.fetch():
        character_id = entity.key.name
        pii_key = client.key("PII", character_id)
        pii_entity = client.get(pii_key)
        if pii_entity:
            character_name = pii_entity.get("character_name")
            if character_id and character_name and character_id not in characters:
                characters[character_id] = {"character_id": character_id, "character_name": character_name}

    # Query CHCProfiles
    query_chc = client.query(kind="CHCProfile")
    query_chc.add_filter(filter=PropertyFilter("user_id", "=", user_id))
    for entity in query_chc.fetch():
        character_id = entity.get("character_id")
        character_name = entity.get("character_name")
        if character_id and character_name and character_id not in characters:
            characters[character_id] = {"character_id": character_id, "character_name": character_name}

    return list(characters.values())

def get_character_profile(character_id: str):
    """Retrieves a CharacterProfile for a given character_id."""
    client = get_datastore_client()
    profile_key = client.key("CharacterProfile", character_id)
    entity = client.get(profile_key)
    if entity:
        profile_data = dict(entity)
        pii_key = client.key("PII", entity.key.name)
        pii_entity = client.get(pii_key)
        if pii_entity:
            profile_data["character_name"] = pii_entity.get("character_name")

        if "tcc_program" in profile_data and profile_data["tcc_program"]:
            profile_data["tcc_program"] = TCCProgram.model_validate_json(profile_data["tcc_program"])

        return CharacterProfile(**profile_data)
    return None

def get_chc_profile(character_id: str):
    """Retrieves a CHCProfile for a given character_id."""
    client = get_datastore_client()
    profile_key = client.key("CHCProfile", character_id)
    entity = client.get(profile_key)
    if entity:
        return CHCModel(**entity)
    return None

def save_user_profile(user_profile: UserProfile):
    """Saves a user profile to Datastore."""
    client = get_datastore_client()
    profile_key = client.key("UserProfile", user_profile.user_id)
    profile_entity = datastore.Entity(key=profile_key)
    profile_entity.update(user_profile.model_dump())
    client.put(profile_entity)

def get_user_profile(user_id: str):
    """Retrieves a user profile from Datastore."""
    client = get_datastore_client()
    profile_key = client.key("UserProfile", user_id)
    entity = client.get(profile_key)
    if entity:
        return UserProfile(**entity)
    return None
