
import pytest
from unittest.mock import patch, MagicMock

from app.models import CharacterProfile, Hexa3DAssessment, ProfilHexaDomaine, NotesHexa, Dimensions3D, ScoreDimension3D
from app.services import generate_hexa3d_profile

@patch('app.database.db_service')
@patch('app.services.get_genai_client')
def test_generate_hexa3d_profile_success(mock_get_genai_client, mock_db_service):
    """
    Tests the successful generation of a character profile with a Hexa3D assessment.
    """
    mock_client = MagicMock()
    mock_get_genai_client.return_value = mock_client

    mock_response = MagicMock()
    mock_profile = CharacterProfile(
        character_name="Test Character",
        profile_datetime="2024-01-01 12:00:00",
        overall_assessment_summary="A test summary.",
        diagnoses=[],
        hexa3d_assessment=Hexa3DAssessment(
            assessment_datetime="2024-01-01 12:00:00",
            profil_activites=ProfilHexaDomaine(notes_brutes=NotesHexa(R=1,I=1,A=1,S=1,E=1,C=1), notes_etalonnees=NotesHexa(R=1,I=1,A=1,S=1,E=1,C=1), code_riasec="RIA"),
            profil_qualites=ProfilHexaDomaine(notes_brutes=NotesHexa(R=1,I=1,A=1,S=1,E=1,C=1), notes_etalonnees=NotesHexa(R=1,I=1,A=1,S=1,E=1,C=1), code_riasec="RIA"),
            profil_professions=ProfilHexaDomaine(notes_brutes=NotesHexa(R=1,I=1,A=1,S=1,E=1,C=1), notes_etalonnees=NotesHexa(R=1,I=1,A=1,S=1,E=1,C=1), code_riasec="RIA"),
            profil_global=ProfilHexaDomaine(notes_brutes=NotesHexa(R=1,I=1,A=1,S=1,E=1,C=1), notes_etalonnees=NotesHexa(R=1,I=1,A=1,S=1,E=1,C=1), code_riasec="RIA"),
            dimensions_secondaires=Dimensions3D(
                prestige_eleve=ScoreDimension3D(note_brute=1, note_etalonnee=1),
                prestige_faible=ScoreDimension3D(note_brute=1, note_etalonnee=1),
                masculinite=ScoreDimension3D(note_brute=1, note_etalonnee=1),
                feminite=ScoreDimension3D(note_brute=1, note_etalonnee=1),
            ),
            code_global_top_themes=["R", "I", "A"],
            niveau_differenciation_global="High",
            niveau_consistance_global="High",
            summary="A test summary."
        )
    )
    mock_response.parsed = mock_profile
    mock_client.models.generate_content.return_value = mock_response

    profile = generate_hexa3d_profile("A test description.", "gemini-1.5-pro-latest", "test_user")

    assert isinstance(profile, CharacterProfile)
    assert profile.character_name == "Test Character"
    assert profile.hexa3d_assessment is not None
    assert isinstance(profile.hexa3d_assessment, Hexa3DAssessment)
    assert profile.hexa3d_assessment.summary == "A test summary."
