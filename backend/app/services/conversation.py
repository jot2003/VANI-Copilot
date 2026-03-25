import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.models.database import Conversation, Feedback, Message


class ConversationService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_or_create(self, conversation_id: str | None) -> Conversation:
        if conversation_id:
            result = await self.session.execute(
                select(Conversation).where(Conversation.id == conversation_id)
            )
            conv = result.scalar_one_or_none()
            if conv:
                return conv

        conv = Conversation(id=str(uuid.uuid4()))
        self.session.add(conv)
        await self.session.flush()
        return conv

    async def add_message(self, conversation_id: str, role: str, content: str) -> Message:
        msg = Message(conversation_id=conversation_id, role=role, content=content)
        self.session.add(msg)

        await self.session.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        result = await self.session.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        conv = result.scalar_one_or_none()
        if conv:
            conv.updated_at = datetime.now(timezone.utc)
            if conv.title == "New Conversation" and role == "user":
                conv.title = content[:50] + ("..." if len(content) > 50 else "")

        await self.session.flush()
        return msg

    async def get_history(self, conversation_id: str, limit: int | None = None) -> list[Message]:
        limit = limit or settings.max_history_messages
        result = await self.session.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        messages = list(result.scalars().all())
        messages.reverse()
        return messages

    async def list_conversations(self) -> list[dict]:
        result = await self.session.execute(
            select(
                Conversation.id,
                Conversation.title,
                Conversation.created_at,
                Conversation.updated_at,
                func.count(Message.id).label("message_count"),
            )
            .outerjoin(Message)
            .group_by(Conversation.id)
            .order_by(Conversation.updated_at.desc())
        )
        return [
            {
                "id": row.id,
                "title": row.title,
                "created_at": row.created_at,
                "updated_at": row.updated_at,
                "message_count": row.message_count,
            }
            for row in result.all()
        ]

    async def get_conversation_detail(self, conversation_id: str) -> dict | None:
        result = await self.session.execute(
            select(Conversation)
            .where(Conversation.id == conversation_id)
            .options(selectinload(Conversation.messages))
        )
        conv = result.scalar_one_or_none()
        if not conv:
            return None
        return {
            "id": conv.id,
            "title": conv.title,
            "created_at": conv.created_at,
            "updated_at": conv.updated_at,
            "messages": [
                {"id": m.id, "role": m.role, "content": m.content, "created_at": m.created_at}
                for m in conv.messages
            ],
        }

    async def save_feedback(self, conversation_id: str, message_id: int, rating: int) -> Feedback:
        fb = Feedback(conversation_id=conversation_id, message_id=message_id, rating=rating)
        self.session.add(fb)
        await self.session.flush()
        return fb
