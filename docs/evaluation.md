# Evaluation Model

The `EvaluationResult` model encapsulates the output of the "LLM-as-a-Judge" system, which assesses the quality and accuracy of the generated clinical profiles.

## Underlying Theory

### LLM-as-a-Judge
This is an evaluation paradigm where a powerful LLM is used to grade the output of another AI system. In this context, it acts as a senior supervisor reviewing the work of a junior psychologist (the profile generator).

### Evaluation Criteria
The judge evaluates profiles based on four key dimensions:
1.  **Diagnostic Accuracy**: Does the diagnosis match the "Gold Standard" or the evidence in the text?
2.  **Holland Code Assessment**: Is the vocational profile logical given the character's description?
3.  **Completeness**: Are all required fields present?
4.  **Clarity and Coherence**: Is the profile written in clear, professional French?

## Data Model

### `EvaluationResult`

| Field | Type | Description |
| :--- | :--- | :--- |
| `score` | `int` | A numerical score from 1 to 5. |
| `rationale` | `str` | A detailed explanation justifying the assigned score. |

### Scoring Rubric
- **5 (Excellent)**: Matches or exceeds the gold standard.
- **4 (Good)**: Accurate with minor flaws.
- **3 (Acceptable)**: Generally correct but has significant omissions or minor inaccuracies.
- **2 (Poor)**: Significant inaccuracies.
- **1 (Very Poor)**: Completely wrong or irrelevant.

## AI Generation Process

1.  **Inputs**:
    - The original character description.
    - The *generated* `CharacterProfile` (the candidate).
    - A *golden* `CharacterProfile` (the ground truth/reference).
2.  **Prompting**: The `evaluate_profile_with_llm` function uses `SYSTEM_PROMPT_JUDGE`.
3.  **Output**: A JSON object containing the score and rationale.
