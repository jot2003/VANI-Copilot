import os
import sys

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

os.environ["LLM_PROVIDER"] = "azure"
os.environ["AZURE_OPENAI_API_KEY"] = ""
os.environ["AZURE_OPENAI_ENDPOINT"] = ""
os.environ["AGENT_ENABLED"] = "false"
os.environ["RERANKER_ENABLED"] = "false"
os.environ["EMBEDDING_MODEL"] = "intfloat/multilingual-e5-small"
os.environ["DB_PATH"] = "data/test_copilot.db"
os.environ["API_KEY"] = "test-key"

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest_asyncio.fixture
async def client():
    from app.models.database import init_db
    await init_db()

    from app.main import app
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def api_headers():
    return {"X-API-Key": "test-key", "Content-Type": "application/json"}
