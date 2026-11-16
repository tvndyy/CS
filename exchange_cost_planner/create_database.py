"""
create_database.py - Exchange Cost Planner

Role: "Daten & Datenbank"

Run this script to build the SQLite database used by the app:

    python create_database.py

It reads three CSV files and stores them in database/exchange_costs.db:

1. data/cities.csv        -> table "cities"        (cost data per city, all amounts in CHF)
2. data/universities.csv  -> table "universities"  (HSG partner universities and their city)
3. data/experiences.csv   -> table "experiences"   (monthly costs of former exchange students,
                                                    the training data for our ML model)

It also creates the empty table "user_submissions" for the page
"Share your experience". This table is NOT deleted when the script runs
again, so answers entered in the app are kept.

IMPORTANT - data honesty:
- The prices in data/cities.csv are PLACEHOLDERS until the team replaces
  them with researched values (see DATA_SOURCES.md). Many cities have no
  prices at all yet (empty cells).
- If data/experiences.csv does not exist, this script creates a SIMULATED
  file, clearly labelled with source = "simulated". Replace it with real
  survey answers as soon as we have them.
"""

# AI assistance:
# Initial implementation developed with assistance from Claude.
# Students reviewed, tested, adapted and must document the exact use
# according to HSG course requirements.

import os
import sqlite3

import numpy as np
import pandas as pd

from calculation import HOUSING_COLUMNS, LIFESTYLES, calculate_monthly_costs

# Build paths relative to THIS file, so the script works from any folder
PROJECT_FOLDER = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(PROJECT_FOLDER, "database", "exchange_costs.db")
CITIES_CSV = os.path.join(PROJECT_FOLDER, "data", "cities.csv")
UNIVERSITIES_CSV = os.path.join(PROJECT_FOLDER, "data", "universities.csv")
EXPERIENCES_CSV = os.path.join(PROJECT_FOLDER, "data", "experiences.csv")

NUMBER_OF_SIMULATED_ROWS = 300

PRICE_COLUMNS = ["rent_shared_room", "rent_dorm", "rent_apartment", "groceries_month",
                 "restaurant_meal", "evening_out", "transport_pass"]


# ---------------------------------------------------------------------------
# Simulated training data (only used until we have real survey answers)
# ---------------------------------------------------------------------------
def simulate_experiences(cities):
    """Create fictional "experience reports" of former exchange students.

    For each fictional student we pick a random city, housing type, lifestyle
    and number of trips, calculate the monthly cost with our own cost
    calculator and add random noise, because real people never spend
    exactly what a formula says.
    """
    # Fixed seed -> every team member gets exactly the same simulated data
    rng = np.random.default_rng(seed=2026)

    # Only cities with a complete set of prices can be simulated
    cities = cities.dropna(subset=PRICE_COLUMNS).reset_index(drop=True)
    housing_types = list(HOUSING_COLUMNS.keys())
    lifestyles = list(LIFESTYLES.keys())

    rows = []
    for i in range(NUMBER_OF_SIMULATED_ROWS):
        city = cities.iloc[rng.integers(len(cities))]
        housing_type = housing_types[rng.integers(len(housing_types))]
        lifestyle = lifestyles[rng.integers(len(lifestyles))]
        trips_per_month = int(rng.integers(0, 5))

        monthly_costs = calculate_monthly_costs(city, housing_type, lifestyle, trips_per_month)
        expected_cost = sum(monthly_costs.values())

        # Real spending differs from the formula: on average +/- 12 %
        real_cost = expected_cost * rng.normal(1.0, 0.12)

        rows.append({
            "city": city["city"],
            "housing_type": housing_type,
            "lifestyle": lifestyle,
            "trips_per_month": trips_per_month,
            "monthly_cost_chf": int(round(real_cost, -1)),  # round to CHF 10
            "source": "simulated",
        })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Building the database
