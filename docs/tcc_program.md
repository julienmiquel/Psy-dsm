# TCC Program (Cognitive Behavioral Therapy)

The `TCCProgram` model represents a structured therapeutic intervention plan based on Cognitive Behavioral Therapy (CBT) principles.

## Underlying Theory

**Cognitive Behavioral Therapy (TCC in French)** is a psycho-social intervention that aims to improve mental health. It focuses on challenging and changing cognitive distortions (e.g., thoughts, beliefs, and attitudes) and behaviors, improving emotional regulation, and the development of personal coping strategies that target solving current problems.

A typical TCC program is structured into **modules**, each addressing specific objectives through **activities** or exercises.

## Purpose of the Model

The `TCCProgram` model structures the therapeutic plan into a machine-readable format that can be:
1.  **Displayed**: Presented to the user as a step-by-step guide.
2.  **Processed**: Used to generate scripts (like podcasts) or reminders.

## Model Structure

- **TCCProgram**: The root object.
    - `global_objective`: The overarching goal of the therapy (e.g., "Reduce social anxiety").
    - `modules`: A list of ordered `Module` objects.
- **Module**: A distinct phase of therapy.
    - `title`: e.g., "Psychoeducation".
    - `session_range`: e.g., "Weeks 1-2".
    - `objective`: Specific goal for this module.
    - `activities`: List of `Activity` items (exercises, homework).

## AI Generation Process

The TCC program is generated using the `SYSTEM_PROMPT_TCC` in `src/app/prompts.py`.
1.  **Input**: The previously generated `CharacterProfile` (including diagnosis and traits).
2.  **Prompting**: The LLM is instructed to act as a clinical psychologist designing a TCC intervention.
    - It must tailor the interventions to the specific diagnosis (e.g., exposure therapy for phobias, DBT skills for borderline personality).
    - Output must be in French.
3.  **Parsing**: The output is validated against the `TCCProgram` schema.
