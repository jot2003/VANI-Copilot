from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import verify_api_key
from app.models.database import get_session
from app.models.schemas import ConversationDetail, ConversationOut, FeedbackRequest
from app.services.conversation import ConversationService

router = APIRouter(prefix="/api", tags=["conversations"], dependencies=[Depends(verify_api_key)])


@router.get("/conversations", response_model=list[ConversationOut])
async def list_conversations(session: AsyncSession = Depends(get_session)):
    service = ConversationService(session)
    conversations = await service.list_conversations()
    return [ConversationOut(**c) for c in conversations]


@router.get("/conversations/{conversation_id}", response_model=ConversationDetail)
async def get_conversation(
    conversation_id: str,
    session: AsyncSession = Depends(get_session),
):
    service = ConversationService(session)
    detail = await service.get_conversation_detail(conversation_id)
    if not detail:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return ConversationDetail(**detail)


@router.post("/feedback")
async def submit_feedback(
    request: FeedbackRequest,
    session: AsyncSession = Depends(get_session),
):
    service = ConversationService(session)
    await service.save_feedback(request.conversation_id, request.message_id, request.rating)
    await session.commit()
    return {"status": "ok"}
