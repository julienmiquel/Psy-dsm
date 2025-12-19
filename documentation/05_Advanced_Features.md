# Advanced Features

Beyond the core psychological profile, the system supports advanced cognitive capabilities and longitudinal tracking.

## 1. Cognitive Profiling (CHC Model)
The system implements the **Cattell-Horn-Carroll (CHC)** theory of cognitive abilities.

*   **Source Code**: `src/app/psychometry_chc_generate.py`
*   **Model**: `CHCModel` (in `src/app/chc_models.py`)
*   **Logic**:
    *   Unlike RIASEC which uses a markdown prompt, the CHC prompt is embedded directly in the Python code (`SYSTEM_PROMPT_CHC`).
    *   It extracts **Broad Abilities** (e.g., Fluid Intelligence, Crystallized Intelligence) and **Narrow Abilities**.
    *   It assigns a score (1-10) where inferable.

### usage
```python
from app.psychometry_chc_generate import generate_chc_profile
profile = generate_chc_profile(description, model_id, user_id)
```

## 2. Profile Comparison (Longitudinal Analysis)
The system can track the evolution of a patient by comparing two profiles generated at different times.

*   **Source Code**: `src/app/comparison_service.py`
*   **Logic**:
    *   **Textual Diff**: Compares the `overall_assessment_summary`.
    *   **Data Diff**: Calculates the delta for RIASEC scores.
    *   **Diagnosis Diff**: Identifies `added`, `removed`, or `modified` diagnoses between the two snapshots.

### Usage
```python
from app.comparison_service import compare_character_profiles
diff = compare_character_profiles(old_profile, new_profile)
print(diff['diagnoses_comparison']['added'])
```
