import sys
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI

from app.core.config import settings
from app.core.middleware import setup_middleware
from app.models.database import init_db
from app.routes import admin, analytics, chat, conversations, health
from app.services.embedding import EmbeddingService
from app.services.reranker import RerankerService
from app.services.retriever import Retriever

# Fix Windows cp1252 console encoding for Vietnamese text
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer(),
    ]
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("starting_up")
    await init_db()

    embedding = EmbeddingService.get_instance()
    embedding.load_model()

    retriever = Retriever.get_instance()
    retriever.load_index()

    reranker = RerankerService.get_instance()
    reranker.load_model()

    if settings.agent_enabled:
        from app.services.agent import AgentService
        try:
            agent = AgentService.get_instance()
            agent._build_agent()
            logger.info("agent_ready")
        except Exception as e:
            logger.warning("agent_init_failed", error=str(e), msg="Will use direct RAG")
            settings.agent_enabled = False

    logger.info(
        "startup_complete",
        agent=settings.agent_enabled,
        llm=settings.llm_provider,
        cors_origins=settings.cors_origin_list,
    )
    yield
    logger.info("shutting_down")
    embed_svc = EmbeddingService.get_instance()
    embed_svc._model = None
    logger.info("shutdown_complete")


app = FastAPI(
    title="VANI Copilot API",
    description="AI Customer Support Copilot for Vietnamese E-commerce",
    version="2.0.0",
    lifespan=lifespan,
)

setup_middleware(app)

app.include_router(health.router)
app.include_router(chat.router)
app.include_router(conversations.router)
app.include_router(admin.router)
app.include_router(analytics.router)
