"""
theme.py — All colors, text, and style knobs for the Streamlit app in ONE place.

If you want to change how the app looks or reads, this is almost always the
only file you need to touch. app.py imports everything from here instead of
having colors/text hardcoded everywhere — so changing one value here updates
the whole app consistently.
"""

# ==============================================================================
# COLORS
# Change these hex codes to re-theme the entire app. Every color used anywhere
# in app.py comes from this block.
# ==============================================================================
NAVY = "#1E2761"          # primary background / header color
NAVY_LIGHT = "#2E3A8C"     # lighter accent (tabs, gradients)
ICE = "#CADCFC"            # light blue text on dark backgrounds
RED = "#C0392B"            # "high risk" color + button color
GREEN = "#1E8A5B"          # "low risk" color
SLATE = "#44546A"          # secondary text color (currently unused, reserved)
CARD_BG = "#F4F6FB"        # light card background (currently unused, reserved)

# Background gradient behind the whole page (top color -> bottom color)
APP_BG_GRADIENT = f"linear-gradient(180deg, #0E1230 0%, #12163A 100%)"

# Gauge chart risk zone colors (low / medium / high) — must be rgba with alpha
GAUGE_ZONE_LOW = "rgba(30,138,91,0.35)"
GAUGE_ZONE_MED = "rgba(230,180,60,0.35)"
GAUGE_ZONE_HIGH = "rgba(192,57,43,0.35)"

# ==============================================================================
# TEXT CONTENT
# Everything the user reads on the page. Change wording here without touching
# any layout code in app.py.
# ==============================================================================
PAGE_TITLE = "Employee Attrition Predictor"
PAGE_ICON = "📊"

HERO_TITLE = "📊 Employee Attrition Prediction System"
HERO_SUBTITLE = "Fill in employee details across the tabs below, then predict attrition risk instantly."

SIDEBAR_HEADING = "📊 About this Project"
SIDEBAR_BODY = (
    "AIML Summer Internship 2026\n"
    "IIHMF, MNNIT Allahabad\n\n"
    "Capstone Project 4"
)
SIDEBAR_MODEL_NOTE = (
    "Logistic Regression was chosen over Decision Tree/Random Forest/XGBoost for the "
    "best Recall & ROC-AUC balance — catching real leavers matters more here than "
    "raw accuracy."
)

SUBMIT_BUTTON_LABEL = "🔮 Predict Attrition Risk"

RESULT_DISCLAIMER = "This is a data-driven estimate for decision support, not a guaranteed outcome."

FOOTER_TEXT = (
    "IIHMF, MNNIT Allahabad — AIML Summer Internship 2026 | Capstone Project 4: "
    "Employee Attrition Prediction System"
)

# Labels for the 4 tabs, in order. Change text/emoji here; the tabs themselves
# are still built in app.py, but this keeps the wording in one spot.
TAB_LABELS = [
    "👤 Personal & Role",
    "💰 Compensation",
    "🙂 Satisfaction & Work-Life",
    "📈 Tenure & History",
]

# Labels shown for the risk result
HIGH_RISK_LABEL = "⚠️ High Attrition Risk"
LOW_RISK_LABEL = "✅ Low Attrition Risk"

# ==============================================================================
# BRANDING — logo + font
# ==============================================================================
# Simple inline SVG logo (a stylized bar-chart mark). Used in the hero header
# and sidebar. Edit the <path>/<rect> shapes to change the mark itself, or
# swap LOGO_SVG for a data URI of your own image if you'd rather use a PNG.
LOGO_SVG = """
<svg width="40" height="40" viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg">
  <rect width="40" height="40" rx="10" fill="#C0392B"/>
  <rect x="8" y="21" width="5" height="11" rx="1.5" fill="white"/>
  <rect x="17" y="14" width="5" height="18" rx="1.5" fill="white"/>
  <rect x="26" y="8" width="5" height="24" rx="1.5" fill="white"/>
</svg>
"""

GOOGLE_FONT_IMPORT = "https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700&family=Inter:wght@400;500;600&display=swap"
HEADING_FONT = "'Sora', 'Georgia', serif"
BODY_FONT = "'Inter', sans-serif"


