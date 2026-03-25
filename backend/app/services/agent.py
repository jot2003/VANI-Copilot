"""LangChain Agent — orchestrates tools based on customer intent.

Supports Azure OpenAI (primary) and OpenAI (alternative) for agent reasoning.
Falls back to direct RAG if agent fails.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field

import structlog
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import AzureChatOpenAI, ChatOpenAI

from app.core.config import settings
from app.services.tools import ALL_TOOLS

logger = structlog.get_logger()

AGENT_SYSTEM_PROMPT = """Bạn là nhân viên chăm sóc khách hàng của VANI Store — shop thời trang nữ online.

QUY TẮC:
- Xưng "em", gọi khách là "chị" hoặc "anh"
- Thân thiện, lịch sự, nhiệt tình
- Trả lời ngắn gọn, đúng trọng tâm
- Không bịa thông tin

BẠN CÓ CÁC CÔNG CỤ:
1. search_knowledge_base: Tìm FAQ, chính sách, thông tin sản phẩm
2. track_order: Tra cứu đơn hàng theo mã
3. search_products: Tìm sản phẩm, giá, size
4. request_human_handoff: Chuyển cho nhân viên thật khi cần

HƯỚNG DẪN:
- Luôn dùng tool phù hợp TRƯỚC KHI trả lời
- Nếu khách hỏi về đơn hàng → dùng track_order
- Nếu khách hỏi FAQ/chính sách → dùng search_knowledge_base
- Nếu khách hỏi sản phẩm cụ thể → dùng search_products
- Nếu khách tức giận/cần hỗ trợ phức tạp → dùng request_human_handoff
- Nếu chỉ chào hỏi → trả lời trực tiếp, không cần tool
- Sau khi có kết quả từ tool, tổng hợp thành câu trả lời tự nhiên bằng tiếng Việt"""


@dataclass
class AgentResult:
    reply: str = ""
    intent: str = "general"
    confidence: float = 1.0
    sources: list[dict] = field(default_factory=list)
    used_tools: list[str] = field(default_factory=list)
    handoff_suggested: bool = False


class AgentService:
    _instance: AgentService | None = None

    def __init__(self):
        self._agent = None
        self._llm = None

    @classmethod
    def get_instance(cls) -> AgentService:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _get_llm(self):
        if self._llm is not None:
            return self._llm

        if settings.azure_openai_api_key and settings.azure_openai_endpoint:
            self._llm = AzureChatOpenAI(
                azure_endpoint=settings.azure_openai_endpoint,
                azure_deployment=settings.azure_openai_deployment,
                api_version=settings.azure_openai_api_version,
                api_key=settings.azure_openai_api_key,
            )
            logger.info("agent_llm_ready", provider="azure_openai")
        elif settings.openai_api_key:
            self._llm = ChatOpenAI(
                model=settings.openai_model,
                api_key=settings.openai_api_key,
                temperature=0.7,
            )
            logger.info("agent_llm_ready", provider="openai")
        else:
            logger.error("no_llm_configured", msg="Set AZURE_OPENAI_* or OPENAI_API_KEY in .env")
            raise RuntimeError("No LLM configured for agent. Set Azure OpenAI or OpenAI credentials.")

        return self._llm

    def _build_agent(self):
        if self._agent is not None:
            return self._agent

        from langchain.agents import AgentExecutor, create_tool_calling_agent

        llm = self._get_llm()

        prompt = ChatPromptTemplate.from_messages([
            ("system", AGENT_SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        agent = create_tool_calling_agent(llm, ALL_TOOLS, prompt)
        self._agent = AgentExecutor(
            agent=agent,
            tools=ALL_TOOLS,
            verbose=False,
            max_iterations=3,
            handle_parsing_errors=True,
            return_intermediate_steps=True,
        )
        logger.info("agent_executor_ready")
        return self._agent

    async def run(
        self,
        message: str,
        history: list[dict] | None = None,
    ) -> AgentResult:
        try:
            return await self._run_agent(message, history)
        except Exception as e:
            logger.error("agent_failed", error=str(e))
            return await self._fallback_rag(message, history)

    async def _run_agent(
        self,
        message: str,
        history: list[dict] | None = None,
    ) -> AgentResult:
        agent = self._build_agent()

        chat_history = []
        if history:
            for msg in history:
                if msg["role"] == "user":
                    chat_history.append(HumanMessage(content=msg["content"]))
                elif msg["role"] == "assistant":
                    chat_history.append(AIMessage(content=msg["content"]))

        result = await agent.ainvoke({
            "input": message,
            "chat_history": chat_history,
        })

        used_tools = []
        sources = []
        handoff = False
        intent = "general"

        for step in result.get("intermediate_steps", []):
            action, observation = step
            tool_name = action.tool
            used_tools.append(tool_name)

            if tool_name == "search_knowledge_base":
                intent = "faq"
            elif tool_name == "track_order":
                intent = "order_tracking"
            elif tool_name == "search_products":
                intent = "product_inquiry"
            elif tool_name == "request_human_handoff":
                intent = "handoff"
                handoff = True

            if tool_name in ("search_knowledge_base", "search_products"):
                sources.extend(self._parse_tool_sources(str(observation)))

        if not used_tools:
            intent = "chitchat"

        reply = result.get("output", "")

        confidence = self._compute_confidence(used_tools, handoff, reply)

        logger.info(
            "agent_response",
            intent=intent,
            tools=used_tools,
            handoff=handoff,
            confidence=confidence,
            reply_len=len(reply),
        )

        return AgentResult(
            reply=reply,
            intent=intent,
            confidence=confidence,
            sources=sources[:5],
            used_tools=used_tools,
            handoff_suggested=handoff,
        )

    @staticmethod
    def _parse_tool_sources(observation: str) -> list[dict]:
        """Extract sources from tool observation text (format: [filename] content)."""
        sources = []
        if not observation or observation.startswith("Không tìm thấy"):
            return sources

        for block in observation.split("\n\n---\n\n"):
            block = block.strip()
            if not block:
                continue
            if block.startswith("[") and "]" in block:
                bracket_end = block.index("]")
                source_file = block[1:bracket_end]
                content = block[bracket_end + 1:].strip()
            else:
                source_file = "knowledge_base"
                content = block
            sources.append({
                "content": content[:200],
                "source_file": source_file,
                "score": 0.0,
            })
        return sources

    @staticmethod
    def _compute_confidence(used_tools: list[str], handoff: bool, reply: str) -> float:
        if handoff:
            return 0.3
        if not used_tools:
            return 0.7 if len(reply) > 20 else 0.5
        if "fallback_rag" in used_tools:
            return 0.5
        has_retrieval = any(t in used_tools for t in ("search_knowledge_base", "search_products"))
        if has_retrieval and len(reply) > 50:
            return 0.9
        return 0.75

    async def _fallback_rag(
        self,
        message: str,
        history: list[dict] | None = None,
    ) -> AgentResult:
        """Direct RAG fallback when agent fails."""
        logger.warning("using_fallback_rag")
        from app.services.rag import RAGService

        rag = RAGService()
        db_history = None
        reply, sources = await rag.generate(message, db_history)

        return AgentResult(
            reply=reply,
            intent="faq",
            confidence=0.5,
            sources=[
                {"content": s.content[:200], "source_file": s.source_file, "score": s.score}
                for s in sources
            ],
            used_tools=["fallback_rag"],
            handoff_suggested=False,
        )
