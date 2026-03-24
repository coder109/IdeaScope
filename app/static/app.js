let currentPapers = [];
let currentRunId = null;
let uiLanguage = "en";

const I18N = {
  en: {
    subtitle: "Search arXiv + DBLP by keyword and year range, with classify/report and BibTeX import/export.",
    labelKeyword: "Keyword",
    hintKeyword: "Supports multi-word queries; use specific terms for better relevance.",
    labelStartYear: "Start year",
    hintStartYear: "Earliest publication year.",
    labelEndYear: "End year",
    hintEndYear: "Latest publication year.",
    labelMaxResults: "Max results/source",
    hintMaxResults: "Used in normal mode.",
    labelMaxFetchLimit: "Approx full crawl cap",
    hintMaxFetchLimit: "Per source upper limit in crawl mode.",
    labelFetchAll: "Approx full crawl mode",
    labelStrictRelevance: "Strict relevance filter",
    labelTitleOnly: "Title-only match",
    labelUseAi: "Use AI for classify",
    btnSearch: "Search",
    btnClassify: "Classify",
    btnZotero: "Import Zotero",
    btnImportBib: "Import BibTeX",
    btnExportBib: "Export BibTeX",
    btnExportMd: "Export Markdown",
    btnReport: "Generate Report",
    btnIdea: "Evaluate Idea Novelty",
    btnLoadRun: "Load Run",
    labelReportKeywords: "Report keywords (comma separated)",
    hintReportKeywords: "Used for keyword coverage and trend summary.",
    labelIdea: "Idea",
    hintIdea: "Used for novelty scoring and risk assessment.",
    labelRunId: "Run ID",
    hintRunId: "A run_id is generated after search.",
    labelTopN: "Analysis top N",
    hintTopN: "Upper bound of papers used for analysis.",
    labelReportLang: "Report language",
    hintReportLang: "Controls report and novelty output language.",
    labelUiLang: "UI language",
    hintUiLang: "Switch UI language.",
    labelTheme: "Theme mode",
    hintTheme: "Dark/Light/System mode.",
    optSystem: "System",
    optLight: "Light",
    optDark: "Dark",
    optChinese: "Chinese",
    optEnglish: "English",
    searching: "Searching...",
    searchFailedNetwork: "Search failed due to network error.",
    searchFailed: (code) => `Search failed: ${code}`,
    foundPapers: (count) => `Found ${count} papers.`,
    emptyKeyword: "Please enter a keyword.",
    maxFetchInvalid: "max fetch limit must be >= 1.",
    noPapersToExport: "No papers to export.",
    mdDownloaded: "Markdown downloaded.",
    exportMdFailed: (code) => `Markdown export failed: ${code}`,
    exportFailed: (code) => `Export failed: ${code}`,
    bibDownloaded: "BibTeX downloaded.",
    classifying: "Classifying papers...",
    classifyingProgress: (done, total) => `Classifying ${done}/${total}...`,
    noPapersToClassify: "No papers to classify.",
    classificationFailed: (code) => `Classification failed: ${code}`,
    classificationFailedNetwork: "Classification failed due to network error.",
    classifiedCount: (count) => `Classified ${count} papers.`,
    importingZotero: "Importing to Zotero...",
    noPapersToImport: "No papers to import.",
    zoteroDone: (ok, total) => `Zotero import done: ${ok}/${total} succeeded.`,
    zoteroFailedNetwork: "Zotero import failed due to network error.",
    importingBib: "Importing BibTeX...",
    bibImportFailedNetwork: "BibTeX import failed due to network error.",
    bibImportFailed: (code) => `BibTeX import failed: ${code}`,
    importedBibCount: (count) => `Imported ${count} papers from BibTeX.`,
    reportNeedKeywords: "Please input report keywords.",
    reportNeedPapers: "No papers available. Search first or load run_id.",
    generatingReport: "Generating keyword report...",
    reportFailed: (code) => `Report failed: ${code}`,
    reportFailedNetwork: "Keyword report failed due to network error.",
    reportDone: "Keyword report generated.",
    needIdea: "Please input your idea.",
    evalNeedPapers: "No papers available. Search first or load run_id.",
    evaluatingIdea: "Evaluating idea novelty...",
    evalFailed: (code) => `Idea evaluation failed: ${code}`,
    evalFailedNetwork: "Idea evaluation failed due to network error.",
    evalDone: "Idea novelty evaluated.",
    needRunId: "Please input run_id.",
    loadingRun: "Loading run...",
    loadRunFailed: (code) => `Load run failed: ${code}`,
    loadRunFailedNetwork: "Load run failed due to network error.",
    runLoaded: (id) => `Run loaded: ${id}.`,
    runStatus: (id) => `Current run_id: ${id}`,
    noveltyLabel: "Novelty",
    confidenceLabel: "Confidence",
    reportTitle: "Keyword Report",
    reportCoverage: "Keyword Coverage",
    reportTrends: "Trends",
    reportGaps: "Research Gaps",
    reportWorks: "Representative Works",
    ideaTitle: "Idea Novelty Evaluation",
    ideaSignals: "Similar Work Signals",
    ideaDiff: "Differentiators",
    ideaRisks: "Risks",
    reportSummary: (a, s, c) => `Analyzed ${a}/${s} papers, ${c} chunks.`,
    presetLabel: "Preset",
    freeLabel: "Free",
  },
  zh: {
    subtitle: "按关键词与年份检索 arXiv + DBLP，支持分类、报告与 BibTeX 导入导出。",
    labelKeyword: "关键词",
    hintKeyword: "支持多词检索；关键词越具体，结果越相关。",
    labelStartYear: "起始年份",
    hintStartYear: "最早发表年份。",
    labelEndYear: "结束年份",
    hintEndYear: "最晚发表年份。",
    labelMaxResults: "每源结果上限",
    hintMaxResults: "普通模式使用。",
    labelMaxFetchLimit: "近似全量抓取上限",
    hintMaxFetchLimit: "全量模式下每个数据源的上限。",
    labelFetchAll: "近似全量抓取模式",
    labelStrictRelevance: "严格相关性过滤",
    labelTitleOnly: "仅标题匹配",
    labelUseAi: "分类使用 AI",
    btnSearch: "检索",
    btnClassify: "分类",
    btnZotero: "导入 Zotero",
    btnImportBib: "导入 BibTeX",
    btnExportBib: "导出 BibTeX",
    btnExportMd: "导出 Markdown",
    btnReport: "生成关键词报告",
    btnIdea: "评估 Idea 新颖性",
    btnLoadRun: "加载 Run",
    labelReportKeywords: "报告关键词（逗号分隔）",
    hintReportKeywords: "用于关键词覆盖统计与趋势摘要。",
    labelIdea: "Idea",
    hintIdea: "用于新颖性评分与风险提示。",
    labelRunId: "Run ID",
    hintRunId: "检索后会自动生成 run_id。",
    labelTopN: "分析 top N",
    hintTopN: "参与报告/评估的论文上限。",
    labelReportLang: "报告语言",
    hintReportLang: "控制报告与新颖性评估输出语言。",
    labelUiLang: "界面语言",
    hintUiLang: "切换界面中英文。",
    labelTheme: "主题模式",
    hintTheme: "黑夜/白天/系统默认。",
    optSystem: "系统默认",
    optLight: "浅色",
    optDark: "深色",
    optChinese: "中文",
    optEnglish: "英文",
    searching: "正在检索...",
    searchFailedNetwork: "检索失败：网络错误。",
    searchFailed: (code) => `检索失败：${code}`,
    foundPapers: (count) => `共找到 ${count} 篇论文。`,
    emptyKeyword: "请输入关键词。",
    maxFetchInvalid: "最大抓取上限必须 >= 1。",
    noPapersToExport: "暂无可导出的论文。",
    mdDownloaded: "Markdown 已下载。",
    exportMdFailed: (code) => `Markdown 导出失败：${code}`,
    exportFailed: (code) => `导出失败：${code}`,
    bibDownloaded: "BibTeX 已下载。",
    classifying: "正在分类...",
    classifyingProgress: (done, total) => `分类中 ${done}/${total}...`,
    noPapersToClassify: "暂无可分类论文。",
    classificationFailed: (code) => `分类失败：${code}`,
    classificationFailedNetwork: "分类失败：网络错误。",
    classifiedCount: (count) => `已分类 ${count} 篇论文。`,
    importingZotero: "正在导入 Zotero...",
    noPapersToImport: "暂无可导入论文。",
    zoteroDone: (ok, total) => `Zotero 导入完成：${ok}/${total} 成功。`,
    zoteroFailedNetwork: "Zotero 导入失败：网络错误。",
    importingBib: "正在导入 BibTeX...",
    bibImportFailedNetwork: "BibTeX 导入失败：网络错误。",
    bibImportFailed: (code) => `BibTeX 导入失败：${code}`,
    importedBibCount: (count) => `已从 BibTeX 导入 ${count} 篇论文。`,
    reportNeedKeywords: "请输入报告关键词。",
    reportNeedPapers: "没有可分析论文，请先检索或加载 run_id。",
    generatingReport: "正在生成关键词报告...",
    reportFailed: (code) => `报告生成失败：${code}`,
    reportFailedNetwork: "报告生成失败：网络错误。",
    reportDone: "关键词报告已生成。",
    needIdea: "请输入你的 idea。",
    evalNeedPapers: "没有可分析论文，请先检索或加载 run_id。",
    evaluatingIdea: "正在评估 idea 新颖性...",
    evalFailed: (code) => `新颖性评估失败：${code}`,
    evalFailedNetwork: "新颖性评估失败：网络错误。",
    evalDone: "idea 新颖性评估完成。",
    needRunId: "请输入 run_id。",
    loadingRun: "正在加载 run...",
    loadRunFailed: (code) => `加载 run 失败：${code}`,
    loadRunFailedNetwork: "加载 run 失败：网络错误。",
    runLoaded: (id) => `已加载 run：${id}`,
    runStatus: (id) => `当前 run_id：${id}`,
    noveltyLabel: "新颖性",
    confidenceLabel: "置信度",
    reportTitle: "关键词报告",
    reportCoverage: "关键词覆盖度",
    reportTrends: "趋势",
    reportGaps: "研究空白",
    reportWorks: "代表论文",
    ideaTitle: "Idea 新颖性评估",
    ideaSignals: "相似工作信号",
    ideaDiff: "差异化点",
    ideaRisks: "风险",
    reportSummary: (a, s, c) => `分析 ${a}/${s} 篇论文，共 ${c} 个分块。`,
    presetLabel: "预设标签",
    freeLabel: "自由标签",
  },
};

