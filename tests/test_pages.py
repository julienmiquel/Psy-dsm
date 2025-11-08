"""
Tests for the functions called within the new UI pages.
"""

import pytest
from unittest.mock import patch, MagicMock
from app.services import (
    generate_hexa3d_profile,
    analyze_profile_comparison,
    combine_character_profiles,
)
from app.psychometry_chc_generate import generate_chc_profile
from app.models import CharacterProfile, Hexa3DAssessment, ProfilHexaDomaine, NotesHexa, Dimensions3D, ScoreDimension3D, HollandCodeAssessment, HollandCode
from app.chc_models import CHCModel

@pytest.fixture
def character_description():
    """Provides a sample character description for testing."""
    return "A sample character description."

@pytest.fixture
def character_profile():
    """Provides a sample character profile for testing."""
    return CharacterProfile(
        character_name="Test Character",
        profile_datetime="2024-01-01 12:00:00",
        overall_assessment_summary="A test summary.",
        diagnoses=[],
        holland_code_assessment=HollandCodeAssessment(
            riasec_scores=[
                HollandCode(theme="R", score=1, description=""),
                HollandCode(theme="I", score=2, description=""),
                HollandCode(theme="A", score=3, description=""),
                HollandCode(theme="S", score=4, description=""),
                HollandCode(theme="E", score=5, description=""),
                HollandCode(theme="C", score=6, description=""),
            ],
            top_themes=["C", "E", "S"],
            summary="A test summary."
        ),
        raw_text_bloc="some text"
    )

@patch('app.services.get_genai_client')
def test_generate_hexa3d_profile(mock_get_genai_client, character_description):
    """Tests the generation of a Hexa3D profile."""
    model_id = "gemini-1.5-pro"
    with patch('app.database.db_service.save_profile'):
        mock_client = MagicMock()
        mock_get_genai_client.return_value = mock_client
        mock_response = MagicMock()
        mock_profile = CharacterProfile(
            character_name="Test Character",
            profile_datetime="2024-01-01 12:00:00",
            overall_assessment_summary="A test summary.",
            diagnoses=[],
            holland_code_assessment=None,
            hexa3d_assessment=Hexa3DAssessment(
                assessment_datetime="2024-01-01 12:00:00",
                summary="A test summary.",
                code_global_top_themes=["Test"],
                profil_activites=ProfilHexaDomaine(notes_brutes=NotesHexa(R=1,I=1,A=1,S=1,E=1,C=1), notes_etalonnees=NotesHexa(R=1,I=1,A=1,S=1,E=1,C=1), code_riasec="RIA"),
                profil_qualites=ProfilHexaDomaine(notes_brutes=NotesHexa(R=1,I=1,A=1,S=1,E=1,C=1), notes_etalonnees=NotesHexa(R=1,I=1,A=1,S=1,E=1,C=1), code_riasec="RIA"),
                profil_professions=ProfilHexaDomaine(notes_brutes=NotesHexa(R=1,I=1,A=1,S=1,E=1,C=1), notes_etalonnees=NotesHexa(R=1,I=1,A=1,S=1,E=1,C=1), code_riasec="RIA"),
                profil_global=ProfilHexaDomaine(notes_brutes=NotesHexa(R=1,I=1,A=1,S=1,E=1,C=1), notes_etalonnees=NotesHexa(R=1,I=1,A=1,S=1,E=1,C=1), code_riasec="RIA"),
                dimensions_secondaires=Dimensions3D(prestige_eleve=ScoreDimension3D(note_brute=1, note_etalonnee=1), prestige_faible=ScoreDimension3D(note_brute=1, note_etalonnee=1), masculinite=ScoreDimension3D(note_brute=1, note_etalonnee=1), feminite=ScoreDimension3D(note_brute=1, note_etalonnee=1))
            ),
        )
        mock_response.parsed = mock_profile
        mock_client.models.generate_content.return_value = mock_response
        profile = generate_hexa3d_profile(character_description, model_id, "test_user")
        assert isinstance(profile, CharacterProfile)
        assert profile.hexa3d_assessment is not None

@patch('app.psychometry_chc_generate.get_genai_client')
def test_generate_chc_profile(mock_get_genai_client, character_description):
    """Tests the generation of a CHC profile."""
    model_id = "gemini-1.5-pro"
    with patch('app.database.db_service.save_chc_profile'):
        mock_client = MagicMock()
        mock_get_genai_client.return_value = mock_client
        mock_response = MagicMock()
        mock_profile = CHCModel(
            character_name="Test Character",
            profile_datetime="2024-01-01 12:00:00",
            g_factor=100,
            broad_abilities=[],
        )
        mock_response.parsed = mock_profile
        mock_client.models.generate_content.return_value = mock_response
        profile = generate_chc_profile(character_description, model_id, "test_user")
        assert isinstance(profile, CHCModel)

@patch('app.services.get_genai_client')
def test_analyze_profile_comparison(mock_get_genai_client, character_profile):
    """Tests the analysis of a profile comparison."""
    model_id = "gemini-1.5-pro"
    mock_client = MagicMock()
    mock_get_genai_client.return_value = mock_client
    mock_response = MagicMock()
    mock_response.text = "A test analysis."
    mock_client.models.generate_content.return_value = mock_response
    analysis = analyze_profile_comparison(character_profile, character_profile, model_id)
    assert isinstance(analysis, str)
    assert analysis == "A test analysis."

@patch('app.services.get_genai_client')
def test_combine_character_profiles(mock_get_genai_client, character_profile):
    """Tests the combination of character profiles."""
    with patch('app.database.db_service.save_profile'):
        mock_client = MagicMock()
        mock_get_genai_client.return_value = mock_client

        # Mock for the first generate_content call (holland_summary)
        mock_holland_response = MagicMock()
        mock_holland_response.text = "A test summary."

        # Mock for the second generate_content call (overall_summary)
        mock_summary_response = MagicMock()
        mock_summary_response.text = "A combined summary."

        mock_client.models.generate_content.side_effect = [mock_holland_response, mock_summary_response]

        combined_profile = combine_character_profiles([character_profile, character_profile], "test_user")
        assert isinstance(combined_profile, CharacterProfile)
        assert combined_profile.overall_assessment_summary == "A combined summary."
