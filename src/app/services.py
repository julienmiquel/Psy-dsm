from datetime import datetime
import json
import os
from .models import CharacterProfile, TCCProgram, HollandCodeAssessment, HollandCode, Module, Activity
from app.database import db_service
import uuid

from google import genai
from google.genai import types

SYSTEM_PROMPT = f"""
You are a clinical psychologist and career counselor. Your task is to analyze the provided character description and generate a clinical profile in JSON format.

Today's date is: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

**Instructions:**

1.  **Analyze the character description** to identify potential DSM-5 diagnoses and assess their personality using the Holland Code (RIASEC) model.
2.  **Generate a JSON object** that strictly adheres to the following schema.
3.  **Output language:** The output must be in French.

**JSON Schema:**

```json
{{
  "character_name": "string",
  "profile_datetime": "YYYY-MM-DD HH:MM:SS",
  "overall_assessment_summary": "string",
  "holland_code_assessment": {{
    "riasec_scores": [
      {{
        "theme": "Realistic",
        "score": "integer (1-10)",
        "description": "string"
      }},
      {{
        "theme": "Investigative",
        "score": "integer (1-10)",
        "description": "string"
      }},
      {{
        "theme": "Artistic",
        "score": "integer (1-10)",
        "description": "string"
      }},
      {{
        "theme": "Social",
        "score": "integer (1-10)",
        "description": "string"
      }},
      {{
        "theme": "Enterprising",
        "score": "integer (1-10)",
        "description": "string"
      }},
      {{
        "theme": "Conventional",
        "score": "integer (1-10)",
        "description": "string"
      }}
    ],
    "top_themes": ["string", "string"],
    "summary": "string"
  }},
  "diagnoses": [
    {{
      "disorder_name": "string",
      "dsm_category": "string",
      "criteria_met": ["string"],
      "specifiers": [
        {{
          "specifier_type": "string",
          "value": "string"
        }}
      ],
      "dsm_code": "string",
      "functional_impairment": "string",
      "diagnostic_note": "string"
    }}
  ]
}}
```

**Important:**

*   If no disorder is apparent, provide an empty `diagnoses` array and explain your reasoning in the `overall_assessment_summary`.
*   For any diagnosis, you **must** list the specific DSM-5 criteria met in the `criteria_met` field.
*   Ensure the `profile_datetime` is set to today's date and time.
*   Your output **must** be a single, valid JSON object, without any markdown formatting or extra text.
"""


SYSTEM_PROMPT_TCC = f"""
You are a clinical psychologist and career counselor. 
Your task is to analyze the clinical profile and create a TCC program adapted to manage disorder in JSON format.


**Important:**
*   Your output **must** be a single, valid JSON object, without any markdown formatting or extra text.
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
        # safety_settings=self.safety_settings
        # thinking_config=types.ThinkingConfig(thinking_budget=-1  )
    )

    prompt = f"{SYSTEM_PROMPT_TCC}\n\nCharacter PROFILE:\n{profile.model_dump_json()}"
    client = get_genai_client()
    response = client.models.generate_content(
        model=model_id,
        contents=prompt,
        config=generation_config,
    )

    # Parse the JSON string into the Pydantic model
    return response.parsed


def generate_character_profile(
    description: str, model_id: str, user_id: str) -> CharacterProfile:
    """
    Generates a character profile using a generative model and validates the
    JSON output against the CharacterProfile Pydantic model.
    """

    generation_config = types.GenerateContentConfig(
        response_schema=CharacterProfile,
        response_mime_type="application/json",
        temperature=0.0,
        top_p=1,
        max_output_tokens=8192,
        # safety_settings=self.safety_settings
        # thinking_config=types.ThinkingConfig(thinking_budget=-1  )
    )

    prompt = f"{SYSTEM_PROMPT}\n\nCharacter Description:\n{description}"
    client = get_genai_client()
    response = client.models.generate_content(
        model=model_id,
        contents=prompt,
        config=generation_config,
    )

    # Parse the JSON string into the Pydantic model
    profile = response.parsed
    if profile is None:
        raise Exception("Failed to generate character profile. The model did not return a valid JSON object.")
    profile.character_id = str(uuid.uuid4())
    profile.raw_text_bloc = description
    db_service.save_profile(profile, user_id)
    return profile


def analyze_profile_comparison(profile1: CharacterProfile, profile2: CharacterProfile, model_id: str) -> str:
    """
    Analyzes the comparison between two character profiles using a generative model.
    """
    client = get_genai_client()

    # Create a prompt for the analysis
    prompt = f"""
