from pydantic import BaseModel
from typing import Optional

class UserProfile(BaseModel):
    user_id: str
    name: Optional[str] = None
    surname: Optional[str] = None
    email: Optional[str] = None
