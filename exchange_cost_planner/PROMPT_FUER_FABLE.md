# Prompt for Claude (Fable) – build the complete Exchange Cost Planner

> Copy everything below the line into a new Claude Code session that has access to the
> repository `tvndyy/CS-Project`. Fill in the parts marked **[FILL IN]** first.

---

You are a careful programming partner for a university group project in the introductory course
"Fundamentals and Methods of Computer Science for Business Studies" at the University of St. Gallen (HSG).
Build the complete Streamlit app **Exchange Cost Planner** in the folder `exchange_cost_planner/` of
this repository. Do not change the other project folders (`cafe_demand_planner/`,
`used_car_price_explorer/`, `student_exchange_planner/`).

## 1. Context: who will use and explain this code

- The team is 5 business students with about 10–12 weeks of Python. Every team member must be able to
  **explain their part of the code in a Q&A**. Write code they can understand: plain functions,
  if/else, loops, lists, dictionaries, pandas DataFrames, `sqlite3`, `requests`, scikit-learn,
  Streamlit, Plotly Express. Do **not** use classes (unless clearly needed), decorators (except Streamlit's
  own if unavoidable), async code, ORMs, design patterns, Docker, React, or custom CSS beyond a few lines.
- The course has covered: Python basics, functions, data structures, file handling, HTTP/APIs and
  distributed systems, relational databases and SQL, simple web apps, data wrangling and visualisation
  with pandas, and introductory machine learning (training simple scikit-learn models).
- Prefer **clarity over sophistication**. It is better to repeat two simple lines than to build an
  abstraction. Comment major sections, SQL, API calls, data cleaning, ML training and predictions,
  and the purpose of every chart. Do not comment trivial lines.

## 2. The problem the app solves

Students planning an exchange semester often do not know how much money they realistically need.
Living costs differ greatly between cities, and the information is scattered across experience reports,
forums and cost-comparison websites. Target group: students (initially at HSG) choosing between partner
universities or planning the budget for a fixed destination. The app gives a **personal cost estimate
for the whole stay**, broken down by category, plus the weather during the semester and nearby
excursion destinations.

## 3. Course requirements – every one must be clearly fulfilled (target: solid "good", not flashy)

1. A clearly stated problem (business or consumer use case).
2. Data loaded via an **API** and/or from a **database** (we use both).
3. **Visualisations** that serve the use case.
4. Meaningful **user interaction** (inputs, filters, adding data, running an analysis).
5. **Machine learning: we train and use our own model** (`model.fit(...)` visible in our code; a
   pre-trained external model does not count).
6. Source code well documented with comments.
7. Contributions of each team member documented (contribution matrix) and use of GenAI reflected.
8. A max. 4-minute video with the students' own voice-over (no generated audio).

GenAI rule of the course: AI-generated code used in the project must be **cited in the source code**.
Put this block at the top of every file you create or substantially change (not on every line):

```python
# AI assistance:
# Initial implementation developed with assistance from Claude.
# Students reviewed, tested, adapted and must document the exact use
# according to HSG course requirements.
```

Never claim that students wrote code they did not write.

## 4. Existing code you MUST reuse (do not rewrite it)

Read these files first:

- `exchange_cost_planner/calculation.py` – rule-based cost calculation (`estimate_exchange_costs`,
  `months_between`, `HOUSING_COLUMNS`, `LIFESTYLES`, `UNCERTAINTY`). Already tested.
- `exchange_cost_planner/currency.py` – Frankfurter API exchange rates with a saved-rates fallback
  (`get_exchange_rates`, `convert_from_chf`).
- `exchange_cost_planner/check_calculation.py` – 30 hand-calculated checks. They must still pass at the end.
- `exchange_cost_planner/demo_app.py` – shows how the modules are used (placeholder data). Use its layout
  and its `get_rate_cached` pattern (`st.session_state`) in the real app; you may delete `demo_app.py`
  once `app.py` replaces it, or keep it – say which.
- `exchange_cost_planner/SCHNITTSTELLEN.md` – the agreed interfaces (in German). **Follow the city-data
  columns defined there** (all amounts in CHF). If you must change an interface, update this file too.

## 5. File structure (one file per team role, so contributions are clear)

```
exchange_cost_planner/
├── app.py                 # Role "App & Design": pages, inputs, results, charts, integration
├── database.py            # Role "Daten & Datenbank": SQLite connection and all SQL queries
├── create_database.py     # Role "Daten & Datenbank": builds database/exchange_costs.db from the CSV files
├── calculation.py         # Role "Berechnung & Wechselkurse" (exists)
├── currency.py            # Role "Berechnung & Wechselkurse" (exists)
├── ml_model.py            # Role "Machine Learning": training data, model training, evaluation, prediction
├── external_data.py       # Weather (Open-Meteo) and excursion destinations API functions
├── check_calculation.py   # (exists)
├── data/cities.csv        # City cost data, one row per city (filled in by the data person)
├── data/experiences.csv   # Training data: real monthly costs of former exchange students
├── database/exchange_costs.db
├── requirements.txt
├── README.md, CONTRIBUTIONS.md, AI_USAGE.md, DATA_SOURCES.md,
├── VIDEO_PLAN.md, TEST_CHECKLIST.md, REQUIREMENTS_AUDIT.md
```

