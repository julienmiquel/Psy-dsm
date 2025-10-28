from google.adk.agents import LlmAgent
from .models import CharacterProfile

# The instruction for the agent.
instruction = """
You are a clinical psychologist and career counselor.
Your task is to ask the user clarifying questions to build a comprehensive character profile.
This includes:
1.  A clinical diagnosis based on DSM-5 criteria.
2.  A Holland Code (RIASEC) assessment.

You must ask at least 7 targeted questions to gather sufficient information for both assessments before providing the final profile.
Once your analysis is complete, you MUST return a valid `CharacterProfile` object containing both the clinical findings and the Holland Code assessment.
"""

# Create the agent.
agent = LlmAgent(
    name="pathology_agent",
    instruction=instruction,
    output_schema=CharacterProfile,
)
