# Technical Implementation Guide

This document provides detailed code samples to replicate the psychological analysis pipeline from scratch.

---

## 1. Environment Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd Psy-dsm

# Install dependencies
poetry install

# Set environment variables (create .env file)
cat > .env << EOF
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=europe-west4
DATABASE_SERVICE=local
EOF
```

---

## 2. Core Architecture

### 2.1 GenAI Client Initialization

The client is initialized using Vertex AI:

```python
# src/app/services.py (lines 34-42)
import os
from google import genai

def get_genai_client() -> genai.Client:
    """Initializes and caches the GenAI client."""
    client = genai.Client(
        vertexai=True,
        project=os.getenv("GOOGLE_CLOUD_PROJECT"),
        location=os.getenv("GOOGLE_CLOUD_LOCATION"),
    )
    return client
```

### 2.2 Prompt Loading Mechanism

Prompts are stored as markdown files and loaded dynamically:

```python
# src/app/services.py (lines 27-31)
from pathlib import Path

def load_prompt(filename: str) -> str:
    """Loads a prompt from the prompts directory."""
    prompt_path = Path(__file__).parent / "prompts" / filename
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()
```

---

## 3. Profile Generation Pipeline

### 3.1 The Core Generation Function

This is the heart of the analysis. It combines prompt, user input, and structured output:

```python
# src/app/services.py (lines 66-98)
import uuid
from datetime import datetime
from google.genai import types
from app.models import CharacterProfile

