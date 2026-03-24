from datetime import datetime
from xml.etree import ElementTree

import httpx

from app.models.paper import Paper


ARXIV_API = "https://export.arxiv.org/api/query"
ATOM_NS = {"atom": "http://www.w3.org/2005/Atom"}
ARXIV_PAGE_SIZE = 100


async def search_arxiv(
    keyword: str,
    max_results: int = 30,
    fetch_all: bool = False,
    max_fetch_limit: int = 1000,
) -> list[Paper]:
    target = max_fetch_limit if fetch_all else max_results
    collected: list[Paper] = []
    start = 0

    async with httpx.AsyncClient(timeout=25.0, follow_redirects=True) as client:
        while len(collected) < target:
            batch_size = min(ARXIV_PAGE_SIZE, target - len(collected))
            params = {
                "search_query": f"all:{keyword}",
                "start": start,
                "max_results": batch_size,
                "sortBy": "submittedDate",
                "sortOrder": "descending",
            }
            resp = await client.get(ARXIV_API, params=params)
            resp.raise_for_status()
            batch = _parse_arxiv_atom(resp.text)
            if not batch:
                break
            collected.extend(batch)
            if len(batch) < batch_size:
                break
            start += len(batch)

    return collected[:target]


def _parse_arxiv_atom(xml_text: str) -> list[Paper]:
    root = ElementTree.fromstring(xml_text.encode("utf-8"))
    entries = root.findall("atom:entry", ATOM_NS)
    papers: list[Paper] = []

    for entry in entries:
        paper_id = _find_text(entry, "atom:id")
        title = (_find_text(entry, "atom:title") or "").replace("\n", " ").strip()
        summary = (_find_text(entry, "atom:summary") or "").replace("\n", " ").strip()
        published_raw = _find_text(entry, "atom:published")
        published_date = None
        year = None
        if published_raw:
            dt = datetime.fromisoformat(published_raw.replace("Z", "+00:00"))
            published_date = dt.date()
            year = dt.year

        authors = [
            (author.find("atom:name", ATOM_NS).text or "").strip()
            for author in entry.findall("atom:author", ATOM_NS)
            if author.find("atom:name", ATOM_NS) is not None
        ]

        doi = None
        for link in entry.findall("atom:link", ATOM_NS):
            if link.attrib.get("title") == "doi":
                doi = link.attrib.get("href")
                break

        papers.append(
            Paper(
                source="arxiv",
                source_id=paper_id,
                title=title,
                authors=authors,
                abstract=summary,
                published_date=published_date,
                year=year,
                doi=doi,
                url=paper_id,
            )
        )
    return papers


def _find_text(element: ElementTree.Element, path: str) -> str | None:
    found = element.find(path, ATOM_NS)
    if found is None or found.text is None:
        return None
    return found.text.strip()
