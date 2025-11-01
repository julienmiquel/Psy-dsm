from google import genai
from google.genai import types
from .models import CharacterProfile

def generate_profile_from_gemini(
    description: str, system_prompt: str, client: genai.Client
) -> CharacterProfile:
    """
    Calls the Gemini API to generate the character profile
    using the genai.Client() and function calling, then
    validates the result with Pydantic.
    """
    pydantic_schema_dict = CharacterProfile.model_json_schema()

    save_profile_tool = types.FunctionDeclaration(
        name="save_character_profile",
        description="Saves the generated clinical profile for the character.",
        parameters_json_schema=pydantic_schema_dict,
    )

    character_tool_config = types.Tool(function_declarations=[save_profile_tool])

    config = types.GenerateContentConfig(
        tools=[character_tool_config],
        tool_config=types.ToolConfig(
            function_calling_config=types.FunctionCallingConfig(mode="ANY")
        ),
    )

    model = client.models.get('gemini-1.5-flash')

    try:
        # Correctly use the system prompt and user input
        response = model.generate_content(
            contents=[
                types.Content(parts=[types.Part(text=system_prompt)], role="system"),
                types.Content(parts=[types.Part(text=description)], role="user")
            ],
            config=config,
        )

        if not response.function_calls:
            if not response.candidates:
                block_reason = response.prompt_feedback.block_reason
                safety_ratings = response.prompt_feedback.safety_ratings
                raise Exception(
                    f"Request was blocked. Reason: {block_reason}. Details: {safety_ratings}"
                )
            raise Exception(
                "Model did not return a function call. Check prompt or model version."
            )

        func_call = response.function_calls[0]

        if func_call.name != "save_character_profile":
            raise Exception(f"Unexpected function call: {func_call.name}")

        profile_dict = dict(func_call.args)

        profile_model = CharacterProfile.model_validate(profile_dict)

        return profile_model

    except Exception as e:
        raise Exception(f"An error occurred during generation or validation: {e}")
