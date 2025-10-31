import pytest
from app.services import generate_character_profile, evaluate_profile_with_llm
from app.models import CharacterProfile, DiagnosisEntry, HollandCodeAssessment, HollandCode

# Mark all tests in this file as quality tests
pytestmark = pytest.mark.quality

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
def golden_profile():
    """Provides the golden standard CharacterProfile for the sample description."""
    return CharacterProfile(
        character_name="John Doe",
        profile_date="2025-10-30",
        overall_assessment_summary="Le sujet présente des symptômes clairs et persistants d'un trouble de la personnalité borderline (TPB), caractérisé par une instabilité marquée des relations interpersonnelles, de l'image de soi et des affects, ainsi qu'une impulsivité notable. L'évaluation du code Holland suggère des intérêts forts pour les domaines Artistique et Investigateur, ce qui est cohérent avec sa profession d'architecte.",
        holland_code_assessment=HollandCodeAssessment(
            riasec_scores=[
                HollandCode(theme="Réaliste", score=6, description="Aime travailler avec des outils, des machines; peut être pratique, mécanique."),
                HollandCode(theme="Investigateur", score=8, description="Aime étudier et résoudre des problèmes mathématiques ou scientifiques; peut être précis, scientifique."),
                HollandCode(theme="Artistique", score=9, description="Aime faire du travail créatif, de l'art, du design; peut être imaginatif, original."),
                HollandCode(theme="Social", score=4, description="Aime aider les gens, enseigner; peut être coopératif, empathique."),
                HollandCode(theme="Entreprenant", score=5, description="Aime diriger, persuader; peut être énergique, ambitieux."),
                HollandCode(theme="Conventionnel", score=3, description="Aime travailler avec des données, avoir des routines; peut être ordonné, efficace."),
            ],
            top_themes=["Artistique", "Investigateur"],
            summary="Les thèmes dominants sont Artistique et Investigateur, indiquant une forte orientation vers la créativité, la résolution de problèmes complexes et l'innovation. Ce profil est typique des professions comme l'architecture, qui demandent à la fois une vision esthétique et une rigueur intellectuelle."
        ),
        diagnoses=[
            DiagnosisEntry(
                disorder_name="Trouble de la personnalité borderline",
                dsm_category="Troubles de la personnalité",
                dsm_code="301.83 (F60.3)",
                criteria_met=[
                    "Efforts effrénés pour éviter les abandons réels ou imaginés.",
                    "Mode de relations interpersonnelles instables et intenses.",
                    "Perturbation de l'identité.",
                    "Idées suicidaires récurrentes, gestes ou menaces suicidaires.",
                    "Sentiments chroniques de vide."
                ],
                functional_impairment="L'instabilité émotionnelle et relationnelle nuit à ses relations professionnelles et personnelles, créant un environnement de travail et de vie stressant.",
                diagnostic_note="Les symptômes correspondent à au moins 5 des 9 critères du DSM-5 pour le trouble de la personnalité borderline."
            )
        ]
    )

def test_character_profile_quality(character_description, golden_profile):
    """
    Tests the quality of the generated character profile by comparing it
    against a golden standard.
    """
    model_id = "gemini-2.5-pro"  # Using the production-level model
    generated_profile = generate_character_profile(character_description, model_id)

    # 1. Exact Match for Critical Fields
    # Compare diagnoses by disorder name for simplicity
    generated_diagnoses = sorted([d.disorder_name for d in generated_profile.diagnoses])
    golden_diagnoses = sorted([d.disorder_name for d in golden_profile.diagnoses])
    assert generated_diagnoses == golden_diagnoses

    # Compare top Holland Code themes
    generated_themes = sorted(generated_profile.holland_code_assessment.top_themes)
    golden_themes = sorted(golden_profile.holland_code_assessment.top_themes)
    assert generated_themes == golden_themes

    # Optional: You could add more assertions here for other fields if needed
    # For example, checking if the number of criteria met is similar.
    assert len(generated_profile.diagnoses) == len(golden_profile.diagnoses)
    if generated_profile.diagnoses and golden_profile.diagnoses:
        assert len(generated_profile.diagnoses[0].criteria_met) >= 3

def test_character_profile_llm_as_judge(character_description, golden_profile):
    """
    Tests the quality of the generated character profile using an LLM-as-a-Judge.
    """
    # 1. Generate the profile to be evaluated
    generation_model_id = "gemini-2.5-pro"
    generated_profile = generate_character_profile(character_description, generation_model_id)

    # 2. Use a powerful model as the judge
    judge_model_id = "gemini-2.5-pro"
    evaluation = evaluate_profile_with_llm(
        description=character_description,
        generated_profile=generated_profile,
        golden_profile=golden_profile,
        model_id=judge_model_id
    )

    # 3. Assert that the score is acceptable
    assert evaluation.score >= 4
    print(f"LLM-as-a-Judge Evaluation Score: {evaluation.score}")
    print(f"Rationale: {evaluation.rationale}")