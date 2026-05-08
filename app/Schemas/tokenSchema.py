from pydantic import BaseModel
from uuid import UUID
from typing import Optional

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: Optional[UUID] = None

class RefreshTokenRequest(BaseModel):
    refresh_token: str