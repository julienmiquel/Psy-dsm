"""
This module provides services for generating character profiles, TCC programs, and podcast scripts.
"""
import os
from google import genai
from google.genai import types
from app.models import CharacterProfile, TCCProgram, EvaluationResult, PodcastScript
from app.prompts import (
    get_system_prompt_profile,
    SYSTEM_PROMPT_TCC,
    SYSTEM_PROMPT_JUDGE,
    SYSTEM_PROMPT_PODCAST
)

def get_genai_client() -> genai.Client:
    """Returns a configured Gemini API client."""
    client = genai.Client(
        vertexai=True,
        project=os.getenv("GOOGLE_CLOUD_PROJECT"),
        location=os.getenv("GOOGLE_CLOUD_LOCATION"),
    )
    return client

def generate_tcc_program(
    profile: CharacterProfile, model_id: str) -> TCCProgram:
    """Generates a TCC program based on the character profile."""

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

def generate_podcast_script(
    profile: CharacterProfile, tcc_program: TCCProgram, model_id: str) -> PodcastScript:
    """Generates a podcast script based on the profile and TCC program."""

    generation_config = types.GenerateContentConfig(
        response_schema=PodcastScript,
        response_mime_type="application/json",
        temperature=0.7,
        top_p=1,
        max_output_tokens=8192,
    )

    prompt = (
        f"{SYSTEM_PROMPT_PODCAST}\n\n"
        f"Character PROFILE:\n{profile.model_dump_json()}\n\n"
        f"TCC PROGRAM:\n{tcc_program.model_dump_json()}"
    )
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

    prompt = f"{get_system_prompt_profile()}\n\nCharacter Description:\n{description}"
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
