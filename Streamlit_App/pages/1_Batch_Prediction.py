"""
pages/1_Batch_Prediction.py — Score a whole CSV of employees at once.
"""

import streamlit as st
import pandas as pd
import io
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import theme
from model_utils import load_artifacts, predict_batch, REQUIRED_RAW_COLUMNS

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
            <div class="hero-title">{theme.BATCH_PAGE_TITLE}</div>
            <div class="hero-sub">{theme.BATCH_PAGE_INTRO}</div>
        </div>
    </div>
</div>
"""), unsafe_allow_html=True)

st.info(theme.BATCH_TEMPLATE_NOTE)

# ----------------------------------------------------------------------------
# Downloadable template
# ----------------------------------------------------------------------------
template_df = pd.DataFrame([{
    "Age": 30, "BusinessTravel": "Travel_Rarely", "DailyRate": 800,
    "Department": "Research & Development", "DistanceFromHome": 5, "Education": 3,
    "EducationField": "Life Sciences", "EnvironmentSatisfaction": 3, "Gender": "Male",
    "HourlyRate": 65, "JobInvolvement": 3, "JobLevel": 2, "JobRole": "Research Scientist",
    "JobSatisfaction": 3, "MaritalStatus": "Single", "MonthlyIncome": 5000,
    "MonthlyRate": 14000, "NumCompaniesWorked": 2, "OverTime": "No",
    "PercentSalaryHike": 15, "PerformanceRating": 3, "RelationshipSatisfaction": 3,
    "StockOptionLevel": 0, "TotalWorkingYears": 8, "TrainingTimesLastYear": 2,
    "WorkLifeBalance": 3, "YearsAtCompany": 5, "YearsInCurrentRole": 3,
    "YearsSinceLastPromotion": 1, "YearsWithCurrManager": 3,
}])
csv_buf = io.StringIO()
template_df.to_csv(csv_buf, index=False)
col_a, col_b = st.columns(2)
with col_a:
    st.download_button(
        "⬇️ Download CSV template (1 row)", csv_buf.getvalue(),
        file_name="batch_prediction_template.csv", mime="text/csv",
        use_container_width=True,
    )

sample_csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "Dataset", "sample_batch_input.csv")
if os.path.exists(sample_csv_path):
    with open(sample_csv_path, "r", encoding="utf-8") as f:
        sample_csv_data = f.read()
    with col_b:
        st.download_button(
            "⬇️ Download sample dataset (10 employees)", sample_csv_data,
            file_name="sample_employees_batch.csv", mime="text/csv",
            use_container_width=True,
        )

st.markdown("---")

uploaded = st.file_uploader("Upload employee CSV", type=["csv"])

if uploaded is not None:
    try:
        df = pd.read_csv(uploaded, encoding="utf-8-sig")
    except Exception as e:
        st.error(f"Couldn't read that file as a CSV: {e}")
        st.stop()

    st.write(f"Loaded **{len(df)}** rows. Preview:")
    st.dataframe(df.head(10), width="stretch")

    if st.button("🔮 Score All Employees", width="stretch"):
        with st.spinner(f"Scoring {len(df)} employees..."):
            try:
                results = predict_batch(df, model, scaler, encoders, feature_names)
            except ValueError as e:
                st.error(str(e))
                st.stop()

        n_errors = results["Error"].notna().sum()
        n_high = (results["AttritionRisk"] == "Yes").sum()
        n_low = (results["AttritionRisk"] == "No").sum()

        c1, c2, c3 = st.columns(3)
        c1.metric("✅ Scored successfully", len(results) - n_errors)
        c2.metric("⚠️ High risk flagged", int(n_high))
        c3.metric("Rows with errors", int(n_errors))

        if n_errors > 0:
            st.warning(
                f"{n_errors} row(s) couldn't be scored — check the 'Error' column "
                "in the results below (usually an unrecognized category value)."
            )

        st.dataframe(results, width="stretch")

        out_buf = io.StringIO()
        results.to_csv(out_buf, index=False)
        st.download_button(
            "⬇️ Download results CSV", out_buf.getvalue(),
            file_name="attrition_predictions.csv", mime="text/csv",
            width="stretch",
        )

st.markdown("---")
st.caption(theme.FOOTER_TEXT)
