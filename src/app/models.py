from typing import List, Optional
from pydantic import BaseModel, Field

class DiagnosisSpecifier(BaseModel):
    specifier_type: str
    value: str

class DiagnosisEntry(BaseModel):
    disorder_name: str
    dsm_category: str
    criteria_met: List[str] = Field(default_factory=list, description="Specific DSM-5 criteria codes/text met")
    specifiers: List[DiagnosisSpecifier] = Field(default_factory=list)
    dsm_code: Optional[str] = Field(None, description="The official DSM-5 code, e.g., '301.7'")
    functional_impairment: Optional[str] = Field(None, description="How the disorder impairs the character's life")
    diagnostic_note: Optional[str] = Field(None, description="Clinical notes or differential diagnosis")

class CharacterProfile(BaseModel):
    character_name: str
    profile_date: str = Field(description="Date of profile generation in YYYY-MM-DD format")
    overall_assessment_summary: Optional[str] = Field(None, description="A brief summary of the clinical assessment")
    character_id: Optional[str] = None
    diagnoses: List[DiagnosisEntry] = Field(default_factory=list)
