/* ==========================================================================
   Employee Attrition Predictor — Custom Frontend
   Talks to the FastAPI backend (see ../backend/main.py).
   Change API_BASE below if you run the backend on a different host/port.
   ========================================================================== */

const API_BASE = "http://localhost:8000";

// ----------------------------------------------------------------------------
// FORM FIELD CONFIG — mirrors Streamlit_App/fields_config.py. Add/remove a
// field here the same way you would there: one object per field.
// "encoder" fields get their options filled in from the backend's
// /model_info response (categorical_options), so they always match the model.
// ----------------------------------------------------------------------------
const FORM_TABS = [
  {
    label: "👤 Personal & Role",
    fields: [
      { key: "Age", label: "Age", widget: "range", min: 18, max: 60, default: 30 },
      { key: "Gender", label: "Gender", widget: "encoder_select", encoder: "Gender" },
      { key: "MaritalStatus", label: "Marital Status", widget: "encoder_select", encoder: "MaritalStatus" },
      { key: "Department", label: "Department", widget: "encoder_select", encoder: "Department" },
      { key: "JobRole", label: "Job Role", widget: "encoder_select", encoder: "JobRole" },
      { key: "JobLevel", label: "Job Level (1-5)", widget: "select", options: [1, 2, 3, 4, 5], default: 2 },
      { key: "Education", label: "Education Level (1-5)", widget: "select", options: [1, 2, 3, 4, 5], default: 3 },
      { key: "EducationField", label: "Education Field", widget: "encoder_select", encoder: "EducationField" },
      { key: "BusinessTravel", label: "Business Travel", widget: "encoder_select", encoder: "BusinessTravel" },
      { key: "DistanceFromHome", label: "Distance From Home (km)", widget: "range", min: 1, max: 30, default: 5 },
    ],
  },
  {
    label: "💰 Compensation",
    fields: [
      { key: "MonthlyIncome", label: "Monthly Income", widget: "number", min: 1000, max: 20000, default: 5000 },
      { key: "DailyRate", label: "Daily Rate", widget: "number", min: 100, max: 1500, default: 800 },
      { key: "MonthlyRate", label: "Monthly Rate", widget: "number", min: 2000, max: 27000, default: 14000 },
      { key: "HourlyRate", label: "Hourly Rate", widget: "number", min: 30, max: 100, default: 65 },
      { key: "PercentSalaryHike", label: "Percent Salary Hike", widget: "range", min: 10, max: 25, default: 15 },
      { key: "StockOptionLevel", label: "Stock Option Level (0-3)", widget: "select", options: [0, 1, 2, 3], default: 0 },
      { key: "PerformanceRating", label: "Performance Rating (3-4)", widget: "select", options: [3, 4], default: 3 },
      { key: "OverTime", label: "OverTime", widget: "encoder_select", encoder: "OverTime" },
    ],
  },
  {
    label: "🙂 Satisfaction & Work-Life",
    fields: [
      { key: "JobSatisfaction", label: "Job Satisfaction (1-4)", widget: "range", min: 1, max: 4, default: 3 },
      { key: "EnvironmentSatisfaction", label: "Environment Satisfaction (1-4)", widget: "range", min: 1, max: 4, default: 3 },
      { key: "RelationshipSatisfaction", label: "Relationship Satisfaction (1-4)", widget: "range", min: 1, max: 4, default: 3 },
      { key: "WorkLifeBalance", label: "Work Life Balance (1-4)", widget: "range", min: 1, max: 4, default: 3 },
      { key: "JobInvolvement", label: "Job Involvement (1-4)", widget: "range", min: 1, max: 4, default: 3 },
    ],
  },
  {
    label: "📈 Tenure & History",
    fields: [
      { key: "TotalWorkingYears", label: "Total Working Years", widget: "range", min: 0, max: 40, default: 8 },
      { key: "YearsAtCompany", label: "Years At Company", widget: "range", min: 0, max: 40, default: 5 },
      { key: "YearsInCurrentRole", label: "Years In Current Role", widget: "range", min: 0, max: 20, default: 3 },
      { key: "YearsSinceLastPromotion", label: "Years Since Last Promotion", widget: "range", min: 0, max: 15, default: 1 },
      { key: "YearsWithCurrManager", label: "Years With Current Manager", widget: "range", min: 0, max: 20, default: 3 },
      { key: "NumCompaniesWorked", label: "Num Companies Worked", widget: "range", min: 0, max: 10, default: 2 },
      { key: "TrainingTimesLastYear", label: "Training Times Last Year", widget: "range", min: 0, max: 6, default: 2 },
    ],
  },
];