# ---------------------------------------------------------------------------
def create_tables(cursor):
    # cities, universities and experiences are rebuilt from the CSV files every time
    cursor.execute("DROP TABLE IF EXISTS cities")
    cursor.execute("DROP TABLE IF EXISTS universities")
    cursor.execute("DROP TABLE IF EXISTS experiences")

    cursor.execute("""
        CREATE TABLE cities (
            city TEXT PRIMARY KEY,
            country TEXT,
            currency TEXT,
            latitude REAL,
            longitude REAL,
            rent_shared_room REAL,
            rent_dorm REAL,
            rent_apartment REAL,
            groceries_month REAL,
            restaurant_meal REAL,
            evening_out REAL,
            transport_pass REAL,
            flight_return REAL,
            visa_fee REAL,
            source TEXT,
            as_of_date TEXT
        )
    """)

    # One city can have several partner universities, so they get their own
    # table. The column city links each university to its row in cities.
    cursor.execute("""
        CREATE TABLE universities (
            university TEXT PRIMARY KEY,
            city TEXT,
            country TEXT,
            portal_location TEXT,
            reports_in_portal INTEGER,
            last_report_year TEXT,
            FOREIGN KEY (city) REFERENCES cities(city)
        )
    """)

    cursor.execute("""
        CREATE TABLE experiences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city TEXT,
            housing_type TEXT,
            lifestyle TEXT,
            trips_per_month INTEGER,
            monthly_cost_chf REAL,
            source TEXT,
            FOREIGN KEY (city) REFERENCES cities(city)
        )
    """)

    # IF NOT EXISTS: answers entered in the app survive a rebuild of the database
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city TEXT,
            housing_type TEXT,
            lifestyle TEXT,
            trips_per_month INTEGER,
            monthly_cost_chf REAL,
            submitted_on TEXT,
            FOREIGN KEY (city) REFERENCES cities(city)
        )
    """)


def none_if_missing(value):
    """Empty CSV cells are NaN in pandas. SQLite should store them as NULL (None)."""
    if pd.isna(value):
        return None
    return value



def insert_cities(cursor, cities):
    for index, row in cities.iterrows():
        values = []
        for column in [
            "city", "country", "currency", "latitude", "longitude",
            "rent_shared_room", "rent_dorm", "rent_apartment",
            "groceries_month", "restaurant_meal", "evening_out",
            "transport_pass", "flight_return", "visa_fee",
            "source", "as_of_date"
        ]:
            values.append(none_if_missing(row[column]))

        # Insert cities into database
        cursor.execute(
            """INSERT INTO cities (city, country, currency, latitude, longitude,
                                   rent_shared_room, rent_dorm, rent_apartment, groceries_month,
                                   restaurant_meal, evening_out, transport_pass, flight_return,
                                   visa_fee, source, as_of_date)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            values,
        )



def insert_universities(cursor, universities):
    for index, row in universities.iterrows():
        cursor.execute(
            """INSERT INTO universities (university, city, country, portal_location,
                                         reports_in_portal, last_report_year)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (row["university"], row["city"], row["country"], none_if_missing(row["portal_location"]),
             int(none_if_missing(row["reports_in_portal"]) or 0), row["last_report_year"]),
        )


def insert_experiences(cursor, experiences):
    for index, row in experiences.iterrows():
        cursor.execute(
            """INSERT INTO experiences (city, housing_type, lifestyle, trips_per_month,
                                        monthly_cost_chf, source)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (row["city"], row["housing_type"], row["lifestyle"], int(row["trips_per_month"]),
             float(row["monthly_cost_chf"]), row["source"]),
        )


if __name__ == "__main__":
    # --- Load the city data ---
    cities = pd.read_csv(CITIES_CSV)
    print("Loaded", len(cities), "cities from data/cities.csv")

    number_of_placeholders = int(cities["source"].str.startswith("PLACEHOLDER").sum())
    if number_of_placeholders > 0:
        print("WARNING:", number_of_placeholders, "cities still have PLACEHOLDER prices.")
    number_without_prices = int(cities[PRICE_COLUMNS].isna().any(axis=1).sum())
    print(number_without_prices, "of these cities have no prices at all yet.")

    # --- Load the partner universities ---
    universities = pd.read_csv(UNIVERSITIES_CSV)
    # Data cleaning: every university must belong to a city we know
    universities = universities[universities["city"].isin(list(cities["city"]))]
    print("Loaded", len(universities), "universities from data/universities.csv")

    # --- Load (or simulate) the experience data ---
    if os.path.exists(EXPERIENCES_CSV):
        experiences = pd.read_csv(EXPERIENCES_CSV)
        print("Loaded", len(experiences), "experience rows from data/experiences.csv")
    else:
        experiences = simulate_experiences(cities)
        experiences.to_csv(EXPERIENCES_CSV, index=False)
        print("data/experiences.csv not found -> created", len(experiences), "SIMULATED rows")

    # Data cleaning: only keep experiences for cities we know, with a cost above 0
    known_cities = list(cities["city"])
    experiences = experiences[experiences["city"].isin(known_cities)]
    experiences = experiences[experiences["monthly_cost_chf"] > 0]

    # --- Write everything into SQLite ---
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    create_tables(cursor)
    insert_cities(cursor, cities)
    insert_universities(cursor, universities)
    insert_experiences(cursor, experiences)

    connection.commit()
    connection.close()
    print("Saved", len(cities), "cities,", len(universities), "universities and", len(experiences),
          "experiences to", DATABASE_PATH)
