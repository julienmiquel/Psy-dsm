# Psychological Assessments

This document details the personality and vocational interest assessments included in the character profile.

## Holland Code (RIASEC)

### Underlying Theory
The **Holland Codes** or the **RIASEC** model, developed by John L. Holland, refers to a theory of careers and vocational choice based upon personality types.
The six types are:
- **R**ealistic (Doers)
- **I**nvestigative (Thinkers)
- **A**rtistic (Creators)
- **S**ocial (Helpers)
- **E**nterprising (Persuaders)
- **C**onventional (Organizers)

### Model: `HollandCodeAssessment`
The `HollandCodeAssessment` model captures:
- `riasec_scores`: A list of scores (typically 1-10) for each of the six themes.
- `top_themes`: The 2-3 dominant themes that best characterize the individual.
- `summary`: A qualitative interpretation of the vocational profile.

### AI Generation
The LLM analyzes the character's reported behaviors, job history, and interests in the input text to infer their alignment with each RIASEC type.

## Big 5 (OCEAN)

### Underlying Theory
The **Big Five personality traits** (OCEAN) is a suggested taxonomy, or grouping, for personality traits.
- **O**penness to experience (inventive/curious vs. consistent/cautious)
- **C**onscientiousness (efficient/organized vs. easy-going/careless)
- **E**xtraversion (outgoing/energetic vs. solitary/reserved)
- **A**greeableness (friendly/compassionate vs. challenging/detached)
- **N**euroticism (sensitive/nervous vs. secure/confident)

### Model: `OceanAssessment`
The `OceanAssessment` model captures:
- `ocean_scores`: A list of `OceanTrait` objects.
    - Each trait has a `score`, a `level` (Low, Medium, High), and a `description`.
- `summary`: A narrative overview of the personality profile.

### AI Generation
The LLM infers personality traits from the character's emotional reactions, interpersonal dynamics, and life choices described in the input.