Paths must work from any working directory: build them from
`os.path.dirname(os.path.abspath(__file__))`, with a short comment explaining why.

## 6. Data – honesty is essential

- **`data/cities.csv`**: columns exactly as in `SCHNITTSTELLEN.md`, plus `city`, `country`, `currency`,
  `latitude`, `longitude`, `university` (partner university in that city), `source` and `as_of_date`.
  Start with **15 cities** popular for HSG exchanges [FILL IN the team's city list, or let Claude propose
  15 and mark them as a proposal]. The team will fill in real prices. Until then put **clearly marked
  placeholder values** and set `source` to `"PLACEHOLDER – replace with real data"`. Never present
  placeholder or simulated numbers as real. The app must show a visible warning for every city whose
  source is a placeholder.
- **`data/experiences.csv`** (ML training data), one row per former exchange student:
  `city, housing_type, lifestyle, trips_per_month, monthly_cost_chf, source`. Real rows will come from
  our survey and from information extracted from the public HSG experience reports (numbers only, no
  copied text, no names). Until we have them, generate a **clearly labelled simulated** dataset
  (about 300 rows, fixed random seed, `source = "simulated"`) based on `calculation.py` plus realistic noise,
  and say so in the app, README and DATA_SOURCES.md.
- **`create_database.py`** loads both CSV files into SQLite (tables `cities`, `experiences`) and
  creates a third table `user_submissions` for the "Share your experience" form. Use `CREATE TABLE`,
  parameterized `INSERT` with `?`, and comments. Running it again must not delete `user_submissions`
  unless a `--reset` argument is given (or simply document clearly that it does).
- **`database.py`**: small functions such as `load_city_names()`, `load_city(name)` (returns a pandas
  Series, see SCHNITTSTELLEN.md), `load_all_cities()`, `load_training_data()` (experiences +
  user_submissions, joined with the city columns via SQL `JOIN`), `save_submission(...)`. Always use
  parameterized SQL for user input. Show at least SELECT, WHERE, ORDER BY, JOIN, INSERT, and GROUP BY
  where it is natural (e.g. average reported cost per city).
- **`DATA_SOURCES.md`**: every source, its date, what is real / placeholder / simulated, and licence or
  terms notes (Numbeo data must not be scraped or copied in bulk; prefer official university cost pages,
  student housing pages, public transport operators, and our own survey).

## 7. External APIs (`external_data.py`)

Every API call: `requests.get` with `timeout`, `try/except`, return `None` on failure, and the app shows
`st.warning` instead of crashing. Comment the HTTP request → JSON → Python dictionary → DataFrame steps.

1. **Weather during the stay** – Open-Meteo **historical/archive API** (free, no key): daily temperature
   and precipitation for the city for the **same months in the last 3 complete years**, averaged per
   month with pandas `groupby`. A forecast months ahead does not exist; say in the app that these are
   climate averages.
2. **Excursion destinations** – nearby sights and nature within a user-chosen radius (e.g. 20–200 km).
   Use a **free API without key** if possible (e.g. Wikipedia GeoSearch API or OpenStreetMap Overpass
   API) [FILL IN if the tutor/team decided on OpenTripMap]. If an API key is needed (OpenTripMap), read it
   from `st.secrets` with a fallback message when it is missing, never hard-code it, and add
   `.streamlit/secrets.toml` to `.gitignore`. Show the results on a map (`px.scatter_map` or
   `px.scatter_mapbox`/`st.map`) and as a table, filterable by category.
3. **Exchange rates** – already in `currency.py`.

## 8. Machine learning (`ml_model.py`)

- **Goal**: predict a person's **monthly cost in CHF** from features: city indicators from the `cities`
  table (e.g. rent for the chosen housing type, groceries, restaurant meal, transport pass) plus
  personal inputs (housing type, lifestyle, trips per month). One-hot encode text features with
  `pd.get_dummies` and align single-row inputs with `reindex(columns=..., fill_value=0)`, with comments.
- **Training**: `train_test_split(test_size=0.2, random_state=42)`; train **`LinearRegression`** and
  a **`RandomForestRegressor`** with modest settings (e.g. 100 trees, `random_state=42`); compare both
  with **MAE in CHF**; use the better one, but prefer LinearRegression if the difference is small
  (easier to explain). Show both MAE values in the app with a plain-English explanation of MAE.
