import json
import os
import re
from datetime import datetime

import httpx

from app.models.paper import Paper


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except ValueError:
        return default


MAX_PAPERS_FOR_ANALYSIS = _env_int("MAX_PAPERS_FOR_ANALYSIS", 120)
CHUNK_SIZE = _env_int("ANALYSIS_CHUNK_SIZE", 20)
MAX_ABSTRACT_CHARS = _env_int("MAX_ABSTRACT_CHARS", 800)


def _lang_name(language: str) -> str:
    return "Chinese" if language.lower().startswith("zh") else "English"


def _truncate(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[:limit].rstrip() + "..."


def build_paper_brief(paper: Paper, max_abstract_chars: int = MAX_ABSTRACT_CHARS) -> dict:
    year = paper.published_date.year if paper.published_date else paper.year
    return {
        "title": paper.title,
        "authors": paper.authors[:6],
        "year": year,
        "venue": paper.venue or "",
        "source": paper.source,
        "url": paper.url,
        "doi": paper.doi,
        "abstract": _truncate(paper.abstract or "", max_abstract_chars),
        "preset_tags": paper.preset_tags,
        "free_tags": paper.free_tags,
    }


def _keyword_score(paper: Paper, keywords: list[str]) -> float:
    text = " ".join(
        [
            paper.title or "",
            paper.abstract or "",
            " ".join(paper.preset_tags or []),
            " ".join(paper.free_tags or []),
        ]
    ).lower()
    score = 0.0
    for kw in keywords:
        q = kw.strip().lower()
        if not q:
            continue
        if q in (paper.title or "").lower():
            score += 4.0
        if q in (paper.abstract or "").lower():
            score += 2.0
        if q in text:
            score += 1.0
    year = paper.published_date.year if paper.published_date else (paper.year or 2000)
    recency_bonus = max(0.0, min(2.0, (year - 2018) / 4))
    return score + recency_bonus


def _select_top_papers(papers: list[Paper], keywords: list[str], top_n: int) -> list[Paper]:
    scored = sorted(papers, key=lambda p: _keyword_score(p, keywords), reverse=True)
    return scored[: min(top_n, len(scored))]


def _chunk(items: list[dict], size: int) -> list[list[dict]]:
    if size <= 0:
        size = 20
    return [items[i : i + size] for i in range(0, len(items), size)]


def _extract_json_payload(content: str) -> dict:
    text = (content or "").strip()
    if not text:
        return {}
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            return {"raw_text": text}
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            return {"raw_text": text}


async def _chat_json(system_prompt: str, user_prompt: str, temperature: float = 0.2) -> dict:
    base_url = os.getenv("OPENAI_BASE_URL", "").rstrip("/")
    api_key = os.getenv("OPENAI_API_KEY", "")
    model = os.getenv("OPENAI_MODEL", "")
    if not base_url or not api_key or not model:
        return {}

    endpoint = f"{base_url}/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    body = {
        "model": model,
        "temperature": temperature,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }
    try:
        async with httpx.AsyncClient(timeout=45.0) as client:
            resp = await client.post(endpoint, headers=headers, json=body)
            resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"]
        return _extract_json_payload(content)
    except Exception:
        return {}


def _fallback_chunk_summary(chunk: list[dict], keywords: list[str]) -> dict:
    representative = [x["title"] for x in chunk[:3]]
    keyword_hits = {kw: 0 for kw in keywords}
    for paper in chunk:
        text = f"{paper.get('title', '')} {paper.get('abstract', '')}".lower()
        for kw in keywords:
            if kw.lower() in text:
                keyword_hits[kw] += 1
    return {
        "summary": f"Chunk with {len(chunk)} papers.",
        "representative_titles": representative,
        "keyword_hits": keyword_hits,
    }


async def _summarize_chunk(chunk: list[dict], keywords: list[str]) -> dict:
    system_prompt = "You summarize paper chunks for later global synthesis."
    user_prompt = (
        "Given papers and target keywords, return strict JSON with keys:\n"
        "- summary (string)\n"
        "- representative_titles (array of strings)\n"
        "- keyword_hits (object mapping keyword->count)\n\n"
        f"keywords: {keywords}\n"
        f"papers: {json.dumps(chunk, ensure_ascii=True)}"
    )
    payload = await _chat_json(system_prompt, user_prompt, temperature=0.2)
    if payload:
        return payload
    return _fallback_chunk_summary(chunk, keywords)


def _fallback_keyword_report(
    selected_briefs: list[dict], chunk_summaries: list[dict], keywords: list[str], language: str
) -> dict:
    coverage = {kw: 0 for kw in keywords}
    for summary in chunk_summaries:
        hits = summary.get("keyword_hits", {})
        if isinstance(hits, dict):
            for kw in keywords:
                try:
                    coverage[kw] += int(hits.get(kw, 0))
                except (ValueError, TypeError):
                    pass

    representative = []
    for summary in chunk_summaries:
        titles = summary.get("representative_titles", [])
        if isinstance(titles, list):
            representative.extend([str(t) for t in titles[:3]])
    representative = representative[:8]

    if language.lower().startswith("zh"):
        trends = ["近期论文主要集中在这些关键词及其组合方向。"]
        gaps = ["跨数据集泛化与统一评测协议仍有明显改进空间。"]
        overview = f"已分析 {len(selected_briefs)} 篇论文，覆盖 {len(keywords)} 个关键词。"
    else:
        trends = ["Recent papers cluster around the requested keywords."]
        gaps = ["Benchmarking consistency and broader domain transfer remain open."]
        overview = f"Analyzed {len(selected_briefs)} papers for {len(keywords)} keywords."
    return {
        "overview": overview,
        "keyword_coverage": coverage,
        "representative_works": representative,
        "trends": trends,
        "research_gaps": gaps,
        "generated_at": datetime.utcnow().isoformat() + "Z",
    }


