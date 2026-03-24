import json
import os
import re

import httpx

from app.models.paper import Paper


DEFAULT_PRESET_TAGS = ["NLP", "CV", "IR", "Recsys", "Systems", "Theory", "Robotics"]
PRESET_RULES: dict[str, list[str]] = {
    "NLP": ["language model", "nlp", "token", "text generation", "transformer"],
    "CV": ["image", "vision", "segmentation", "detection", "video"],
    "IR": ["information retrieval", "retrieval", "search engine", "ranking"],
    "Recsys": ["recommendation", "recommender", "collaborative filtering"],
    "Systems": ["distributed", "database", "operating system", "compiler", "network"],
    "Theory": ["theorem", "proof", "complexity", "optimization"],
    "Robotics": ["robot", "robotics", "navigation", "control"],
}


def classify_with_rules(paper: Paper, preset_tags: list[str] | None = None) -> list[str]:
    tags = preset_tags or DEFAULT_PRESET_TAGS
    text = f"{paper.title} {paper.abstract}".lower()
    matched = []
    for tag in tags:
        rules = PRESET_RULES.get(tag, [])
        if any(rule in text for rule in rules):
            matched.append(tag)
    return matched


async def classify_with_llm(paper: Paper, preset_tags: list[str] | None = None) -> tuple[list[str], list[str]]:
    preset = classify_with_rules(paper, preset_tags)
    if os.getenv("CLASSIFIER_ENABLED", "true").lower() == "false":
        return (preset or ["Uncategorized"], [])

    base_url = os.getenv("OPENAI_BASE_URL", "").rstrip("/")
    api_key = os.getenv("OPENAI_API_KEY", "")
    model = os.getenv("OPENAI_MODEL", "")
    if not base_url or not api_key or not model:
        return (preset or ["Uncategorized"], [])

    prompt = _build_prompt(paper, preset_tags or DEFAULT_PRESET_TAGS)
    endpoint = f"{base_url}/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    body = {
        "model": model,
        "temperature": 0.2,
        "messages": [
            {"role": "system", "content": "You classify computer science papers."},
            {"role": "user", "content": prompt},
        ],
    }

    try:
        async with httpx.AsyncClient(timeout=25.0) as client:
            resp = await client.post(endpoint, headers=headers, json=body)
            resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"]
        free_tags = _parse_free_tags(content)
        final_preset = preset or ["Uncategorized"]
        return (final_preset, free_tags)
    except Exception:
        return (preset or ["Uncategorized"], [])


def _build_prompt(paper: Paper, preset_tags: list[str]) -> str:
    allowed = ", ".join(preset_tags)
    return (
        "Given a paper, generate 1-3 short topic tags.\n"
        f"Paper title: {paper.title}\n"
        f"Abstract: {paper.abstract}\n"
        f"Known preset categories for reference: {allowed}\n"
        'Return only JSON like {"free_tags":["tag1","tag2"]}.'
    )


def _parse_free_tags(content: str) -> list[str]:
    content = content.strip()
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", content, re.DOTALL)
        if not match:
            return []
        try:
            parsed = json.loads(match.group(0))
        except json.JSONDecodeError:
            return []
    tags = parsed.get("free_tags", [])
    if not isinstance(tags, list):
        return []
    cleaned = [str(t).strip() for t in tags if str(t).strip()]
    return cleaned[:3]


async def classify_papers(
    papers: list[dict],
    use_ai: bool = True,
    preset_tags: list[str] | None = None,
) -> list[dict]:
    result: list[dict] = []
    for raw in papers:
        normalized = dict(raw)
        source = str(normalized.get("source", "imported")).strip().lower()
        if source not in {"arxiv", "dblp", "imported"}:
            source = "imported"
        normalized["source"] = source
        paper = Paper(**normalized)
        preset = classify_with_rules(paper, preset_tags)
        free: list[str] = []
        if use_ai:
            preset, free = await classify_with_llm(paper, preset_tags)
        paper.preset_tags = preset or ["Uncategorized"]
        paper.free_tags = free
        result.append(paper.model_dump())
    return result
