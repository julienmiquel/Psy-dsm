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

class NotesHexa(BaseModel):
    """Stocke les notes (brutes ou étalonnées) pour les 6 pôles RIASEC."""
    R: int = Field(description="Score pour le type Réaliste")
    I: int = Field(description="Score pour le type Investigateur")
    A: int = Field(description="Score pour le type Artistique")
    S: int = Field(description="Score pour le type Social")
    E: int = Field(description="Score pour le type Entreprenant")
    C: int = Field(description="Score pour le type Conventionnel")

class ProfilHexaDomaine(BaseModel):
    """
    Représente le profil RIASEC pour un domaine spécifique (Activités, Qualités, etc.)
    en incluant les notes brutes et étalonnées (NE, souvent sur 5 classes).
    """
    notes_brutes: NotesHexa
    notes_etalonnees: NotesHexa = Field(description="Notes étalonnées (NE) en classes (ex: 1 à 5)")
    code_riasec: str = Field(description="Le code à 3 lettres pour ce domaine (ex: 'SIA')")

class ScoreDimension3D(BaseModel):
    """Stocke le score brut et étalonné pour une dimension secondaire."""
    note_brute: int
    note_etalonnee: int

class Dimensions3D(BaseModel):
    """
    Modélise les dimensions secondaires de l'Hexa3D :
    Prestige (P+/P-) et Genre (Masculinité/Féminité).
    """
    prestige_eleve: ScoreDimension3D = Field(description="Score pour la préférence Prestige Élevé (P+)")
    prestige_faible: ScoreDimension3D = Field(description="Score pour la préférence Prestige Faible (P-)")
    masculinite: ScoreDimension3D = Field(description="Score pour la préférence de type 'Masculin'")
    feminite: ScoreDimension3D = Field(description="Score pour la préférence de type 'Féminin'")

class Hexa3DAssessment(BaseModel):
    """
    Modèle dédié aux résultats complets du questionnaire d'intérêts Hexa3D.

    Ce modèle capture la structure multidimensionnelle du test, incluant :
    1. Les 3 domaines d'intérêts (Activités, Qualités, Professions).
    2. Le profil global synthétique.
    3. Les dimensions secondaires (Prestige et Genre).
    """
    assessment_datetime: str = Field(description="Date et heure de l'évaluation")

    # 1. Profils par Domaine (la spécificité de l'Hexa3D)
    profil_activites: ProfilHexaDomaine = Field(description="Profil RIASEC pour le domaine 'Activités'")
    profil_qualites: ProfilHexaDomaine = Field(description="Profil RIASEC pour le domaine 'Qualités'")
    profil_professions: ProfilHexaDomaine = Field(description="Profil RIASEC pour le domaine 'Professions'")

    # 2. Profil Global (la synthèse)
    profil_global: ProfilHexaDomaine = Field(description="Profil global des intérêts (synthèse des 3 domaines)")

    # 3. Les Dimensions "3D"
    dimensions_secondaires: Dimensions3D

    # 4. Données interprétatives (issues de notre critique précédente)
    code_global_top_themes: List[str] = Field(
        description="Les 2-3 thèmes dominants du profil global (ex: ['S', 'I', 'A'])"
    )
    niveau_differenciation_global: Optional[str] = Field(
        None, description="Niveau de différenciation du profil global (Faible, Moyen, Élevé)"
    )
    niveau_consistance_global: Optional[str] = Field(
        None, description="Consistance du profil global (Consistant, Inconsistant)"
    )

    summary: Optional[str] = Field(None, description="Synthèse interprétative de l'évaluation Hexa3D")

class CharacterProfile(BaseModel):
    character_name: str
    profile_datetime: str = Field(description="Date and time of profile generation in YYYY-MM-DD HH:MM:SS format")
    overall_assessment_summary: Optional[str] = Field(None, description="A brief summary of the clinical assessment")
    holland_code_assessment: Optional[HollandCodeAssessment] = Field(None, description="Holland Code (RIASEC) assessment results.")
    hexa3d_assessment: Optional[Hexa3DAssessment] = Field(None, description="Hexa3D assessment results.")
    character_id: Optional[str] = None
    user_id: Optional[str] = None
    diagnoses: List[DiagnosisEntry] = Field(default_factory=list)
    raw_text_bloc: Optional[str] = None
    tcc_program: Optional[TCCProgram] = None