async def generate_keyword_report(
    papers: list[Paper],
    keywords: list[str],
    top_n: int = MAX_PAPERS_FOR_ANALYSIS,
    language: str = "en",
) -> dict:
    clean_keywords = [k.strip() for k in keywords if k and k.strip()]
    if not clean_keywords:
        return {"error": "keywords cannot be empty"}
    if not papers:
        return {"error": "papers cannot be empty"}

    selected = _select_top_papers(papers, clean_keywords, top_n)
    briefs = [build_paper_brief(p) for p in selected]
    chunked = _chunk(briefs, CHUNK_SIZE)
    chunk_summaries = [await _summarize_chunk(c, clean_keywords) for c in chunked]

    system_prompt = "You are a concise research analyst. Output strict JSON only."
    user_prompt = (
        "Synthesize a keyword-focused report from chunk summaries.\n"
        "Return strict JSON keys:\n"
        "- overview\n"
        "- keyword_coverage (object keyword->count)\n"
        "- representative_works (array)\n"
        "- trends (array)\n"
        "- research_gaps (array)\n\n"
        f"Output language: {_lang_name(language)}.\n"
        f"keywords: {json.dumps(clean_keywords, ensure_ascii=True)}\n"
        f"chunk_summaries: {json.dumps(chunk_summaries, ensure_ascii=True)}"
    )
    final_payload = await _chat_json(system_prompt, user_prompt, temperature=0.2)
    if not final_payload:
        final_payload = _fallback_keyword_report(briefs, chunk_summaries, clean_keywords, language)

    final_payload["source_paper_count"] = len(papers)
    final_payload["analyzed_paper_count"] = len(selected)
    final_payload["chunk_count"] = len(chunked)
    final_payload["keywords"] = clean_keywords
    final_payload["language"] = language
    final_payload["generated_at"] = datetime.utcnow().isoformat() + "Z"
    return final_payload


def _fallback_novelty(
    idea: str, keywords: list[str], selected_briefs: list[dict], language: str
) -> dict:
    tokens = [t for t in re.split(r"[^a-zA-Z0-9]+", idea.lower()) if len(t) >= 4]
    hit = 0
    for paper in selected_briefs:
        text = f"{paper.get('title', '')} {paper.get('abstract', '')}".lower()
        if any(t in text for t in tokens[:25]):
            hit += 1
    overlap_ratio = hit / max(1, len(selected_briefs))
    novelty = max(0.0, min(10.0, 8.5 - overlap_ratio * 6.0))
    if language.lower().startswith("zh"):
        similar = [f"在已分析论文中，有 {hit}/{len(selected_briefs)} 篇与该 idea 术语存在重叠。"]
        diff = ["建议明确方法创新点，并补充更强对比实验。"]
        risks = ["可能与已有工作部分重叠，需要更系统的基线验证。"]
        overall = f"基于关键词 {keywords}，该 idea 具备中等新颖性。"
    else:
        similar = [f"{hit} of {len(selected_briefs)} analyzed papers share idea terms."]
        diff = ["Clarify methodological novelty and stronger ablations."]
        risks = ["Potential overlap with existing work; run stronger baselines."]
        overall = f"Idea appears moderately novel for keywords {keywords}."
    return {
        "novelty_score": round(novelty, 2),
        "confidence": "medium",
        "similar_work_signals": similar,
        "differentiators": diff,
        "risks": risks,
        "overall_assessment": overall,
    }


async def evaluate_idea_novelty(
    papers: list[Paper],
    idea: str,
    keywords: list[str],
    top_n: int = MAX_PAPERS_FOR_ANALYSIS,
    language: str = "en",
) -> dict:
    clean_keywords = [k.strip() for k in keywords if k and k.strip()]
    if not idea.strip():
        return {"error": "idea cannot be empty"}
    if not papers:
        return {"error": "papers cannot be empty"}

    selected = _select_top_papers(papers, clean_keywords or [idea], top_n)
    briefs = [build_paper_brief(p) for p in selected]
    chunked = _chunk(briefs, CHUNK_SIZE)
    chunk_summaries = [await _summarize_chunk(c, clean_keywords or [idea]) for c in chunked]

    system_prompt = "You evaluate research idea novelty with practical evidence. Output strict JSON only."
    user_prompt = (
        "Given idea and chunk summaries from related papers, return strict JSON keys:\n"
        "- novelty_score (0-10)\n"
        "- confidence (low|medium|high)\n"
        "- similar_work_signals (array)\n"
        "- differentiators (array)\n"
        "- risks (array)\n"
        "- overall_assessment (string)\n\n"
        f"Output language: {_lang_name(language)}.\n"
        f"keywords: {json.dumps(clean_keywords, ensure_ascii=True)}\n"
        f"idea: {idea}\n"
        f"chunk_summaries: {json.dumps(chunk_summaries, ensure_ascii=True)}"
    )
    payload = await _chat_json(system_prompt, user_prompt, temperature=0.2)
    if not payload:
        payload = _fallback_novelty(idea, clean_keywords, briefs, language)

    payload["idea"] = idea
    payload["source_paper_count"] = len(papers)
    payload["analyzed_paper_count"] = len(selected)
    payload["chunk_count"] = len(chunked)
    payload["keywords"] = clean_keywords
    payload["language"] = language
    payload["generated_at"] = datetime.utcnow().isoformat() + "Z"
    return payload