def clean_html(html_string: str) -> str:
    """Strips leading whitespace from every line of an HTML string before it
    goes into st.markdown(..., unsafe_allow_html=True).

    Why this exists: Streamlit's markdown parser treats any line starting
    with 4+ spaces as a Markdown "indented code block" and renders it as
    literal text instead of HTML. Writing multi-line f-string HTML with
    normal Python indentation (for readability) triggers this constantly.
    textwrap.dedent() looks like a fix but is NOT reliable here, because it
    only removes the *common* leading whitespace across all lines, and an
    interpolated multi-line variable (like LOGO_SVG, which starts at column 0)
    drags that common minimum down to near-zero, so the surrounding div's
    indentation never actually gets stripped.

    Always wrap HTML passed to st.markdown with this function:
        st.markdown(theme.clean_html(f\"\"\"<div>...</div>\"\"\"), unsafe_allow_html=True)
    """
    lines = html_string.strip("\n").split("\n")
    return "\n".join(line.lstrip() for line in lines)

# ==============================================================================
# MULTI-PAGE APP TEXT (Batch Prediction / Model Insights / About pages)
# ==============================================================================
BATCH_PAGE_TITLE = "📂 Batch Prediction"
BATCH_PAGE_INTRO = (
    "Upload a CSV of multiple employees to score them all at once — the same "
    "way HR would run this over a whole department, instead of one person "
    "at a time."
)
BATCH_TEMPLATE_NOTE = (
    "Your CSV needs the same raw columns as the training dataset "
    "(see `Dataset/HR-Employee-Attrition.csv` for the exact column names). "
    "You can download a ready-made template below."
)

INSIGHTS_PAGE_TITLE = "📊 Model Insights"
INSIGHTS_PAGE_INTRO = (
    "How the deployed model was chosen, and what it learned from the data — "
    "the same analysis from the project report, in interactive form."
)

ABOUT_PAGE_TITLE = "ℹ️ About this Project"
ABOUT_PAGE_BODY = """
### Employee Attrition Prediction System
**AIML Summer Internship 2026 — IIHMF, MNNIT Allahabad**
**Capstone Project 4**

This tool predicts whether an employee is likely to leave an organization,
using historical HR data and a Logistic Regression model chosen for its
strong recall (catching real leavers) and ROC-AUC, rather than raw accuracy
alone.

**Pipeline:** data cleaning → EDA → feature engineering (TenureRatio,
IncomePerYearExp, PromotionGap, AvgSatisfaction) → SMOTE balancing →
model comparison (Logistic Regression, Decision Tree, Random Forest, XGBoost)
→ deployment.

**Team:**
- Archit Srivastava — Team Lead
- Param Gupta — Team Member
- Adish Tripathi — Team Member

B.Tech CSE, United College of Engineering & Research (UCER), Prayagraj
"""


# ==============================================================================
# "CONTRIBUTING CONTEXT" RULES
# Simple, readable rule-of-thumb messages shown under the result. These are
# NOT model explanations (no SHAP/feature attribution) — just quick, honest
# context based on well-known risk factors from the EDA. Edit freely, or add
# your own rule as a new (condition, message) pair.
# ==============================================================================
CONTEXT_RULES_HELP = """
Each rule below is (condition_function, message). condition_function receives
the `raw` dict of engineered+raw inputs and the individual named variables
used in the form. Add a new tuple to CONTEXT_RULES to add a new callout.
"""

NO_FLAGS_MESSAGE = "No major red-flag factors detected among the strongest known predictors."

