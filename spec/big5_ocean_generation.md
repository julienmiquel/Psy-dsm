# Feature: Big 5 (OCEAN) Personality Assessment

## Description

This feature extends the character profile generation to include an assessment based on the Big 5 (OCEAN) personality model. The system analyzes the character description to evaluate five key personality traits: Openness, Conscientiousness, Extraversion, Agreeableness, and Neuroticism.

## Theory

The Big Five personality traits, also known as the five-factor model (FFM) and the OCEAN model, is a taxonomy, or grouping, for personality traits. The five factors are:

-   **Openness to Experience (Ouverture):** Appreciating art, emotion, adventure, unusual ideas, curiosity, and variety of experience.
-   **Conscientiousness (Conscience):** A tendency to be organized and dependable, show self-discipline, act dutifully, aim for achievement, and prefer planned rather than spontaneous behavior.
-   **Extraversion (Extraversion):** Energy, positive emotions, surgency, assertiveness, sociability and the tendency to seek stimulation in the company of others, and talkativeness.
-   **Agreeableness (Agréabilité):** A tendency to be compassionate and cooperative rather than suspicious and antagonistic towards others.
-   **Neuroticism (Névrosisme):** The tendency to experience unpleasant emotions easily, such as anger, anxiety, depression, and vulnerability.

## Data Model

The assessment is represented by the `OceanAssessment` model, which contains a list of `OceanTrait` objects and a summary.

### OceanTrait

| Field | Type | Description |
| :--- | :--- | :--- |
| `trait` | `str` | The name of the trait (e.g., "Openness"). |
| `score` | `int` | A numerical score representing the intensity of the trait (typically 1-10 or 1-100). |
| `level` | `str` | A categorical level (e.g., "Low", "Medium", "High"). |
| `description` | `str` | A brief description of how this trait manifests in the character. |

### OceanAssessment

| Field | Type | Description |
| :--- | :--- | :--- |
| `ocean_scores` | `List[OceanTrait]` | A list containing the assessment for each of the five traits. |
| `summary` | `str` | A textual summary of the character's overall personality based on the Big 5 model. |

## Integration

The `OceanAssessment` is embedded within the `CharacterProfile` object under the `ocean_assessment` field. The generation logic in `src/app/services.py` has been updated to prompt the LLM to include this assessment in the output.
