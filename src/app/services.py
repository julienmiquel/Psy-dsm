from datetime import date
from google import genai
from google.genai import types
from .models import CharacterProfile

# Updated system prompt to explicitly command the AI to use the tool
SYSTEM_PROMPT = f"""
You are a clinical psychologist and career counselor.
Your tasks are to:
1. Analyze the provided character description to generate a clinical profile based on DSM-5 criteria.
2. Conduct a Holland Code (RIASEC) assessment to identify the character's primary occupational themes.

Today's date is: {date.today().isoformat()}

CRITICAL INSTRUCTION: You MUST call the 'save_character_profile' function
with your complete analysis, including both the clinical profile and the Holland Code assessment.
Do not provide a text response, only call the function.

Clinical Profile Instructions:
- For any diagnosis, you MUST list the specific DSM-5 criteria met in the 'criteria_met' field.
- If no disorder is apparent, use an empty 'diagnoses' array and explain your reasoning in the 'overall_assessment_summary'.
- Be objective and clinical in your tone. Do not invent information.
- Ensure the 'profile_date' is set to today's date in 'YYYY-MM-DD' format.

Holland Code Assessment Instructions:
- Populate the 'holland_code_assessment' field.
- Provide a score (1-10) for each of the six RIASEC themes (Realistic, Investigative, Artistic, Social, Enterprising, Conventional).
- Identify the top 2-3 themes in the 'top_themes' list.
- Write a concise summary of the assessment in the 'summary' field.
"""

def generate_character_profile(description: str, client: genai.Client) -> CharacterProfile:
    """
    Calls the Gemini API to generate the character profile
    using the genai.Client() and function calling, then
    validates the result with Pydantic.
    """
    pydantic_schema_dict = CharacterProfile.model_json_schema()

    save_profile_tool = types.FunctionDeclaration(
        name="save_character_profile",
        description="Saves the generated clinical profile for the character.",
        parameters_json_schema=pydantic_schema_dict
    )

    character_tool_config = types.Tool(function_declarations=[save_profile_tool])

    config = types.GenerateContentConfig(
        tools=[character_tool_config],
        tool_config=types.ToolConfig(
            function_calling_config=types.FunctionCallingConfig(mode='ANY')
        ),
    )

    try:
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=description,
            config=config
        )

        if not response.function_calls:
            if not response.candidates:
                block_reason = response.prompt_feedback.block_reason
                safety_ratings = response.prompt_feedback.safety_ratings
                raise Exception(f"Request was blocked. Reason: {block_reason}. Details: {safety_ratings}")
            raise Exception("Model did not return a function call. Check prompt or model version.")

        func_call = response.function_calls[0]

        if func_call.name != "save_character_profile":
            raise Exception(f"Unexpected function call: {func_call.name}")

        profile_dict = dict(func_call.args)

        profile_model = CharacterProfile.model_validate(profile_dict)

        return profile_model

    except Exception as e:
        raise Exception(f"An error occurred during generation or validation: {e}")
