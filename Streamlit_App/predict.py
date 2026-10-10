"""
predict.py — The main "Predict" page (single-employee scoring form).

Navigated to via app.py's st.navigation() router. Shares the model + theme
via model_utils.py and theme.py, same as every other page.

EDITING THIS APP:
  - Colors, text, logo, fonts             -> theme.py
  - Form fields (add/remove/reorder)      -> fields_config.py
  - Prediction logic (shared everywhere)  -> model_utils.py
  - Page-specific layout                  -> this file / pages/*.py
See EDITING_GUIDE.md for step-by-step recipes.
"""

import streamlit as st
import numpy as np
import plotly.graph_objects as go

import theme
from fields_config import FORM_TABS, CONTEXT_RULES
from model_utils import load_artifacts, engineer_features, predict_one, explain_prediction

st.markdown(theme.build_css(), unsafe_allow_html=True)

model, scaler, encoders, feature_names, model_meta = load_artifacts()
m = model_meta["metrics"]

if "prediction_history" not in st.session_state:
    st.session_state.prediction_history = []

# ----------------------------------------------------------------------------
# SIDEBAR
# ----------------------------------------------------------------------------
with st.sidebar:
    st.markdown(theme.clean_html(f"""
    <div class="brand-row">
        {theme.LOGO_SVG}
        <div style="font-weight:700; font-size:1.1rem; color:white;">Attrition Predictor</div>
    </div>
    """), unsafe_allow_html=True)
    st.markdown("---")
    st.markdown(theme.SIDEBAR_BODY)
    st.markdown("---")
    st.markdown("### Deployed Model")
    st.markdown(f"**{model_meta['best_model']}**")
    st.metric("F1-Score", f"{m['f1']:.3f}")
    st.metric("ROC-AUC", f"{m['roc_auc']:.3f}")
    st.metric("Recall", f"{m['recall']:.3f}")
    st.markdown("---")
    st.markdown("### Decision Sensitivity")
    threshold = st.slider(
        "Risk Cutoff Threshold",
        min_value=0.20,
        max_value=0.80,
        value=0.50,
        step=0.05,
        help="Probability threshold to classify an employee as High Risk. Lower values catch more at-risk employees (higher recall) at the cost of more false alarms.",
    )
    st.markdown("---")
    st.caption(theme.SIDEBAR_MODEL_NOTE)

# ----------------------------------------------------------------------------
# HERO HEADER
# ----------------------------------------------------------------------------
st.markdown(theme.clean_html(f"""
<div class="hero-card">
    <div class="brand-row">
        {theme.LOGO_SVG}
        <div>
            <div class="hero-title">{theme.HERO_TITLE}</div>
            <div class="hero-sub">{theme.HERO_SUBTITLE}</div>
        </div>
    </div>
    <div style="margin-top:0.8rem;">
        <span class="metric-pill">Model: {model_meta['best_model']}</span>
        <span class="metric-pill">F1: {m['f1']:.2f}</span>
        <span class="metric-pill">ROC-AUC: {m['roc_auc']:.2f}</span>
    </div>
</div>
"""), unsafe_allow_html=True)


def render_field(spec):
    label = spec["label"]
    widget = spec["widget"]
    key = spec["key"]
    help_text = spec.get("help")
    if widget == "slider":
        return st.slider(label, spec["min"], spec["max"], spec["default"], key=key, help=help_text)
    elif widget == "number_input":
        return st.number_input(label, spec["min"], spec["max"], spec["default"], key=key, help=help_text)
    elif widget == "select_slider":
        return st.select_slider(label, spec["options"], value=spec["default"], key=key, help=help_text)
    elif widget == "selectbox":
        return st.selectbox(label, spec["options"], index=spec["default_index"], key=key, help=help_text)
    elif widget == "encoder_select":
        return st.selectbox(label, encoders[spec["encoder"]].classes_, key=key, help=help_text)
    else:
        raise ValueError(f"Unknown widget type in fields_config.py: {widget!r}")


# ----------------------------------------------------------------------------
# INPUT FORM
# ----------------------------------------------------------------------------
with st.form("attrition_form"):
    tabs = st.tabs([t["label"] for t in FORM_TABS])
    values = {}

    for tab_spec, tab in zip(FORM_TABS, tabs):
        with tab:
            fields = tab_spec["fields"]
            col1_fields = [f for f in fields if f.get("col", 1) == 1 and not f.get("full_width")]
            col2_fields = [f for f in fields if f.get("col", 1) == 2 and not f.get("full_width")]
            full_fields = [f for f in fields if f.get("full_width")]

            c1, c2 = st.columns(2)
            with c1:
                for spec in col1_fields:
                    values[spec["key"]] = render_field(spec)
            with c2:
                for spec in col2_fields:
                    values[spec["key"]] = render_field(spec)
            for spec in full_fields:
                values[spec["key"]] = render_field(spec)

    st.markdown("<br>", unsafe_allow_html=True)
    submitted = st.form_submit_button(theme.SUBMIT_BUTTON_LABEL, width="stretch")

reset_col, _ = st.columns([1, 3])
with reset_col:
    if st.button("Clear & Start Over", key="reset_form_btn", type="secondary", width="stretch"):
        for tab_spec in FORM_TABS:
            for spec in tab_spec["fields"]:
                st.session_state.pop(spec["key"], None)
        st.session_state.pop("last_prediction", None)
        st.rerun()

