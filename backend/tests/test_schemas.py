"""Tests for Pydantic schemas."""
import pytest
from pydantic import ValidationError

from app.models.schemas import ChatRequest, ChatResponse, FeedbackRequest, SourceReference


def test_chat_request_valid():
    req = ChatRequest(message="Hello")
    assert req.message == "Hello"
    assert req.conversation_id is None


def test_chat_request_with_conversation():
    req = ChatRequest(message="Hello", conversation_id="abc-123")
    assert req.conversation_id == "abc-123"


def test_chat_request_empty_message():
    with pytest.raises(ValidationError):
        ChatRequest(message="")


def test_chat_request_too_long():
    with pytest.raises(ValidationError):
        ChatRequest(message="x" * 2001)


def test_chat_response_defaults():
    resp = ChatResponse(reply="Hi", conversation_id="c1")
    assert resp.intent == "general"
    assert resp.confidence == 1.0
    assert resp.used_tools == []
    assert resp.handoff_suggested is False
    assert resp.sources == []


def test_feedback_request_valid():
    fb = FeedbackRequest(conversation_id="c1", message_id=1, rating=1)
    assert fb.rating == 1


def test_feedback_request_invalid_rating():
    with pytest.raises(ValidationError):
        FeedbackRequest(conversation_id="c1", message_id=1, rating=5)


def test_source_reference():
    src = SourceReference(content="test", source_file="test.txt", score=0.95)
    assert src.score == 0.95
