import os
import pytest
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
def character_profile(character_description):
    """Generates a character profile for testing."""
    model_id = "gemini-2.5-pro"
    return generate_character_profile(character_description, model_id)


@pytest.mark.stability
def test_character_profile_stability(character_description):
    """
    Tests the stability of character profile generation by ensuring key fields
    are consistent across multiple runs.
    """
    model_id = "gemini-2.5-flash"
    num_runs = 3
    profiles = [
        generate_character_profile(character_description, model_id)
        for _ in range(num_runs)
    ]
    assert len(profiles) == num_runs
    for profile in profiles:
        assert isinstance(profile, CharacterProfile)
        print(profile.holland_code_assessment.top_themes[0])
        print("----")


    # Check for consistency in top Holland Code themes
    first_holland_themes = sorted(profiles[0].holland_code_assessment.top_themes)
    for profile in profiles[1:]:
        assert sorted(profile.holland_code_assessment.top_themes)[0] == first_holland_themes[0]
        assert sorted(profile.holland_code_assessment.top_themes)[1] == first_holland_themes[1]

    # Check for consistency in diagnoses
    first_diagnoses = [d.disorder_name for d in profiles[0].diagnoses]
    for profile in profiles[1:]:
        diagnoses = [d.disorder_name for d in profile.diagnoses]
        assert sorted(diagnoses) == sorted(first_diagnoses)


def test_generate_tcc_program(character_profile):
    """
    Tests the generation of a TCC program based on a character profile.
    """
    model_id = "gemini-2.5-pro"
    tcc_program = generate_tcc_program(character_profile, model_id)

    assert isinstance(tcc_program, TCCProgram)
    assert len(tcc_program.modules) > 0
    for module in tcc_program.modules:
        assert len(module.activities) > 0
        assert module.title != ""
    assert tcc_program.title != ""
    assert tcc_program.global_objective != ""   