# ==============================================================================
# CSS TEMPLATE
# The actual injected stylesheet. Uses the color constants above — you should
# not need to edit this block unless you want to change spacing/shape/fonts.
# ==============================================================================
def build_css() -> str:
    return f"""
<style>
    @import url('{GOOGLE_FONT_IMPORT}');

    .stApp {{
        background: {APP_BG_GRADIENT};
        font-family: {BODY_FONT};
    }}
    section[data-testid="stSidebar"] {{
        background: {NAVY};
    }}
    section[data-testid="stSidebar"] * {{
        color: {ICE} !important;
    }}
    h1, h2, h3 {{
        color: #FFFFFF !important;
        font-family: {HEADING_FONT};
    }}
    p, label, .stMarkdown {{
        color: #DCE3F5;
        font-family: {BODY_FONT};
    }}
    .brand-row {{
        display: flex;
        align-items: center;
        gap: 0.7rem;
    }}
    .hero-card {{
        background: linear-gradient(135deg, {NAVY} 0%, {NAVY_LIGHT} 100%);
        padding: 1.6rem 2rem;
        border-radius: 16px;
        margin-bottom: 1.2rem;
        border: 1px solid rgba(255,255,255,0.08);
        box-shadow: 0 12px 28px rgba(0,0,0,0.28);
    }}
    .hero-title {{
        font-size: 2.1rem;
        font-weight: 700;
        color: white;
        font-family: {HEADING_FONT};
        margin-bottom: 0.2rem;
    }}
    .hero-sub {{
        color: {ICE};
        font-size: 0.95rem;
        font-family: {BODY_FONT};
    }}
    .metric-pill {{
        display: inline-block;
        background: rgba(255,255,255,0.08);
        border: 1px solid rgba(255,255,255,0.15);
        border-radius: 999px;
        padding: 0.3rem 0.9rem;
        margin-right: 0.5rem;
        font-size: 0.85rem;
        color: {ICE};
    }}
    div[data-baseweb="tab-list"] {{
        gap: 4px;
    }}
    button[data-baseweb="tab"] {{
        background: rgba(255,255,255,0.04);
        border-radius: 10px 10px 0 0;
        color: {ICE};
        padding: 10px 18px;
        border-bottom: 3px solid transparent;
        transition: background 0.15s ease, border-color 0.15s ease;
    }}
    button[data-baseweb="tab"][aria-selected="true"] {{
        background: {NAVY_LIGHT};
        color: white !important;
        border-bottom: 3px solid {RED};
        font-weight: 600;
    }}
    .stButton > button {{
        background: {RED};
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.7rem 1rem;
        font-weight: 600;
        font-size: 1.05rem;
        width: 100%;
        box-shadow: 0 6px 16px rgba(192,57,43,0.35);
        transition: transform 0.1s ease, box-shadow 0.15s ease;
    }}
    .stButton > button:hover {{
        background: #A5321F;
        color: white;
        box-shadow: 0 8px 20px rgba(192,57,43,0.45);
        transform: translateY(-1px);
    }}
    button[kind="secondary"] {{
        background: rgba(255,255,255,0.06) !important;
        box-shadow: none !important;
        border: 1px solid rgba(255,255,255,0.18) !important;
        color: {ICE} !important;
    }}
    button[kind="secondary"]:hover {{
        background: rgba(255,255,255,0.12) !important;
        transform: none !important;
    }}
    div[data-baseweb="select"] > div {{
        background: rgba(255,255,255,0.09);
        border-color: rgba(255,255,255,0.25);
    }}
    div[data-baseweb="select"] span {{
        color: #F0F3FA;
    }}
    ul[data-baseweb="menu"] {{
        background: {NAVY_LIGHT};
    }}
    li[data-baseweb="menu-item"]:hover {{
        background: rgba(255,255,255,0.12);
    }}
    .result-card {{
        border-radius: 16px;
        padding: 1.6rem 2rem;
        margin-top: 1rem;
        border: 1px solid rgba(255,255,255,0.1);
        box-shadow: 0 12px 28px rgba(0,0,0,0.28);
    }}
    .result-card.high {{
        background: linear-gradient(135deg, #3A1414 0%, #4A1A1A 100%);
    }}
    .result-card.low {{
        background: linear-gradient(135deg, #12331F 0%, #16412A 100%);
    }}
    .empty-state {{
        border: 1px dashed rgba(255,255,255,0.15);
        border-radius: 12px;
        padding: 1.2rem 1.4rem;
        margin-top: 1rem;
        color: {ICE};
        font-size: 0.9rem;
        text-align: center;
    }}
    footer {{visibility: hidden;}}

    /* Print / Save-as-PDF button (plain HTML button, no Streamlit rerun) */
    .print-btn {{
        background: rgba(255,255,255,0.06);
        border: 1px solid rgba(255,255,255,0.18);
        color: {ICE};
        border-radius: 8px;
        padding: 0.5rem 0.9rem;
        font-size: 0.85rem;
        cursor: pointer;
        font-family: 'Inter', sans-serif;
        margin-top: 0.6rem;
    }}
    .print-btn:hover {{
        background: rgba(255,255,255,0.12);
    }}

    /* When the browser print dialog opens (incl. "Save as PDF"), hide chrome
       that doesn't make sense on paper: sidebar, header bar, buttons, forms. */
    @media print {{
        section[data-testid="stSidebar"], header, .stButton, .print-btn,
        div[data-testid="stForm"], div[data-baseweb="tab-list"] {{
            display: none !important;
        }}
        .stApp {{ background: white !important; }}
        .result-card, .hero-card {{ box-shadow: none !important; }}
    }}
</style>
"""
