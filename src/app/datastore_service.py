from google.cloud import datastore
from app.models import CharacterProfile
import os

def get_datastore_client():
    """Initializes and returns a Datastore client."""
    return datastore.Client(project=os.getenv("GOOGLE_CLOUD_PROJECT"))

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

def get_user_profiles(user_id: str):
    """Retrieves all profiles for a given user."""
    client = get_datastore_client()
    query = client.query(kind="CharacterProfile")
    query.add_filter("user_id", "=", user_id)

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