function byId(id) {
  return document.getElementById(id);
}

function t(key, ...args) {
  const lang = I18N[uiLanguage] ? uiLanguage : "en";
  const value = I18N[lang][key];
  if (typeof value === "function") {
    return value(...args);
  }
  return value || key;
}

function sourceText(src) {
  return (src || "unknown").toUpperCase();
}

function renderPapers(papers) {
  const target = byId("results");
  target.innerHTML = "";
  papers.forEach((p) => {
    const div = document.createElement("div");
    div.className = "paper";
    const date = p.published_date || (p.year ? `${p.year}` : "unknown");
    const source = sourceText(p.source);
    const authors = (p.authors || []).join(", ");
    const preset = (p.preset_tags || []).join(", ");
    const free = (p.free_tags || []).join(", ");
    div.innerHTML = `
      <h3>${p.url ? `<a href="${p.url}" target="_blank" rel="noreferrer">${p.title}</a>` : p.title}</h3>
      <div class="meta">${source} | ${date} | ${authors}</div>
      <div>${p.abstract || ""}</div>
      <div class="tags"><strong>${t("presetLabel")}:</strong> ${preset || "Uncategorized"} | <strong>${t("freeLabel")}:</strong> ${free || "-"}</div>
    `;
    target.appendChild(div);
  });
}

