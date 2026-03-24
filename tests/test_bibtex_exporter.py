from app.services.bibtex_exporter import papers_to_bibtex


def test_bibtex_export_basic():
    papers = [
        {
            "title": "Test Title",
            "authors": ["Ada Lovelace", "Alan Turing"],
            "year": 2024,
            "url": "https://example.org/paper",
            "doi": "10.1000/xyz",
            "venue": "ArXiv",
        }
    ]
    bib = papers_to_bibtex(papers)
    assert "@misc{" in bib
    assert "title = {Test Title}" in bib
    assert "author = {Ada Lovelace and Alan Turing}" in bib
    assert "year = {2024}" in bib
    assert "doi = {10.1000/xyz}" in bib
    assert "url = {https://example.org/paper}" in bib


def test_bibtex_export_handles_duplicate_keys():
    papers = [
        {"title": "Alpha", "authors": ["Ada Lovelace"], "year": 2024},
        {"title": "Alpha", "authors": ["Ada Lovelace"], "year": 2024},
    ]
    bib = papers_to_bibtex(papers)
    assert bib.count("@misc{") == 2
