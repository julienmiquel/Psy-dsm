
import pytest
from unittest.mock import MagicMock, patch
from app.models import CharacterProfile, OceanAssessment, OceanTrait
from app.services import generate_character_profile

@pytest.fixture
def mock_genai_client():
    with patch("app.services.get_genai_client") as mock:
        yield mock

def test_generate_character_profile_with_ocean(mock_genai_client):
    # Mock response data
    ocean_trait = OceanTrait(
        trait="Openness",
        score=9,
        level="High",
        description="Very open"
    )
    ocean_assessment = OceanAssessment(
        ocean_scores=[ocean_trait],
        summary="Summary"
    )
    expected_profile = CharacterProfile(
        character_name="Test Character",
        profile_date="2023-10-27",
        ocean_assessment=ocean_assessment,
        overall_assessment_summary="Test Summary",
        diagnoses=[]
    )

    # Setup mock
    mock_client_instance = MagicMock()
    mock_genai_client.return_value = mock_client_instance
    mock_response = MagicMock()
    mock_response.parsed = expected_profile
    mock_client_instance.models.generate_content.return_value = mock_response

    # Call function
    profile = generate_character_profile("Test description", "model-id")

    # Verify
    assert profile.character_name == "Test Character"
    assert profile.ocean_assessment is not None
    assert len(profile.ocean_assessment.ocean_scores) == 1
    assert profile.ocean_assessment.ocean_scores[0].trait == "Openness"
    assert profile.ocean_assessment.ocean_scores[0].score == 9
