from collections import defaultdict


def papers_to_markdown(papers: list[dict]) -> str:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for paper in papers:
        free_tags = paper.get("free_tags") or []
        preset = paper.get("preset_tags") or []
        if free_tags and isinstance(free_tags, list):
            group = str(free_tags[0]).strip() or "Uncategorized"
        elif preset and isinstance(preset, list):
            group = str(preset[0]).strip() or "Uncategorized"
        else:
            group = "Uncategorized"
        grouped[group].append(paper)

    lines: list[str] = ["# Papers by Category", ""]
    for category in sorted(grouped.keys(), key=lambda x: x.lower()):
        lines.append(f"## {category}")
        entries = grouped[category]
        if not entries:
            lines.append("- (empty)")
            lines.append("")
            continue
        for paper in entries:
            title = str(paper.get("title") or "").strip()
            if not title:
                continue
            url = str(paper.get("url") or "").strip()
            if url:
                lines.append(f"- [{title}]({url})")
            else:
                lines.append(f"- {title}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"
