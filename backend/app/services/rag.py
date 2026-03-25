from collections.abc import AsyncGenerator

import structlog

from app.models.database import Message
from app.models.schemas import SourceReference
from app.prompts.templates import (
    DEFAULT_SHOP_NAME,
    SYSTEM_PROMPT,
    USER_PROMPT_NO_HISTORY,
    USER_PROMPT_WITH_HISTORY,
)
from app.services.llm import LLMService
from app.services.retriever import Retriever

logger = structlog.get_logger()


class RAGService:
    """Orchestrates the full RAG pipeline: retrieve context -> build prompt -> call LLM."""

    def __init__(self):
        self.retriever = Retriever.get_instance()
        self.llm = LLMService()

    def _build_prompts(
        self,
        message: str,
        history: list[Message] | None = None,
        shop_name: str = DEFAULT_SHOP_NAME,
    ) -> tuple[str, str, list[SourceReference]]:
        retrieved = self.retriever.search(message)
        sources = [
            SourceReference(
                content=chunk["content"],
                source_file=chunk["source_file"],
                score=chunk["score"],
            )
            for chunk in retrieved
        ]

        context_text = "\n\n---\n\n".join(chunk["content"] for chunk in retrieved)
        if not context_text:
            context_text = "(Không tìm thấy thông tin liên quan trong cơ sở dữ liệu)"

        system_prompt = SYSTEM_PROMPT.format(shop_name=shop_name, context=context_text)

        if history:
            history_text = "\n".join(
                f"{'Khách' if m.role == 'user' else 'CSKH'}: {m.content}" for m in history
            )
            user_prompt = USER_PROMPT_WITH_HISTORY.format(history=history_text, message=message)
        else:
            user_prompt = USER_PROMPT_NO_HISTORY.format(message=message)

        logger.info("rag_context", num_sources=len(sources), query_preview=message[:80])
        return system_prompt, user_prompt, sources

    async def generate(
        self,
        message: str,
        history: list[Message] | None = None,
        shop_name: str = DEFAULT_SHOP_NAME,
    ) -> tuple[str, list[SourceReference]]:
        system_prompt, user_prompt, sources = self._build_prompts(message, history, shop_name)
        reply = await self.llm.generate(system_prompt, user_prompt)
        return reply, sources

    async def stream(
        self,
        message: str,
        history: list[Message] | None = None,
        shop_name: str = DEFAULT_SHOP_NAME,
    ) -> tuple[AsyncGenerator[str, None], list[SourceReference]]:
        system_prompt, user_prompt, sources = self._build_prompts(message, history, shop_name)
        token_stream = self.llm.stream(system_prompt, user_prompt)
        return token_stream, sources