function listHtml(items) {
  if (!items || !items.length) {
    return "<div class=\"muted\">-</div>";
  }
  return `<ul>${items.map((x) => `<li>${x}</li>`).join("")}</ul>`;
}

function noveltyChip(score) {
  const val = Number(score || 0);
  if (val >= 7) {
    return `<span class="chip good">${t("noveltyLabel")} ${val.toFixed(1)}/10</span>`;
  }
  if (val >= 4.5) {
    return `<span class="chip mid">${t("noveltyLabel")} ${val.toFixed(1)}/10</span>`;
  }
  return `<span class="chip low">${t("noveltyLabel")} ${val.toFixed(1)}/10</span>`;
}

function renderReportPanel(report) {
  const panel = byId("reportPanel");
  if (!report || report.error) {
    panel.style.display = "none";
    return;
  }
  const coverage = report.keyword_coverage || {};
  const maxVal = Math.max(1, ...Object.values(coverage).map((x) => Number(x || 0)));
  const bars = Object.entries(coverage)
    .map(([k, v]) => {
      const n = Number(v || 0);
      const pct = Math.min(100, Math.round((n / maxVal) * 100));
      return `
        <div class="kv">
          <div><strong>${k}</strong>: ${n}</div>
          <div class="bar"><span style="width:${pct}%"></span></div>
        </div>
      `;
    })
    .join("");

  panel.innerHTML = `
    <h3>${t("reportTitle")}</h3>
    <div class="muted">${t("reportSummary", report.analyzed_paper_count || 0, report.source_paper_count || 0, report.chunk_count || 0)}</div>
    <p>${report.overview || "-"}</p>
    <h4>${t("reportCoverage")}</h4>
    ${bars || "<div class=\"muted\">-</div>"}
    <h4>${t("reportTrends")}</h4>
    ${listHtml(report.trends || [])}
    <h4>${t("reportGaps")}</h4>
    ${listHtml(report.research_gaps || [])}
    <h4>${t("reportWorks")}</h4>
    ${listHtml(report.representative_works || [])}
  `;
  panel.style.display = "block";
}

