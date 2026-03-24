import re
from collections import defaultdict


def papers_to_bibtex(papers: list[dict]) -> str:
    key_count: defaultdict[str, int] = defaultdict(int)
    entries: list[str] = []

    for paper in papers:
        title = (paper.get("title") or "").strip()
        if not title:
            continue
        authors = paper.get("authors") or []
        author_field = " and ".join(authors) if authors else "Unknown"
        year = paper.get("year") or (
            str(paper.get("published_date", ""))[:4] if paper.get("published_date") else "n.d."
        )
        url = paper.get("url") or ""
        doi = paper.get("doi") or ""
        venue = paper.get("venue") or ""
        keywords = [str(t).strip() for t in (paper.get("preset_tags") or []) if str(t).strip()]
        keywords.extend([str(t).strip() for t in (paper.get("free_tags") or []) if str(t).strip()])

        key = _build_bibtex_key(authors, str(year), title)
        key_count[key] += 1
        if key_count[key] > 1:
            key = f"{key}{key_count[key]}"

        lines = [
            f"@misc{{{key},",
            f"  title = {{{_escape(title)}}},",
            f"  author = {{{_escape(author_field)}}},",
            f"  year = {{{_escape(str(year))}}},",
        ]
        if venue:
            lines.append(f"  howpublished = {{{_escape(venue)}}},")
        if doi:
            lines.append(f"  doi = {{{_escape(doi)}}},")
        if url:
            lines.append(f"  url = {{{_escape(url)}}},")
        if keywords:
            lines.append(f"  keywords = {{{_escape(', '.join(keywords))}}},")
        lines.append("}")
        entries.append("\n".join(lines))

    return "\n\n".join(entries) + ("\n" if entries else "")


def _build_bibtex_key(authors: list[str], year: str, title: str) -> str:
    first_author = "unknown"
    if authors:
        cleaned = re.sub(r"[^a-zA-Z0-9]", "", authors[0].split()[-1].lower())
        if cleaned:
            first_author = cleaned
    short_title = re.sub(r"[^a-zA-Z0-9]", "", title.lower())[:20] or "paper"
    year_clean = re.sub(r"[^0-9]", "", year)[:4] or "nd"
    return f"{first_author}{year_clean}{short_title}"


def _escape(value: str) -> str:
    return value.replace("{", "\\{").replace("}", "\\}")
