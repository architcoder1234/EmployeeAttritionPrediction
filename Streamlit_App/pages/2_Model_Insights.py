"""
pages/2_Model_Insights.py — Interactive view of model comparison + EDA highlights.
"""

import streamlit as st
import pandas as pd
import os
import sys
import plotly.graph_objects as go
import plotly.express as px

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import theme
from model_utils import load_artifacts, MODEL_DIR, BASE_DIR

st.markdown(theme.build_css(), unsafe_allow_html=True)


@st.cache_resource
def get_artifacts():
    return load_artifacts()


model, scaler, encoders, feature_names, model_meta = get_artifacts()

st.markdown(theme.clean_html(f"""
<div class="hero-card">
    <div class="brand-row">
        {theme.LOGO_SVG}
        <div>
            <div class="hero-title">{theme.INSIGHTS_PAGE_TITLE}</div>
            <div class="hero-sub">{theme.INSIGHTS_PAGE_INTRO}</div>
        </div>
    </div>
</div>
"""), unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# Model comparison table + interactive bar chart
# ----------------------------------------------------------------------------
st.markdown("### Model Comparison")
comp_path = os.path.join(MODEL_DIR, "model_comparison.csv")
comp_df = pd.read_csv(comp_path, index_col=0)
comp_df.index.name = "Model"

st.dataframe(
    comp_df.style.format("{:.3f}").highlight_max(axis=0, color="rgba(30,138,91,0.35)"),
    width="stretch",
)

melted = comp_df.reset_index().melt(id_vars="Model", var_name="Metric", value_name="Score")
fig_bar = px.bar(
    melted, x="Model", y="Score", color="Metric", barmode="group",
    color_discrete_sequence=px.colors.qualitative.Set2,
)
fig_bar.update_layout(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,0.03)",
    font={"color": "white"}, legend_title_text="",
    xaxis_tickangle=-15, height=420,
)
st.plotly_chart(fig_bar, width="stretch")

st.markdown(f"""
**Why {model_meta['best_model']} was deployed:** models within 0.02 F1-score of each
other are treated as "practically tied," and the tie is broken using ROC-AUC — a
more robust, threshold-independent metric. Decision Tree edges out Logistic
Regression on raw F1 (0.517 vs 0.507), but Logistic Regression's ROC-AUC (0.807)
is well ahead of Decision Tree's (0.736), making it the more reliable choice.
""")

st.markdown("---")

# ----------------------------------------------------------------------------
# EDA highlights (static figures generated during training)
# ----------------------------------------------------------------------------
st.markdown("### EDA Highlights")
fig_dir = os.path.join(BASE_DIR, "Documentation", "figures")

col1, col2, col3 = st.columns(3)
captions = [
    ("04_overtime_vs_attrition.png", "OverTime is one of the strongest single predictors."),
    ("06_jobrole_attrition_rate.png", "Sales Reps & Lab Technicians attrite most by role."),
    ("03_income_vs_attrition.png", "Leavers skew toward lower Monthly Income."),
]
for col, (fname, caption) in zip([col1, col2, col3], captions):
    fpath = os.path.join(fig_dir, fname)
    if os.path.exists(fpath):
        col.image(fpath, caption=caption, width="stretch")

st.markdown("---")
st.caption(theme.FOOTER_TEXT)
