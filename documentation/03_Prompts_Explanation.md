# Prompts & Logic

The project uses "System Prompts" to define the role of the AI.

## Prompt Strategy
All prompts are located in `src/app/prompts/`. They share a common structure:
1.  **Role Definition**: "You are a clinical psychologist..."
2.  **Context**: "Today's date is..."
3.  **Task**: "Analyze the character description..."
4.  **Schema Enforcement**: "Generate a JSON object that strictly adheres to the following schema..." followed by the JSON schema representation.
5.  **Constraints**: "Output language: French", "No markdown", "Explain reasoning".

## Key Prompts

### `riasec.md`
*   **Goal**: General psychological profile + Basic Interest (RIASEC).
*   **Use Case**: Initial screening, general personality overview.
*   **Key Instruction**: "Identify potential DSM-5 diagnoses and assess their personality using the Holland Code."

### `hexa3d.md`
*   **Goal**: Deep career/interest profiling.
*   **Use Case**: Career counseling, detailed personality structure.
*   **Key Instruction**: Assess personality using the Hexa3D model (Activity, Quality, Profession domains). requires inferring these distinct domains from a single text description.

### `tcc.md`
*   **Goal**: Treatment planning.
*   **Input**: Takes the *output* of the profile generation (JSON) as input, not just the raw text.
*   **Key Instruction**: "Create a TCC program adapted to manage disorder."

## Code Implementation (`services.py`)

*   `load_prompt(filename)`: Reads the markdown file.
*   `_generate_profile(...)`:
    1.  Loads the prompt.
    2.  Appends the user's character description: `f"{system_prompt}\n\nCharacter Description:\n{description}"`.
    3.  Calls `client.models.generate_content` with `response_schema` set to the Pydantic class. This forces the model to output valid JSON.
    4.  Parses the response into the object.
