import os
import sys
import pytest
import pandas as pd
import numpy as np

# Ensure Streamlit_App is in path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(CURRENT_DIR)
sys.path.insert(0, os.path.join(PROJECT_DIR, "Streamlit_App"))

from model_utils import (
    load_artifacts,
    engineer_features,
    encode_row,
    predict_one,
    predict_batch,
    explain_prediction,
    REQUIRED_RAW_COLUMNS,
)


@pytest.fixture(scope="module")
def artifacts():
    return load_artifacts()


@pytest.fixture
def sample_row():
    return {
        "Age": 35,
        "BusinessTravel": "Travel_Rarely",
        "DailyRate": 1102,
        "Department": "Sales",
        "DistanceFromHome": 1,
        "Education": 2,
        "EducationField": "Life Sciences",
        "EnvironmentSatisfaction": 2,
        "Gender": "Female",
        "HourlyRate": 94,
        "JobInvolvement": 3,
        "JobLevel": 2,
        "JobRole": "Sales Executive",
        "JobSatisfaction": 4,
        "MaritalStatus": "Single",
        "MonthlyIncome": 5993,
        "MonthlyRate": 19479,
        "NumCompaniesWorked": 8,
        "OverTime": "Yes",
        "PercentSalaryHike": 11,
        "PerformanceRating": 3,
        "RelationshipSatisfaction": 1,
        "StockOptionLevel": 0,
        "TotalWorkingYears": 8,
        "TrainingTimesLastYear": 0,
        "WorkLifeBalance": 1,
        "YearsAtCompany": 6,
        "YearsInCurrentRole": 4,
        "YearsSinceLastPromotion": 0,
        "YearsWithCurrManager": 5,
    }


def test_load_artifacts(artifacts):
    model, scaler, encoders, feature_names, model_meta = artifacts
    assert model is not None
    assert scaler is not None
    assert isinstance(encoders, dict)
    assert len(encoders) > 0
    assert isinstance(feature_names, list)
    assert len(feature_names) == 34
    assert "best_model" in model_meta


def test_engineer_features(sample_row):
    engineered = engineer_features(sample_row)
    assert "TenureRatio" in engineered
    assert "IncomePerYearExp" in engineered
    assert "PromotionGap" in engineered
    assert "AvgSatisfaction" in engineered

    expected_tenure = sample_row["YearsAtCompany"] / (sample_row["TotalWorkingYears"] + 1)
    assert pytest.approx(engineered["TenureRatio"]) == expected_tenure

    expected_income = sample_row["MonthlyIncome"] / (sample_row["TotalWorkingYears"] + 1)
    assert pytest.approx(engineered["IncomePerYearExp"]) == expected_income

    expected_gap = sample_row["YearsAtCompany"] - sample_row["YearsSinceLastPromotion"]
    assert engineered["PromotionGap"] == expected_gap


def test_encode_row(artifacts, sample_row):
    _, _, encoders, _, _ = artifacts
    encoded = encode_row(sample_row, encoders)
    for col in encoders:
        assert isinstance(encoded[col], (int, np.integer))

    # Test invalid category
    bad_row = sample_row.copy()
    bad_row["OverTime"] = "Invalid_Value"
    with pytest.raises(ValueError):
        encode_row(bad_row, encoders)


def test_predict_one(artifacts, sample_row):
    model, scaler, encoders, feature_names, _ = artifacts
    prediction, probability = predict_one(sample_row, model, scaler, encoders, feature_names)
    assert prediction in (0, 1)
    assert 0.0 <= probability <= 1.0


def test_predict_threshold(artifacts, sample_row):
    model, scaler, encoders, feature_names, _ = artifacts
    _, probability = predict_one(sample_row, model, scaler, encoders, feature_names)

    # Threshold very high -> prediction should be 0 (unless prob is 1.0)
    pred_high, _ = predict_one(sample_row, model, scaler, encoders, feature_names, threshold=0.999)
    if probability < 0.999:
        assert pred_high == 0

    # Threshold very low -> prediction should be 1 (unless prob is 0.0)
    pred_low, _ = predict_one(sample_row, model, scaler, encoders, feature_names, threshold=0.001)
    if probability > 0.001:
        assert pred_low == 1


def test_explain_prediction(artifacts, sample_row):
    model, scaler, encoders, feature_names, _ = artifacts
    exp = explain_prediction(sample_row, model, scaler, encoders, feature_names, top_n=3)
    assert "risk_drivers" in exp
    assert "retention_anchors" in exp
    assert len(exp["risk_drivers"]) <= 3
    assert len(exp["retention_anchors"]) <= 3


def test_predict_batch(artifacts, sample_row):
    model, scaler, encoders, feature_names, _ = artifacts
    df = pd.DataFrame([sample_row, sample_row])
    results = predict_batch(df, model, scaler, encoders, feature_names)
    assert "AttritionRisk" in results.columns
    assert "AttritionProbability" in results.columns
    assert len(results) == 2

    # Test missing column validation
    incomplete_df = df.drop(columns=["MonthlyIncome"])
    with pytest.raises(ValueError, match="Missing required column"):
        predict_batch(incomplete_df, model, scaler, encoders, feature_names)
