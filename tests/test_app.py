import pytest
from unittest.mock import patch, MagicMock

# Import the functions and classes from your main application
from src.app.models import CharacterProfile
from src.app.services import generate_character_profile
from src.app.main import app, State, send_chat_message

@patch('google.genai.Client')
def test_generate_character_profile_success(mock_client):
    """
    Tests the successful generation of a character profile.
    """
    mock_response = MagicMock()
    mock_function_call = MagicMock()
    mock_function_call.name = "save_character_profile"
    mock_function_call.args = {
        "character_name": "Test Character",
        "profile_date": "2024-01-01",
        "overall_assessment_summary": "A test summary.",
        "diagnoses": [],
    }
    mock_response.function_calls = [mock_function_call]

    mock_client.models.generate_content.return_value = mock_response

    profile = generate_character_profile("A test description.", mock_client)

    assert isinstance(profile, CharacterProfile)
    assert profile.character_name == "Test Character"
    assert profile.profile_date == "2024-01-01"