- **Use in the app**: show the rule-based estimate (`calculation.py`) **and** the model's estimate
  ("based on real experiences of former students") side by side, with an honest note when the training
  data is simulated or small (state the number of training rows).
- New rows from the "Share your experience" page are included the next time the model is trained.
- Keep it to these two simple models: no hyperparameter search, no neural networks, no pipelines that
  the students cannot explain.
- [FILL IN tutor feedback from the coaching on whether this counts as "own ML model", e.g. "Tutor said: …"]

## 9. Pages and interaction (`app.py`)

Use sidebar navigation (`st.sidebar.radio`). Layout of the calculator agreed by the team: **inputs
left, monthly and total costs right, cost breakdown below**.

1. **Home / Problem** – problem, target group, how to use the app, where the data comes from, data honesty
   warnings.
2. **Cost calculator** (MVP) – city, start/end date, housing type, lifestyle, trips per month, extra flights
   home, optional budget → monthly costs, one-time costs, total, min–max range, local currency, budget
   check, ML estimate, donut/stacked bar chart of the categories, "How is this calculated?" expander.
3. **City comparison** – choose 2–3 cities with the same personal inputs → grouped bar chart of the
   total cost per category and a table; highlight the cheapest city.
4. **Weather & excursions** – climate chart (temperature line + precipitation bars per month of the stay)
   and the excursion map with radius and category filters.
5. **Share your experience** – form (`st.form`) where former exchange students enter city, housing,
   lifestyle, trips and their real monthly cost; validate input with widget limits; save with
   `INSERT`; show a thank-you message and the number of submissions per city (`GROUP BY`).
6. **About the model** – what is predicted, inputs, training data size and source, MAE of both models,
   predicted-vs-actual scatter, limitations.

Error handling at student level: missing database file → clear `st.error` with the command to run;
no data for a city → `st.info`; API down → `st.warning`; end date before start date → message and
`st.stop()`.

## 10. Priorities and timeline

Today is [FILL IN date]. The **MVP presentation is on 20 November** in the exercise group. Work in
this order and commit after each phase:

1. **MVP**: `create_database.py`, `database.py`, `app.py` with Home + Cost calculator (using
   `calculation.py`/`currency.py`), weather chart, first version of `ml_model.py`.
2. City comparison, excursions, Share your experience, About the model.
3. Documentation files (Section 11).
4. Self-audit and simplification (Section 12).

## 11. Documentation to create

- `README.md`: title, problem, target group, features, data sources and what is real/placeholder/simulated,
  ML method, installation (`pip install -r requirements.txt`), how to run
  (`streamlit run app.py`; on a Mac `python3 -m streamlit run app.py`), file structure with the role that
  owns each file, dependencies, limitations, AI-use note, and a mapping to requirements 1–8
  ("Requirement X – … / How fulfilled: …").
- `CONTRIBUTIONS.md`: contribution matrix **template** with roles App & Design, Daten & Datenbank,
  Berechnung & Wechselkurse, Machine Learning, Externe Daten/Präsentation [FILL IN names if known],
  clearly marked as a template that must reflect reality.
- `AI_USAGE.md`: honest description that Claude generated code and documentation, sections for the
  students to fill in (what they did themselves, reflection, list of other aids).
- `VIDEO_PLAN.md`: timed plan for max. 4:00 (problem, data, demo of every page, ML, teamwork and
  contributions, GenAI and aids, limitations, closing), voice-over by the students.
- `TEST_CHECKLIST.md`: simple manual tests (app starts, database loads, each page and chart works,
  filters change results, form saves data, API failure handled, fresh clone works).
- `REQUIREMENTS_AUDIT.md`: for each requirement 1–8 a status (PASS / NEEDS WORK) with evidence
  (file and function names), then a "course-level realism check": could a student after ~12 weeks
  explain the database, the APIs, the ML model and every chart? Simplify anything that is too advanced.

## 12. Verify before you finish

- Run `python check_calculation.py` – all checks must pass.
- Run `create_database.py` from a fresh state and start the app headlessly (e.g. Streamlit's
  `streamlit.testing.v1.AppTest`) to click through every page, including: no data, API failure
  (mock `requests.get` to raise), end date before start date, and a form submission. Fix every error.
  Do not commit test scripts unless they are as simple as `check_calculation.py`.
- Make sure no API key or secret is committed, and that `data/last_rates.json` stays ignored.
- `requirements.txt` must contain everything needed for Streamlit Community Cloud
  (streamlit, pandas, numpy, scikit-learn, plotly, requests).
- Commit with clear messages and push to the branch [FILL IN branch name].

At the end, give a short summary in German: files created, how to start the app on a Mac, which model
won and its MAE, which data is still placeholder or simulated, and the concrete manual steps the team
still has to do (fill in real city data, run the survey, add tutor feedback, record the video).
