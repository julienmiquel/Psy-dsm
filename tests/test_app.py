import pytest
from unittest.mock import patch, MagicMock

# Import the functions and classes from your main application
from app.models import CharacterProfile
from app.services import generate_character_profile

@patch('app.database.db_service')
@patch('app.services.get_genai_client')
def test_generate_character_profile_success(mock_get_genai_client, mock_db_service):
    """
    Tests the successful generation of a character profile.
    """
    mock_client = MagicMock()
    mock_get_genai_client.return_value = mock_client

    mock_response = MagicMock()
    mock_profile = CharacterProfile(
        character_name="Test Character",
        profile_datetime="2024-01-01 12:00:00",
        overall_assessment_summary="A test summary.",
        diagnoses=[],
        holland_code_assessment=None,
    )
    mock_response.parsed = mock_profile

    mock_client.models.generate_content.return_value = mock_response

    profile = generate_character_profile("A test description.", "gemini-1.5-pro-latest", "test_user")

    assert isinstance(profile, CharacterProfile)
    assert profile.character_name == "Test Character"
    assert profile.profile_datetime == "2024-01-01 12:00:00"

from app.models import TCCProgram
from app.services import generate_tcc_program

@patch('app.services.get_genai_client')
def test_generate_tcc_program_success(mock_get_genai_client):
    """
    Tests the successful generation of a TCC program.
    """
    mock_client = MagicMock()
    mock_get_genai_client.return_value = mock_client

    mock_response = MagicMock()
    mock_program = TCCProgram(
        title="Test Program",
        global_objective="A test objective.",
        modules=[],
    )
    mock_response.parsed = mock_program

    mock_client.models.generate_content.return_value = mock_response

    profile = CharacterProfile(
        character_name="Test Character",
        profile_datetime="2024-01-01 12:00:00",
        overall_assessment_summary="A test summary.",
        diagnoses=[],
        holland_code_assessment=None,
    )

    program = generate_tcc_program(profile, "gemini-2.5-pro")

    assert isinstance(program, TCCProgram)
    assert program.title == "Test Program"
