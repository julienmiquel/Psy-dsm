"""
This module defines the Pydantic data models for the Cattell-Horn-Carroll (CHC)
theory of cognitive abilities.
"""

from typing import List, Optional
from pydantic import BaseModel, Field

class NarrowAbility(BaseModel):
    """A Pydantic model for a narrow cognitive ability."""
    id: str = Field(..., description="The ID of the narrow ability.")
    name: str = Field(..., description="The name of the narrow ability.")
    description: str = Field(..., description="A description of the narrow ability.")
    score: Optional[float] = Field(None, description="The score for this narrow ability.")
    evidence_summary: Optional[str] = Field(None, description="A summary of the evidence supporting this narrow ability score.")

class BroadAbility(BaseModel):
    """A Pydantic model for a broad cognitive ability."""
    id: str = Field(..., description="The ID of the broad ability (e.g., 'Gf', 'Gc').")
    name: str = Field(..., description="The name of the broad ability (e.g., 'Fluid Intelligence').")
    description: str = Field(..., description="A description of the broad ability.")
    narrow_abilities: List[NarrowAbility] = Field([], description="A list of narrow abilities that fall under this broad ability.")
    score: Optional[float] = Field(None, description="The overall score for this broad ability.")
    evidence_summary: Optional[str] = Field(None, description="A summary of the evidence supporting this broad ability score.")

class CHCModel(BaseModel):
    """
    A representation of the Cattell-Horn-Carroll (CHC) model of cognitive abilities.
    """
    character_name: Optional[str] = None
    profile_datetime: Optional[str] = Field(None, description="Date and time of profile generation in YYYY-MM-DD HH:MM:SS format")
    g_factor: Optional[float] = Field(None, description="A general intelligence factor (g).")
    broad_abilities: List[BroadAbility] = Field([], description="A list of broad cognitive abilities.")
    character_id: Optional[str] = None
    user_id: Optional[str] = None
    poor_coverage_topics: List[str] = Field([], description="A list of topics with poor coverage in the provided text.")
    raw_text_bloc: Optional[str] = None
