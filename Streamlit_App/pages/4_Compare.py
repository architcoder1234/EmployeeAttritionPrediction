"""
pages/4_Compare.py — Score two employees side-by-side.

Reuses the same FORM_TABS config and prediction logic as the Predict page,
but with prefixed widget keys ("a_"/"b_") so this page's state never
collides with the main Predict page's session_state.
"""

import streamlit as st
import plotly.graph_objects as go
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import theme
from fields_config import FORM_TABS, CONTEXT_RULES
from model_utils import load_artifacts, engineer_features, predict_one

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
            <div class="hero-title">⚖️ Compare Two Employees</div>
            <div class="hero-sub">Fill in both profiles and compare attrition risk side-by-side.</div>
        </div>
    </div>
</div>
"""), unsafe_allow_html=True)


def render_field(spec, prefix):
    label = spec["label"]
    widget = spec["widget"]
    key = f"{prefix}_{spec['key']}"
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


def render_employee_form(prefix, heading):
    st.markdown(f"#### {heading}")
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
                    values[spec["key"]] = render_field(spec, prefix)
            with c2:
                for spec in col2_fields:
                    values[spec["key"]] = render_field(spec, prefix)
            for spec in full_fields:
                values[spec["key"]] = render_field(spec, prefix)
    return values


col_a, col_b = st.columns(2)
with col_a:
    values_a = render_employee_form("a", "👤 Employee A")
with col_b:
    values_b = render_employee_form("b", "👤 Employee B")

compare_clicked = st.button("⚖️ Compare Attrition Risk", key="compare_btn", width="stretch")

if compare_clicked:
    with st.spinner("Scoring both employees..."):
        raw_a = engineer_features(values_a)
        raw_a["OverTime_label"] = values_a["OverTime"]
        pred_a, prob_a = predict_one(values_a, model, scaler, encoders, feature_names)

        raw_b = engineer_features(values_b)
        raw_b["OverTime_label"] = values_b["OverTime"]
        pred_b, prob_b = predict_one(values_b, model, scaler, encoders, feature_names)

    def result_block(label, pred, prob, raw_for_rules):
        pct = prob * 100
        card_class = "high" if pred == 1 else "low"
        risk_label = theme.HIGH_RISK_LABEL if pred == 1 else theme.LOW_RISK_LABEL
        risk_color = theme.RED if pred == 1 else theme.GREEN

        st.markdown(theme.clean_html(f"""
        <div class="result-card {card_class}">
            <div style="font-size:1rem; color:{theme.ICE};">{label}</div>
            <div style="font-size:1.3rem; font-weight:700; color:{risk_color}; margin-top:0.2rem;">{risk_label}</div>
            <div style="font-size:2.2rem; font-weight:800; color:white; margin-top:0.3rem;">{pct:.1f}%</div>
        </div>
        """), unsafe_allow_html=True)

        notes = [msg for condition, msg in CONTEXT_RULES if condition(raw_for_rules)]
        if not notes:
            notes = [theme.NO_FLAGS_MESSAGE]
        for n in notes:
            st.markdown(f"- {n}")
        return pct, risk_color

    res_a, res_b = st.columns(2)
    with res_a:
        pct_a, color_a = result_block("Employee A", pred_a, prob_a, raw_a)
    with res_b:
        pct_b, color_b = result_block("Employee B", pred_b, prob_b, raw_b)

    st.markdown("---")
    diff = abs(pct_a - pct_b)
    higher = "Employee A" if pct_a > pct_b else ("Employee B" if pct_b > pct_a else None)
    if higher:
        st.markdown(
            f"**{higher}** has a **{diff:.1f} percentage point** higher attrition risk "
            f"than the other employee."
        )
    else:
        st.markdown("Both employees have the same predicted attrition risk.")

    fig = go.Figure(go.Bar(
        x=["Employee A", "Employee B"], y=[pct_a, pct_b],
        marker_color=[color_a, color_b], text=[f"{pct_a:.1f}%", f"{pct_b:.1f}%"],
        textposition="outside",
    ))
    fig.update_layout(
        height=280, margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,0.03)",
        font={"color": "white"}, yaxis={"range": [0, 100], "title": "Attrition Risk %"},
    )
    st.plotly_chart(fig, width="stretch", key="compare_bar_chart")

st.markdown("---")
st.caption(theme.FOOTER_TEXT)
