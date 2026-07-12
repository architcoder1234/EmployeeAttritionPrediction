# Editing Guide — Streamlit App

The app is now split into several files so you can change things safely without
touching the "plumbing" code:

| File | What it controls | Edit this when you want to... |
|---|---|---|
| `theme.py` | Colors, all page text/wording, the CSS, logo, fonts | Change the color scheme, rename headings, tweak button/result text, swap the logo |
| `fields_config.py` | Every form field (what it is, its range, which tab/column it's in) | Add, remove, reorder, or rename a form field |
| `model_utils.py` | Shared prediction logic (loading the model, feature engineering, encoding, single + batch prediction) | Rarely — this is also used by the FastAPI backend in `Advanced_Web_App/`, so changing it affects BOTH deployments |
| `app.py` | The "Predict" page layout | Rarely — only if you want to change *how* the main prediction page is laid out |
| `pages/1_📂_Batch_Prediction.py` | The batch CSV upload/scoring page | Change the batch page's layout or messaging |
| `pages/2_📊_Model_Insights.py` | The model comparison + EDA page | Add more charts or change what's shown |
| `pages/3_ℹ️_About.py` | The About page | Update project description/credits |

You should almost never need to add a new `st.slider(...)` or `st.selectbox(...)`
line by hand anymore — both `theme.py` and `fields_config.py` are just plain data
(colors, text, lists of fields), and `app.py` reads them automatically.

**Note on multi-page structure:** Streamlit automatically turns any `.py` file inside
`pages/` into a sidebar navigation item — the number prefix (`1_`, `2_`, `3_`) controls
the order, and the emoji + name (with underscores replaced by spaces) becomes the label.
To add a whole new page, just add a new file to `pages/` following that naming pattern.

---

## Recipe: Change a color

Open `theme.py`, find the `COLORS` block near the top:

```python
NAVY = "#1E2761"
RED = "#C0392B"
GREEN = "#1E8A5B"
```

Change any hex code and save. Every place that color is used across the whole
app (background, buttons, result cards, gauge) updates automatically —
you don't need to hunt through `app.py`.

---

## Recipe: Change wording / labels

Also in `theme.py`, e.g.:

```python
HERO_TITLE = "📊 Employee Attrition Prediction System"
SUBMIT_BUTTON_LABEL = "🔮 Predict Attrition Risk"
```

Change the string, save, rerun. Nothing else to touch.

---

## Recipe: Add a new form field

Open `fields_config.py`. Find the tab you want it in (e.g. `"👤 Personal & Role"`)
and add one dict to that tab's `"fields"` list. For example, to add a slider
for a hypothetical `"CommuteMinutes"` field:

```python
{"key": "CommuteMinutes", "label": "Commute Time (minutes)", "widget": "slider",
 "min": 0, "max": 120, "default": 20, "col": 1},
```

**Important:** the model was only trained on the columns listed in
`Model/feature_names.json` — adding a field the model doesn't know about will
cause an error when predicting. If you want a genuinely new predictive field,
you'd need to retrain the model in the notebook first with that column
included, then add it here to match.

To just reorder existing fields or move one to the other column, move its
dict up/down in the list, or change `"col": 1` to `"col": 2` (and vice versa).

---

## Recipe: Remove a form field

Delete its dict from `fields_config.py`. Don't do this for a field the model
actually uses for prediction (check `Model/feature_names.json`) unless you
also give `app.py` a fixed default value to use in its place — otherwise
the prediction step will fail with a missing-column error.

---

## Recipe: Change a field's type (e.g. slider → dropdown)

Change `"widget"` to one of:
- `"slider"` — needs `min`, `max`, `default`
- `"number_input"` — needs `min`, `max`, `default`
- `"select_slider"` — needs `options` (a list) and `default`
- `"selectbox"` — needs `options` (a list) and `default_index`
- `"encoder_select"` — needs `encoder` (must match a key in `Model/label_encoders.pkl`,
  e.g. `"Gender"`, `"JobRole"`, `"OverTime"`) — options come from the model
  automatically, so don't hardcode them.

---

## Recipe: Add/change a "contributing context" callout

At the bottom of `fields_config.py`:

```python
CONTEXT_RULES = [
    (lambda raw: raw.get("OverTime_label") == "Yes",
     "Works OverTime — one of the strongest attrition signals in this dataset."),
    ...
]
```

Add a new tuple: `(condition, message)`. The condition is a function that
receives the final `raw` dict (all form inputs + the 4 engineered features:
`TenureRatio`, `IncomePerYearExp`, `PromotionGap`, `AvgSatisfaction`) and
returns True/False. If it returns True, the message shows up under the result.

Example — flag employees with very low income directly (not just relative to experience):

```python
(lambda raw: raw["MonthlyIncome"] < 3000,
 "Monthly income is notably low compared to the wider workforce."),
```

---

## Testing your changes without a browser

If you have Python but don't want to open a browser every time, you can
sanity-check the app still runs with no errors using:

```bash
cd Streamlit_App
python -c "
from streamlit.testing.v1 import AppTest
at = AppTest.from_file('app.py')
at.run()
print('Exceptions:', at.exception)
at.button[0].click().run()
print('Exceptions after submit:', at.exception)
"
```

If both print `Exceptions: ElementList()` (empty), you're good — no crashes.
Then run `streamlit run app.py` as normal to actually see it.
