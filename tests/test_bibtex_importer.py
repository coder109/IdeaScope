from app.services.bibtex_importer import bibtex_to_papers


def test_bibtex_to_papers_parses_basic_fields():
    bib = """
@misc{lovelace2024test,
  title = {Test Paper},
  author = {Ada Lovelace and Alan Turing},
  year = {2024},
  doi = {10.1000/xyz},
  url = {https://example.org/paper},
  howpublished = {arXiv},
  keywords = {NLP, LLM}
}
"""
    papers = bibtex_to_papers(bib)
    assert len(papers) == 1
    p = papers[0]
    assert p["title"] == "Test Paper"
    assert p["authors"] == ["Ada Lovelace", "Alan Turing"]
    assert p["year"] == 2024
    assert p["doi"] == "10.1000/xyz"
    assert p["url"] == "https://example.org/paper"
    assert p["venue"] == "arXiv"
    assert p["preset_tags"] == ["NLP", "LLM"]


def test_bibtex_to_papers_skips_entry_without_title():
    bib = """
@misc{x,
  author = {A},
  year = {2020}
}
"""
    papers = bibtex_to_papers(bib)
    assert papers == []
