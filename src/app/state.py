from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from app.models import CharacterProfile
from app.chc_models import CHCModel

@dataclass
class AppState:
    """
    A centralized data class to manage the application's session state.
    """
    # Authentication
    authenticated: bool = False
    user_id: Optional[str] = None

    # Character and Profile Management
    character_selected: bool = False
    character_id: Optional[str] = None
    profile: Optional[CharacterProfile] = None
    chc_profile: Optional[CHCModel] = None
    tcc_program: Optional[Any] = None # Using Any to avoid circular import issues if TCCProgram is complex
    detailed_sessions: Dict[str, str] = field(default_factory=dict)

    # UI State Flags
    combining: bool = False
    combine_character_name: Optional[str] = None

    comparing: bool = False
    compare_character_name: Optional[str] = None
    comparison_ready: bool = False

    # Data for Comparison
    compare_profile1: Optional[Any] = None
    compare_profile2: Optional[Any] = None
    comparison_analysis: Optional[str] = None

    def reset_character_data(self):
        """Resets all data related to a specific character."""
        self.profile = None
        self.chc_profile = None
        self.tcc_program = None
        self.character_id = None
        self.detailed_sessions = {}

    def back_to_character_selection(self):
        """Resets the UI state to the main character selection screen."""
        self.character_selected = False
        self.comparing = False
        self.comparison_ready = False
        self.combining = False
        self.reset_character_data()
