import pytest
from unittest.mock import MagicMock
from app.models import CharacterProfile
from app.services import generate_character_profile

@pytest.fixture
def mock_genai_client():
    """Fixture for a mocked google.genai.Client."""
    mock_client = MagicMock()
    mock_model = MagicMock()
    mock_response = MagicMock()
    mock_function_call = MagicMock()

    mock_function_call.name = "save_character_profile"
    mock_function_call.args = {
        "character_name": "Test Character",
        "profile_date": "2024-01-01",
        "overall_assessment_summary": "A test summary.",
        "diagnoses": [],
        "holland_code_assessment": None,
        "character_id": None,
    }
    mock_response.function_calls = [mock_function_call]
    mock_response.candidates = [MagicMock()]  # Ensure candidates list is not empty
    mock_response.prompt_feedback = MagicMock()

    mock_model.generate_content.return_value = mock_response
    mock_client.models.get.return_value = mock_model
    return mock_client

def test_generate_character_profile_success(mock_genai_client):
    """
    Tests the successful generation of a character profile.
    """
    profile = generate_character_profile("A test description.", mock_genai_client)

    assert isinstance(profile, CharacterProfile)
    assert profile.character_name == "Test Character"
    assert profile.profile_date == "2024-01-01"
    mock_genai_client.models.get.assert_called_with('gemini-1.5-flash')

def test_generate_character_profile_no_function_call(mock_genai_client):
    """
    Tests the case where the model does not return a function call.
    """
    mock_response = MagicMock()
    mock_response.function_calls = []
    mock_response.candidates = [MagicMock()]
    mock_response.prompt_feedback = MagicMock()
    mock_genai_client.models.get.return_value.generate_content.return_value = mock_response

    with pytest.raises(Exception, match="Model did not return a function call"):
        generate_character_profile("A test description.", mock_genai_client)
