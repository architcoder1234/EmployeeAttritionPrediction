# Advanced Web App (Optional Alternate Deployment)

This is a **custom, non-Streamlit-looking** deployment of the same trained
model — a FastAPI backend + a hand-built HTML/CSS/JS frontend. It's an
**optional extra**, not a replacement: the project's required deliverable
(per the AIML Internship guidelines: "Deploy using Streamlit or Flask") is
still the Streamlit app in `Streamlit_App/`. Show this one if you want to
demonstrate the model can be wrapped in a fully custom UI too.

Both deployments share the exact same prediction logic
(`Streamlit_App/model_utils.py`) — so results always match between them.

## Folder structure
```
Advanced_Web_App/
├── backend/
│   ├── main.py            FastAPI app (REST API wrapping the model)
│   └── requirements.txt
└── frontend/
    ├── index.html          Page structure (4 views: Predict, Batch, Insights, About)
    ├── style.css            All colors/fonts/layout — same navy/red brand as the report & PPT
    └── app.js               Form generation, API calls, gauge rendering, batch upload
```

## How to run

### 1. Start the backend
```bash
cd Advanced_Web_App/backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```
Leave this running. You should see `Application startup complete.`

Quick check it's alive: open `http://localhost:8000/health` in a browser —
you should see `{"status":"ok"}`. Interactive API docs are auto-generated at
`http://localhost:8000/docs`.

### 2. Serve the frontend
Opening `index.html` directly by double-clicking it can run into browser
security restrictions on `fetch()`. Instead, serve it with a simple local
server:
```bash
cd Advanced_Web_App/frontend
python -m http.server 5500
```
Then open `http://localhost:5500` in your browser.

### 3. If you changed the backend's port
Edit the first line of `frontend/app.js`:
```js
const API_BASE = "http://localhost:8000";
```

## API endpoints (for reference / the `/docs` page)
- `GET /health` — liveness check
- `GET /model_info` — deployed model name, metrics, and valid categorical values
- `POST /predict` — single employee JSON -> `{prediction, risk_label, probability}`
- `POST /predict_batch` — multipart CSV upload -> JSON array of scored rows
- `GET /required_columns` — list of raw columns a batch CSV must contain

## Customizing this version
- **Colors/fonts:** `frontend/style.css`, the `:root { --navy: ...; }` block at the top
- **Form fields:** `frontend/app.js`, the `FORM_TABS` array near the top (same shape as
  `Streamlit_App/fields_config.py` — add/remove/reorder the same way)
- **Contributing-context rules:** `frontend/app.js`, `CONTEXT_RULES` array
- **Prediction logic:** don't edit it here — it's shared from
  `Streamlit_App/model_utils.py` so both deployments never drift out of sync

## Known limitations of this version
- No authentication — anyone who can reach the backend can call the API.
  Fine for a local demo; add auth before exposing this publicly.
- CORS is wide open (`allow_origins=["*"]`) for local development convenience.
  Restrict this in `backend/main.py` before any real deployment.
- The Model Insights page's comparison table is hardcoded from the notebook's
  results rather than fetched live — if you retrain and get different numbers,
  update the `MODEL_COMPARISON` array in `app.js` to match.
