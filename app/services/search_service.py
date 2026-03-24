import asyncio
import os
import re
from datetime import date

from app.models.paper import Paper
from app.services.classifier import classify_with_llm
from app.sources.arxiv_client import search_arxiv
from app.sources.dblp_client import search_dblp


def _norm_title(title: str) -> str:
    return re.sub(r"\W+", "", title.lower())


def _in_year_range(paper: Paper, start_year: int, end_year: int) -> bool:
    if paper.published_date:
        year = paper.published_date.year
        return start_year <= year <= end_year
    if paper.year:
        return start_year <= paper.year <= end_year
    return False


def _keyword_tokens(keyword: str) -> list[str]:
    return [x for x in re.split(r"\s+", keyword.lower().strip()) if x]


def _is_relevant(paper: Paper, keyword: str, title_only: bool = False) -> bool:
    tokens = _keyword_tokens(keyword)
    if not tokens:
        return True
    title = (paper.title or "").lower()
    if title_only:
        return all(tok in title for tok in tokens)
    abstract = (paper.abstract or "").lower()
    text = f"{title} {abstract}"
    return all(tok in text for tok in tokens)


def _dedupe(papers: list[Paper]) -> list[Paper]:
    seen_doi: set[str] = set()
    seen_title: set[str] = set()
    seen_url: set[str] = set()
    result: list[Paper] = []

    for paper in papers:
        doi = (paper.doi or "").lower().strip()
        norm_title = _norm_title(paper.title)
        url = (paper.url or "").strip().lower()

        if doi and doi in seen_doi:
            continue
        if norm_title and norm_title in seen_title:
            continue
        if url and url in seen_url:
            continue

        if doi:
            seen_doi.add(doi)
        if norm_title:
            seen_title.add(norm_title)
        if url:
            seen_url.add(url)

        result.append(paper)
    return result


async def _classify_all(papers: list[Paper]) -> list[Paper]:
    preset_str = os.getenv("DEFAULT_PRESET_TAGS", "")
    preset_tags = [x.strip() for x in preset_str.split(",") if x.strip()]

    async def _one(p: Paper) -> Paper:
        preset, free = await classify_with_llm(p, preset_tags if preset_tags else None)
        p.preset_tags = preset
        p.free_tags = free
        return p

    return await asyncio.gather(*[_one(p) for p in papers])


async def search_papers(
    keyword: str,
    start_year: int,
    end_year: int,
    max_results_per_source: int = 30,
    fetch_all: bool = False,
    max_fetch_limit_per_source: int = 1000,
    strict_relevance: bool = False,
    title_only_match: bool = False,
) -> list[Paper]:
    if start_year > end_year:
        raise ValueError("start_year must be <= end_year")
    if max_fetch_limit_per_source < 1:
        raise ValueError("max_fetch_limit_per_source must be >= 1")

    arxiv_task = search_arxiv(
        keyword,
        max_results=max_results_per_source,
        fetch_all=fetch_all,
        max_fetch_limit=max_fetch_limit_per_source,
    )
    dblp_task = search_dblp(
        keyword,
        max_results=max_results_per_source,
        fetch_all=fetch_all,
        max_fetch_limit=max_fetch_limit_per_source,
    )
    arxiv_result, dblp_result = await asyncio.gather(
        arxiv_task, dblp_task, return_exceptions=True
    )
    arxiv_papers = arxiv_result if isinstance(arxiv_result, list) else []
    dblp_papers = dblp_result if isinstance(dblp_result, list) else []

    combined = arxiv_papers + dblp_papers
    filtered = [paper for paper in combined if _in_year_range(paper, start_year, end_year)]
    if strict_relevance:
        filtered = [
            paper
            for paper in filtered
            if _is_relevant(paper, keyword=keyword, title_only=title_only_match)
        ]
    deduped = _dedupe(filtered)
    classified = await _classify_all(deduped)
    classified.sort(
        key=lambda p: p.published_date or date(p.year or 1970, 1, 1),
        reverse=True,
    )
    return classified