You are a clinical psychologist. Analyze the two following clinical profiles for the same person, generated at different times.
Focus on the evolution, changes, and any significant differences between the two.
Provide a summary of your analysis in French.

**Profile 1 ({profile1.profile_datetime}):**
{profile1.model_dump_json(indent=2)}

**Profile 2 ({profile2.profile_datetime}):**
{profile2.model_dump_json(indent=2)}

**Analysis:**
"""

    response = client.models.generate_content(
        model=model_id,
        contents=prompt,
    )

    return response.text

def combine_character_profiles(profiles: list[CharacterProfile], user_id: str) -> CharacterProfile:
    """
    Merges multiple character profiles into a new one.
    """
    if not profiles:
        raise ValueError("Cannot combine an empty list of profiles.")

    # Sort profiles by datetime to handle conflicts
    profiles.sort(key=lambda p: p.profile_datetime, reverse=True)

    # --- Raw Text ---
    raw_text_bloc = "\n\n--- MERGED FROM OLDER PROFILE ---\n\n".join([p.raw_text_bloc for p in profiles if p.raw_text_bloc])

    # --- Holland Code Assessment ---
    all_scores = {"Réaliste": [], "Investigateur": [], "Artistique": [], "Social": [], "Entreprenant": [], "Conventionnel": []}
    for profile in profiles:
        if profile.holland_code_assessment:
            for score in profile.holland_code_assessment.riasec_scores:
                if score.theme in all_scores:
                    all_scores[score.theme].append(score.score)
    
    new_riasec_scores = []
    for theme, scores in all_scores.items():
        if scores:
            avg_score = int(round(sum(scores) / len(scores)))
        else:
            avg_score = 0
        # Find description from the latest profile that has it
        description = ""
        for p in profiles:
            if p.holland_code_assessment:
                for s in p.holland_code_assessment.riasec_scores:
                    if s.theme == theme and s.description:
                        description = s.description
                        break
            if description:
                break
        new_riasec_scores.append(HollandCode(theme=theme, score=avg_score, description=description))

    new_riasec_scores.sort(key=lambda s: s.score, reverse=True)
    top_themes = [s.theme for s in new_riasec_scores[:3]]

    # Use Gemini to generate the Holland summary
    client = get_genai_client()
    holland_prompt = f"""
Based on the following new RIASEC scores, write a summary of the Holland Code assessment in French.
Scores:
{[(s.theme, s.score) for s in new_riasec_scores]}

Top themes: {top_themes}

Summary:
"""
    holland_summary_response = client.models.generate_content(model="gemini-2.5-pro", contents=holland_prompt)
    holland_summary = holland_summary_response.text

    new_holland_assessment = HollandCodeAssessment(
        riasec_scores=new_riasec_scores,
        top_themes=top_themes,
        summary=holland_summary
    )

    # --- Diagnoses ---
    # Simple union, taking the version from the latest profile in case of conflict
    diagnoses_by_name = {}
    for profile in reversed(profiles): # Iterate from oldest to newest
        for diagnosis in profile.diagnoses:
            diagnoses_by_name[diagnosis.disorder_name] = diagnosis
    new_diagnoses = list(diagnoses_by_name.values())

    # --- Overall Summary (Gemini) ---
    summaries_text = "\n\n---\n\n".join([p.overall_assessment_summary for p in profiles if p.overall_assessment_summary])
    summary_prompt = f"""