function renderIdeaPanel(result) {
  const panel = byId("ideaPanel");
  if (!result || result.error) {
    panel.style.display = "none";
    return;
  }
  panel.innerHTML = `
    <h3>${t("ideaTitle")}</h3>
    <div class="chip-row">
      ${noveltyChip(result.novelty_score)}
      <span class="chip">${t("confidenceLabel")}: ${result.confidence || "unknown"}</span>
    </div>
    <p>${result.overall_assessment || "-"}</p>
    <h4>${t("ideaSignals")}</h4>
    ${listHtml(result.similar_work_signals || [])}
    <h4>${t("ideaDiff")}</h4>
    ${listHtml(result.differentiators || [])}
    <h4>${t("ideaRisks")}</h4>
    ${listHtml(result.risks || [])}
  `;
  panel.style.display = "block";
}

function parseKeywords() {
  return byId("reportKeywords").value
    .split(",")
    .map((x) => x.trim())
    .filter((x) => x);
}

function getTopN() {
  const value = Number(byId("analysisTopN").value);
  if (!value || value < 1) {
    return 120;
  }
  return value;
}

function updateRunStatus() {
  byId("runStatus").textContent = currentRunId ? t("runStatus", currentRunId) : "";
}

function resolveUiLanguage() {
  const selected = byId("uiLanguage").value;
  if (selected === "system") {
    const browser = (navigator.language || "en").toLowerCase();
    uiLanguage = browser.startsWith("zh") ? "zh" : "en";
  } else {
    uiLanguage = selected;
  }
  document.documentElement.lang = uiLanguage === "zh" ? "zh" : "en";
}

function applyTheme() {
  const mode = byId("themeMode").value;
  const isDarkSystem = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
  const dark = mode === "dark" || (mode === "system" && isDarkSystem);
  document.body.setAttribute("data-theme", dark ? "dark" : "light");
}

