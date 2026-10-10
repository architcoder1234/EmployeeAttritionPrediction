"""
model_utils.py — Shared model loading + prediction logic.

Every page of the app (Predict, Batch Predict, Model Insights) and the
optional FastAPI backend all call into this file instead of duplicating the
preprocessing/feature-engineering steps in five different places. If you ever
change how a feature is engineered, change it here ONCE.
"""

import os
import json
import joblib
import numpy as np
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(BASE_DIR, "Model")

RAW_CATEGORICAL_COLS = [
    "BusinessTravel", "Department", "EducationField", "Gender",
    "JobRole", "MaritalStatus", "OverTime",
]

# The exact set of raw columns the model needs before feature engineering.
# Used by the batch-prediction CSV validator to give a clear error message
# instead of a confusing pandas KeyError.
REQUIRED_RAW_COLUMNS = [
    "Age", "BusinessTravel", "DailyRate", "Department", "DistanceFromHome",
    "Education", "EducationField", "EnvironmentSatisfaction", "Gender",
    "HourlyRate", "JobInvolvement", "JobLevel", "JobRole", "JobSatisfaction",
    "MaritalStatus", "MonthlyIncome", "MonthlyRate", "NumCompaniesWorked",
    "OverTime", "PercentSalaryHike", "PerformanceRating",
    "RelationshipSatisfaction", "StockOptionLevel", "TotalWorkingYears",
    "TrainingTimesLastYear", "WorkLifeBalance", "YearsAtCompany",
    "YearsInCurrentRole", "YearsSinceLastPromotion", "YearsWithCurrManager",
]


def load_artifacts():
    """Loads the trained model, scaler, label encoders, and metadata.
    Cache this in Streamlit with @st.cache_resource where it's called."""
    model = joblib.load(os.path.join(MODEL_DIR, "best_model.pkl"))
    scaler = joblib.load(os.path.join(MODEL_DIR, "scaler.pkl"))
    encoders = joblib.load(os.path.join(MODEL_DIR, "label_encoders.pkl"))
    with open(os.path.join(MODEL_DIR, "feature_names.json")) as f:
        feature_names = json.load(f)
    with open(os.path.join(MODEL_DIR, "best_model_name.json")) as f:
        model_meta = json.load(f)
    return model, scaler, encoders, feature_names, model_meta


def engineer_features(row: dict) -> dict:
    """Adds the 4 engineered features to a raw input row. `row` must already
    contain the raw columns with their ORIGINAL string labels for categoricals
    (not yet encoded)."""
    row = dict(row)
    row["TenureRatio"] = row["YearsAtCompany"] / (row["TotalWorkingYears"] + 1)
    row["IncomePerYearExp"] = row["MonthlyIncome"] / (row["TotalWorkingYears"] + 1)
    row["PromotionGap"] = row["YearsAtCompany"] - row["YearsSinceLastPromotion"]
    row["AvgSatisfaction"] = np.mean([
        row["JobSatisfaction"], row["EnvironmentSatisfaction"],
        row["RelationshipSatisfaction"], row["WorkLifeBalance"],
    ])
    return row


def encode_row(row: dict, encoders: dict) -> dict:
    """Encodes categorical columns in-place using the SAME encoders fit
    during training. Raises a ValueError with a clear message if a category
    value wasn't seen during training (e.g. a typo in an uploaded CSV)."""
    row = dict(row)
    for col in RAW_CATEGORICAL_COLS:
        try:
            row[col] = encoders[col].transform([row[col]])[0]
        except ValueError:
            valid = list(encoders[col].classes_)
            raise ValueError(
                f"Unrecognized value {row[col]!r} for column '{col}'. "
                f"Valid values are: {valid}"
            )
    return row


def predict_one(raw_row: dict, model, scaler, encoders, feature_names, threshold: float = 0.5):
    """Runs the full pipeline (engineer -> encode -> scale -> predict) on a
    single employee record and returns (prediction, probability).
    `threshold` determines the cutoff probability for predicting positive (Yes/1)."""
    row = engineer_features(raw_row)
    row = encode_row(row, encoders)
    input_df = pd.DataFrame([{k: row[k] for k in feature_names}])
    input_scaled = scaler.transform(input_df)
    probability = float(model.predict_proba(input_scaled)[0][1])
    prediction = int(1 if probability >= threshold else 0)
    return prediction, probability


def explain_prediction(raw_row: dict, model, scaler, encoders, feature_names, top_n: int = 5):
    """Computes exact linear feature contributions (log-odds impact) for the input employee.
    Features with positive contribution push towards attrition (risk drivers).
    Features with negative contribution pull towards retention (retention anchors)."""
    row = engineer_features(raw_row)
    row = encode_row(row, encoders)
    input_df = pd.DataFrame([{k: row[k] for k in feature_names}])
    input_scaled = scaler.transform(input_df)

    if hasattr(model, "coef_"):
        contributions = pd.Series(model.coef_[0] * input_scaled[0], index=feature_names)
        drivers = contributions[contributions > 0].sort_values(ascending=False).head(top_n)
        anchors = contributions[contributions < 0].sort_values(ascending=True).head(top_n)
        return {
            "risk_drivers": [(k, float(v)) for k, v in drivers.items()],
            "retention_anchors": [(k, float(v)) for k, v in anchors.items()],
        }
    return {"risk_drivers": [], "retention_anchors": []}


def predict_batch(df: pd.DataFrame, model, scaler, encoders, feature_names, threshold: float = 0.5):
    """Runs the full pipeline on a DataFrame of many employees (e.g. an
    uploaded CSV). Returns a copy of df with two new columns:
    'AttritionRisk' (Yes/No) and 'AttritionProbability' (0-1 float).

    Raises ValueError listing any missing required columns before doing
    any work, so the caller can show one clear message instead of a
    cryptic KeyError partway through."""
    missing = [c for c in REQUIRED_RAW_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required column(s): {', '.join(missing)}")

    results = []
    for _, r in df.iterrows():
        row = r.to_dict()
        try:
            pred, prob = predict_one(row, model, scaler, encoders, feature_names, threshold=threshold)
            results.append((("Yes" if pred == 1 else "No"), prob, None))
        except Exception as e:
            results.append((None, None, str(e)))

    out = df.copy()
    out["AttritionRisk"] = [r[0] for r in results]
    out["AttritionProbability"] = [r[1] for r in results]
    out["Error"] = [r[2] for r in results]
    return out

