# Requirement audit – Exchange Cost Planner

Status of the app against the eight course requirements, with evidence.

## 1. Clear problem
Status: PASS
Evidence:
- `app.py`, page "Home / Problem": problem, target group and what the app does.
- `README.md` sections 1–2.

## 2. API and/or database
Status: PASS (code) – NEEDS WORK (data)
Evidence:
- **Database:** `create_database.py` builds SQLite tables `cities`, `experiences`, `user_submissions` (CREATE TABLE, parameterized INSERT).
- **SQL in `database.py`:** `load_city()` (WHERE with `?`), `load_city_names()` (ORDER BY), `load_training_data()` (JOIN), `average_reported_cost_per_city()` and `count_submissions_per_city()` (GROUP BY), `save_submission()` (INSERT).
- **APIs:** `currency.py → get_exchange_rates()` (Frankfurter), `external_data.py → get_monthly_climate()` (Open-Meteo), `get_nearby_places()` (OpenStreetMap Overpass). All use `requests.get` with a timeout and return `None` on failure.
- **Needs work:** the city prices are placeholders and the training data is simulated (see requirement 5 and `DATA_SOURCES.md`). The APIs were tested with simulated answers only; test them once with internet.

## 3. Visualisation
Status: PASS
Evidence (all in `app.py`, each with a "Purpose" caption):
- Cost calculator: donut chart and bar chart of the cost categories.
- City comparison: total cost per city, costs per category (grouped bars).
- Weather & excursions: temperature line chart, rain bar chart, map of excursion destinations.
- About the model: predicted vs. real cost, average reported cost per city.

## 4. User interaction
Status: PASS
Evidence:
- Inputs: city, dates, housing, lifestyle, trips, flights, budget (`st.selectbox`, `st.date_input`, `st.radio`, `st.slider`, `st.number_input`).
- City multiselect (max. 3), radius slider, search button, category filter.
- **Adding data:** the form on "Share your experience" writes into the database.
- Invalid input is handled: end before start, unconfirmed form, fewer than two cities.

## 5. Own machine-learning model
Status: PASS (code) – NEEDS WORK (training data)
Evidence:
- `ml_model.py → train_models()`: `train_test_split`, `LinearRegression().fit(...)`, `RandomForestRegressor(n_estimators=100).fit(...)`, comparison by `mean_absolute_error`.
- `ml_model.py → predict_monthly_cost()` is used on the pages "Cost calculator" and "City comparison".
- Page "About the model" explains inputs, training data, MAE and limitations.
- **Needs work:** all 300 training rows are simulated from our own calculator, so the model mostly re-learns the calculator. Real survey answers or numbers from experience reports are needed. Ask the tutor whether this setup counts as "own model" and how many real rows are expected.

## 6. Code comments
Status: PASS
Evidence:
- Header docstring in all eight Python files, naming the responsible role.
- Comments on SQL (JOIN, GROUP BY, parameters), the three API requests, data cleaning, one-hot encoding, `reindex`, training, model choice and every chart's purpose.

## 7. Team contributions and GenAI reflection
Status: NEEDS WORK – only student actions remain
Evidence:
- `CONTRIBUTIONS.md`: matrix template with the five roles (marked as a template).
- `AI_USAGE.md`: honest statement that Claude generated the code; sections for the team to fill in.
- `# AI assistance:` comment at the top of every Python file.
- **To do:** fill in names, real contributions and the reflection; show both in the video.

## 8. Four-minute video
Status: NEEDS WORK – only student actions remain
Evidence:
- `VIDEO_PLAN.md`: timed plan up to 4:00 with a speaker per section and an upload checklist.
- **To do:** record the video with the students' own voices.

## Course-level realism check

- **Could a student after about 12 weeks understand this?**
  Yes. Eight Python files with plain functions, if/else, loops, lists, dictionaries and DataFrames.
  No classes, no decorators, no async code. The largest file is `app.py` (about 640 lines), structured page by page.
- **Could they explain the database?**
  Yes. Three small tables; the queries are short and cover SELECT, WHERE, ORDER BY, JOIN, GROUP BY and INSERT.
- **Could they explain the APIs?**
  Yes. Each is one `requests.get` call followed by `response.json()`. The comments describe request → JSON → DataFrame.
- **Could they explain the ML model?**
  Yes. Two standard scikit-learn models, one metric (MAE), and a written rule for choosing between them.
  The linear regression's coefficients are shown in the app.
- **Could they explain the charts?**
  Yes. Every chart is one `plotly.express` call with a stated purpose.
- **Parts that need a sentence of explanation (all commented):**
  - `st.session_state` to remember API answers between reruns (`get_rate_cached`, `get_climate_cached`).
  - `reindex(columns=..., fill_value=0)` in `predict_monthly_cost`.
  - The Overpass query text and the haversine distance formula in `external_data.py`.
  - `months_of_stay()` in `app.py` (handles a stay that goes over New Year).
- **Simplified during the audit:** one combined placeholder warning on the comparison page instead of one
  per city; `demo_app.py` was removed because `app.py` replaces it.
- **If the team wants less:** the excursion search (Overpass + map) is the most advanced part and can be
  removed without affecting the other pages.
