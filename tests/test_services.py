import os
import pytest
from unittest.mock import patch, MagicMock
from app.services import generate_character_profile, generate_tcc_program
from app.models import CharacterProfile, TCCProgram

# Mark all tests in this file as integration tests
pytestmark = pytest.mark.integration

@pytest.fixture
def character_description():
    """Provides a sample character description for testing."""
    return """
    Subject is a 52-year-old male architect. He reports chronic feelings of
    emptiness and instability in his interpersonal relationships, self-image,
    and emotions. He has a history of intense and unstable relationships,
    marked by alternating between extremes of idealization and devaluation.
    He describes frantic efforts to avoid real or imagined abandonment.
    He also reports recurrent suicidal ideation and gestures,
    as well as chronic feelings of emptiness.
    """

@pytest.fixture
@patch('app.services.get_genai_client')
def character_profile(mock_get_genai_client, character_description):
    """Generates a character profile for testing."""
    model_id = "gemini-2.5-pro"
    with patch('app.services.datastore_service.save_profile'):
        # Mock the response from the generative model
        mock_client = MagicMock()
        mock_get_genai_client.return_value = mock_client
        mock_response = MagicMock()
        mock_profile = CharacterProfile(
            character_name="Test Character",
            profile_date="2024-01-01",
            overall_assessment_summary="A test summary.",
            diagnoses=[],
            holland_code_assessment=None,
        )
        mock_response.parsed = mock_profile
        mock_client.models.generate_content.return_value = mock_response
        return generate_character_profile(character_description, model_id, "test_user")


@pytest.mark.stability
@patch('app.services.get_genai_client')
def test_character_profile_stability(mock_get_genai_client, character_description):
    """
    Tests the stability of character profile generation by ensuring key fields
    are consistent across multiple runs.
    """
    model_id = "gemini-2.5-pro"
    num_runs = 3
    with patch('app.services.datastore_service.save_profile'):
        # Mock the response from the generative model
        mock_client = MagicMock()
        mock_get_genai_client.return_value = mock_client
        mock_response = MagicMock()
        mock_profile = CharacterProfile(
            character_name="Test Character",
            profile_date="2024-01-01",
            overall_assessment_summary="A test summary.",
            diagnoses=[],
            holland_code_assessment=None,
        )
        mock_response.parsed = mock_profile
        mock_client.models.generate_content.return_value = mock_response
        profiles = [
            generate_character_profile(character_description, model_id, "test_user")
            for _ in range(num_runs)
        ]

    # Check for consistency in top Holland Code themes
    first_holland_themes = profiles[0].holland_code_assessment
    for profile in profiles[1:]:
        assert profile.holland_code_assessment == first_holland_themes

    # Check for consistency in diagnoses
    first_diagnoses = [d.disorder_name for d in profiles[0].diagnoses]
    for profile in profiles[1:]:
        diagnoses = [d.disorder_name for d in profile.diagnoses]
        assert sorted(diagnoses) == sorted(first_diagnoses)


@patch('app.services.get_genai_client')
def test_generate_tcc_program(mock_get_genai_client, character_profile):
    """
    Tests the generation of a TCC program based on a character profile.
    """
    model_id = "gemini-2.5-pro"
    # Mock the response from the generative model
    mock_client = MagicMock()
    mock_get_genai_client.return_value = mock_client
    mock_response = MagicMock()
    mock_program = TCCProgram(
        title="Test Program",
        global_objective="A test objective.",
        modules=[{"title": "Module 1", "session_range": "1-2", "objective": "Objective 1", "activities": []}],
    )
    mock_response.parsed = mock_program
    mock_client.models.generate_content.return_value = mock_response
    tcc_program = generate_tcc_program(character_profile, model_id)

    assert isinstance(tcc_program, TCCProgram)
    assert len(tcc_program.modules) > 0
