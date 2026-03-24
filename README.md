# IdeaScope 🔎💡

[中文 README](./README.zh-CN.md)

IdeaScope is a FastAPI web app for searching papers from arXiv + DBLP, classifying them, exporting/importing BibTeX, generating keyword reports, and evaluating idea novelty.

## ✨ What this project does

- Search papers by keyword and year range
- Support normal mode and approximate full crawl mode
- Classify papers with preset tags and optional AI-generated free tags
- Export results to `BibTeX` or `Markdown`
- Import `BibTeX` files back into the UI
- Import current papers into Zotero via API
- Persist search snapshots into `runs/<run_id>.json`
- Re-open a previous run by `run_id`
- Generate a keyword report from current papers or a saved run
- Evaluate novelty of a research idea against current papers or a saved run

## 📦 Requirements

- Python 3.10+ recommended
- Network access to arXiv/DBLP
- Optional: OpenAI-compatible API for AI classification/reporting/novelty
- Optional: Zotero API credentials for Zotero import

## ⚙️ Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Create or edit `.env` in project root (`project_root/.env`):

- `OPENAI_BASE_URL` (OpenAI-compatible endpoint, usually ending with `/v1`)
- `OPENAI_API_KEY`
- `OPENAI_MODEL`
- `CLASSIFIER_ENABLED=true|false`
- `DEFAULT_PRESET_TAGS` (comma-separated)
- `MAX_PAPERS_FOR_ANALYSIS` (optional, default `120`)
- `ANALYSIS_CHUNK_SIZE` (optional, default `20`)
- `MAX_ABSTRACT_CHARS` (optional, default `800`)
- `ZOTERO_LIBRARY_TYPE` (`user` or `group`)
- `ZOTERO_LIBRARY_ID`
- `ZOTERO_API_KEY`
- `ZOTERO_COLLECTION_KEY` (optional)

## 🚀 Run the app

```bash
uvicorn app.main:app --reload
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000).

## 🧭 UI Guide (every control and button)

### Top-right controls

- `UI language`: switch interface language between system/Chinese/English.
- `Theme mode`: switch between system/light/dark theme.

### Search form fields

- `Keyword`: required for `Search`.
- `Start year` / `End year`: publication year filter.
- `Max results/source`: used in normal mode only.
- `Approx full crawl cap`: used only when full crawl mode is enabled.
- `Approx full crawl mode` (checkbox): when enabled, paginated fetching is used until per-source cap.
- `Use AI for classify` (checkbox): controls whether `Classify` calls AI free-tag generation.

### Analysis fields

- `Report keywords`: comma-separated keywords for report coverage/trend analysis.
- `Idea`: free text for novelty evaluation.
- `Run ID`: target `run_id` to reload.
- `Analysis top N`: upper bound of papers used by report and idea evaluation.
- `Report language`: output language for report and novelty result.

### Buttons (detailed)

#### `Search`

- Calls `POST /api/search`.
- Requires `Keyword`.
- Returns papers and a new `run_id`.
- Side effects:
  - Updates paper list on page.
  - Shows status line with paper count.
  - Fills `Run ID` input automatically.
  - Stores run snapshot under `runs/<run_id>.json`.

#### `Classify`

- Calls `POST /api/classify` in batches.
- Requires current paper list (from Search/Load Run/BibTeX import).
- Uses `Use AI for classify` checkbox to set `use_ai`.
- Side effects:
  - Rewrites tags in current paper list.
  - Does not create a new `run_id` by itself.

#### `Import Zotero`

- Calls `POST /api/export/zotero`.
- Requires current paper list.
- Needs Zotero credentials in `.env`.
- Side effects:
  - Creates/updates items in your Zotero library.

#### `Import BibTeX`

- Opens local file picker (`.bib`, `.bibtex`, `.txt`).
- Uploads file to `POST /api/import/bibtex`.
- Side effects:
  - Replaces current paper list with imported entries.
  - Does not auto-create `run_id` unless you run `Search` (or later generate analysis against an existing run).

#### `Export BibTeX`

- Calls `POST /api/export/bibtex` with current papers.
- Downloads `papers.bib`.
- Requires current paper list.

#### `Export Markdown`

- Calls `POST /api/export/markdown` with current papers.
- Downloads `papers.md`.
- Requires current paper list.

#### `Generate Report`

- Calls `POST /api/report/keywords`.
- Requires:
  - `Report keywords` not empty.
  - Either current paper list or a valid `run_id`.
- Uses `Analysis top N` and `Report language`.
- Side effects:
  - Renders keyword report panel.
  - If request is based on `run_id`, report is persisted to `runs/<run_id>.json` under `analysis.keyword_report`.

#### `Evaluate Idea Novelty`

- Calls `POST /api/idea/evaluate`.
- Requires:
  - `Idea` not empty.
  - Either current paper list or a valid `run_id`.
- Uses `Report keywords` (optional), `Analysis top N`, and `Report language`.
- Side effects:
  - Renders novelty panel.
  - If request is based on `run_id`, result is persisted under `analysis.idea_novelty`.

#### `Load Run`

- Calls `GET /api/runs/{run_id}`.
- Requires `Run ID` input.
- Side effects:
  - Reloads papers from saved run (`papers_brief`).
  - Restores saved report/novelty panels if present.
  - Sets current context to the loaded run.

## 🆔 Where to find `run_id` (important)

Use any of these methods:

- **After Search in UI**:
  - The `Run ID` input is auto-filled.
  - Status line displays current run id (`Current run_id: ...`).
- **From local files**:
  - Search snapshots are saved in `runs/`.
  - Filename is exactly `<run_id>.json`.
  - Example: `runs/b048f98f0c2b4fc6bacb3928623eb42f.json` -> `run_id = b048f98f0c2b4fc6bacb3928623eb42f`.
- **From API response**:
  - `POST /api/search` returns JSON field `run_id`.

If `Load Run` returns 404, usually the `run_id` does not exist under `runs/` or was typed incorrectly.

## 📚 Typical workflows

### Workflow A: search -> classify -> export

1. Fill search fields and click `Search`.
2. (Optional) Enable/disable `Use AI for classify`, then click `Classify`.
3. Click `Export BibTeX` or `Export Markdown`.

### Workflow B: load historical run -> generate report

1. Put a known `run_id` into `Run ID`.
2. Click `Load Run`.
3. Fill `Report keywords`, set `Analysis top N`, click `Generate Report`.

### Workflow C: import external BibTeX -> evaluate idea

1. Click `Import BibTeX` and select file.
2. Fill `Idea` (+ optional `Report keywords`).
3. Click `Evaluate Idea Novelty`.

## 🔌 API overview

- `POST /api/search`
- `POST /api/classify`
- `POST /api/import/bibtex`
- `POST /api/export/bibtex`
- `POST /api/export/markdown`
- `POST /api/export/zotero`
- `POST /api/report/keywords`
- `POST /api/idea/evaluate`
- `GET /api/runs/{run_id}`

## ✅ Run tests

```bash
pytest
```
