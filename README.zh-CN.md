# IdeaScope（中文说明）🔎💡

[English README (主文档)](./README.md)

IdeaScope 是一个基于 FastAPI 的论文检索与分析工具，支持 arXiv + DBLP 检索、分类、BibTeX 导入导出、关键词报告与 Idea 新颖性评估。

## ✨ 功能概览

- 按关键词与年份区间检索论文
- 支持普通模式与近似全量抓取模式
- 论文分类（预设标签 + 可选 AI 自由标签）
- 导出 `BibTeX` 与 `Markdown`
- 导入 `BibTeX` 恢复论文列表
- 通过 API 导入 Zotero
- 将检索快照保存到 `runs/<run_id>.json`
- 使用 `run_id` 回载历史结果
- 生成关键词报告
- 评估研究 Idea 新颖性

## 📦 环境要求

- 建议 Python 3.10+
- 可访问 arXiv/DBLP
- 可选：OpenAI 兼容接口（用于 AI 分类/报告/新颖性）
- 可选：Zotero API 凭据（用于导入 Zotero）

## ⚙️ 安装与配置

1. 安装依赖：

```bash
pip install -r requirements.txt
```

2. 在项目根目录创建/编辑 `.env`（`project_root/.env`）：

- `OPENAI_BASE_URL`（OpenAI 兼容地址，通常以 `/v1` 结尾）
- `OPENAI_API_KEY`
- `OPENAI_MODEL`
- `CLASSIFIER_ENABLED=true|false`
- `DEFAULT_PRESET_TAGS`（逗号分隔）
- `MAX_PAPERS_FOR_ANALYSIS`（可选，默认 `120`）
- `ANALYSIS_CHUNK_SIZE`（可选，默认 `20`）
- `MAX_ABSTRACT_CHARS`（可选，默认 `800`）
- `ZOTERO_LIBRARY_TYPE`（`user` 或 `group`）
- `ZOTERO_LIBRARY_ID`
- `ZOTERO_API_KEY`
- `ZOTERO_COLLECTION_KEY`（可选）

## 🚀 启动

```bash
uvicorn app.main:app --reload
```

打开 [http://127.0.0.1:8000](http://127.0.0.1:8000)。

## 🧭 前端界面说明（逐项）

### 右上角设置

- `UI language`：切换界面语言（系统/中文/英文）。
- `Theme mode`：切换主题（系统/浅色/深色）。

### 检索区域输入项

- `Keyword`：`Search` 必填。
- `Start year` / `End year`：年份过滤区间。
- `Max results/source`：仅普通模式生效。
- `Approx full crawl cap`：仅全量模式生效。
- `Approx full crawl mode`（勾选框）：开启后按分页抓取直到达到每源上限。
- `Use AI for classify`（勾选框）：控制 `Classify` 是否使用 AI 生成自由标签。

### 分析区域输入项

- `Report keywords`：逗号分隔，用于关键词覆盖和趋势分析。
- `Idea`：新颖性评估输入文本。
- `Run ID`：用于加载历史 run。
- `Analysis top N`：报告/评估参与论文上限。
- `Report language`：控制报告和新颖性输出语言。

### 按钮详解

#### `Search`

- 调用 `POST /api/search`。
- 必须填写 `Keyword`。
- 返回论文列表和新的 `run_id`。
- 执行后会：
  - 刷新页面论文列表；
  - 显示检索状态；
  - 自动写入 `Run ID` 输入框；
  - 在本地写入 `runs/<run_id>.json`。

#### `Classify`

- 分批调用 `POST /api/classify`。
- 需要当前已有论文（来自 Search / Load Run / Import BibTeX）。
- 读取 `Use AI for classify` 作为 `use_ai` 参数。
- 执行后会更新当前列表中的标签，不会单独创建新的 `run_id`。

#### `Import Zotero`

- 调用 `POST /api/export/zotero`。
- 需要当前论文列表。
- 依赖 `.env` 中的 Zotero 凭据。
- 执行后会把论文写入你的 Zotero 库。

#### `Import BibTeX`

- 打开本地文件选择器（支持 `.bib` / `.bibtex` / `.txt`）。
- 上传到 `POST /api/import/bibtex`。
- 执行后会用导入结果替换当前论文列表。
- 单独导入 BibTeX 不会自动产生新的 `run_id`。

#### `Export BibTeX`

- 调用 `POST /api/export/bibtex`。
- 需要当前论文列表。
- 下载文件 `papers.bib`。

#### `Export Markdown`

- 调用 `POST /api/export/markdown`。
- 需要当前论文列表。
- 下载文件 `papers.md`。

#### `Generate Report`

- 调用 `POST /api/report/keywords`。
- 前置条件：
  - `Report keywords` 不能为空；
  - 必须有当前论文列表，或提供有效 `run_id`。
- 使用 `Analysis top N` 与 `Report language`。
- 执行后会显示关键词报告面板。
- 若基于 `run_id` 生成，会写回 `runs/<run_id>.json` 的 `analysis.keyword_report`。

#### `Evaluate Idea Novelty`

- 调用 `POST /api/idea/evaluate`。
- 前置条件：
  - `Idea` 不能为空；
  - 必须有当前论文列表，或提供有效 `run_id`。
- 可读取 `Report keywords`（可选）、`Analysis top N`、`Report language`。
- 执行后会显示新颖性评估面板。
- 若基于 `run_id` 评估，会写回 `analysis.idea_novelty`。

#### `Load Run`

- 调用 `GET /api/runs/{run_id}`。
- 需要在 `Run ID` 输入框填入值。
- 执行后会：
  - 从已保存 run 恢复 `papers_brief`；
  - 若存在历史分析结果，一并恢复报告与新颖性面板；
  - 将当前上下文切换到该 run。

## 🆔 `run_id` 在哪里找（重点）

可通过以下方式获取：

- **在页面中（推荐）**
  - 点击 `Search` 后，`Run ID` 输入框会自动填充；
  - 下方状态会显示当前 `run_id`。
- **在本地文件中**
  - 检索结果会保存到 `runs/` 目录；
  - 文件名即 `<run_id>.json`；
  - 例如 `runs/b048f98f0c2b4fc6bacb3928623eb42f.json`，对应 `run_id` 就是 `b048f98f0c2b4fc6bacb3928623eb42f`。
- **从接口响应中**
  - `POST /api/search` 的返回 JSON 包含 `run_id` 字段。

若 `Load Run` 报 404，通常是 `run_id` 输入错误，或该 run 文件不存在于 `runs/`。

## 📚 常见流程

### 流程 A：检索 -> 分类 -> 导出

1. 填检索条件并点击 `Search`。
2. （可选）设置 `Use AI for classify` 后点击 `Classify`。
3. 点击 `Export BibTeX` 或 `Export Markdown`。

### 流程 B：加载历史 run -> 生成报告

1. 在 `Run ID` 中粘贴已有 `run_id`。
2. 点击 `Load Run`。
3. 填写 `Report keywords`，设置 `Analysis top N` 后点击 `Generate Report`。

### 流程 C：导入 BibTeX -> 评估 Idea

1. 点击 `Import BibTeX` 选择文件。
2. 填写 `Idea`（可选填写 `Report keywords`）。
3. 点击 `Evaluate Idea Novelty`。

## 🔌 API 列表

- `POST /api/search`
- `POST /api/classify`
- `POST /api/import/bibtex`
- `POST /api/export/bibtex`
- `POST /api/export/markdown`
- `POST /api/export/zotero`
- `POST /api/report/keywords`
- `POST /api/idea/evaluate`
- `GET /api/runs/{run_id}`

## ✅ 测试

```bash
pytest
```
