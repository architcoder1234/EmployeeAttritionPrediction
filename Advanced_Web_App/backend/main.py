"""
Advanced_Web_App/backend/main.py

A standalone FastAPI backend wrapping the same trained model used by the
Streamlit app. This is an OPTIONAL alternate deployment path — the project's
primary required deliverable is still the Streamlit app in Streamlit_App/.
This exists for a more customizable, non-Streamlit-looking frontend.

Run with:
    cd Advanced_Web_App/backend
    pip install -r requirements.txt
    uvicorn main:app --reload --port 8000

Then open Advanced_Web_App/frontend/index.html in a browser (or serve it
with any static file server) — it calls this API at http://localhost:8000.
"""

import io
import os
import sys

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd

# Reuse the EXACT SAME prediction logic as the Streamlit app — single source
# of truth for preprocessing/feature engineering, so results always match.
STREAMLIT_APP_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "Streamlit_App")
)
sys.path.insert(0, STREAMLIT_APP_DIR)
from model_utils import (  # noqa: E402
    load_artifacts, predict_one, predict_batch, REQUIRED_RAW_COLUMNS,
)

app = FastAPI(
    title="Employee Attrition Prediction API",
    description="REST API wrapping the Employee Attrition Prediction System's trained model.",
    version="1.0.0",
)

# Allow the local static frontend (opened via file:// or a simple dev server)
# to call this API. Tighten this before deploying publicly.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

model, scaler, encoders, feature_names, model_meta = load_artifacts()


class EmployeeRecord(BaseModel):
    Age: int
    BusinessTravel: str
    DailyRate: int
    Department: str
    DistanceFromHome: int
    Education: int
    EducationField: str
    EnvironmentSatisfaction: int
    Gender: str
    HourlyRate: int
    JobInvolvement: int
    JobLevel: int
    JobRole: str
    JobSatisfaction: int
    MaritalStatus: str
    MonthlyIncome: int
    MonthlyRate: int
    NumCompaniesWorked: int
    OverTime: str
    PercentSalaryHike: int
    PerformanceRating: int
    RelationshipSatisfaction: int
    StockOptionLevel: int
    TotalWorkingYears: int
    TrainingTimesLastYear: int
    WorkLifeBalance: int
    YearsAtCompany: int
    YearsInCurrentRole: int
    YearsSinceLastPromotion: int
    YearsWithCurrManager: int


class PredictionResponse(BaseModel):
    prediction: int
    risk_label: str
    probability: float


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/model_info")
def model_info():
    return {
        "model_name": model_meta["best_model"],
        "metrics": model_meta["metrics"],
        "categorical_options": {col: list(enc.classes_) for col, enc in encoders.items()},
    }


@app.post("/predict", response_model=PredictionResponse)
def predict(record: EmployeeRecord):
    try:
        prediction, probability = predict_one(
            record.model_dump(), model, scaler, encoders, feature_names
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return PredictionResponse(
        prediction=prediction,
        risk_label="High" if prediction == 1 else "Low",
        probability=probability,
    )


@app.post("/predict_batch")
async def predict_batch_endpoint(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a .csv file")

    contents = await file.read()
    try:
        df = pd.read_csv(io.BytesIO(contents), encoding="utf-8-sig")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Couldn't parse CSV: {e}")

    try:
        results = predict_batch(df, model, scaler, encoders, feature_names)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return results.to_dict(orient="records")


@app.get("/required_columns")
def required_columns():
    return {"columns": REQUIRED_RAW_COLUMNS}