// Contributing-context rules — mirrors Streamlit_App/fields_config.py CONTEXT_RULES.
const CONTEXT_RULES = [
  { test: (v) => v.OverTime === "Yes", msg: "Works OverTime — one of the strongest attrition signals in this dataset." },
  { test: (v) => (v.MonthlyIncome / (v.TotalWorkingYears + 1)) < 500, msg: "Income relative to experience is on the lower side." },
  { test: (v) => v.WorkLifeBalance <= 2, msg: "Reports below-average Work-Life Balance." },
  { test: (v) => v.YearsSinceLastPromotion >= 5, msg: "Long gap since last promotion." },
];

const MODEL_COMPARISON = [
  { model: "Logistic Regression", accuracy: 0.762, precision: 0.379, recall: 0.766, f1: 0.507, roc_auc: 0.807, deployed: true },
  { model: "Decision Tree", accuracy: 0.810, precision: 0.435, recall: 0.638, f1: 0.517, roc_auc: 0.736, deployed: false },
  { model: "Random Forest", accuracy: 0.847, precision: 0.538, recall: 0.298, f1: 0.384, roc_auc: 0.794, deployed: false },
  { model: "XGBoost", accuracy: 0.864, precision: 0.640, recall: 0.340, f1: 0.444, roc_auc: 0.784, deployed: false },
];

// Top 10 feature importances from the Random Forest importance check
// (Notebook Section 5.1) — used only for the Model Insights chart.
const FEATURE_IMPORTANCE = [
  { feature: "MonthlyIncome", importance: 0.0636 },
  { feature: "Age", importance: 0.0549 },
  { feature: "OverTime", importance: 0.0512 },
  { feature: "IncomePerYearExp*", importance: 0.0492 },
  { feature: "DailyRate", importance: 0.0460 },
  { feature: "MonthlyRate", importance: 0.0452 },
  { feature: "TotalWorkingYears", importance: 0.0440 },
  { feature: "AvgSatisfaction*", importance: 0.0435 },
  { feature: "DistanceFromHome", importance: 0.0426 },
  { feature: "HourlyRate", importance: 0.0416 },
];

const CLASS_DISTRIBUTION = { stayed: 1233, left: 237 };

// Shared Chart.js styling so every chart looks consistent with the dark theme
Chart.defaults.color = "#C7D2EF";
Chart.defaults.borderColor = "rgba(255,255,255,0.08)";
Chart.defaults.font.family = "'Inter', sans-serif";

let categoricalOptions = {};
let modelInfo = null;
let lastBatchResults = null;

// ----------------------------------------------------------------------------
// SIDEBAR NAVIGATION
// ----------------------------------------------------------------------------
document.querySelectorAll(".nav-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".nav-btn").forEach((b) => b.classList.remove("active"));
    document.querySelectorAll(".view").forEach((v) => v.classList.remove("active"));
    btn.classList.add("active");
    document.getElementById(`view-${btn.dataset.view}`).classList.add("active");
  });
});

