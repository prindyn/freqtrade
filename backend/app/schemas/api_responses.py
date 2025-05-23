from pydantic import BaseModel
from typing import Optional, Dict, Any


class BotStatusResponse(BaseModel):
    bot_id: str
    status: str  # e.g., "running", "exited", "error"
    message: Optional[str] = None
    details: Optional[Dict[str, Any]] = None  # For container info, port, etc.


class BotDeleteResponse(BaseModel):
    bot_id: str
    message: str


class BotLogResponse(BaseModel):
    bot_id: str
    logs: Optional[str] = None
    message: Optional[str] = None
