"""
pages/3_About.py — Project background and credits.
"""

import streamlit as st
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import theme

st.markdown(theme.build_css(), unsafe_allow_html=True)

st.markdown(theme.clean_html(f"""
<div class="hero-card">
    <div class="brand-row">
        {theme.LOGO_SVG}
        <div>
            <div class="hero-title">{theme.ABOUT_PAGE_TITLE}</div>
        </div>
    </div>
</div>
"""), unsafe_allow_html=True)

st.markdown(theme.ABOUT_PAGE_BODY)

st.markdown("---")
st.markdown("### Pages in this app")
st.markdown("""
- **Predict** — score one employee at a time through an interactive form
- **Batch Prediction** — upload a CSV and score many employees at once
- **Compare** — score two employees side-by-side and see the risk gap between them
- **Model Insights** — interactive model comparison + key EDA findings
- **About** — this page
""")

st.markdown("---")
st.caption(theme.FOOTER_TEXT)