// ----------------------------------------------------------------------------
// BUILD FORM (tabs + fields) once categorical options are known
// ----------------------------------------------------------------------------
function buildForm() {
  const tabsEl = document.getElementById("form-tabs");
  const panelsEl = document.getElementById("form-panels");
  tabsEl.innerHTML = "";
  panelsEl.innerHTML = "";

  FORM_TABS.forEach((tab, i) => {
    const tabBtn = document.createElement("button");
    tabBtn.type = "button";
    tabBtn.className = "tab-btn" + (i === 0 ? " active" : "");
    tabBtn.textContent = tab.label;
    tabBtn.addEventListener("click", () => {
      document.querySelectorAll(".tab-btn").forEach((b) => b.classList.remove("active"));
      document.querySelectorAll(".tab-panel").forEach((p) => p.classList.remove("active"));
      tabBtn.classList.add("active");
      panel.classList.add("active");
    });
    tabsEl.appendChild(tabBtn);

    const panel = document.createElement("div");
    panel.className = "tab-panel" + (i === 0 ? " active" : "");

    tab.fields.forEach((field) => {
      const group = document.createElement("div");
      group.className = "field-group";
      const label = document.createElement("label");
      label.textContent = field.label;
      label.setAttribute("for", field.key);
      group.appendChild(label);

      let input;
      if (field.widget === "range") {
        const wrap = document.createElement("div");
        input = document.createElement("input");
        input.type = "range";
        input.min = field.min; input.max = field.max; input.value = field.default;
        input.id = field.key;
        const valueSpan = document.createElement("span");
        valueSpan.className = "range-value";
        valueSpan.textContent = field.default;
        input.addEventListener("input", () => { valueSpan.textContent = input.value; });
        wrap.appendChild(input);
        wrap.appendChild(valueSpan);
        group.appendChild(wrap);
      } else if (field.widget === "number") {
        input = document.createElement("input");
        input.type = "number";
        input.min = field.min; input.max = field.max; input.value = field.default;
        input.id = field.key;
        group.appendChild(input);
      } else if (field.widget === "select") {
        input = document.createElement("select");
        input.id = field.key;
        field.options.forEach((opt) => {
          const o = document.createElement("option");
          o.value = opt; o.textContent = opt;
          if (opt === field.default) o.selected = true;
          input.appendChild(o);
        });
        group.appendChild(input);
      } else if (field.widget === "encoder_select") {
        input = document.createElement("select");
        input.id = field.key;
        (categoricalOptions[field.encoder] || []).forEach((opt) => {
          const o = document.createElement("option");
          o.value = opt; o.textContent = opt;
          input.appendChild(o);
        });
        group.appendChild(input);
      }
      panel.appendChild(group);
    });

    panelsEl.appendChild(panel);
  });
}

function collectFormValues() {
  const values = {};
  FORM_TABS.forEach((tab) => {
    tab.fields.forEach((field) => {
      const el = document.getElementById(field.key);
      const isNumeric = field.widget === "range" || field.widget === "number" || field.widget === "select";
      values[field.key] = isNumeric ? Number(el.value) : el.value;
    });
  });
  return values;
}

// ----------------------------------------------------------------------------
// GAUGE RENDERING (SVG arc, 0-100 -> full semicircle)
// ----------------------------------------------------------------------------
function updateGauge(pct, color) {
  const arc = document.getElementById("gauge-arc");
  const circumference = 251; // approx length of the semicircle path at r=80
  const filled = (pct / 100) * circumference;
  arc.setAttribute("stroke-dasharray", `${filled} ${circumference}`);
  arc.setAttribute("stroke", color);
  document.getElementById("gauge-value").textContent = `${pct.toFixed(1)}%`;
}

// ----------------------------------------------------------------------------
// PREDICT FORM SUBMIT
// ----------------------------------------------------------------------------
document.getElementById("predict-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const values = collectFormValues();
  const btn = document.getElementById("predict-btn");
  btn.disabled = true;
  btn.textContent = "Scoring...";

  try {
    const res = await fetch(`${API_BASE}/predict`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(values),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Prediction failed");
    }
    const data = await res.json();
    renderResult(data, values);
  } catch (err) {
    alert(`Prediction error: ${err.message}\n\nMake sure the FastAPI backend is running at ${API_BASE}.`);
  } finally {
    btn.disabled = false;
    btn.textContent = "🔮 Predict Attrition Risk";
  }
});

