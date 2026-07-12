"""
fields_config.py — Defines every input field on the form as plain data.

To ADD a field: add one dict to the right tab's "fields" list.
To REMOVE a field: delete its dict.
To REORDER fields: reorder the list (top to bottom = left column, then right column, per tab).
To MOVE a field to the other column: change "col" to 1 or 2.
To RENAME a label: edit "label" — no need to touch app.py at all.

app.py reads this file and builds the actual Streamlit widgets automatically —
you should never need to add new st.slider()/st.selectbox() calls by hand.

WIDGET TYPES available:
  "slider"        -> st.slider(label, min, max, default)
  "number_input"  -> st.number_input(label, min, max, default)
  "select_slider"  -> st.select_slider(label, options, default)   (used for 1-4 rating scales)
  "selectbox"     -> st.selectbox(label, options, index=default_index)
  "encoder_select" -> st.selectbox(label, options=<from Model/label_encoders.pkl>)
                       Use this for any categorical column the model was trained on
                       (BusinessTravel, Department, EducationField, Gender, JobRole,
                       MaritalStatus, OverTime) — the options list comes from the saved
                       encoder automatically, so it always matches what the model expects.

Every field's "key" MUST exactly match the column name the model expects
(see Model/feature_names.json for the full list) — app.py uses these keys
directly when building the row to send to the model.
"""

