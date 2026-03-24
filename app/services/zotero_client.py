import os
from datetime import date, datetime

import httpx


def _split_name(full_name: str) -> tuple[str, str]:
    parts = full_name.strip().split()
    if len(parts) <= 1:
        return ("", parts[0] if parts else "Unknown")
    return (" ".join(parts[:-1]), parts[-1])


def _paper_to_zotero_item(paper: dict, collection_key: str | None = None) -> dict:
    authors = paper.get("authors") or []
    creators = []
    for a in authors:
        first, last = _split_name(str(a))
        creators.append(
            {
                "creatorType": "author",
                "firstName": first,
                "lastName": last,
            }
        )

    pub_date = paper.get("published_date")
    year = paper.get("year")
    if isinstance(pub_date, (date, datetime)):
        zotero_date = str(pub_date)
    elif isinstance(pub_date, str) and pub_date:
        zotero_date = pub_date
    elif year:
        zotero_date = str(year)
    else:
        zotero_date = ""

    tags = []
    for tag in (paper.get("preset_tags") or []):
        tags.append({"tag": str(tag)})
    for tag in (paper.get("free_tags") or []):
        tags.append({"tag": str(tag)})

    item = {
        "itemType": "journalArticle",
        "title": paper.get("title") or "Untitled",
        "creators": creators,
        "abstractNote": paper.get("abstract") or "",
        "publicationTitle": paper.get("venue") or "",
        "date": zotero_date,
        "DOI": paper.get("doi") or "",
        "url": paper.get("url") or "",
        "tags": tags,
    }
    if collection_key:
        item["collections"] = [collection_key]
    return item


async def import_papers_to_zotero(papers: list[dict]) -> dict:
    library_type = os.getenv("ZOTERO_LIBRARY_TYPE", "user").strip().lower()
    library_id = os.getenv("ZOTERO_LIBRARY_ID", "").strip()
    api_key = os.getenv("ZOTERO_API_KEY", "").strip()
    collection_key = os.getenv("ZOTERO_COLLECTION_KEY", "").strip() or None

    if library_type not in {"user", "group"}:
        raise ValueError("ZOTERO_LIBRARY_TYPE must be 'user' or 'group'")
    if not library_id or not api_key:
        raise ValueError("Missing Zotero config: ZOTERO_LIBRARY_ID or ZOTERO_API_KEY")

    endpoint = f"https://api.zotero.org/{library_type}s/{library_id}/items"
    items = [_paper_to_zotero_item(p, collection_key=collection_key) for p in papers]
    headers = {
        "Zotero-API-Version": "3",
        "Zotero-API-Key": api_key,
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(endpoint, headers=headers, json=items)
        resp.raise_for_status()
        payload = resp.json()

    return {
        "total": len(items),
        "success_count": len((payload.get("successful") or {}).keys()),
        "failed_count": len((payload.get("failed") or {}).keys()),
    }
