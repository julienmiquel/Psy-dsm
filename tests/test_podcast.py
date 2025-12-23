"""Tests for podcast generation."""
from unittest.mock import patch, MagicMock
import pytest
from app.models import PodcastScript, PodcastSegment, CharacterProfile, TCCProgram
from app.services import generate_podcast_script

@pytest.fixture
def mock_profile():
    """Mock character profile."""
    return CharacterProfile(
        character_name="Test User",
        profile_date="2023-10-27",
        overall_assessment_summary="Test summary",
        diagnoses=[]
    )

@pytest.fixture
def mock_tcc_program():
    """Mock TCC program."""
    return TCCProgram(
        title="Test Program",
        global_objective="Test Objective",
        modules=[]
    )

@patch('app.services.get_genai_client')
def test_generate_podcast_script(mock_get_client, mock_profile, mock_tcc_program): # pylint: disable=redefined-outer-name
    """Test generating a podcast script."""
    # Setup mock response
    mock_client = MagicMock()
    mock_response = MagicMock()

    expected_script = PodcastScript(
        title="Test Podcast",
        target_audience="General",
        segments=[
            PodcastSegment(speaker="Host", text="Hello"),
            PodcastSegment(speaker="Expert", text="Hi")
        ]
    )

    mock_response.parsed = expected_script
    mock_client.models.generate_content.return_value = mock_response
    mock_get_client.return_value = mock_client

    # Call function
    result = generate_podcast_script(mock_profile, mock_tcc_program, "model-id")

    # Verify results
    assert result == expected_script
    assert result.title == "Test Podcast"
    assert len(result.segments) == 2
    assert result.segments[0].speaker == "Host"

    # Verify call arguments
    mock_client.models.generate_content.assert_called_once()
    call_args = mock_client.models.generate_content.call_args
    assert call_args.kwargs['model'] == "model-id"