def _generate_profile(
    description: str, model_id: str, user_id: str, prompt_filename: str
) -> CharacterProfile:
    """Helper function to generate a character profile."""
    
    # 1. Configure LLM for structured JSON output
    generation_config = types.GenerateContentConfig(
        response_schema=CharacterProfile,  # <-- Forces output to match Pydantic model
        response_mime_type="application/json",
        temperature=0.0,  # Deterministic output
        top_p=1,
        max_output_tokens=8192,
    )

    # 2. Load and format the prompt
    system_prompt = load_prompt(prompt_filename).format(
        datetime=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    prompt = f"{system_prompt}\n\nCharacter Description:\n{description}"
    
    # 3. Call the LLM
    client = get_genai_client()
    response = client.models.generate_content(
        model=model_id,
        contents=prompt,
        config=generation_config,
    )

    # 4. Parse and enrich the result
    profile = response.parsed  # Automatically parsed into CharacterProfile
    if profile is None:
        raise Exception("Failed to generate character profile.")
    
    profile.character_id = str(uuid.uuid4())
    profile.raw_text_bloc = description
    
    # 5. Persist to database (abstracted by service layer)
    db_service.save_profile(profile, user_id)
    return profile
```

### 3.2 Public API Functions

```python
# src/app/services.py (lines 101-116)
def generate_character_profile(
    description: str, model_id: str, user_id: str
) -> CharacterProfile:
    """RIASEC-based profile generation."""
    return _generate_profile(description, model_id, user_id, "riasec.md")


def generate_hexa3d_profile(
    description: str, model_id: str, user_id: str
) -> CharacterProfile:
    """Hexa3D-based profile generation (more detailed)."""
    return _generate_profile(description, model_id, user_id, "hexa3d.md")
```

---

## 4. Data Models (Pydantic)

### 4.1 Diagnosis Structure

```python
# src/app/models.py (lines 9-22)
from pydantic import BaseModel, Field
from typing import List, Optional

class DiagnosisSpecifier(BaseModel):
    specifier_type: str
    value: str

class DiagnosisEntry(BaseModel):
    disorder_name: str
    dsm_category: str
    criteria_met: List[str] = Field(
        default_factory=list,
        description="Specific DSM-5 criteria codes/text met"
    )
    specifiers: List[DiagnosisSpecifier] = Field(default_factory=list)
    dsm_code: Optional[str] = Field(None, description="Official DSM-5 code")
    functional_impairment: Optional[str] = Field(None)
    diagnostic_note: Optional[str] = Field(None)
```

### 4.2 RIASEC Assessment

```python
# src/app/models.py (lines 24-34)
class HollandCode(BaseModel):
    theme: str = Field(description="e.g., 'Social', 'Investigative'")
    score: int = Field(description="Score (1-10)")
    description: str

class HollandCodeAssessment(BaseModel):
    riasec_scores: List[HollandCode] = Field(default_factory=list)
    top_themes: List[str] = Field(description="Top 2-3 RIASEC themes")
    summary: str
```

### 4.3 The Main CharacterProfile

```python
# src/app/models.py (lines 122-134)
class CharacterProfile(BaseModel):
    character_name: str
    profile_datetime: str = Field(
        description="YYYY-MM-DD HH:MM:SS"
    )
    overall_assessment_summary: Optional[str] = None
    holland_code_assessment: Optional[HollandCodeAssessment] = None
    hexa3d_assessment: Optional[Hexa3DAssessment] = None
    character_id: Optional[str] = None
    user_id: Optional[str] = None
    diagnoses: List[DiagnosisEntry] = Field(default_factory=list)
    raw_text_bloc: Optional[str] = None
    tcc_program: Optional[TCCProgram] = None
```

---

## 5. Prompt Engineering (System Instructions)

### 5.1 RIASEC Prompt Template

```markdown
<!-- src/app/prompts/riasec.md -->
You are a clinical psychologist and career counselor. Your task is to
analyze the provided character description and generate a clinical
profile in JSON format.

Today's date is: {datetime}

**Instructions:**
1. Analyze the character description to identify potential DSM-5
   diagnoses and assess their personality using the Holland Code
   (RIASEC) model.
2. Generate a JSON object that strictly adheres to the following schema.
3. Output language: French.

**JSON Schema:**
{{
  "character_name": "string",
  "profile_datetime": "YYYY-MM-DD HH:MM:SS",
  "overall_assessment_summary": "string",
  "holland_code_assessment": {{ ... }},
  "diagnoses": [ ... ]
}}

**Important:**
- If no disorder is apparent, provide an empty `diagnoses` array.
- For any diagnosis, list the specific DSM-5 criteria met.
- Output MUST be a single, valid JSON object.
```

---

## 6. TCC (CBT) Program Generation

This takes an *existing* profile as input to generate therapy plans:

```python
# src/app/services.py (lines 45-63)
from app.models import TCCProgram

def generate_tcc_program(profile: CharacterProfile, model_id: str) -> TCCProgram:
    """Generates a Cognitive Behavioral Therapy program."""
    generation_config = types.GenerateContentConfig(
        response_schema=TCCProgram,
        response_mime_type="application/json",
        temperature=0.0,
        top_p=1,
        max_output_tokens=8192,
    )

    system_prompt = load_prompt("tcc.md")
    prompt = f"{system_prompt}\n\nCharacter PROFILE:\n{profile.model_dump_json()}"
    
    client = get_genai_client()
    response = client.models.generate_content(
        model=model_id,
        contents=prompt,
        config=generation_config,
    )
    return response.parsed
```

---

## 7. CHC Cognitive Profiling

A separate analysis focusing on cognitive abilities:

```python
# src/app/psychometry_chc_generate.py (lines 64-93)
from app.chc_models import CHCModel

SYSTEM_PROMPT_CHC = """
You are a psychometrician. Analyze the text and generate a cognitive
profile based on the Cattell-Horn-Carroll (CHC) model.

**Schema:**
{{
  "g_factor": "number | null",
  "broad_abilities": [
    {{
      "id": "Gf", "name": "Fluid Intelligence",
      "narrow_abilities": [...]
    }}
  ]
}}
"""

def generate_chc_profile(
    description: str, model_id: str, user_id: str
) -> CHCModel:
    generation_config = types.GenerateContentConfig(
        response_schema=CHCModel,
        response_mime_type="application/json",
        temperature=0.0,
        max_output_tokens=8192,
    )

    prompt = f"{SYSTEM_PROMPT_CHC}\n\nDescription:\n{description}"
    client = get_genai_client()
    response = client.models.generate_content(
        model=model_id,
        contents=prompt,
        config=generation_config,
    )
    return response.parsed
```

---

## 8. Profile Comparison (Longitudinal Tracking)

```python
# src/app/comparison_service.py (lines 24-78)
from typing import Dict, Any

def compare_character_profiles(
    profile1: CharacterProfile,
    profile2: CharacterProfile
) -> Dict[str, Any]:
    """Compares two profiles, returning structured diffs."""
    comparison = {}

    # --- Holland Score Delta ---
    p1_scores = {s.theme: s.score for s in profile1.holland_code_assessment.riasec_scores}
    p2_scores = {s.theme: s.score for s in profile2.holland_code_assessment.riasec_scores}
    
    holland_comparison = []
    for theme in sorted(p1_scores.keys()):
        score1 = p1_scores.get(theme, 0)
        score2 = p2_scores.get(theme, 0)
        holland_comparison.append({
            "theme": theme,
            "score1": score1,
            "score2": score2,
            "difference": score2 - score1
        })
    comparison['holland_comparison'] = holland_comparison

    # --- Diagnosis Changes ---
    p1_diag = {d.disorder_name: d for d in profile1.diagnoses}
    p2_diag = {d.disorder_name: d for d in profile2.diagnoses}

    comparison['diagnoses_comparison'] = {
        "added": [p2_diag[n].model_dump() for n in p2_diag if n not in p1_diag],
        "removed": [p1_diag[n].model_dump() for n in p1_diag if n not in p2_diag],
    }
    return comparison
```

---

## 9. Complete Standalone Example

```python
"""standalone_analysis.py - Run this file directly."""
import os
from dotenv import load_dotenv

# 1. Load environment
load_dotenv()
os.environ.setdefault("DATABASE_SERVICE", "local")

# 2. Import after env is set
from app.services import generate_character_profile, generate_tcc_program

# 3. Define input
description = """
Jean est un homme de 45 ans qui se présente avec une fatigue chronique,
un manque de motivation, et des difficultés de concentration au travail
depuis 6 mois. Il rapporte des troubles du sommeil et une perte d'intérêt
pour ses hobbies habituels. Il a tendance à s'isoler socialement.
"""

# 4. Generate profile
profile = generate_character_profile(
    description=description,
    model_id="gemini-2.5-flash",
    user_id="demo_user"
)

# 5. Print results
print(f"Name: {profile.character_name}")
print(f"Summary: {profile.overall_assessment_summary[:200]}...")
print("\nDiagnoses:")
for d in profile.diagnoses:
    print(f"  - {d.disorder_name} ({d.dsm_code})")
    print(f"    Criteria: {d.criteria_met[:2]}...")

print("\nRIASEC Scores:")
for score in profile.holland_code_assessment.riasec_scores:
    print(f"  {score.theme}: {score.score}/10")

# 6. Generate TCC Program
tcc = generate_tcc_program(profile, "gemini-2.5-flash")
print(f"\nTCC Program: {tcc.title}")
for module in tcc.modules[:2]:
    print(f"  - {module.title} ({module.session_range})")
```

Run with:
```bash
poetry run python standalone_analysis.py
```
