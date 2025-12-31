"""Data models for the application."""
from typing import List, Optional
from pydantic import BaseModel, Field

class DiagnosisSpecifier(BaseModel):
    """
    Represents a specific feature or severity of a diagnosis.
    e.g., 'Severity: Severe' or 'Course: Episodic'.
    """
    specifier_type: str
    value: str

class DiagnosisEntry(BaseModel):
    """
    Represents a single DSM-5 diagnosis identified for the character.
    Includes the disorder name, criteria met, and functional impact.
    """
    disorder_name: str
    dsm_category: str
    criteria_met: List[str] = Field(
        default_factory=list,
        description="Specific DSM-5 criteria codes/text met"
    )
    specifiers: List[DiagnosisSpecifier] = Field(default_factory=list)
    dsm_code: Optional[str] = Field(
        None,
        description="The official DSM-5 code, e.g., '301.7'"
    )
    functional_impairment: Optional[str] = Field(
        None,
        description="How the disorder impairs the character's life"
    )
    diagnostic_note: Optional[str] = Field(
        None,
        description="Clinical notes or differential diagnosis"
    )

class HollandCode(BaseModel):
    """
    Represents a score for a single RIASEC theme (Realistic, Investigative, etc.).
    """
    theme: str = Field(description="The dominant Holland Code theme (e.g., 'Social').")
    score: int = Field(description="Score for the theme (typically 1-10).")
    description: str = Field(description="Brief description of the theme.")

class HollandCodeAssessment(BaseModel):
    """Represents a Holland Code (RIASEC) assessment."""
    riasec_scores: List[HollandCode] = Field(
        default_factory=list,
        description="List of RIASEC scores."
    )
    top_themes: List[str] = Field(
        description="The top 2-3 RIASEC themes that best fit the character."
    )
    summary: str = Field(description="A summary of the Holland Code assessment.")

class OceanTrait(BaseModel):
    """
    Represents a score for a single Big 5 trait (Openness, Conscientiousness, etc.).
    """
    trait: str = Field(description="The trait name (e.g., 'Openness').")
    score: int = Field(description="Score for the trait (typically 1-100 or 1-10).")
    level: str = Field(description="Level of the trait (e.g., 'Low', 'Medium', 'High').")
    description: str = Field(
        description="Brief description of the trait manifestation in the character."
    )

class OceanAssessment(BaseModel):
    """Represents a Big 5 (OCEAN) personality assessment."""
    ocean_scores: List[OceanTrait] = Field(
        default_factory=list,
        description="List of OCEAN traits and scores."
    )
    summary: str = Field(description="A summary of the Big 5 assessment.")

class CharacterProfile(BaseModel):
    """
    The main data model for a character's clinical profile.
    Aggregates diagnoses, personality assessments, and vocational interests.
    """
    character_name: str
    profile_date: str = Field(description="Date of profile generation in YYYY-MM-DD format")
    overall_assessment_summary: Optional[str] = Field(
        None,
        description="A brief summary of the clinical assessment"
    )
    holland_code_assessment: Optional[HollandCodeAssessment] = Field(
        None,
        description="Holland Code (RIASEC) assessment results."
    )
    ocean_assessment: Optional[OceanAssessment] = Field(
        None,
        description="Big 5 (OCEAN) personality assessment results."
    )
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

class EvaluationResult(BaseModel):
    """
    Represents the result of an AI evaluation of the profile quality.
    """
    score: int = Field(description="The quality score from 1 (poor) to 5 (excellent).")
    rationale: str = Field(description="The rationale for the given score.")


class PodcastSegment(BaseModel):
    """
    Represents a single turn of dialogue in the podcast script.
    """
    speaker: str = Field(description="The name of the speaker (e.g., Host, Guest, Psychologist).")
    text: str = Field(description="The dialogue spoken by the speaker.")

class PodcastScript(BaseModel):
    """
    Represents a full podcast script generated from the profile.
    """
    title: str = Field(description="Podcast title.")
    target_audience: str = Field(description="Target audience.")
    segments: List[PodcastSegment] = Field(
        default_factory=list,
        description="Dialogue segments."
    )

class SleepcastScript(PodcastScript):
    """
    Represents a specific Sleepcast script, including music prompts.
    Inherits from PodcastScript.
    """
    music_prompt: str = Field(
        description="A specific prompt for the music generation model (e.g. Lyria)."
    )

class DarkPattern(BaseModel):
    """
    Represents a detected dark pattern, manipulation, or lie in a sentence.
    """
    type: str = Field(description="Type of dark pattern, manipulation, or lie.")
    description: str = Field(
        description="Explanation of why this is considered a dark pattern or lie."
    )
    confidence: str = Field(description="Confidence level: Low, Medium, High.")

class SentenceAnalysis(BaseModel):
    """
    Represents the analysis of a single sentence in the audio.
    Includes diarization, transcription, emotion, and dark patterns.
    """
    speaker_label: str = Field(description="Label of the speaker, e.g., Speaker 1, Speaker 2")
    text: str = Field(description="The transcribed text of the sentence")
    emotional_tone: str = Field(description="The emotional tone conveyed in the sentence")
    dark_patterns: List[DarkPattern] = Field(
        description="Potential dark patterns, manipulation, or lies detected",
        default_factory=list
    )

class AudioAnalysisResult(BaseModel):
    """
    Represents the full analysis of the audio file.
    """
    segments: List[SentenceAnalysis] = Field(description="List of analyzed sentence segments.")
    overall_assessment: str = Field(
        description="Overall assessment of the conversation, speakers, and dynamics."
    )
