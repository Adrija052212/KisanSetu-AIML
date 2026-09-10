from pydantic import BaseModel, Field
from typing import Optional

class ChatRequest(BaseModel):

    conversation_id: str = Field(..., min_length=1)

    message: str = Field(..., min_length=1)

    language: str = Field(default="English", min_length=1)

    location: Optional[str] = None


class ChatResponse(BaseModel):
    conversation_id: str
    response: str
    language: str