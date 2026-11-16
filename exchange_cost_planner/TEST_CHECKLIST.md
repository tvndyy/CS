# Manual test checklist – Exchange Cost Planner

Tick each box after testing. Tester: ________ Date: ________

## Setup

- [ ] Fresh copy of the folder: `pip install -r requirements.txt` finishes without errors
- [ ] `python check_calculation.py` ends with "All 30 checks passed."
- [ ] `python create_database.py` prints "Saved 116 cities, 185 universities and 313 experiences …"
- [ ] `streamlit run app.py` opens the app without an error
- [ ] `python currency.py` (with internet) reports which currencies are supported

## Home / Problem

- [ ] Problem, target group and data sources are shown
- [ ] The data-honesty warning shows the number of placeholder cities and simulated rows
- [ ] The city table lists all cities

## Cost calculator

- [ ] Changing the city changes all numbers
- [ ] "Own apartment" costs more than "Student dormitory"; "comfortable" costs more than "frugal"
- [ ] More weekend trips and extra flights increase the total
- [ ] A longer stay increases the total; end date before start date shows an error (no crash)
- [ ] With internet: the amount in local currency and "live (ECB, date)" are shown
- [ ] Budget far above the total → green message; far below → red message with months covered
- [ ] The model estimate is shown next to the calculator estimate
- [ ] Donut chart, bar chart and cost table are shown; "How is this calculated?" opens
- [ ] A city with placeholder prices shows the yellow placeholder warning

## City comparison

- [ ] With one city: "Please choose at least two cities."
- [ ] With two or three cities: cheapest city message, two charts and the table
- [ ] A fourth city cannot be selected

## Weather & excursions

- [ ] With internet: temperature and rain charts show only the months of the stay, in the right order
      (test a stay from September to January)
- [ ] A city in the southern hemisphere (Sydney) is warm in January
- [ ] "Search excursion destinations" shows a map and a table; the category filter changes both
- [ ] Changing the city hides the old search result
- [ ] **API failure:** turn off Wi-Fi → yellow warnings, no crash

## Share your experience

- [ ] Submitting without the confirmation box shows an error
- [ ] Submitting with the box shows the thank-you message and the city appears in the table
- [ ] The number of training rows on "About the model" has increased by one
- [ ] The submission is still there after restarting the app

## About the model

- [ ] Both MAE values, the scatter chart and the per-city chart are shown
- [ ] The warning about simulated training rows is shown (until real data is in)
- [ ] The coefficient table is shown when the linear regression is used

## Error cases

- [ ] Rename `database/exchange_costs.db` → the app shows "database file … was not found" (rename it back)
- [ ] Empty one price cell in `data/cities.csv`, run `create_database.py` → the calculator warns
      "Missing data for this city" (restore the value afterwards)
- [ ] The app can be stopped (Ctrl + C) and started again
