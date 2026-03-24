from app.services.zotero_client import _paper_to_zotero_item


def test_paper_to_zotero_item_includes_tags_and_collections():
    paper = {
        "title": "Test Paper",
        "authors": ["Ada Lovelace", "Alan Turing"],
        "abstract": "Abstract text",
        "venue": "arXiv",
        "year": 2024,
        "doi": "10.1000/xyz",
        "url": "https://example.org",
        "preset_tags": ["NLP"],
        "free_tags": ["LLM"],
    }
    item = _paper_to_zotero_item(paper, collection_key="ABC123")
    assert item["itemType"] == "journalArticle"
    assert item["title"] == "Test Paper"
    assert item["date"] == "2024"
    assert item["DOI"] == "10.1000/xyz"
    assert item["collections"] == ["ABC123"]
    tags = [t["tag"] for t in item["tags"]]
    assert "NLP" in tags
    assert "LLM" in tags