You are a clinical psychologist. Synthesize the following assessment summaries for the same person into a single, updated summary.
Capture the most current and relevant information. The output must be in French.

Summaries to synthesize:
{summaries_text}

New Synthesized Summary:
"""
    overall_summary_response = client.models.generate_content(model="gemini-2.5-pro", contents=summary_prompt)
    overall_summary = overall_summary_response.text

    # --- Create new profile ---
    new_profile = CharacterProfile(
        character_name=profiles[0].character_name,
        profile_datetime=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        overall_assessment_summary=overall_summary,
        holland_code_assessment=new_holland_assessment,
        diagnoses=[d.model_dump() for d in new_diagnoses],
        raw_text_bloc=raw_text_bloc,
        character_id=str(uuid.uuid4()),
        user_id=user_id,
        tcc_program=None # To be generated separately
    )

    return new_profile

def generate_detailed_session(profile: CharacterProfile, module: Module, activity: Activity) -> str:
    """
    Generates a detailed session plan for a specific TCC activity.
    """
    client = get_genai_client()

    prompt = f"""
You are a clinical psychologist creating a detailed session plan for a Cognitive Behavioral Therapy (CBT) session.
The plan should be a practical, step-by-step guide for the therapist to follow during the session.
The output must be in French and formatted in Markdown.

**Patient Profile Summary:**
{profile.overall_assessment_summary}

**Relevant Diagnoses:**
{[diag.disorder_name for diag in profile.diagnoses]}

**CBT Program Module:**
- **Title:** {module.title}
- **Objective:** {module.objective}

**Activity to Detail:**
- **Title:** {activity.title}
- **Description:** {', '.join(activity.details)}

**Instructions:**
Generate a detailed session plan for the activity '{activity.title}'.
The plan should include:
1.  **Session Objectives:** What are the specific, measurable goals for this session?
2.  **Materials Needed:** Any worksheets, handouts, or tools required.
3.  **Session Agenda (with timings):** A step-by-step agenda for the session (e.g., Check-in, Agenda Setting, Main Activity, Homework Assignment, Feedback).
4.  **Therapist's Script/Prompts:** Concrete examples of what the therapist can say to introduce the activity, guide the patient, and handle potential difficulties.
5.  **Patient Exercise/Worksheet:** A template for any exercise or worksheet the patient will complete during the session.

**Detailed Session Plan (Markdown):**
"""

    response = client.models.generate_content(
        model="gemini-2.5-pro",
        contents=prompt
    )

    return response.text

    # except Exception as e:
    #     error_message = f"An error occurred during generation or validation: {e}"
    #     if "response" in locals() and hasattr(response, "text"):
    #         error_message += f"\nRaw response text: {response.text}"
    #     raise Exception(error_message) from e


# --- Example Usage ---
#
# (This part is just to show you how to call the new function)
#
# import os
# from .models import CharacterProfile # Make sure this import works
#
# # 1. Initialize the client as shown in your example
# client = get_genai_client()
#
# # 2. Define your model and prompt
# # Use a model that supports JSON mode
# model_id = "gemini-2.5-pro"
# test_description = (
#     "Subject is a 30-year-old male software engineer. "
#     "He reports persistent feelings of anxiety in social situations, "
#     "actively avoids public speaking, and spends most of his free time "
#     "on solitary hobbies like coding and complex model building (planes, ships). "
#     "He is highly organized and detail-oriented, but finds collaborative "
#     "work 'draining'."
# )
#
# # 3. Call the function
# try:
#     profile = generate_character_profile(
#         description=test_description,
#         client=client,
#         model_id=model_id
#     )
#     print("Successfully generated profile:")
#     print(profile.model_dump_json(indent=2))
#
# except Exception as e:
#     print(e)
#
