from datetime import date
import json
from datetime import date
import os
from .models import CharacterProfile, TCCProgram

from google import genai
from google.genai import types

SYSTEM_PROMPT = f"""
You are a clinical psychologist and career counselor. Your task is to analyze the provided character description and generate a clinical profile in JSON format.

Today's date is: {date.today().isoformat()}

**Instructions:**

1.  **Analyze the character description** to identify potential DSM-5 diagnoses and assess their personality using the Holland Code (RIASEC) model.
2.  **Generate a JSON object** that strictly adheres to the following schema.
3.  **Output language:** The output must be in French.

**JSON Schema:**

```json
{{
  "character_name": "string",
  "profile_date": "YYYY-MM-DD",
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
*   Ensure the `profile_date` is set to today's date.
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
        temperature=1.0,
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
    description: str, model_id: str) -> CharacterProfile:
    """
    Generates a character profile using a generative model and validates the
    JSON output against the CharacterProfile Pydantic model.
    """
    # try:
        # generation_config = types.GenerationConfig(
        #     response_mime_type="application/json",
        #     response_schema=CharacterProfile,
        #     temperature=1.0,
        #     top_p=1,
        #     max_output_tokens=8192,
        # )

    generation_config = types.GenerateContentConfig(
        response_schema=CharacterProfile,
        response_mime_type="application/json",
        temperature=1.0,
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
    return response.parsed

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
