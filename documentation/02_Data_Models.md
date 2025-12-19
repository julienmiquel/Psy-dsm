# Data Models Structure

The output of the analysis is strictly typed using Pydantic models. This ensures consistency and allows for easy parsing.

## 1. CharacterProfile (`CharacterProfile`)
The root object for any analysis.
*   `character_name`: Name of the subject.
*   `profile_datetime`: Timestamp of analysis.
*   `overall_assessment_summary`: Textual summary of the psychologist's view.
*   `diagnoses`: List of `DiagnosisEntry`.
*   `holland_code_assessment`: Optional `HollandCodeAssessment`.
*   `hexa3d_assessment`: Optional `Hexa3DAssessment`.
*   `tcc_program`: Optional `TCCProgram`.

## 2. Diagnosis (`DiagnosisEntry`)
Represents a single DSM-5 disorder.
*   `disorder_name`: e.g., "Major Depressive Disorder".
*   `dsm_category`: e.g., "Depressive Disorders".
*   `criteria_met`: List of specific criteria matched (e.g., "A. Depressed mood").
*   `functional_impairment`: How it affects life.
*   `dsm_code`: Official code (e.g., "296.20").

## 3. Psychometrics

### RIASEC (`HollandCodeAssessment`)
*   `riasec_scores`: List of 6 scores (Realistic, Investigative, Artistic, Social, Enterprising, Conventional).
*   `top_themes`: 3 dominant themes.
*   `summary`: Interpretation.

### Hexa3D (`Hexa3DAssessment`)
A more complex version of RIASEC.
*   **3 Domains**: Activities, Qualities, Professions. Each has its own RIASEC score.
*   **Global Profile**: Synthesis of the 3 domains.
*   **Secondary Dimensions**: Prestige (High/Low) and Gender (Masculine/Feminine).

## 4. TCC Program (`TCCProgram`)
*   `global_objective`: Main goal of therapy.
*   `modules`: List of therapeutic modules (Time range, Objective, Activities).
