"""Tests for configuration and settings."""
from app.core.config import Settings


def test_default_settings():
    s = Settings(
        _env_file=None,
        api_key="test",
        cors_origins="http://a.com,http://b.com",
    )
    assert s.llm_provider == "azure"
    assert s.top_k_retrieval == 20
    assert s.top_k_rerank == 5
    assert s.llm_timeout == 120.0
    assert s.agent_timeout == 60.0
    assert s.rate_limit == "30/minute"


def test_cors_origin_list():
    s = Settings(
        _env_file=None,
        cors_origins="http://a.com, http://b.com , http://c.com",
    )
    assert s.cors_origin_list == ["http://a.com", "http://b.com", "http://c.com"]


def test_cors_empty():
    s = Settings(_env_file=None, cors_origins="")
    assert s.cors_origin_list == []


def test_resolved_embedding_model_fallback():
    s = Settings(_env_file=None, embedding_model_path="", embedding_model="intfloat/e5-small")
    assert s.resolved_embedding_model == "intfloat/e5-small"


def test_db_url():
    s = Settings(_env_file=None, db_path="test.db")
    assert s.db_url == "sqlite+aiosqlite:///test.db"