# ----------------------------------------------------------------------------
# PREDICTION
# ----------------------------------------------------------------------------
if submitted:
    with st.spinner("Scoring employee..."):
        raw_for_rules = engineer_features(values)
        raw_for_rules["OverTime_label"] = values["OverTime"]
        prediction, probability = predict_one(values, model, scaler, encoders, feature_names, threshold=threshold)

    risk_pct = probability * 100
    card_class = "high" if prediction == 1 else "low"
    risk_label = theme.HIGH_RISK_LABEL if prediction == 1 else theme.LOW_RISK_LABEL
    risk_color = theme.RED if prediction == 1 else theme.GREEN

    st.toast(
        f"{'⚠️ High' if prediction == 1 else '✅ Low'} risk — {risk_pct:.1f}% (threshold: {int(threshold*100)}%)",
        icon="⚠️" if prediction == 1 else "✅",
    )

    # Record this prediction in the session history table
    st.session_state.prediction_history.insert(0, {
        "Job Role": values["JobRole"],
        "Age": values["Age"],
        "OverTime": values["OverTime"],
        "Monthly Income": values["MonthlyIncome"],
        "Risk": "High" if prediction == 1 else "Low",
        "Probability": f"{risk_pct:.1f}%",
    })
    st.session_state.prediction_history = st.session_state.prediction_history[:5]

    left, right = st.columns([1.3, 1])

    with left:
        st.markdown(theme.clean_html(f"""
        <div class="result-card {card_class}">
            <div style="font-size:1.4rem; font-weight:700; color:{risk_color};">{risk_label}</div>
            <div style="font-size:2.6rem; font-weight:800; color:white; margin-top:0.3rem;">{risk_pct:.1f}%</div>
            <div style="color:{theme.ICE}; font-size:0.9rem; margin-top:0.4rem;">
                estimated probability this employee leaves (decision threshold: {int(threshold*100)}%)
            </div>
        </div>
        """), unsafe_allow_html=True)

        notes = [msg for condition, msg in CONTEXT_RULES if condition(raw_for_rules)]
        if not notes:
            notes = [theme.NO_FLAGS_MESSAGE]

        st.markdown("**Contributing context:**")
        for n in notes:
            st.markdown(f"- {n}")

    with right:
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=risk_pct,
            number={"suffix": "%", "font": {"color": "white", "size": 36}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": "white"},
                "bar": {"color": risk_color},
                "bgcolor": "rgba(255,255,255,0.05)",
                "borderwidth": 0,
                "steps": [
                    {"range": [0, 40], "color": theme.GAUGE_ZONE_LOW},
                    {"range": [40, 70], "color": theme.GAUGE_ZONE_MED},
                    {"range": [70, 100], "color": theme.GAUGE_ZONE_HIGH},
                ],
                "threshold": {
                    "line": {"color": "white", "width": 4},
                    "thickness": 0.8,
                    "value": threshold * 100,
                },
            },
        ))
        fig.update_layout(
            height=260, margin=dict(l=20, r=20, t=30, b=10),
            paper_bgcolor="rgba(0,0,0,0)", font={"color": "white"},
            transition={"duration": 700, "easing": "cubic-in-out"},
        )
        st.plotly_chart(fig, width="stretch", key="risk_gauge_chart")

    # Local Explainability (Feature Contribution Analysis)
    exp = explain_prediction(values, model, scaler, encoders, feature_names, top_n=4)
    drivers = exp.get("risk_drivers", [])
    anchors = exp.get("retention_anchors", [])

    if drivers or anchors:
        st.markdown("---")
        st.markdown("### 🔬 Explainable AI: Feature Influence Breakdown")
        st.caption("How this specific employee's attributes pushed the model towards attrition vs. retention (log-odds impact):")

        exp_cols, exp_vals, exp_colors = [], [], []
        for feat, val in reversed(anchors):
            exp_cols.append(f"{feat} (Retention)")
            exp_vals.append(val)
            exp_colors.append(theme.GREEN)
        for feat, val in drivers:
            exp_cols.append(f"{feat} (Risk)")
            exp_vals.append(val)
            exp_colors.append(theme.RED)

        exp_fig = go.Figure(go.Bar(
            x=exp_vals,
            y=exp_cols,
            orientation="h",
            marker=dict(color=exp_colors),
        ))
        exp_fig.update_layout(
            height=280,
            margin=dict(l=20, r=20, t=10, b=20),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(title="Log-Odds Contribution (< 0 Stay, > 0 Leave)", color="white", gridcolor="rgba(255,255,255,0.1)"),
            yaxis=dict(color="white"),
        )
        st.plotly_chart(exp_fig, width="stretch", key="explainability_chart")

    st.markdown(theme.clean_html("""
    <button class="print-btn" onclick="window.print()">🖨️ Print / Save as PDF</button>
    """), unsafe_allow_html=True)
    st.caption(theme.RESULT_DISCLAIMER)
else:
    st.markdown(theme.clean_html("""
    <div class="empty-state">
        Fill in the form above and click <strong>Predict Attrition Risk</strong> to see a
        result here — a risk gauge, probability score, and the key factors behind it.
    </div>
    """), unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# SESSION HISTORY
# ----------------------------------------------------------------------------
if st.session_state.prediction_history:
    st.markdown("---")
    st.markdown("### 🕒 Recent Predictions (this session)")
    st.dataframe(st.session_state.prediction_history, width="stretch", hide_index=True)

st.markdown("---")
st.caption(theme.FOOTER_TEXT)