FORM_TABS = [
    {
        "label": "👤 Personal & Role",
        "fields": [
            {"key": "Age", "label": "Age", "widget": "slider", "min": 18, "max": 60, "default": 30, "col": 1},
            {"key": "Gender", "label": "Gender", "widget": "encoder_select", "encoder": "Gender", "col": 1},
            {"key": "MaritalStatus", "label": "Marital Status", "widget": "encoder_select", "encoder": "MaritalStatus", "col": 1},
            {"key": "Department", "label": "Department", "widget": "encoder_select", "encoder": "Department", "col": 1},
            {"key": "JobRole", "label": "Job Role", "widget": "encoder_select", "encoder": "JobRole", "col": 1},

            {"key": "JobLevel", "label": "Job Level (1-5)", "widget": "selectbox", "options": [1, 2, 3, 4, 5], "default_index": 1, "col": 2},
            {"key": "Education", "label": "Education Level (1-5)", "widget": "selectbox", "options": [1, 2, 3, 4, 5], "default_index": 2, "col": 2},
            {"key": "EducationField", "label": "Education Field", "widget": "encoder_select", "encoder": "EducationField", "col": 2},
            {"key": "BusinessTravel", "label": "Business Travel", "widget": "encoder_select", "encoder": "BusinessTravel", "col": 2},
            {"key": "DistanceFromHome", "label": "Distance From Home (km)", "widget": "slider", "min": 1, "max": 30, "default": 5, "col": 2, "help": "One-way commute distance. Longer commutes are mildly associated with higher attrition in this dataset."},
        ],
    },
    {
        "label": "💰 Compensation",
        "fields": [
            {"key": "MonthlyIncome", "label": "Monthly Income", "widget": "number_input", "min": 1000, "max": 20000, "default": 5000, "col": 1},
            {"key": "DailyRate", "label": "Daily Rate", "widget": "number_input", "min": 100, "max": 1500, "default": 800, "col": 1},
            {"key": "MonthlyRate", "label": "Monthly Rate", "widget": "number_input", "min": 2000, "max": 27000, "default": 14000, "col": 1},
            {"key": "HourlyRate", "label": "Hourly Rate", "widget": "number_input", "min": 30, "max": 100, "default": 65, "col": 1},

            {"key": "PercentSalaryHike", "label": "Percent Salary Hike", "widget": "slider", "min": 10, "max": 25, "default": 15, "col": 2, "help": "Most recent annual salary increase, as a percentage."},
            {"key": "StockOptionLevel", "label": "Stock Option Level (0-3)", "widget": "selectbox", "options": [0, 1, 2, 3], "default_index": 0, "col": 2, "help": "0 = no stock options, 3 = highest equity tier. Higher levels are a retention incentive."},
            {"key": "PerformanceRating", "label": "Performance Rating (3-4)", "widget": "selectbox", "options": [3, 4], "default_index": 0, "col": 2, "help": "Most recent performance review score. This dataset only contains 3 (Excellent) and 4 (Outstanding) ratings."},
            {"key": "OverTime", "label": "OverTime", "widget": "encoder_select", "encoder": "OverTime", "col": 2},
        ],
    },
    {
        "label": "🙂 Satisfaction & Work-Life",
        "fields": [
            {"key": "JobSatisfaction", "label": "Job Satisfaction (1-4)", "widget": "select_slider", "options": [1, 2, 3, 4], "default": 3, "col": 1},
            {"key": "EnvironmentSatisfaction", "label": "Environment Satisfaction (1-4)", "widget": "select_slider", "options": [1, 2, 3, 4], "default": 3, "col": 1},

            {"key": "RelationshipSatisfaction", "label": "Relationship Satisfaction (1-4)", "widget": "select_slider", "options": [1, 2, 3, 4], "default": 3, "col": 2},
            {"key": "WorkLifeBalance", "label": "Work Life Balance (1-4)", "widget": "select_slider", "options": [1, 2, 3, 4], "default": 3, "col": 2},

            {"key": "JobInvolvement", "label": "Job Involvement (1-4)", "widget": "select_slider", "options": [1, 2, 3, 4], "default": 3, "col": 1, "full_width": True, "help": "How engaged the employee is with their day-to-day work, self-reported (1 = low, 4 = high)."},
        ],
    },
    {
        "label": "📈 Tenure & History",
        "fields": [
            {"key": "TotalWorkingYears", "label": "Total Working Years", "widget": "slider", "min": 0, "max": 40, "default": 8, "col": 1},
            {"key": "YearsAtCompany", "label": "Years At Company", "widget": "slider", "min": 0, "max": 40, "default": 5, "col": 1},
            {"key": "YearsInCurrentRole", "label": "Years In Current Role", "widget": "slider", "min": 0, "max": 20, "default": 3, "col": 1},

            {"key": "YearsSinceLastPromotion", "label": "Years Since Last Promotion", "widget": "slider", "min": 0, "max": 15, "default": 1, "col": 2, "help": "A gap of 5+ years here is flagged in the result as a possible career-stagnation signal."},
            {"key": "YearsWithCurrManager", "label": "Years With Current Manager", "widget": "slider", "min": 0, "max": 20, "default": 3, "col": 2},
            {"key": "NumCompaniesWorked", "label": "Num Companies Worked", "widget": "slider", "min": 0, "max": 10, "default": 2, "col": 2, "help": "Total number of employers this person has worked for prior to the current one."},
            {"key": "TrainingTimesLastYear", "label": "Training Times Last Year", "widget": "slider", "min": 0, "max": 6, "default": 2, "col": 2, "help": "Number of training sessions attended in the last 12 months."},
        ],
    },
]


# ==============================================================================
# CONTRIBUTING CONTEXT RULES (shown under the prediction result)
# Add/remove tuples of (lambda taking the final `raw` dict -> bool, message).
# Keep messages short — they're meant to be a quick, honest gut-check, not a
# full explanation. See theme.py for the "no flags" fallback message.
# ==============================================================================
CONTEXT_RULES = [
    (lambda raw: raw.get("OverTime_label") == "Yes",
     "Works OverTime — one of the strongest attrition signals in this dataset."),
    (lambda raw: raw["IncomePerYearExp"] < 500,
     "Income relative to experience is on the lower side."),
    (lambda raw: raw["WorkLifeBalance"] <= 2,
     "Reports below-average Work-Life Balance."),
    (lambda raw: raw["YearsSinceLastPromotion"] >= 5,
     "Long gap since last promotion."),
]
