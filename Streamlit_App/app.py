"""
Employee Attrition Prediction System - Streamlit App (multi-page router)
Run with: streamlit run app.py

This file is just the navigation router. Page titles and icons are declared
here as plain Python strings (not derived from filenames), which avoids the
mojibake bug that happens when emoji-in-filenames get mangled by zip/OS
filename encoding on some platforms.

EDITING THIS APP:
  - Colors, text, logo, fonts             -> theme.py
  - Form fields (add/remove/reorder)      -> fields_config.py
  - Prediction logic (shared everywhere)  -> model_utils.py
  - Page titles/icons/order               -> this file, the st.Page(...) list below
  - Page-specific layout                  -> predict.py / pages/*.py
See EDITING_GUIDE.md for step-by-step recipes.
"""

import streamlit as st
import theme

st.set_page_config(
    page_title=theme.PAGE_TITLE,
    page_icon=theme.PAGE_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)

pg = st.navigation([
    st.Page("predict.py", title="Predict", icon="🔮", default=True),
    st.Page("pages/1_Batch_Prediction.py", title="Batch Prediction", icon="📂"),
    st.Page("pages/4_Compare.py", title="Compare", icon="⚖️"),
    st.Page("pages/2_Model_Insights.py", title="Model Insights", icon="📊"),
    st.Page("pages/3_About.py", title="About", icon="ℹ️"),
])
pg.run()
