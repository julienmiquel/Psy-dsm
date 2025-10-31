# -*- coding: utf-8 -*-
"""
This script evaluates the 'generate_character_profile' function
using the existing LLM-as-a-Judge function in services.py.
"""

import os
import sys
import pandas as pd
from dotenv import load_dotenv

# Add project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.app.services import generate_character_profile, evaluate_profile_with_llm
from src.app.models import CharacterProfile, HollandCodeAssessment, Diagnosis, EvaluationResult

# Load environment variables from .env file
load_dotenv()

def main():
    """
    Main function to run the evaluation.
    """
    # @title ### Set Google Cloud project information
    PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT")
    if not PROJECT_ID:
        raise ValueError("GOOGLE_CLOUD_PROJECT environment variable not set.")

    model_id = "gemini-2.5-flash" # Using a recent model
    judge_model_id = "gemini-2.5-pro" # It's good practice to use a powerful model for judging

    # @title ### Prepare Evaluation Dataset
    # We define a list of test cases, each with a description and a golden profile.
    test_cases = [
        {
            "description": "Subject is a 52-year-old male architect. He reports chronic feelings of emptiness and instability in his interpersonal relationships, self-image, and emotions. He has a history of intense and unstable relationships, marked by alternating between extremes of idealization and devaluation. He describes frantic efforts to avoid real or imagined abandonment. He also reports recurrent suicidal ideation and gestures, as well as chronic feelings of emptiness.",
            "golden_profile": CharacterProfile(
                character_name="John Doe",
                profile_date="2025-10-31",
                overall_assessment_summary="Le sujet présente des symptômes clairs et persistants d'un trouble de la personnalité borderline (TPB), caractérisé par une instabilité marquée des relations interpersonnelles, de l'image de soi et des affects, ainsi qu'une impulsivité notable. L'évaluation du code Holland suggère des intérêts forts pour les domaines Artistique et Investigateur, ce qui est cohérent avec sa profession d'architecte.",
                holland_code_assessment=HollandCodeAssessment(
                    riasec_scores=[
                        {"theme": "Réaliste", "score": 6, "description": "Aime travailler avec des outils, des machines; peut être pratique, mécanique."},
                        {"theme": "Investigateur", "score": 8, "description": "Aime étudier et résoudre des problèmes mathématiques ou scientifiques; peut être précis, scientifique."},
                        {"theme": "Artistique", "score": 9, "description": "Aime faire du travail créatif, de l'art, du design; peut être imaginatif, original."},
                        {"theme": "Social", "score": 4, "description": "Aime aider les gens, enseigner; peut être coopératif, empathique."},
                        {"theme": "Entreprenant", "score": 5, "description": "Aime diriger, persuader; peut être énergique, ambitieux."},
                        {"theme": "Conventionnel", "score": 3, "description": "Aime travailler avec des données, avoir des routines; peut être ordonné, efficace."}
                    ],
                    top_themes=["Artistique", "Investigateur"],
                    summary="Les thèmes dominants sont Artistique et Investigateur, indiquant une forte orientation vers la créativité, la résolution de problèmes complexes et l'innovation. Ce profil est typique des professions comme l'architecture, qui demandent à la fois une vision esthétique et une rigueur intellectuelle."
                ),
                diagnoses=[
                    Diagnosis(
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
        },
        # Add more test cases here
    ]

    print("Running evaluations...")
    for i, case in enumerate(test_cases):
        print(f"--- Evaluating case {i+1}/{len(test_cases)} ---")
        description = case["description"]
        golden_profile = case["golden_profile"]

        print("Generating profile...")
        generated_profile = generate_character_profile(description=description, model_id=model_id)

        print("Evaluating profile...")
        evaluation_result = evaluate_profile_with_llm(
            description=description,
            generated_profile=generated_profile,
            golden_profile=golden_profile,
            model_id=judge_model_id
        )

        print("--- Evaluation Result ---")
        print(evaluation_result.model_dump_json(indent=2))
        print("-------------------------")

if __name__ == "__main__":
    main()
