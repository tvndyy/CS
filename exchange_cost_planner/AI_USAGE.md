# Use of generative AI – Exchange Cost Planner

The HSG rules on AI use, citation and the declaration of authorship apply to this project. This file
documents how GenAI was used. **The team must check every statement and adapt it to what really happened.**

## Tool

- **Claude** (Anthropic), used through Claude Code.

## What the AI did

| Area | Use |
|------|-----|
| Concept | Helped to compare project ideas, to refine the concept and to prepare questions for the coaching |
| Source code | **Generated the initial implementation of all Python files**: `app.py`, `database.py`, `create_database.py`, `calculation.py`, `currency.py`, `check_calculation.py`, `ml_model.py`, `external_data.py` |
| Data | Proposed the 15 cities and entered the **placeholder** prices; wrote the rules for the **simulated** training data |
| Documentation | Drafted README, DATA_SOURCES, SCHNITTSTELLEN, CONTRIBUTIONS, VIDEO_PLAN, TEST_CHECKLIST, REQUIREMENTS_AUDIT and this file |
| Testing | Ran automated tests of every page during development, including API failures |

The prompt that was given to the AI to build the app is stored in `PROMPT_FUER_FABLE.md`.

## Citation in the source code

Because AI-generated code is used in the project, it is cited in the code. Every Python file starts with:

```python
# AI assistance:
# Initial implementation developed with assistance from Claude.
# Students reviewed, tested, adapted and must document the exact use
# according to HSG course requirements.
```

When you change or rewrite a part yourselves, add a line such as
`# Function compare_with_budget rewritten by <name>` so that it stays clear which parts are your own work.

## What the students did (fill in honestly)

- _e.g. had the project idea and defined the concept and the roles_
- _e.g. researched the real city prices and replaced the placeholders_
- _e.g. ran the survey and replaced the simulated training data_
- _e.g. reviewed and tested every page with TEST_CHECKLIST.md_
- _e.g. changed the lifestyle assumptions / charts / texts_
- _e.g. can explain every function of their own module_

## Reflection (fill in, also for the video)

- What worked well with AI? _…_
- Where was the AI wrong or unhelpful? _…_
- What did we have to check or fix ourselves? _…_
- What did we learn about programming by reviewing generated code? _…_

## Other aids

- Streamlit, pandas, scikit-learn and Plotly documentation
- API documentation of Frankfurter, Open-Meteo and the OpenStreetMap Overpass API
- Lecture slides and exercises of the course
- _add further aids_
