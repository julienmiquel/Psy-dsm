"""
This module defines the Pydantic data model for a user profile.
"""

from typing import Optional
from pydantic import BaseModel

class UserProfile(BaseModel):
    """A Pydantic model for a user profile."""
    user_id: str
    name: Optional[str] = None
    surname: Optional[str] = None
    email: Optional[str] = None
