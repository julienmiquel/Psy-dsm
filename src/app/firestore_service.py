# TODO: Refactor this service to use the character index service.

from google.cloud import firestore
from app.models import CharacterProfile, TCCProgram
from app.chc_models import CHCModel
from app.user_models import UserProfile
import os

def get_firestore_client():
    """Initializes and returns a Firestore client."""
    db_name = "psy-dsm"
    return firestore.Client(project=os.getenv("GOOGLE_CLOUD_PROJECT"), database=db_name)

def save_profile(profile: CharacterProfile, user_id: str):
    """Saves a character profile to Firestore, separating PII."""
    client = get_firestore_client()

    # Document reference for the main profile
    profile_ref = client.collection("CharacterProfile").document(profile.character_id)

    # Store non-PII data
    profile.user_id = user_id
    profile_data = profile.model_dump(exclude={"character_name"})
    profile_ref.set(profile_data)

    # Document reference for PII
    pii_ref = client.collection("PII").document(profile.character_id)

    # Store PII in a separate document
    pii_ref.set({
        "character_name": profile.character_name
    })

def save_chc_profile(profile: CHCModel, user_id: str):
    """Saves a CHC profile to Firestore."""
    client = get_firestore_client()

    # Document reference for the CHC profile
    profile_ref = client.collection("CHCProfile").document(profile.character_id)

    # Store CHC profile data
    profile.user_id = user_id
    profile_data = profile.model_dump()
    profile_ref.set(profile_data)

def update_profile_with_tcc_program(character_id: str, tcc_program: TCCProgram):
    """Updates an existing CharacterProfile document with the TCC program data."""
    client = get_firestore_client()
    profile_ref = client.collection("CharacterProfile").document(character_id)
    
    profile_doc = profile_ref.get()

    if profile_doc.exists:
        profile_ref.update({
            "tcc_program": tcc_program.model_dump()
        })
    else:
        print(f"CharacterProfile with ID {character_id} not found.")

def get_user_profiles(user_id: str):
    """Retrieves all profiles for a given user from Firestore."""
    client = get_firestore_client()
    profiles_query = client.collection('CharacterProfile').where('user_id', '==', user_id)

    profiles = []
    for doc in profiles_query.stream():
        profile_data = doc.to_dict()

        # Fetch and re-attach PII
        pii_ref = client.collection("PII").document(doc.id)
        pii_doc = pii_ref.get()
        if pii_doc.exists:
            pii_data = pii_doc.to_dict()
            profile_data["character_name"] = pii_data.get("character_name")

        profiles.append(CharacterProfile(**profile_data))

    return profiles

def get_user_characters(user_id: str):
    """Retrieves all characters for a given user from Firestore."""
    client = get_firestore_client()
    characters = {}

    # Query CharacterProfiles
    query_char = client.collection('CharacterProfile').where('user_id', '==', user_id)
    for doc in query_char.stream():
        character_id = doc.id
        pii_ref = client.collection("PII").document(character_id)
        pii_doc = pii_ref.get()
        if pii_doc.exists:
            character_name = pii_doc.to_dict().get("character_name")
            if character_id and character_name and character_id not in characters:
                characters[character_id] = {"character_id": character_id, "character_name": character_name}

    # Query CHCProfiles
    query_chc = client.collection('CHCProfile').where('user_id', '==', user_id)
    for doc in query_chc.stream():
        data = doc.to_dict()
        character_id = data.get("character_id")
        character_name = data.get("character_name")
        if character_id and character_name and character_id not in characters:
            characters[character_id] = {"character_id": character_id, "character_name": character_name}

    return list(characters.values())

def get_character_profile(character_id: str):
    """Retrieves a CharacterProfile for a given character_id from Firestore."""
    client = get_firestore_client()
    profile_ref = client.collection("CharacterProfile").document(character_id)
    doc = profile_ref.get()
    if doc.exists:
        profile_data = doc.to_dict()
        pii_ref = client.collection("PII").document(doc.id)
        pii_doc = pii_ref.get()
        if pii_doc.exists:
            profile_data["character_name"] = pii_doc.to_dict().get("character_name")
        return CharacterProfile(**profile_data)
    return None

def get_chc_profile(character_id: str):
    """Retrieves a CHCProfile for a given character_id from Firestore."""
    client = get_firestore_client()
    profile_ref = client.collection("CHCProfile").document(character_id)
    doc = profile_ref.get()
    if doc.exists:
        return CHCModel(**doc.to_dict())
    return None

def save_user_profile(user_profile: UserProfile):
    """Saves a user profile to Firestore."""
    client = get_firestore_client()
    profile_ref = client.collection("UserProfile").document(user_profile.user_id)
    profile_ref.set(user_profile.model_dump())

def get_user_profile(user_id: str):
    """Retrieves a user profile from Firestore."""
    client = get_firestore_client()
    profile_ref = client.collection("UserProfile").document(user_id)
    doc = profile_ref.get()
    if doc.exists:
        return UserProfile(**doc.to_dict())
    return None