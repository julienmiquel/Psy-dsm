# Chat-Based Profile Generation

This document describes the interactive chat feature for generating clinical profiles.

## Overview
The Chat-Based Profile Generation feature allows users to interact with an AI agent ("Pathology Agent") to build a character profile through conversation. Instead of providing a single static description, the user answers questions posed by the agent, allowing for a more detailed and refined assessment.

## Underlying Technology

### Google Agent Development Kit (ADK)
The feature is powered by the `google-adk` library.
- **`LlmAgent`**: The core logic is encapsulated in an `LlmAgent` configured with a specific persona.
- **Session Management**: The conversation state is managed to ensure continuity.

## Workflow

1.  **Initiation**: The user starts a chat session.
2.  **Investigation**: The agent asks a series of targeted questions (minimum 7) to gather information about:
    - Symptoms and behaviors (for DSM-5 diagnosis).
    - Interests and preferences (for Holland Code).
3.  **Completion**: Once the agent has sufficient information, it generates a final `CharacterProfile` object.
4.  **Display**: The application detects the structured output and renders the full clinical profile.

## Agent Persona
The agent is instructed to act as a **Clinical Psychologist and Career Counselor**. Its goal is to be inquisitive but professional, digging for details that are relevant for a differential diagnosis.
