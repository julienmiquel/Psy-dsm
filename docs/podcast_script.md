# Podcast Script

The `PodcastScript` model represents a generated audio script designed to explain the clinical profile and therapy plan to the user in an engaging format.

## Concept

This feature uses the concept of **Psychoeducation** delivered through a modern medium. By turning the clinical report and TCC plan into a dialogue, it makes the information more accessible, less intimidating, and easier to digest for the patient or user.

## Model Structure

- **PodcastScript**:
    - `title`: Creative title for the episode.
    - `target_audience`: Who this is for (usually the patient).
    - `segments`: A list of `PodcastSegment` objects.
- **PodcastSegment**:
    - `speaker`: Identifies who is talking (Host vs. Expert).
    - `text`: The actual dialogue.

## AI Generation Process

The script is generated using the `SYSTEM_PROMPT_PODCAST`.
1.  **Inputs**:
    - `CharacterProfile`: To personalize the discussion of symptoms and traits.
    - `TCCProgram`: To explain the proposed solutions.
2.  **Prompting**: The LLM acts as a scriptwriter and psychologist.
    - It is instructed to create a dialogue between a Host and an Expert.
    - The tone should be supportive and educational.
    - It must synthesize the technical details of the profile and program into conversational French.
3.  **Parsing**: The JSON output is validated against `PodcastScript`.
