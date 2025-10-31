from datetime import date
import json
from datetime import date
import os
from .models import CharacterProfile, TCCProgram, EvaluationResult

from google import genai
from google.genai import types


SYSTEM_PROMPT = f"""
You are a clinical psychologist and career counselor. Your task is to analyze the provided character description and generate a clinical profile in JSON format.

**CRITICAL INSTRUCTIONS:**
1.  **Analyze the character description** to identify potential DSM-5 diagnoses and assess their personality using the Holland Code (RIASEC) model.
2.  **ALL TEXT OUTPUT MUST BE IN FRENCH.** This includes all summaries, descriptions, and notes.
3.  If no disorder is apparent, provide an empty `diagnoses` array and explain your reasoning in the `overall_assessment_summary`.
4.  For any diagnosis, you **must** list the specific DSM-5 criteria met in the `criteria_met` field.
5.  Set the `profile_date` to today's date: {date.today().isoformat()}.
6.  Your output **must** be a single, valid JSON object, without any markdown formatting or extra text.

**EXAMPLE:**

**Input Description:**
```
Subject is a 52-year-old male architect. He reports chronic feelings of emptiness and instability in his interpersonal relationships, self-image, and emotions. He has a history of intense and unstable relationships, marked by alternating between extremes of idealization and devaluation. He describes frantic efforts to avoid real or imagined abandonment. He also reports recurrent suicidal ideation and gestures, as well as chronic feelings of emptiness.
```

**Output JSON:**
```json
{{
    "character_name": "John Doe",
    "profile_date": "2025-10-30",
    "overall_assessment_summary": "Le sujet présente des symptômes clairs et persistants d'un trouble de la personnalité borderline (TPB), caractérisé par une instabilité marquée des relations interpersonnelles, de l'image de soi et des affects, ainsi qu'une impulsivité notable. L'évaluation du code Holland suggère des intérêts forts pour les domaines Artistique et Investigateur, ce qui est cohérent avec sa profession d'architecte.",
    "holland_code_assessment": {{
        "riasec_scores": [
            {{"theme": "Réaliste", "score": 6, "description": "Aime travailler avec des outils, des machines; peut être pratique, mécanique."}},
            {{"theme": "Investigateur", "score": 8, "description": "Aime étudier et résoudre des problèmes mathématiques ou scientifiques; peut être précis, scientifique."}},
            {{"theme": "Artistique", "score": 9, "description": "Aime faire du travail créatif, de l'art, du design; peut être imaginatif, original."}},
            {{"theme": "Social", "score": 4, "description": "Aime aider les gens, enseigner; peut être coopératif, empathique."}},
            {{"theme": "Entreprenant", "score": 5, "description": "Aime diriger, persuader; peut être énergique, ambitieux."}},
            {{"theme": "Conventionnel", "score": 3, "description": "Aime travailler avec des données, avoir des routines; peut être ordonné, efficace."}}
        ],
        "top_themes": ["Artistique", "Investigateur"],
        "summary": "Les thèmes dominants sont Artistique et Investigateur, indiquant une forte orientation vers la créativité, la résolution de problèmes complexes et l'innovation. Ce profil est typique des professions comme l'architecture, qui demandent à la fois une vision esthétique et une rigueur intellectuelle."
    }},
    "diagnoses": [
        {{
            "disorder_name": "Trouble de la personnalité borderline",
            "dsm_category": "Troubles de la personnalité",
            "dsm_code": "301.83 (F60.3)",
            "criteria_met": [
                "Efforts effrénés pour éviter les abandons réels ou imaginés.",
                "Mode de relations interpersonnelles instables et intenses.",
                "Perturbation de l'identité.",
                "Idées suicidaires récurrentes, gestes ou menaces suicidaires.",
                "Sentiments chroniques de vide."
            ],
            "functional_impairment": "L'instabilité émotionnelle et relationnelle nuit à ses relations professionnelles et personnelles, créant un environnement de travail et de vie stressant.",
            "diagnostic_note": "Les symptômes correspondent à au moins 5 des 9 critères du DSM-5 pour le trouble de la personnalité borderline."
        }}
    ]
}}
```
"""

