import json
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from app.models.paper import Paper
from app.services.report_service import build_paper_brief


BASE_DIR = Path(__file__).resolve().parents[2]
RUNS_DIR = BASE_DIR / "runs"


def _run_file(run_id: str) -> Path:
    safe = "".join(ch for ch in run_id if ch.isalnum() or ch in ("-", "_"))
    return RUNS_DIR / f"{safe}.json"


def _ensure_dir() -> None:
    RUNS_DIR.mkdir(parents=True, exist_ok=True)


def create_search_run(query: dict, papers: list[Paper]) -> dict:
    _ensure_dir()
    run_id = uuid4().hex
    payload = {
        "run_id": run_id,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "query": query,
        "papers_count": len(papers),
        "papers_brief": [build_paper_brief(p) for p in papers],
        "analysis": {},
    }
    _run_file(run_id).write_text(
        json.dumps(payload, ensure_ascii=True, indent=2), encoding="utf-8"
    )
    return payload


def get_run(run_id: str) -> dict:
    path = _run_file(run_id)
    if not path.exists():
        raise FileNotFoundError(f"run_id not found: {run_id}")
    return json.loads(path.read_text(encoding="utf-8"))


def add_analysis(run_id: str, key: str, value: dict) -> dict:
    payload = get_run(run_id)
    analysis = payload.get("analysis", {})
    if not isinstance(analysis, dict):
        analysis = {}
    analysis[key] = value
    payload["analysis"] = analysis
    payload["updated_at"] = datetime.utcnow().isoformat() + "Z"
    _run_file(run_id).write_text(
        json.dumps(payload, ensure_ascii=True, indent=2), encoding="utf-8"
    )
    return payload
