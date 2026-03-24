from datetime import date

import pytest

from app.models.paper import Paper
from app.services import search_service


def test_in_year_range_with_published_date():
    paper = Paper(source="arxiv", title="x", published_date=date(2024, 5, 1), year=2024)
    assert search_service._in_year_range(paper, 2023, 2026) is True
    assert search_service._in_year_range(paper, 2025, 2026) is False


def test_in_year_range_with_year_fallback():
    paper = Paper(source="dblp", title="x", year=2022)
    assert search_service._in_year_range(paper, 2021, 2023) is True
    assert search_service._in_year_range(paper, 2023, 2024) is False


def test_dedupe_prefers_unique_items():
    papers = [
        Paper(source="arxiv", title="Same Title", doi="10.1/abc", url="https://a"),
        Paper(source="dblp", title="Same Title", doi="10.1/abc", url="https://b"),
        Paper(source="dblp", title="same title", url="https://c"),
        Paper(source="dblp", title="Different", url="https://a"),
        Paper(source="dblp", title="Different 2", url="https://d"),
    ]
    deduped = search_service._dedupe(papers)
    assert len(deduped) == 2
    assert deduped[0].title == "Same Title"
    assert deduped[1].title == "Different 2"


@pytest.mark.asyncio
async def test_search_papers_invalid_year_range():
    with pytest.raises(ValueError):
        await search_service.search_papers("test", 2026, 2023, 5)


@pytest.mark.asyncio
async def test_search_papers_invalid_fetch_limit():
    with pytest.raises(ValueError):
        await search_service.search_papers("test", 2023, 2026, 5, True, 0)


@pytest.mark.asyncio
async def test_search_papers_passes_fetch_all_params(monkeypatch):
    called = {"arxiv": None, "dblp": None}

    async def fake_arxiv(keyword, max_results, fetch_all, max_fetch_limit):
        called["arxiv"] = (keyword, max_results, fetch_all, max_fetch_limit)
        return [Paper(source="arxiv", title="A", year=2024)]

    async def fake_dblp(keyword, max_results, fetch_all, max_fetch_limit):
        called["dblp"] = (keyword, max_results, fetch_all, max_fetch_limit)
        return [Paper(source="dblp", title="B", year=2024)]

    monkeypatch.setattr(search_service, "search_arxiv", fake_arxiv)
    monkeypatch.setattr(search_service, "search_dblp", fake_dblp)

    papers = await search_service.search_papers(
        "llm",
        2023,
        2026,
        max_results_per_source=20,
        fetch_all=True,
        max_fetch_limit_per_source=500,
    )
    assert len(papers) == 2
    assert called["arxiv"] == ("llm", 20, True, 500)
    assert called["dblp"] == ("llm", 20, True, 500)


@pytest.mark.asyncio
async def test_search_papers_survives_single_source_failure(monkeypatch):
    async def fake_arxiv(keyword, max_results, fetch_all, max_fetch_limit):
        return [Paper(source="arxiv", title="A", year=2024)]

    async def fake_dblp(keyword, max_results, fetch_all, max_fetch_limit):
        raise RuntimeError("dblp failure")

    monkeypatch.setattr(search_service, "search_arxiv", fake_arxiv)
    monkeypatch.setattr(search_service, "search_dblp", fake_dblp)

    papers = await search_service.search_papers("agent", 2023, 2026, 10)
    assert len(papers) == 1
    assert papers[0].source == "arxiv"
