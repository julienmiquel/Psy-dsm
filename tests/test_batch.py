"""
Tests for batch processing.
"""
import os
import json
from unittest.mock import patch
from app.batch import batch_process
from app.models import CharacterProfile

def test_batch_process(tmp_path):
    """Test batch processing of character descriptions."""
    input_file = tmp_path / "input.txt"
    output_file = tmp_path / "output.json"

    with open(input_file, "w", encoding='utf-8') as f:
        f.write("Test character 1\n")
        f.write("Test character 2\n")

    mock_profile = CharacterProfile(
        character_name="Test Character",
        profile_date="2024-01-01",
        overall_assessment_summary="A test summary.",
        diagnoses=[],
        holland_code_assessment=None,
    )

    with patch('app.batch.generate_character_profile', return_value=mock_profile):
        batch_process(str(input_file), str(output_file), "gemini-2.5-pro")

    assert os.path.exists(output_file)

    with open(output_file, "r", encoding='utf-8') as f:
        profiles = json.load(f)
        assert isinstance(profiles, list)
        assert len(profiles) == 2
        assert profiles[0]["character_name"] == "Test Character"
        assert profiles[1]["character_name"] == "Test Character"
