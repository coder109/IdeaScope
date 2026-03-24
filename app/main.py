from pathlib import Path

from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
from pydantic import BaseModel, Field

from app.models.paper import Paper
from app.services.bibtex_exporter import papers_to_bibtex
from app.services.bibtex_importer import bibtex_to_papers
from app.services.classifier import classify_papers
from app.services.markdown_exporter import papers_to_markdown
from app.services.persistence_service import add_analysis, create_search_run, get_run
from app.services.report_service import evaluate_idea_novelty, generate_keyword_report
from app.services.search_service import search_papers
from app.services.zotero_client import import_papers_to_zotero


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(Path(BASE_DIR).parent / ".env")

app = FastAPI(title="IdeaScope")
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


class SearchRequest(BaseModel):
    keyword: str = Field(min_length=1)
    start_year: int = Field(ge=1900, le=2100)
    end_year: int = Field(ge=1900, le=2100)
    max_results_per_source: int = Field(default=30, ge=1, le=200)
    fetch_all: bool = False
    max_fetch_limit_per_source: int = Field(default=1000, ge=1, le=5000)
    strict_relevance: bool = False
    title_only_match: bool = False


class BibTeXRequest(BaseModel):
    papers: list[dict]


class ClassifyRequest(BaseModel):
    papers: list[dict]
    use_ai: bool = True


class ZoteroImportRequest(BaseModel):
    papers: list[dict]


class ReportRequest(BaseModel):
    keywords: list[str] = Field(default_factory=list)
    papers: list[dict] | None = None
    run_id: str | None = None
    top_n: int = Field(default=120, ge=1, le=500)
    language: str = "en"


class IdeaEvaluateRequest(BaseModel):
    idea: str = Field(min_length=1)
    keywords: list[str] = Field(default_factory=list)
    papers: list[dict] | None = None
    run_id: str | None = None
    top_n: int = Field(default=120, ge=1, le=500)
    language: str = "en"


def _paper_from_any(raw: dict) -> dict:
    source = str(raw.get("source", "imported")).strip().lower()
    if source not in {"arxiv", "dblp", "imported"}:
        source = "imported"
    return {
        "source": source,
        "source_id": raw.get("source_id"),
        "title": raw.get("title", ""),
        "authors": raw.get("authors", []),
        "abstract": raw.get("abstract", ""),
        "venue": raw.get("venue"),
        "published_date": raw.get("published_date"),
        "year": raw.get("year"),
        "doi": raw.get("doi"),
        "url": raw.get("url"),
        "preset_tags": raw.get("preset_tags", []),
        "free_tags": raw.get("free_tags", []),
    }


def _load_analysis_papers(papers: list[dict] | None, run_id: str | None) -> tuple[list[dict], str | None]:
    if papers:
        return ([_paper_from_any(p) for p in papers], run_id)
    if run_id:
        run_payload = get_run(run_id)
        return ([_paper_from_any(p) for p in run_payload.get("papers_brief", [])], run_id)
    return ([], run_id)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "index.html")


@app.post("/api/search")
async def api_search(payload: SearchRequest) -> dict:
    try:
        papers = await search_papers(
            keyword=payload.keyword,
            start_year=payload.start_year,
            end_year=payload.end_year,
            max_results_per_source=payload.max_results_per_source,
            fetch_all=payload.fetch_all,
            max_fetch_limit_per_source=payload.max_fetch_limit_per_source,
            strict_relevance=payload.strict_relevance,
            title_only_match=payload.title_only_match,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    query = {
        "keyword": payload.keyword,
        "start_year": payload.start_year,
        "end_year": payload.end_year,
        "max_results_per_source": payload.max_results_per_source,
        "fetch_all": payload.fetch_all,
        "max_fetch_limit_per_source": payload.max_fetch_limit_per_source,
        "strict_relevance": payload.strict_relevance,
        "title_only_match": payload.title_only_match,
    }
    run_payload = create_search_run(query=query, papers=papers)
    return {
        "count": len(papers),
        "papers": [paper.model_dump() for paper in papers],
        "run_id": run_payload["run_id"],
    }


@app.post("/api/export/bibtex")
async def export_bibtex(payload: BibTeXRequest) -> StreamingResponse:
    bibtext = papers_to_bibtex(payload.papers)
    filename = "papers.bib"
    return StreamingResponse(
        iter([bibtext.encode("utf-8")]),
        media_type="application/x-bibtex",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.post("/api/export/markdown")
async def export_markdown(payload: BibTeXRequest) -> StreamingResponse:
    md = papers_to_markdown(payload.papers)
    filename = "papers.md"
    return StreamingResponse(
        iter([md.encode("utf-8")]),
        media_type="text/markdown; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.post("/api/import/bibtex")
async def import_bibtex(file: UploadFile = File(...)) -> dict:
    try:
        content = await file.read()
        text = content.decode("utf-8", errors="ignore")
        papers = bibtex_to_papers(text)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid BibTeX file: {exc}") from exc
    return {"count": len(papers), "papers": papers}


@app.post("/api/classify")
async def api_classify(payload: ClassifyRequest) -> dict:
    papers = await classify_papers(payload.papers, use_ai=payload.use_ai)
    return {"count": len(papers), "papers": papers}


@app.post("/api/export/zotero")
async def export_zotero(payload: ZoteroImportRequest) -> dict:
    try:
        result = await import_papers_to_zotero(payload.papers)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Zotero import failed: {exc}") from exc
    return result


@app.post("/api/report/keywords")
async def api_report_keywords(payload: ReportRequest) -> dict:
    try:
        papers_raw, run_id = _load_analysis_papers(payload.papers, payload.run_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    if not papers_raw:
        raise HTTPException(status_code=400, detail="Provide papers or run_id.")
    papers = [Paper(**p) for p in papers_raw]
    report = await generate_keyword_report(
        papers, payload.keywords, top_n=payload.top_n, language=payload.language
    )
    if run_id:
        add_analysis(run_id, "keyword_report", report)
    return {"run_id": run_id, "report": report}


@app.post("/api/idea/evaluate")
async def api_idea_evaluate(payload: IdeaEvaluateRequest) -> dict:
    try:
        papers_raw, run_id = _load_analysis_papers(payload.papers, payload.run_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    if not papers_raw:
        raise HTTPException(status_code=400, detail="Provide papers or run_id.")
    papers = [Paper(**p) for p in papers_raw]
    novelty = await evaluate_idea_novelty(
        papers,
        idea=payload.idea,
        keywords=payload.keywords,
        top_n=payload.top_n,
        language=payload.language,
    )
    if run_id:
        add_analysis(run_id, "idea_novelty", novelty)
    return {"run_id": run_id, "result": novelty}


@app.get("/api/runs/{run_id}")
async def api_get_run(run_id: str) -> dict:
    try:
        return get_run(run_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