function applyUiLabels() {
  byId("subtitleMain").textContent = t("subtitle");
  byId("labelKeyword").textContent = t("labelKeyword");
  byId("hintKeyword").textContent = t("hintKeyword");
  byId("labelStartYear").textContent = t("labelStartYear");
  byId("hintStartYear").textContent = t("hintStartYear");
  byId("labelEndYear").textContent = t("labelEndYear");
  byId("hintEndYear").textContent = t("hintEndYear");
  byId("labelMaxResults").textContent = t("labelMaxResults");
  byId("hintMaxResults").textContent = t("hintMaxResults");
  byId("labelMaxFetchLimit").textContent = t("labelMaxFetchLimit");
  byId("hintMaxFetchLimit").textContent = t("hintMaxFetchLimit");
  byId("labelFetchAll").textContent = t("labelFetchAll");
  byId("labelStrictRelevance").textContent = t("labelStrictRelevance");
  byId("labelTitleOnly").textContent = t("labelTitleOnly");
  byId("labelUseAi").textContent = t("labelUseAi");
  byId("searchBtn").textContent = t("btnSearch");
  byId("classifyBtn").textContent = t("btnClassify");
  byId("zoteroBtn").textContent = t("btnZotero");
  byId("importBibBtn").textContent = t("btnImportBib");
  byId("exportBtn").textContent = t("btnExportBib");
  byId("exportMdBtn").textContent = t("btnExportMd");
  byId("reportBtn").textContent = t("btnReport");
  byId("ideaBtn").textContent = t("btnIdea");
  byId("loadRunBtn").textContent = t("btnLoadRun");
  byId("labelReportKeywords").textContent = t("labelReportKeywords");
  byId("hintReportKeywords").textContent = t("hintReportKeywords");
  byId("labelIdea").textContent = t("labelIdea");
  byId("hintIdea").textContent = t("hintIdea");
  byId("labelRunId").textContent = t("labelRunId");
  byId("hintRunId").textContent = t("hintRunId");
  byId("labelTopN").textContent = t("labelTopN");
  byId("hintTopN").textContent = t("hintTopN");
  byId("labelReportLang").textContent = t("labelReportLang");
  byId("hintReportLang").textContent = t("hintReportLang");
  byId("labelUiLang").textContent = t("labelUiLang");
  byId("labelTheme").textContent = t("labelTheme");
  byId("optUiLangSystem").textContent = t("optSystem");
  byId("optUiLangZh").textContent = "中文";
  byId("optUiLangEn").textContent = "English";
  byId("optThemeSystem").textContent = t("optSystem");
  byId("optThemeLight").textContent = t("optLight");
  byId("optThemeDark").textContent = t("optDark");
  byId("optReportLangZh").textContent = "中文";
  byId("optReportLangEn").textContent = "English";
  renderPapers(currentPapers);
}

async function classifyBatch(batch, useAi) {
  const resp = await fetch("/api/classify", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      papers: batch,
      use_ai: useAi,
    }),
  });
  return resp;
}

async function search() {
  toggleControls(true);
  const payload = {
    keyword: byId("keyword").value.trim(),
    start_year: Number(byId("startYear").value),
    end_year: Number(byId("endYear").value),
    max_results_per_source: Number(byId("maxResults").value),
    fetch_all: byId("fetchAll").checked,
    max_fetch_limit_per_source: Number(byId("maxFetchLimit").value),
    strict_relevance: byId("strictRelevance").checked,
    title_only_match: byId("titleOnlyMatch").checked,
  };
  if (!payload.keyword) {
    byId("status").textContent = t("emptyKeyword");
    toggleControls(false);
    return;
  }
  if (payload.fetch_all && payload.max_fetch_limit_per_source < 1) {
    byId("status").textContent = t("maxFetchInvalid");
    toggleControls(false);
    return;
  }
  byId("status").textContent = t("searching");
  try {
    const resp = await fetch("/api/search", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!resp.ok) {
      byId("status").textContent = t("searchFailed", resp.status);
      return;
    }
    const data = await resp.json();
    currentPapers = data.papers || [];
    currentRunId = data.run_id || null;
    updateRunStatus();
    byId("runIdInput").value = currentRunId || "";
    renderPapers(currentPapers);
    byId("status").textContent = t("foundPapers", data.count);
  } catch (err) {
    byId("status").textContent = t("searchFailedNetwork");
  } finally {
    toggleControls(false);
  }
}

