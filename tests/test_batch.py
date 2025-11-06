import os
import json
import pytest
from app.batch import batch_process
from unittest.mock import patch
from app.models import CharacterProfile

def test_batch_process(tmp_path):
    input_file = tmp_path / "input.txt"
    output_file = tmp_path / "output.json"

    with open(input_file, "w") as f:
        f.write("Test character 1\n")
        f.write("Test character 2\n")

    mock_profile = CharacterProfile(
        character_name="Test Character",
        profile_datetime="2024-01-01 12:00:00",
        overall_assessment_summary="A test summary.",
        diagnoses=[],
        holland_code_assessment=None,
    )

    with patch('app.batch.generate_character_profile', return_value=mock_profile):
        batch_process(str(input_file), str(output_file), "gemini-2.5-pro")

    assert os.path.exists(output_file)

    with open(output_file, "r") as f:
        profile = json.load(f)
        assert profile["character_name"] == "Test Character"
