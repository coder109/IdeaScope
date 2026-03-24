import re


ENTRY_RE = re.compile(r"@\w+\s*\{\s*([^,]+)\s*,(.*?)\n\}", re.DOTALL)
FIELD_RE = re.compile(r"(\w+)\s*=\s*[\{\"](.+?)[\}\"]\s*,?", re.DOTALL)


def bibtex_to_papers(bibtex_text: str) -> list[dict]:
    papers: list[dict] = []
    for _, body in ENTRY_RE.findall(bibtex_text):
        fields = _parse_fields(body)
        title = fields.get("title", "").strip()
        if not title:
            continue
        authors = _parse_authors(fields.get("author", ""))
        year = _to_int(fields.get("year"))
        keywords = _parse_keywords(fields.get("keywords", ""))

        papers.append(
            {
                "source": "imported",
                "source_id": None,
                "title": title,
                "authors": authors,
                "abstract": fields.get("abstract", "") or fields.get("abstractnote", ""),
                "venue": fields.get("howpublished", "") or fields.get("journal", ""),
                "published_date": None,
                "year": year,
                "doi": fields.get("doi", ""),
                "url": fields.get("url", ""),
                "preset_tags": keywords,
                "free_tags": [],
            }
        )
    return papers


def _parse_fields(body: str) -> dict:
    result: dict[str, str] = {}
    for key, value in FIELD_RE.findall(body):
        result[key.strip().lower()] = _clean_value(value)
    return result


def _clean_value(value: str) -> str:
    return value.replace("\n", " ").replace("\\{", "{").replace("\\}", "}").strip()


def _parse_authors(raw: str) -> list[str]:
    if not raw:
        return []
    return [part.strip() for part in raw.split(" and ") if part.strip()]


def _parse_keywords(raw: str) -> list[str]:
    if not raw:
        return []
    return [part.strip() for part in raw.split(",") if part.strip()]


def _to_int(value: str | None) -> int | None:
    if not value:
        return None
    try:
        return int(str(value).strip())
    except ValueError:
        return None