function renderResult(data, values) {
  const pct = data.probability * 100;
  const isHigh = data.prediction === 1;
  const color = isHigh ? "#C0392B" : "#1E8A5B";

  document.getElementById("predict-result").style.display = "grid";
  const card = document.getElementById("result-card");
  card.className = "card result-card " + (isHigh ? "high" : "low");
  document.getElementById("result-label").textContent = isHigh ? "⚠️ High Attrition Risk" : "✅ Low Attrition Risk";
  document.getElementById("result-label").style.color = color;
  document.getElementById("result-pct").textContent = `${pct.toFixed(1)}%`;

  const notes = CONTEXT_RULES.filter((r) => r.test(values)).map((r) => r.msg);
  const notesEl = document.getElementById("context-notes");
  if (notes.length === 0) {
    notesEl.innerHTML = "<strong>Contributing context:</strong><ul><li>No major red-flag factors detected among the strongest known predictors.</li></ul>";
  } else {
    notesEl.innerHTML = "<strong>Contributing context:</strong><ul>" + notes.map((n) => `<li>${n}</li>`).join("") + "</ul>";
  }

  updateGauge(pct, color);
  document.getElementById("predict-result").scrollIntoView({ behavior: "smooth", block: "nearest" });
}

// ----------------------------------------------------------------------------
// MODEL INFO / HEALTH CHECK (runs on page load)
// ----------------------------------------------------------------------------
async function loadModelInfo() {
  const statusEl = document.getElementById("api-status");
  try {
    const healthRes = await fetch(`${API_BASE}/health`);
    if (!healthRes.ok) throw new Error();
    statusEl.textContent = "✅ Connected to API";
    statusEl.className = "api-status ok";

    const res = await fetch(`${API_BASE}/model_info`);
    modelInfo = await res.json();
    categoricalOptions = modelInfo.categorical_options;

    document.getElementById("model-badge").innerHTML =
      `<strong>${modelInfo.model_name}</strong><br>F1: ${modelInfo.metrics.f1.toFixed(3)} · ROC-AUC: ${modelInfo.metrics.roc_auc.toFixed(3)}`;

    document.getElementById("hero-pills").innerHTML = `
      <span class="pill">Model: ${modelInfo.model_name}</span>
      <span class="pill">F1: ${modelInfo.metrics.f1.toFixed(2)}</span>
      <span class="pill">ROC-AUC: ${modelInfo.metrics.roc_auc.toFixed(2)}</span>`;

    buildForm();
  } catch (err) {
    statusEl.textContent = `⚠️ Can't reach API at ${API_BASE} — start the backend first (see README).`;
    statusEl.className = "api-status error";
    document.getElementById("model-badge").textContent = "Model info unavailable";
  }
}

// ----------------------------------------------------------------------------
// BATCH PREDICTION VIEW
// ----------------------------------------------------------------------------
const uploadZone = document.getElementById("upload-zone");
const csvInput = document.getElementById("csv-input");
let selectedFile = null;

uploadZone.addEventListener("click", () => csvInput.click());
uploadZone.addEventListener("dragover", (e) => { e.preventDefault(); uploadZone.style.borderColor = "#C0392B"; });
uploadZone.addEventListener("dragleave", () => { uploadZone.style.borderColor = ""; });
uploadZone.addEventListener("drop", (e) => {
  e.preventDefault();
  uploadZone.style.borderColor = "";
  if (e.dataTransfer.files.length) {
    selectedFile = e.dataTransfer.files[0];
    handleFileSelected();
  }
});
csvInput.addEventListener("change", () => {
  if (csvInput.files.length) {
    selectedFile = csvInput.files[0];
    handleFileSelected();
  }
});

function handleFileSelected() {
  document.getElementById("batch-file-name").textContent = `Selected: ${selectedFile.name}`;
  document.getElementById("batch-predict-btn").style.display = "block";
}

document.getElementById("show-columns-btn").addEventListener("click", async () => {
  const el = document.getElementById("columns-list");
  if (el.style.display === "block") { el.style.display = "none"; return; }
  try {
    const res = await fetch(`${API_BASE}/required_columns`);
    const data = await res.json();
    el.textContent = data.columns.join(", ");
    el.style.display = "block";
  } catch {
    el.textContent = "Couldn't reach the API.";
    el.style.display = "block";
  }
});

