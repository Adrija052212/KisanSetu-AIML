from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    conversation_id: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1)
    language: str = Field(default="English", min_length=1)


class ChatResponse(BaseModel):
    conversation_id: str
    response: str
    language: str