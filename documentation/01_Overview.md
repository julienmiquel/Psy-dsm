# Project Overview: Psychological Analysis

## Goal
The goal of this project is to simulate a "virtual clinical psychologist" capable of analyzing character descriptions (or real person descriptions) to generate:
1.  **DSM-5 Diagnoses**: Identifying potential mental health disorders based on clinical criteria.
2.  **Psychometric Profiles**: assessing personality and interests using standard models like **Holland Code (RIASEC)** and **Hexa3D**.
3.  **Therapeutic Programs**: Generating tailored **Cognitive Behavioral Therapy (CBT/TCC)** programs.

## Core Workflow
The analysis pipeline follows these steps:
1.  **Input**: A text description of the character/person.
2.  **Prompt Engineering**: specific prompts (`riasec.md`, `hexa3d.md`) are selected based on the desired analysis.
3.  **LLM Inference**: The prompt + input is sent to Google Gemini (Pro 1.5 or Flash).
4.  **Structured Output**: The LLM returns a JSON object strictly adhering to Pydantic models defined in the code.
5.  **Storage/Presentation**: The result is stored (local/cloud) and presented via Streamlit.

## Key Components
*   **`src/app/services.py`**: The "brain" of the application. Handles prompt loading, LLM calls, and consistency checks.
*   **`src/app/models.py`**: Defines the "language" of the analysis (the data structure).
*   **`src/app/prompts/`**: Contains the "knowledge" instructions for the LLM.