document.getElementById("batch-predict-btn").addEventListener("click", async () => {
  if (!selectedFile) return;
  const btn = document.getElementById("batch-predict-btn");
  btn.disabled = true;
  btn.textContent = "Scoring...";

  const formData = new FormData();
  formData.append("file", selectedFile);

  try {
    const res = await fetch(`${API_BASE}/predict_batch`, { method: "POST", body: formData });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Batch prediction failed");
    }
    const results = await res.json();
    lastBatchResults = results;
    renderBatchResults(results);
  } catch (err) {
    alert(`Batch prediction error: ${err.message}`);
  } finally {
    btn.disabled = false;
    btn.textContent = "🔮 Score All Employees";
  }
});

function renderBatchResults(results) {
  const nErrors = results.filter((r) => r.Error).length;
  const nHigh = results.filter((r) => r.AttritionRisk === "Yes").length;

  document.getElementById("batch-summary").innerHTML = `
    <span class="pill">✅ Scored: ${results.length - nErrors}</span>
    <span class="pill">⚠️ High risk: ${nHigh}</span>
    <span class="pill">Errors: ${nErrors}</span>`;

  const table = document.getElementById("batch-table");
  const cols = ["JobRole", "Age", "OverTime", "MonthlyIncome", "AttritionRisk", "AttritionProbability", "Error"]
    .filter((c) => results[0] && c in results[0]);

  let html = "<tr>" + cols.map((c) => `<th>${c}</th>`).join("") + "</tr>";
  results.forEach((row) => {
    const riskClass = row.AttritionRisk === "Yes" ? "risk-high" : row.AttritionRisk === "No" ? "risk-low" : "";
    html += `<tr class="${riskClass}">` + cols.map((c) => {
      const cls = c === "AttritionRisk" ? "risk-cell" : "";
      let val = row[c];
      if (c === "AttritionProbability" && val != null) val = (val * 100).toFixed(1) + "%";
      return `<td class="${cls}">${val ?? ""}</td>`;
    }).join("") + "</tr>";
  });
  table.innerHTML = html;
  renderBatchCharts(results);
  document.getElementById("batch-results").style.display = "block";
}

document.getElementById("download-results-btn").addEventListener("click", () => {
  if (!lastBatchResults) return;
  const cols = Object.keys(lastBatchResults[0]);
  let csv = cols.join(",") + "\n";
  lastBatchResults.forEach((row) => {
    csv += cols.map((c) => JSON.stringify(row[c] ?? "")).join(",") + "\n";
  });
  const blob = new Blob([csv], { type: "text/csv" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url; a.download = "attrition_predictions.csv";
  a.click();
  URL.revokeObjectURL(url);
});

// ----------------------------------------------------------------------------
// MODEL INSIGHTS VIEW — table + 3 charts
// ----------------------------------------------------------------------------
function renderComparisonTable() {
  const table = document.getElementById("model-comparison-table");
  let html = "<tr><th>Model</th><th>Accuracy</th><th>Precision</th><th>Recall</th><th>F1</th><th>ROC-AUC</th></tr>";
  MODEL_COMPARISON.forEach((row) => {
    html += `<tr class="${row.deployed ? "deployed-row" : ""}">
      <td>${row.model}${row.deployed ? " ✅" : ""}</td>
      <td>${row.accuracy.toFixed(3)}</td>
      <td>${row.precision.toFixed(3)}</td>
      <td>${row.recall.toFixed(3)}</td>
      <td>${row.f1.toFixed(3)}</td>
      <td>${row.roc_auc.toFixed(3)}</td>
    </tr>`;
  });
  table.innerHTML = html;
}

function renderMetricsChart() {
  const ctx = document.getElementById("metrics-chart");
  const labels = MODEL_COMPARISON.map((m) => m.model);
  const metricSeries = [
    { key: "accuracy", label: "Accuracy", color: "#378ADD" },
    { key: "precision", label: "Precision", color: "#EF9F27" },
    { key: "recall", label: "Recall", color: "#639922" },
    { key: "f1", label: "F1", color: "#C0392B" },
    { key: "roc_auc", label: "ROC-AUC", color: "#7F77DD" },
  ];
  new Chart(ctx, {
    type: "bar",
    data: {
      labels,
      datasets: metricSeries.map((s) => ({
        label: s.label,
        data: MODEL_COMPARISON.map((m) => m[s.key]),
        backgroundColor: s.color,
      })),
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      scales: {
        y: { beginAtZero: true, max: 1, grid: { color: "rgba(255,255,255,0.06)" } },
        x: { grid: { display: false } },
      },
      plugins: { legend: { position: "bottom", labels: { boxWidth: 12, padding: 12 } } },
    },
  });
}

function renderImportanceChart() {
  const ctx = document.getElementById("importance-chart");
  new Chart(ctx, {
    type: "bar",
    data: {
      labels: FEATURE_IMPORTANCE.map((f) => f.feature),
      datasets: [{
        label: "Importance",
        data: FEATURE_IMPORTANCE.map((f) => f.importance),
        backgroundColor: "#378ADD",
      }],
    },
    options: {
      indexAxis: "y",
      responsive: true, maintainAspectRatio: false,
      scales: {
        x: { beginAtZero: true, grid: { color: "rgba(255,255,255,0.06)" } },
        y: { grid: { display: false } },
      },
      plugins: { legend: { display: false } },
    },
  });
}

function renderDistributionChart() {
  const ctx = document.getElementById("distribution-chart");
  new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: ["Stayed", "Left"],
      datasets: [{
        data: [CLASS_DISTRIBUTION.stayed, CLASS_DISTRIBUTION.left],
        backgroundColor: ["#1E8A5B", "#C0392B"],
        borderWidth: 0,
      }],
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { position: "bottom" } },
    },
  });
}

