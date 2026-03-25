from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import verify_api_key
from app.models.database import (
    AnalyticsEvent,
    Conversation,
    Feedback,
    Message,
    get_session,
)

router = APIRouter(prefix="/api/analytics", tags=["analytics"], dependencies=[Depends(verify_api_key)])


@router.get("/overview")
async def overview(session: AsyncSession = Depends(get_session)):
    # Total conversations
    total_convs = (await session.execute(select(func.count(Conversation.id)))).scalar() or 0

    # Total messages
    total_msgs = (await session.execute(select(func.count(Message.id)))).scalar() or 0

    # Conversations in last 7 days
    week_ago = datetime.now(timezone.utc) - timedelta(days=7)
    recent_convs = (await session.execute(
        select(func.count(Conversation.id)).where(Conversation.created_at >= week_ago)
    )).scalar() or 0

    # Feedback stats
    fb_result = await session.execute(select(Feedback.rating))
    ratings = [r[0] for r in fb_result.all()]
    positive = sum(1 for r in ratings if r > 0)
    negative = sum(1 for r in ratings if r < 0)
    total_fb = len(ratings)

    # Intent distribution from analytics events
    intent_result = await session.execute(
        select(AnalyticsEvent.intent, func.count(AnalyticsEvent.id))
        .where(AnalyticsEvent.event_type == "chat_query")
        .group_by(AnalyticsEvent.intent)
    )
    intent_dist = {row[0]: row[1] for row in intent_result.all() if row[0]}

    return {
        "total_conversations": total_convs,
        "total_messages": total_msgs,
        "conversations_last_7d": recent_convs,
        "avg_messages_per_conversation": round(total_msgs / max(total_convs, 1), 1),
        "feedback": {
            "total": total_fb,
            "positive": positive,
            "negative": negative,
            "satisfaction_rate": round(positive / max(total_fb, 1) * 100, 1),
        },
        "intent_distribution": intent_dist,
    }


@router.get("/intents")
async def intent_stats(
    days: int = 30,
    session: AsyncSession = Depends(get_session),
):
    since = datetime.now(timezone.utc) - timedelta(days=days)
    result = await session.execute(
        select(AnalyticsEvent.intent, func.count(AnalyticsEvent.id))
        .where(
            AnalyticsEvent.event_type == "chat_query",
            AnalyticsEvent.created_at >= since,
        )
        .group_by(AnalyticsEvent.intent)
        .order_by(func.count(AnalyticsEvent.id).desc())
    )
    return {
        "period_days": days,
        "intents": [{"intent": row[0], "count": row[1]} for row in result.all() if row[0]],
    }


@router.get("/feedback")
async def feedback_list(
    limit: int = 20,
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(
        select(Feedback, Message)
        .join(Message, Feedback.message_id == Message.id)
        .order_by(Feedback.created_at.desc())
        .limit(limit)
    )

    items = []
    for fb, msg in result.all():
        items.append({
            "feedback_id": fb.id,
            "rating": fb.rating,
            "conversation_id": fb.conversation_id,
            "message_content": msg.content[:300],
            "message_role": msg.role,
            "created_at": fb.created_at.isoformat() if fb.created_at else None,
        })

    return {"feedback": items, "total": len(items)}
