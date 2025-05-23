from pydantic import BaseModel
from typing import Optional


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = (
        None  # 'sub' in JWT usually stores the user identifier (email in this case)
    )
