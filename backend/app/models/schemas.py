from datetime import datetime

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    conversation_id: str | None = None


class SourceReference(BaseModel):
    content: str
    source_file: str
    score: float


class ChatResponse(BaseModel):
    reply: str
    conversation_id: str
    sources: list[SourceReference] = []
    intent: str = "general"
    confidence: float = 1.0
    used_tools: list[str] = []
    handoff_suggested: bool = False


class StreamChunk(BaseModel):
    token: str = ""
    done: bool = False
    conversation_id: str = ""
    sources: list[SourceReference] = []
    intent: str = ""
    confidence: float = 1.0
    used_tools: list[str] = []
    handoff_suggested: bool = False


class MessageOut(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime


class ConversationOut(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: int = 0


class ConversationDetail(ConversationOut):
    messages: list[MessageOut] = []


class FeedbackRequest(BaseModel):
    conversation_id: str
    message_id: int
    rating: int = Field(..., ge=-1, le=1)  # -1 = bad, 0 = neutral, 1 = good


class DocumentUpload(BaseModel):
    filename: str
    content: str


class HealthResponse(BaseModel):
    status: str = "ok"
    llm_provider: str = ""
    faiss_index_loaded: bool = False
    embedding_model_loaded: bool = False
