"""Tests for agent utility methods (static, no LLM required)."""
from app.services.agent import AgentService


def test_parse_tool_sources_empty():
    assert AgentService._parse_tool_sources("") == []
    assert AgentService._parse_tool_sources("Không tìm thấy") == []


def test_parse_tool_sources_with_brackets():
    obs = "[faq.txt] Chính sách đổi trả trong 7 ngày"
    sources = AgentService._parse_tool_sources(obs)
    assert len(sources) == 1
    assert sources[0]["source_file"] == "faq.txt"
    assert "đổi trả" in sources[0]["content"]


def test_parse_tool_sources_multiple():
    obs = "[a.txt] Content A\n\n---\n\n[b.txt] Content B"
    sources = AgentService._parse_tool_sources(obs)
    assert len(sources) == 2
    assert sources[0]["source_file"] == "a.txt"
    assert sources[1]["source_file"] == "b.txt"


def test_parse_tool_sources_no_brackets():
    obs = "Some generic observation text"
    sources = AgentService._parse_tool_sources(obs)
    assert len(sources) == 1
    assert sources[0]["source_file"] == "knowledge_base"


def test_compute_confidence_handoff():
    assert AgentService._compute_confidence([], True, "") == 0.3


def test_compute_confidence_no_tools_long():
    assert AgentService._compute_confidence([], False, "a" * 30) == 0.7


def test_compute_confidence_no_tools_short():
    assert AgentService._compute_confidence([], False, "hi") == 0.5


def test_compute_confidence_retrieval():
    assert AgentService._compute_confidence(["search_knowledge_base"], False, "a" * 100) == 0.9


def test_compute_confidence_tool_short_reply():
    assert AgentService._compute_confidence(["track_order"], False, "short") == 0.75


def test_compute_confidence_fallback():
    assert AgentService._compute_confidence(["fallback_rag"], False, "some reply") == 0.5
