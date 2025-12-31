"""
This module provides services for generating character profiles, TCC programs, and podcast scripts.
"""
import os
import functools
import streamlit as st
from google import genai
from google.genai import types
from google.genai.errors import ClientError
import logging
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
    retry_if_exception
)
import httpx

logger = logging.getLogger(__name__)

# Retry configuration
def is_retryable_error(exception):
    """Returns True if the exception is a retryable ClientError (429 or 5xx) or timeout."""
    return (isinstance(exception, ClientError) and (
        exception.code == 429 or exception.code >= 500
    )) or isinstance(exception, httpx.TimeoutException)

COMMON_RETRY_ARGS = {
    "stop": stop_after_attempt(5),
    "wait": wait_exponential(multiplier=2, min=2, max=60),
    "retry": retry_if_exception(is_retryable_error),
    "before_sleep": before_sleep_log(logger, logging.WARNING),
    "reraise": True
}

from app.models import (
    CharacterProfile,
    TCCProgram,
    Module,
    EvaluationResult,
    EvaluationResult,
    PodcastScript,
    SleepcastScript,
    AudioAnalysisResult
)
from app.prompts import (
    get_system_prompt_profile,
    SYSTEM_PROMPT_TCC,
    SYSTEM_PROMPT_JUDGE,
    SYSTEM_PROMPT_PODCAST,
    SYSTEM_PROMPT_AUDIO_ANALYSIS,
    SYSTEM_PROMPT_MODULE_PODCAST,
    SYSTEM_PROMPT_SLEEPCAST
)

@functools.lru_cache(maxsize=None)
def get_genai_client() -> genai.Client:
    """Returns a configured Gemini API client."""
    client = genai.Client(
        vertexai=True,
        project=os.getenv("GOOGLE_CLOUD_PROJECT"),
        location=os.getenv("GOOGLE_CLOUD_LOCATION"),
        http_options={'timeout': 600000}
    )
    return client


@retry(**COMMON_RETRY_ARGS)
def generate_tcc_program(
    profile: CharacterProfile, model_id: str) -> TCCProgram:
    """Generates a TCC program based on the character profile."""

    tools = [types.Tool(google_search=types.GoogleSearch())]
    generation_config = types.GenerateContentConfig(
        temperature=0.0,
        top_p=1,
        max_output_tokens=8192,
        tools=tools,
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=False, maximum_remote_calls=5),
    )

    prompt = f"{SYSTEM_PROMPT_TCC}\n\nCharacter PROFILE:\n{profile.model_dump_json()}\n\nUse the Google Search tool to ensure the proposed modules reflect the latest clinical research and TCC theories applicable to this profile."
    client = get_genai_client()
    
    response = client.models.generate_content(
        model=model_id,
        contents=prompt,
        config=generation_config,
    )
    
    try:
        text = response.text
        if not text:
             logger.error("Empty response text.")
             return None
        
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        
        return TCCProgram.model_validate_json(text)
    except Exception as e:
        logger.error(f"Failed to parse TCC JSON: {e}")
        return None

@retry(**COMMON_RETRY_ARGS)
def analyze_audio(audio_bytes: bytes, mime_type: str, model_id: str) -> AudioAnalysisResult:
    """
    Analyzes an audio file for diarization, emotional tone, and dark patterns.
    """
    client = get_genai_client()

    generation_config = types.GenerateContentConfig(
        response_schema=AudioAnalysisResult,
        response_mime_type="application/json",
        temperature=0.2,
        top_p=1,
        max_output_tokens=8192,
    )

    audio_part = types.Part.from_bytes(data=audio_bytes, mime_type=mime_type)

    response = client.models.generate_content(
        model=model_id,
        contents=[SYSTEM_PROMPT_AUDIO_ANALYSIS, audio_part],
        config=generation_config,
    )

    return response.parsed

@retry(**COMMON_RETRY_ARGS)
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

@retry(**COMMON_RETRY_ARGS)
def generate_module_podcast_script(
    profile: CharacterProfile, module: Module, model_id: str) -> PodcastScript:
    """Generates a podcast script for a specific module."""

    tools = [types.Tool(google_search=types.GoogleSearch())]
    generation_config = types.GenerateContentConfig(
        temperature=0.7,
        top_p=1,
        max_output_tokens=8192,
        tools=tools,
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=False, maximum_remote_calls=5),
    )

    prompt = (
        f"{SYSTEM_PROMPT_MODULE_PODCAST}\n\n"
        f"Character PROFILE:\n{profile.model_dump_json()}\n\n"
        f"MODULE DETAILS:\n{module.model_dump_json()}\n\n"
        f"Use Google Search to find specific, deep details and practical examples for this TCC module."
    )
    client = get_genai_client()
    
    response = client.models.generate_content(
        model=model_id,
        contents=prompt,
        config=generation_config,
    )
    
    try:
        # Manual parsing because we disabled response_mime_type="application/json"
        # to allow tools to work without conflict.
        text = response.text
        if not text:
             logger.error("Empty response text.")
             return None
        
        # Strip markdown code blocks if present
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        
        # Parse
        return PodcastScript.model_validate_json(text)
    except Exception as e:
        logger.error(f"Failed to parse JSON response: {e}")
        logger.debug(f"Raw text was: {response.text}")
        return None

@retry(**COMMON_RETRY_ARGS)
def generate_sleepcast_script(
    profile: CharacterProfile, module: Module, model_id: str) -> SleepcastScript:
    """Generates a Sleepcast script for a specific module."""

    # Note: We use manual parsing to ensure robustness and consistency with other functions
    # that might use tools, avoiding conflicts with strict JSON mode / AFC.
    
    generation_config = types.GenerateContentConfig(
        temperature=0.7,
        top_p=1,
        max_output_tokens=8192,
    )

    prompt = (
        f"{SYSTEM_PROMPT_SLEEPCAST}\n\n"
        f"Character PROFILE:\n{profile.model_dump_json()}\n\n"
        f"MODULE DETAILS:\n{module.model_dump_json()}\n\n"
    )
    client = get_genai_client()
    
    response = client.models.generate_content(
        model=model_id,
        contents=prompt,
        config=generation_config,
    )
    
    try:
        text = response.text
        if not text:
             logger.error(f"Sleepcast generation: Empty response text. Finish reason: {response.candidates[0].finish_reason if response.candidates else 'Unknown'}")
             return None
        
        # Strip markdown code blocks if present
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        
        # Parse
        return SleepcastScript.model_validate_json(text)
    except Exception as e:
        logger.error(f"Failed to parse Sleepcast JSON: {e}")
        logger.debug(f"Raw text was: {response.text}")
        return None

@retry(**COMMON_RETRY_ARGS)
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

@retry(**COMMON_RETRY_ARGS)
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
