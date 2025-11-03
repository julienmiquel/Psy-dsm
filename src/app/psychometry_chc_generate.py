from datetime import datetime
import json
import os
from google import genai
from google.genai import types

from app.chc_models import CHCModel

SYSTEM_PROMPT_CHC = f"""
You are a psychometrician. Your task is to analyze the provided text and generate a cognitive profile based on the Cattell-Horn-Carroll (CHC) model in JSON format.

Today's date is: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

**Instructions:**

1.  **Analyze the text** to assess the individual's cognitive abilities according to the CHC theory.
2.  **Identify broad and narrow abilities**. For each broad ability, list the relevant narrow abilities you can infer from the text.
3.  **Generate a JSON object** that strictly adheres to the following schema.
4.  **Output language:** The output must be in French.

**JSON Schema:**

```json
{{
  "character_name": "string",
  "profile_datetime": "YYYY-MM-DD HH:MM:SS",
  "g_factor": "number | null",
  "broad_abilities": [
    {{
      "id": "string (e.g., 'Gf', 'Gc')",
      "name": "string (e.g., 'Fluid Intelligence')",
      "description": "string",
      "narrow_abilities": [
        {{
          "id": "string",
          "name": "string",
          "description": "string",
          "score": "number | null"
        }}
      ],
      "score": "number | null"
    }}
  ]
}}
```

**Important:**

*   Provide scores where possible, on a scale of 1 to 10, where 5 is average.
*   If an ability cannot be assessed, you can omit it or set the score to null.
*   Your output **must** be a single, valid JSON object, without any markdown formatting or extra text.
"""


def get_genai_client() -> genai.Client:
    client = genai.Client(
        vertexai=True,
        project=os.getenv("GOOGLE_CLOUD_PROJECT"),
        location=os.getenv("GOOGLE_CLOUD_LOCATION"),
    )
    return client


def generate_chc_profile(
    description: str, model_id: str, user_id: str
) -> CHCModel:
    """
    Generates a CHC profile using a generative model and validates the
    JSON output against the CHCModel Pydantic model.
    """

    generation_config = types.GenerateContentConfig(
        response_schema=CHCModel,
        response_mime_type="application/json",
        temperature=0.0,
        top_p=1,
        max_output_tokens=8192,
    )

    prompt = f"{SYSTEM_PROMPT_CHC}\n\nCharacter Description:\n{description}"
    client = get_genai_client()
    response = client.models.generate_content(
        model=model_id,
        contents=prompt,
        config=generation_config,
    )

    # Parse the JSON string into the Pydantic model
    profile = response.parsed
    if profile is None:
        raise Exception("Failed to generate CHC profile. The model did not return a valid JSON object.")
    profile.raw_text_bloc = description
    return profile
