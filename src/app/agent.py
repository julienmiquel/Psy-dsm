from google.adk.agents import LlmAgent
from .models import CharacterProfile

# The instruction for the agent.
instruction = """
You are a clinical psychologist and forensic analyst.
Your task is to ask the user questions to determine the correct pathology and fill out the CharacterProfile data model.
You must ask at least 5 questions before you can make a diagnosis.
Once you have made a diagnosis, you must return a valid CharacterProfile object.
"""

# Create the agent.
agent = LlmAgent(
    name="pathology_agent",
    instruction=instruction,
    output_schema=CharacterProfile,
)
