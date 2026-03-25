import json

import structlog
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette.sse import EventSourceResponse

from app.core.config import settings
from app.core.middleware import limiter
from app.core.security import verify_api_key
from app.models.database import AnalyticsEvent, get_session
from app.models.schemas import ChatRequest, ChatResponse, SourceReference, StreamChunk
from app.services.conversation import ConversationService

logger = structlog.get_logger()

router = APIRouter(prefix="/api", tags=["chat"], dependencies=[Depends(verify_api_key)])


async def _get_agent_or_rag():
    """Return agent service if enabled, else RAG service."""
    if settings.agent_enabled:
        from app.services.agent import AgentService
        return AgentService.get_instance(), True
    from app.services.rag import RAGService
    return RAGService(), False


@router.post("/chat", response_model=ChatResponse)
@limiter.limit(settings.rate_limit)
async def chat(
    request: Request,
    body: ChatRequest,
    session: AsyncSession = Depends(get_session),
):
    request_id = getattr(request.state, "request_id", None)
    try:
        conv_service = ConversationService(session)
        conversation = await conv_service.get_or_create(body.conversation_id)

        await conv_service.add_message(conversation.id, "user", body.message)
        history = await conv_service.get_history(conversation.id)

        service, is_agent = await _get_agent_or_rag()

        if is_agent:
            history_dicts = [
                {"role": m.role, "content": m.content}
                for m in (history or [])
            ]
            result = await service.run(body.message, history_dicts)

            await conv_service.add_message(conversation.id, "assistant", result.reply)

            session.add(AnalyticsEvent(
                event_type="chat_query",
                intent=result.intent,
                confidence=int(result.confidence * 100),
                data=json.dumps({
                    "tools": result.used_tools,
                    "sources_count": len(result.sources),
                    "handoff": result.handoff_suggested,
                    "conversation_id": conversation.id,
                }, ensure_ascii=False),
            ))
            await session.commit()

            sources = [
                SourceReference(
                    content=s["content"],
                    source_file=s["source_file"],
                    score=s.get("score", 0.0),
                )
                for s in result.sources
            ]

            return ChatResponse(
                reply=result.reply,
                conversation_id=conversation.id,
                sources=sources,
                intent=result.intent,
                confidence=result.confidence,
                used_tools=result.used_tools,
                handoff_suggested=result.handoff_suggested,
            )

        reply, sources = await service.generate(body.message, history)
        await conv_service.add_message(conversation.id, "assistant", reply)

        session.add(AnalyticsEvent(
            event_type="chat_query",
            intent="rag",
            confidence=80,
            data=json.dumps({
                "tools": ["rag"],
                "sources_count": len(sources),
                "conversation_id": conversation.id,
            }, ensure_ascii=False),
        ))
        await session.commit()

        return ChatResponse(
            reply=reply,
            conversation_id=conversation.id,
            sources=sources,
        )
    except Exception as e:
        logger.error("chat_error", error=str(e), request_id=request_id)
        return JSONResponse(
            status_code=500,
            content={
                "error": "chat_failed",
                "message": "Failed to process chat request. Please try again.",
                "request_id": request_id,
            },
        )


@router.post("/chat/stream")
@limiter.limit(settings.rate_limit)
async def chat_stream(
    request: Request,
    body: ChatRequest,
    session: AsyncSession = Depends(get_session),
):
    request_id = getattr(request.state, "request_id", None)
    try:
        conv_service = ConversationService(session)
        conversation = await conv_service.get_or_create(body.conversation_id)

        await conv_service.add_message(conversation.id, "user", body.message)
        history = await conv_service.get_history(conversation.id)

        service, is_agent = await _get_agent_or_rag()

        if is_agent:
            history_dicts = [
                {"role": m.role, "content": m.content}
                for m in (history or [])
            ]
            result = await service.run(body.message, history_dicts)

            async def agent_event_generator():
                await conv_service.add_message(conversation.id, "assistant", result.reply)
                session.add(AnalyticsEvent(
                    event_type="chat_query",
                    intent=result.intent,
                    confidence=int(result.confidence * 100),
                    data=json.dumps({
                        "tools": result.used_tools,
                        "sources_count": len(result.sources),
                        "handoff": result.handoff_suggested,
                        "conversation_id": conversation.id,
                    }, ensure_ascii=False),
                ))
                await session.commit()

                sources = [
                    SourceReference(
                        content=s["content"],
                        source_file=s["source_file"],
                        score=s.get("score", 0.0),
                    )
                    for s in result.sources
                ]

                final = StreamChunk(
                    token=result.reply,
                    done=True,
                    conversation_id=conversation.id,
                    sources=sources,
                    intent=result.intent,
                    confidence=result.confidence,
                    used_tools=result.used_tools,
                    handoff_suggested=result.handoff_suggested,
                )
                yield {"data": final.model_dump_json()}

            return EventSourceResponse(agent_event_generator())

        token_stream, sources = await service.stream(body.message, history)

        async def rag_event_generator():
            full_reply = ""
            async for token in token_stream:
                full_reply += token
                chunk = StreamChunk(token=token, conversation_id=conversation.id)
                yield {"data": chunk.model_dump_json()}

            await conv_service.add_message(conversation.id, "assistant", full_reply)
            session.add(AnalyticsEvent(
                event_type="chat_query",
                intent="rag",
                confidence=80,
                data=json.dumps({
                    "tools": ["rag"],
                    "sources_count": len(sources),
                    "conversation_id": conversation.id,
                }, ensure_ascii=False),
            ))
            await session.commit()

            final = StreamChunk(
                done=True,
                conversation_id=conversation.id,
                sources=sources,
            )
            yield {"data": final.model_dump_json()}

        return EventSourceResponse(rag_event_generator())
    except Exception as e:
        logger.error("chat_stream_error", error=str(e), request_id=request_id)
        return JSONResponse(
            status_code=500,
            content={
                "error": "chat_stream_failed",
                "message": "Failed to process chat stream request. Please try again.",
                "request_id": request_id,
            },
        )
