# Video plan – Exchange Cost Planner (maximum 4:00)

> The voice-over **must be recorded by the students themselves** (no generated audio).
> Before recording: check the internet connection (exchange rate, weather and excursions are live),
> start the app, and open the "Weather & excursions" page once so the data is already loaded.

| Time | Section | On screen | Key points to say | Speaker |
|------|---------|-----------|-------------------|---------|
| 0:00–0:25 | **Problem and target group** | Home / Problem | Students do not know what an exchange semester really costs; information is scattered. Our app gives a personal estimate per city. | Person 3 |
| 0:25–0:50 | **Data and technology** | Home: "Where does the data come from?" | SQLite database with three tables, read with SQL. Three APIs: HTTP request → JSON → DataFrame. Say honestly which data is real, placeholder or simulated. | Person 2 |
| 0:50–1:35 | **Demo: Cost calculator** | Choose a city, change housing and lifestyle, enter a budget | Costs per month and for the stay, range, local currency (live rate), budget check, cost breakdown charts. | Person 1 |
| 1:35–1:55 | **Demo: City comparison** | Compare three cities | The app names the cheapest city and shows where the difference comes from. | Person 1 |
| 1:55–2:20 | **Demo: Weather & excursions** | Climate charts, search excursions, filter a category | Climate averages instead of a forecast; map of places nearby from OpenStreetMap. | Person 5 |
| 2:20–2:40 | **Demo: Share your experience** | Submit one answer, show the table | The form writes into the database (`INSERT`); the new row is used for the next training. | Person 2 |
| 2:40–3:10 | **Machine learning** | About the model | We train two models ourselves (`model.fit`), compare them with MAE and explain which one we use and why. State the MAE and the size of the training data. | Person 4 |
| 3:10–3:35 | **Teamwork and contributions** | Slide: contribution matrix | Who did what, how we organised the work, one challenge and how we solved it. | Person 5 |
| 3:35–3:55 | **GenAI, aids and limitations** | Slide: list of aids + the `# AI assistance:` comment | What Claude generated, what we checked and changed, what we learned. Limitations: estimates only, data quality. | Person 4 |
| 3:55–4:00 | **Closing** | Home | Thank you, questions welcome. | All |

## Checklist before uploading

- [ ] The video is 4:00 or shorter
- [ ] Every team member speaks
- [ ] The contribution matrix is shown (requirement 7)
- [ ] GenAI use and the list of aids are shown (requirement 7)
- [ ] Data honesty is mentioned (which data is real / placeholder / simulated)
- [ ] The demo shows at least one input change, one chart and one model result
- [ ] The voice-over is recorded by the students, not generated
- [ ] The video file itself is uploaded to Canvas (a link alone is not sufficient)
