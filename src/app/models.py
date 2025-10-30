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

class HollandCode(BaseModel):
    theme: str = Field(description="The dominant Holland Code theme (e.g., 'Social').")
    score: int = Field(description="Score for the theme (typically 1-10).")
    description: str = Field(description="Brief description of the theme.")

class HollandCodeAssessment(BaseModel):
    """Represents a Holland Code (RIASEC) assessment."""
    riasec_scores: List[HollandCode] = Field(default_factory=list, description="List of RIASEC scores.")
    top_themes: List[str] = Field(description="The top 2-3 RIASEC themes that best fit the character.")
    summary: str = Field(description="A summary of the Holland Code assessment.")

class CharacterProfile(BaseModel):
    character_name: str
    profile_date: str = Field(description="Date of profile generation in YYYY-MM-DD format")
    overall_assessment_summary: Optional[str] = Field(None, description="A brief summary of the clinical assessment")
    holland_code_assessment: Optional[HollandCodeAssessment] = Field(None, description="Holland Code (RIASEC) assessment results.")
    character_id: Optional[str] = None
    diagnoses: List[DiagnosisEntry] = Field(default_factory=list)



class Activity(BaseModel):
    """Représente une intervention ou un exercice spécifique au sein d'un module."""
    title: str
    details: List[str] = Field(default_factory=list)

class Module(BaseModel):
    """Représente un module complet du programme TCC."""
    title: str
    session_range: str
    objective: str
    activities: List[Activity] = Field(default_factory=list)

class TCCProgram(BaseModel):
    """Modélise l'ensemble du programme de Thérapie Comportementale et Cognitive."""
    title: str
    global_objective: str
    modules: List[Module] = Field(default_factory=list)