SYSTEM_PROMPT_TCC = f"""
You are a clinical psychologist and career counselor. 
Your task is to analyze the clinical profile and create a TCC program adapted to manage disorder in JSON format.


**Important:**
*   Your output **must** be a single, valid JSON object, without any markdown formatting or extra text.
"""

SYSTEM_PROMPT_JUDGE = f"""
You are an expert clinical psychologist. Your task is to evaluate the quality of a generated clinical profile against a golden standard.

**EVALUATION CRITERIA:**
1.  **Diagnostic Accuracy:** How accurate is the diagnosis compared to the golden standard? Are the DSM criteria relevant?
2.  **Holland Code Assessment:** Is the Holland Code assessment plausible and well-justified?
3.  **Completeness:** Does the generated profile contain all the necessary fields?
4.  **Clarity and Coherence:** Is the summary clear, coherent, and well-written (in French)?

**SCORING:**
- **5 (Excellent):** The generated profile is as good as or better than the golden standard.
- **4 (Good):** The profile is accurate and complete, with minor deviations.
- **3 (Acceptable):** The profile has some inaccuracies or omissions but is generally on the right track.
- **2 (Poor):** The profile has significant inaccuracies or omissions.
- **1 (Very Poor):** The profile is completely wrong or irrelevant.

Your output **must** be a single, valid JSON object matching the `EvaluationResult` schema.
"""

def get_genai_client() -> genai.Client:
        client = genai.Client(                                                                                                                                                            
            vertexai=True,                                                                                                                                                    
            project=os.getenv("GOOGLE_CLOUD_PROJECT"),                                                                                                                                                    
            location=os.getenv("GOOGLE_CLOUD_LOCATION"),                                                                                                                                                     
        ) 
        return client

def generate_tcc_program(
    profile: CharacterProfile, model_id: str) -> TCCProgram:
    
    generation_config = types.GenerateContentConfig(
        response_schema=TCCProgram,
        response_mime_type="application/json",
        temperature=0.0,
        top_p=1,
        max_output_tokens=8192,
    )

    prompt = f"{SYSTEM_PROMPT_TCC}\n\nCharacter PROFILE:\n{profile.model_dump_json()}"
    client = get_genai_client()
    response = client.models.generate_content(
        model=model_id,
        contents=prompt,
        config=generation_config,
    )

    return response.parsed

def generate_character_profile(
    description: str, model_id: str) -> CharacterProfile:
    """
    Generates a character profile using a generative model.
    """

    generation_config = types.GenerateContentConfig(
        response_schema=CharacterProfile,
        response_mime_type="application/json",
        temperature=0.0,
        top_p=0,
        top_k=1,
        max_output_tokens=8192,
        thinking_config=types.ThinkingConfig(thinking_budget=-1)
    )

    prompt = f"{SYSTEM_PROMPT}\n\nCharacter Description:\n{description}"
    client = get_genai_client()
    response = client.models.generate_content(
        model=model_id,
        contents=prompt,
        config=generation_config,
    )

    return response.parsed

def evaluate_profile_with_llm(
    description: str,
    generated_profile: CharacterProfile,
    golden_profile: CharacterProfile,
    model_id: str
) -> EvaluationResult:
    """
    Evaluates a generated character profile using an LLM-as-a-Judge.
    """
    generation_config = types.GenerateContentConfig(
        response_schema=EvaluationResult,
        response_mime_type="application/json",
        temperature=0.0,
        top_p=0,
        top_k=1,
        max_output_tokens=8192,
    )

    prompt = f"""{SYSTEM_PROMPT_JUDGE}

    **Original Description:**
    ```
    {description}
    ```

    **Golden Standard Profile:**
    ```json
    {golden_profile.model_dump_json(indent=2)}
    ```

    **Generated Profile to Evaluate:**
    ```json
    {generated_profile.model_dump_json(indent=2)}
    ```
    """

    client = get_genai_client()
    response = client.models.generate_content(
        model=model_id,
        contents=prompt,
        config=generation_config,
    )

    return response.parsed