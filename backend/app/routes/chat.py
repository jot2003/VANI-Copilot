import json

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette.sse import EventSourceResponse

from app.core.config import settings
from app.core.security import verify_api_key
from app.models.database import get_session
from app.models.schemas import ChatRequest, ChatResponse, SourceReference, StreamChunk
from app.services.conversation import ConversationService

router = APIRouter(prefix="/api", tags=["chat"], dependencies=[Depends(verify_api_key)])


async def _get_agent_or_rag():
    """Return agent service if enabled, else RAG service."""
    if settings.agent_enabled:
        from app.services.agent import AgentService
        return AgentService.get_instance(), True
    from app.services.rag import RAGService
    return RAGService(), False


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    session: AsyncSession = Depends(get_session),
):
    conv_service = ConversationService(session)
    conversation = await conv_service.get_or_create(request.conversation_id)

    await conv_service.add_message(conversation.id, "user", request.message)
    history = await conv_service.get_history(conversation.id)

    service, is_agent = await _get_agent_or_rag()

    if is_agent:
        history_dicts = [
            {"role": m.role, "content": m.content}
            for m in (history or [])
        ]
        result = await service.run(request.message, history_dicts)

        await conv_service.add_message(conversation.id, "assistant", result.reply)
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

    # Direct RAG path (agent disabled)
    reply, sources = await service.generate(request.message, history)
    await conv_service.add_message(conversation.id, "assistant", reply)
    await session.commit()

    return ChatResponse(
        reply=reply,
        conversation_id=conversation.id,
        sources=sources,
    )


@router.post("/chat/stream")
async def chat_stream(
    request: ChatRequest,
    session: AsyncSession = Depends(get_session),
):
    conv_service = ConversationService(session)
    conversation = await conv_service.get_or_create(request.conversation_id)

    await conv_service.add_message(conversation.id, "user", request.message)
    history = await conv_service.get_history(conversation.id)

    service, is_agent = await _get_agent_or_rag()

    if is_agent:
        # Agent doesn't stream — run fully then send result as SSE
        history_dicts = [
            {"role": m.role, "content": m.content}
            for m in (history or [])
        ]
        result = await service.run(request.message, history_dicts)

        async def agent_event_generator():
            # Send full reply as single chunk (agent doesn't support token streaming)
            await conv_service.add_message(conversation.id, "assistant", result.reply)
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

    # Direct RAG streaming path
    token_stream, sources = await service.stream(request.message, history)

    async def rag_event_generator():
        full_reply = ""
        async for token in token_stream:
            full_reply += token
            chunk = StreamChunk(token=token, conversation_id=conversation.id)
            yield {"data": chunk.model_dump_json()}

        await conv_service.add_message(conversation.id, "assistant", full_reply)
        await session.commit()

        final = StreamChunk(
            done=True,
            conversation_id=conversation.id,
            sources=sources,
        )
        yield {"data": final.model_dump_json()}

    return EventSourceResponse(rag_event_generator())