async function generateKeywordReport() {
  const keywords = parseKeywords();
  if (!keywords.length) {
    byId("status").textContent = t("reportNeedKeywords");
    return;
  }
  if (!currentPapers.length && !currentRunId) {
    byId("status").textContent = t("reportNeedPapers");
    return;
  }
  toggleControls(true);
  byId("status").textContent = t("generatingReport");
  try {
    const payload = {
      keywords,
      run_id: currentRunId,
      papers: currentRunId ? null : currentPapers,
      top_n: getTopN(),
      language: byId("reportLanguage").value,
    };
    const resp = await fetch("/api/report/keywords", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await resp.json();
    if (!resp.ok) {
      byId("status").textContent = data.detail || t("reportFailed", resp.status);
      return;
    }
    if (data.run_id) {
      currentRunId = data.run_id;
      updateRunStatus();
      byId("runIdInput").value = currentRunId || "";
    }
    renderReportPanel(data.report);
    byId("status").textContent = t("reportDone");
  } catch (err) {
    byId("status").textContent = t("reportFailedNetwork");
  } finally {
    toggleControls(false);
  }
}

async function evaluateIdeaNovelty() {
  const idea = byId("ideaInput").value.trim();
  const keywords = parseKeywords();
  if (!idea) {
    byId("status").textContent = t("needIdea");
    return;
  }
  if (!currentPapers.length && !currentRunId) {
    byId("status").textContent = t("evalNeedPapers");
    return;
  }
  toggleControls(true);
  byId("status").textContent = t("evaluatingIdea");
  try {
    const payload = {
      idea,
      keywords,
      run_id: currentRunId,
      papers: currentRunId ? null : currentPapers,
      top_n: getTopN(),
      language: byId("reportLanguage").value,
    };
    const resp = await fetch("/api/idea/evaluate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await resp.json();
    if (!resp.ok) {
      byId("status").textContent = data.detail || t("evalFailed", resp.status);
      return;
    }
    if (data.run_id) {
      currentRunId = data.run_id;
      updateRunStatus();
      byId("runIdInput").value = currentRunId || "";
    }
    renderIdeaPanel(data.result);
    byId("status").textContent = t("evalDone");
  } catch (err) {
    byId("status").textContent = t("evalFailedNetwork");
  } finally {
    toggleControls(false);
  }
}

async function loadRunById() {
  const runId = byId("runIdInput").value.trim();
  if (!runId) {
    byId("status").textContent = t("needRunId");
    return;
  }
  toggleControls(true);
  byId("status").textContent = t("loadingRun");
  try {
    const resp = await fetch(`/api/runs/${encodeURIComponent(runId)}`);
    const data = await resp.json();
    if (!resp.ok) {
      byId("status").textContent = data.detail || t("loadRunFailed", resp.status);
      return;
    }
    currentRunId = data.run_id || runId;
    updateRunStatus();
    currentPapers = data.papers_brief || [];
    renderPapers(currentPapers);
    renderReportPanel((data.analysis || {}).keyword_report || null);
    renderIdeaPanel((data.analysis || {}).idea_novelty || null);
    byId("status").textContent = t("runLoaded", currentRunId);
  } catch (err) {
    byId("status").textContent = t("loadRunFailedNetwork");
  } finally {
    toggleControls(false);
  }
}

async function exportBib() {
  if (!currentPapers.length) {
    byId("status").textContent = t("noPapersToExport");
    return;
  }
  const resp = await fetch("/api/export/bibtex", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ papers: currentPapers }),
  });
  if (!resp.ok) {
    byId("status").textContent = t("exportFailed", resp.status);
    return;
  }
  const blob = await resp.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "papers.bib";
  a.click();
  window.URL.revokeObjectURL(url);
  byId("status").textContent = t("bibDownloaded");
}

async function exportMarkdown() {
  if (!currentPapers.length) {
    byId("status").textContent = t("noPapersToExport");
    return;
  }
  const resp = await fetch("/api/export/markdown", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ papers: currentPapers }),
  });
  if (!resp.ok) {
    byId("status").textContent = t("exportMdFailed", resp.status);
    return;
  }
  const blob = await resp.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "papers.md";
  a.click();
  window.URL.revokeObjectURL(url);
  byId("status").textContent = t("mdDownloaded");
}

async function classifyCurrentPapers() {
  if (!currentPapers.length) {
    byId("status").textContent = t("noPapersToClassify");
    return;
  }
  toggleControls(true);
  byId("status").textContent = t("classifying");
  try {
    const useAi = byId("useAiClassify").checked;
    const total = currentPapers.length;
    const batchSize = 20;
    const nextPapers = [];
    let done = 0;

    while (done < total) {
      const batch = currentPapers.slice(done, done + batchSize);
      const resp = await classifyBatch(batch, useAi);
      if (!resp.ok) {
        byId("status").textContent = t("classificationFailed", resp.status);
        return;
      }
      const data = await resp.json();
      const classified = data.papers || [];
      nextPapers.push(...classified);
      done += batch.length;
      byId("status").textContent = t("classifyingProgress", done, total);
    }

    currentPapers = nextPapers;
    renderPapers(currentPapers);
    byId("status").textContent = t("classifiedCount", currentPapers.length);
  } catch (err) {
    byId("status").textContent = t("classificationFailedNetwork");
  } finally {
    toggleControls(false);
  }
}

