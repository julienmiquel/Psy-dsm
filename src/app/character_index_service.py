import json
from pathlib import Path
from typing import Dict, Any

LOCAL_DB_PATH = Path("local_db")
INDEX_PATH = LOCAL_DB_PATH / "character_index.json"

def _read_index() -> Dict[str, Any]:
    """Reads the character index file."""
    if not INDEX_PATH.exists():
        return {}
    with open(INDEX_PATH, "r") as f:
        return json.load(f)

def _write_index(index: Dict[str, Any]):
    """Writes to the character index file."""
    LOCAL_DB_PATH.mkdir(parents=True, exist_ok=True)
    with open(INDEX_PATH, "w") as f:
        json.dump(index, f, indent=2)

def add_character_to_index(character_id: str, character_name: str):
    """Adds a new character to the index."""
    index = _read_index()
    if character_id not in index:
        index[character_id] = {
            "pii": {"character_name": character_name},
            "profiles": {}
        }
        _write_index(index)

def add_profile_to_character(character_id: str, profile_type: str, profile_path: str):
    """Adds a profile path to a character in the index."""
    index = _read_index()
    if character_id in index:
        index[character_id]["profiles"][profile_type] = profile_path
        _write_index(index)

def get_character_data(character_id: str) -> Dict[str, Any]:
    """Gets all data for a character from the index."""
    index = _read_index()
    return index.get(character_id)

def get_all_characters_from_index() -> list:
    """Gets all characters from the index."""
    index = _read_index()
    characters = []
    for char_id, char_data in index.items():
        characters.append({
            "character_id": char_id,
            "character_name": char_data["pii"]["character_name"]
        })
    return characters
