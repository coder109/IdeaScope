import pytest

from app.models.paper import Paper
from app.services.classifier import _parse_free_tags, classify_with_llm, classify_with_rules


def test_rule_classifier_hits_nlp():
    paper = Paper(source="arxiv", title="Transformer language model for text generation")
    tags = classify_with_rules(paper)
    assert "NLP" in tags


def test_parse_free_tags_json_and_fallback():
    assert _parse_free_tags('{"free_tags":["a","b"]}') == ["a", "b"]
    assert _parse_free_tags('answer: {"free_tags":["x"]}') == ["x"]
    assert _parse_free_tags("not-json") == []


@pytest.mark.asyncio
async def test_classify_with_llm_fallback_when_not_configured(monkeypatch):
    monkeypatch.delenv("OPENAI_BASE_URL", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_MODEL", raising=False)
    paper = Paper(source="arxiv", title="A distributed database system")
    preset, free = await classify_with_llm(paper)
    assert "Systems" in preset
    assert free == []