async function importZotero() {
  if (!currentPapers.length) {
    byId("status").textContent = t("noPapersToImport");
    return;
  }
  toggleControls(true);
  byId("status").textContent = t("importingZotero");
  try {
    const resp = await fetch("/api/export/zotero", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ papers: currentPapers }),
    });
    const data = await resp.json();
    if (!resp.ok) {
      byId("status").textContent = data.detail || `Zotero import failed: ${resp.status}`;
      return;
    }
    byId("status").textContent = t("zoteroDone", data.success_count, data.total);
  } catch (err) {
    byId("status").textContent = t("zoteroFailedNetwork");
  } finally {
    toggleControls(false);
  }
}

async function importBibtexFromFile(file) {
  toggleControls(true);
  byId("status").textContent = t("importingBib");
  try {
    const form = new FormData();
    form.append("file", file);
    const resp = await fetch("/api/import/bibtex", {
      method: "POST",
      body: form,
    });
    const data = await resp.json();
    if (!resp.ok) {
      byId("status").textContent = data.detail || t("bibImportFailed", resp.status);
      return;
    }
    currentPapers = data.papers || [];
    renderPapers(currentPapers);
    byId("status").textContent = t("importedBibCount", data.count);
  } catch (err) {
    byId("status").textContent = t("bibImportFailedNetwork");
  } finally {
    toggleControls(false);
  }
}

byId("searchBtn").addEventListener("click", search);
byId("classifyBtn").addEventListener("click", classifyCurrentPapers);
byId("zoteroBtn").addEventListener("click", importZotero);
byId("importBibBtn").addEventListener("click", () => byId("bibFileInput").click());
byId("reportBtn").addEventListener("click", generateKeywordReport);
byId("ideaBtn").addEventListener("click", evaluateIdeaNovelty);
byId("loadRunBtn").addEventListener("click", loadRunById);
byId("bibFileInput").addEventListener("change", async (e) => {
  const file = e.target.files && e.target.files[0];
  if (!file) {
    return;
  }
  await importBibtexFromFile(file);
  e.target.value = "";
});
byId("exportBtn").addEventListener("click", exportBib);
byId("exportMdBtn").addEventListener("click", exportMarkdown);
byId("fetchAll").addEventListener("change", syncFetchModeUi);
byId("uiLanguage").addEventListener("change", () => {
  resolveUiLanguage();
  applyUiLabels();
  updateRunStatus();
});
byId("themeMode").addEventListener("change", applyTheme);
window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", () => {
  if (byId("themeMode").value === "system") {
    applyTheme();
  }
});

function syncFetchModeUi() {
  const fetchAll = byId("fetchAll").checked;
  byId("maxResults").disabled = fetchAll;
  byId("maxResults").title = fetchAll ? "Disabled in full crawl mode" : "";
  byId("maxFetchLimit").disabled = !fetchAll;
  byId("maxFetchLimit").title = !fetchAll ? "Only used in full crawl mode" : "";
}

function toggleControls(disabled) {
  byId("searchBtn").disabled = disabled;
  byId("classifyBtn").disabled = disabled;
  byId("zoteroBtn").disabled = disabled;
  byId("importBibBtn").disabled = disabled;
  byId("exportBtn").disabled = disabled;
  byId("exportMdBtn").disabled = disabled;
  byId("reportBtn").disabled = disabled;
  byId("ideaBtn").disabled = disabled;
  byId("loadRunBtn").disabled = disabled;
  byId("keyword").disabled = disabled;
  byId("startYear").disabled = disabled;
  byId("endYear").disabled = disabled;
  byId("reportKeywords").disabled = disabled;
  byId("ideaInput").disabled = disabled;
  byId("runIdInput").disabled = disabled;
  byId("analysisTopN").disabled = disabled;
  byId("reportLanguage").disabled = disabled;
  byId("uiLanguage").disabled = disabled;
  byId("themeMode").disabled = disabled;
  byId("fetchAll").disabled = disabled;
  byId("strictRelevance").disabled = disabled;
  byId("titleOnlyMatch").disabled = disabled;
  byId("useAiClassify").disabled = disabled;
  byId("bibFileInput").disabled = disabled;
  const fetchAll = byId("fetchAll").checked;
  byId("maxResults").disabled = disabled || fetchAll;
  byId("maxFetchLimit").disabled = disabled || !fetchAll;
}

syncFetchModeUi();
resolveUiLanguage();
applyUiLabels();
applyTheme();
updateRunStatus();
