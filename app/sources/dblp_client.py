import asyncio
from datetime import date

import httpx

from app.models.paper import Paper


DBLP_API = "https://dblp.org/search/publ/api"
DBLP_PAGE_SIZE = 30
DBLP_MAX_RETRIES = 2


async def search_dblp(
    keyword: str,
    max_results: int = 30,
    fetch_all: bool = False,
    max_fetch_limit: int = 1000,
) -> list[Paper]:
    target = max_fetch_limit if fetch_all else max_results
    collected: list[Paper] = []
    offset = 0

    async with httpx.AsyncClient(timeout=25.0) as client:
        while len(collected) < target:
            batch_size = min(DBLP_PAGE_SIZE, target - len(collected))
            params = {"q": keyword, "h": batch_size, "f": offset, "format": "json"}
            resp = await _get_with_retry(client, params)
            if resp is None:
                break
            batch = _parse_dblp_json(resp.json())
            if not batch:
                break
            collected.extend(batch)
            if len(batch) < batch_size:
                break
            offset += len(batch)

    return collected[:target]


def _parse_dblp_json(payload: dict) -> list[Paper]:
    result = payload.get("result", {})
    hits = (((result.get("hits") or {}).get("hit")) or [])
    if isinstance(hits, dict):
        hits = [hits]

    papers: list[Paper] = []
    for hit in hits:
        info = hit.get("info", {})
        title = (info.get("title") or "").strip()
        authors_raw = ((info.get("authors") or {}).get("author")) or []
        if isinstance(authors_raw, str):
            authors = [authors_raw]
        elif isinstance(authors_raw, dict):
            authors = [authors_raw.get("text", "")]
        else:
            authors = [a if isinstance(a, str) else a.get("text", "") for a in authors_raw]

        year = _to_int(info.get("year"))
        published_date = date(year, 1, 1) if year else None
        doi = info.get("doi")
        url = info.get("ee") or info.get("url")
        venue = info.get("venue")

        papers.append(
            Paper(
                source="dblp",
                source_id=info.get("key"),
                title=title,
                authors=[a.strip() for a in authors if a and a.strip()],
                abstract="",
                venue=venue,
                published_date=published_date,
                year=year,
                doi=doi,
                url=url,
            )
        )
    return papers


def _to_int(value: object) -> int | None:
    if value is None:
        return None
    try:
        return int(str(value))
    except ValueError:
        return None


async def _get_with_retry(client: httpx.AsyncClient, params: dict) -> httpx.Response | None:
    for attempt in range(DBLP_MAX_RETRIES + 1):
        try:
            resp = await client.get(DBLP_API, params=params)
            if resp.status_code >= 500:
                raise httpx.HTTPStatusError(
                    f"DBLP server error: {resp.status_code}",
                    request=resp.request,
                    response=resp,
                )
            resp.raise_for_status()
            return resp
        except (httpx.HTTPStatusError, httpx.RequestError):
            if attempt >= DBLP_MAX_RETRIES:
                return None
            await asyncio.sleep(0.4 * (attempt + 1))
    return None