// ----------------------------------------------------------------------------
// BATCH RESULTS CHARTS — rendered fresh each time new results come in
// ----------------------------------------------------------------------------
let batchRiskChartInstance = null;
let batchHistChartInstance = null;

function renderBatchCharts(results) {
  const nHigh = results.filter((r) => r.AttritionRisk === "Yes").length;
  const nLow = results.filter((r) => r.AttritionRisk === "No").length;

  if (batchRiskChartInstance) batchRiskChartInstance.destroy();
  batchRiskChartInstance = new Chart(document.getElementById("batch-risk-chart"), {
    type: "doughnut",
    data: {
      labels: ["Low risk", "High risk"],
      datasets: [{ data: [nLow, nHigh], backgroundColor: ["#1E8A5B", "#C0392B"], borderWidth: 0 }],
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { position: "bottom" }, title: { display: true, text: "Risk split", color: "white" } },
    },
  });

  const probs = results.filter((r) => r.AttritionProbability != null).map((r) => r.AttritionProbability * 100);
  const bins = [0, 20, 40, 60, 80, 100];
  const binCounts = new Array(bins.length - 1).fill(0);
  probs.forEach((p) => {
    for (let i = 0; i < bins.length - 1; i++) {
      if (p >= bins[i] && p < bins[i + 1] + (i === bins.length - 2 ? 0.001 : 0)) { binCounts[i]++; break; }
    }
  });
  const binLabels = bins.slice(0, -1).map((b, i) => `${b}-${bins[i + 1]}%`);

  if (batchHistChartInstance) batchHistChartInstance.destroy();
  batchHistChartInstance = new Chart(document.getElementById("batch-histogram-chart"), {
    type: "bar",
    data: {
      labels: binLabels,
      datasets: [{ label: "Employees", data: binCounts, backgroundColor: "#378ADD" }],
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      scales: {
        y: { beginAtZero: true, grid: { color: "rgba(255,255,255,0.06)" } },
        x: { grid: { display: false } },
      },
      plugins: { legend: { display: false }, title: { display: true, text: "Probability distribution", color: "white" } },
    },
  });
}

// ----------------------------------------------------------------------------
// INIT
// ----------------------------------------------------------------------------
loadModelInfo();
renderComparisonTable();
renderMetricsChart();
renderImportanceChart();
renderDistributionChart();
