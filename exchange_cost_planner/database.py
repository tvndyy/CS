"""
database.py - Exchange Cost Planner

Role: "Daten & Datenbank"

All SQL queries of the app are in this file. The other modules never talk
to SQLite directly - they call these functions and get pandas objects back.

Tables (created by create_database.py):
- cities            one row per city, cost data in CHF
- experiences       monthly costs of former exchange students (ML training data)
- user_submissions  answers entered on the page "Share your experience"
"""

# AI assistance:
# Initial implementation developed with assistance from Claude.
# Students reviewed, tested, adapted and must document the exact use
# according to HSG course requirements.

import os
import sqlite3
from datetime import date

import pandas as pd

# Build the path relative to THIS file, so it works from any folder
PROJECT_FOLDER = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(PROJECT_FOLDER, "database", "exchange_costs.db")


# ---------------------------------------------------------------------------
# Basic helpers
# ---------------------------------------------------------------------------
def database_exists():
    return os.path.exists(DATABASE_PATH)


def run_query(sql, parameters=()):
    """Run a SELECT statement and return the result as a DataFrame."""
    connection = sqlite3.connect(DATABASE_PATH)
    result = pd.read_sql_query(sql, connection, params=parameters)
    connection.close()
    return result


def run_change(sql, parameters=()):
    """Run an INSERT statement and save (commit) the change."""
    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()
    cursor.execute(sql, parameters)
    connection.commit()
    connection.close()


# ---------------------------------------------------------------------------
# Cities
# ---------------------------------------------------------------------------
def load_city_names():
    """Alphabetical list of all city names (for the dropdowns)."""
    cities = run_query("SELECT city FROM cities ORDER BY city")
    return list(cities["city"])


def load_city_names_with_prices():
    """Only the cities for which we already have a complete set of monthly prices.

    Many partner-university cities are in the database without prices.
    They can be used for the weather page, but not for a cost comparison.
    """
    cities = run_query("""
        SELECT city FROM cities
        WHERE rent_shared_room IS NOT NULL AND rent_dorm IS NOT NULL AND rent_apartment IS NOT NULL
          AND groceries_month IS NOT NULL AND restaurant_meal IS NOT NULL
          AND evening_out IS NOT NULL AND transport_pass IS NOT NULL
        ORDER BY city
    """)
    return list(cities["city"])


def load_city(city_name):
    """All data of ONE city as a pandas Series, or None if the city is unknown.

    The city name comes from the user, so we pass it as a parameter (?)
    instead of pasting it into the SQL text. This prevents SQL injection.
    """
    result = run_query("SELECT * FROM cities WHERE city = ?", (city_name,))
    if result.empty:
        return None
    return result.iloc[0]


def load_all_cities():
    return run_query("SELECT * FROM cities ORDER BY city")


# ---------------------------------------------------------------------------
# Partner universities
# ---------------------------------------------------------------------------
def load_universities():
    """All HSG partner universities with their city, sorted by country and city.

    JOIN: the currency is stored in the table cities, so we combine the
    two tables on the city name.
    """
    return run_query("""
        SELECT universities.university, universities.city, universities.country,
               cities.currency, universities.reports_in_portal, universities.last_report_year
        FROM universities
        JOIN cities ON universities.city = cities.city
        ORDER BY universities.country, universities.city, universities.university
    """)


def load_universities_in_city(city_name):
    """Names of the partner universities in ONE city (WHERE with a parameter)."""
    result = run_query(
        "SELECT university FROM universities WHERE city = ? ORDER BY university", (city_name,)
    )
    return list(result["university"])


def count_universities_per_country():
    """GROUP BY: how many partner universities each country has."""
    return run_query("""
        SELECT country, COUNT(*) AS number_of_universities
        FROM universities
        GROUP BY country
        ORDER BY number_of_universities DESC, country
    """)


# ---------------------------------------------------------------------------
# Training data for the ML model
# ---------------------------------------------------------------------------
def load_training_data():
    """All reported monthly costs together with the price data of their city.

    JOIN: each experience row only stores the city name. The prices of that
    city (rent, groceries, ...) are in the table cities, so we combine the
    two tables on the city name.

    Answers from the app (user_submissions) are added to the experiences,
    so the model also learns from them.
    """
    experiences = run_query("""
        SELECT experiences.city, experiences.housing_type, experiences.lifestyle,
               experiences.trips_per_month, experiences.monthly_cost_chf, experiences.source,
               cities.rent_shared_room, cities.rent_dorm, cities.rent_apartment,
               cities.groceries_month, cities.restaurant_meal, cities.evening_out,
               cities.transport_pass
        FROM experiences
        JOIN cities ON experiences.city = cities.city
    """)

    submissions = run_query("""
        SELECT user_submissions.city, user_submissions.housing_type, user_submissions.lifestyle,
               user_submissions.trips_per_month, user_submissions.monthly_cost_chf,
               'app submission' AS source,
               cities.rent_shared_room, cities.rent_dorm, cities.rent_apartment,
               cities.groceries_month, cities.restaurant_meal, cities.evening_out,
               cities.transport_pass
        FROM user_submissions
        JOIN cities ON user_submissions.city = cities.city
    """)

    if submissions.empty:
        training_data = experiences
    else:
        # Stack the two tables on top of each other
        training_data = pd.concat([experiences, submissions], ignore_index=True)

    # Data cleaning: a report from a city without prices cannot be used for
    # training, because the model needs the prices as inputs
    price_columns = ["rent_shared_room", "rent_dorm", "rent_apartment", "groceries_month",
                     "restaurant_meal", "evening_out", "transport_pass"]
    training_data = training_data.dropna(subset=price_columns).reset_index(drop=True)
    return training_data


def count_training_rows_by_source():
    """How many training rows come from which source (e.g. simulated / survey)."""
    return run_query("""
        SELECT source, COUNT(*) AS number_of_rows
        FROM experiences
        GROUP BY source
        ORDER BY number_of_rows DESC
    """)


def average_reported_cost_per_city():
    """GROUP BY: average monthly cost that students reported, per city."""
    return run_query("""
        SELECT city,
               COUNT(*) AS number_of_reports,
               ROUND(AVG(monthly_cost_chf), 0) AS average_monthly_cost_chf
        FROM experiences
        GROUP BY city
        ORDER BY average_monthly_cost_chf DESC
    """)


# ---------------------------------------------------------------------------
# "Share your experience"
# ---------------------------------------------------------------------------
def save_submission(city, housing_type, lifestyle, trips_per_month, monthly_cost_chf):
    """Store one answer from the form in the table user_submissions."""
    run_change(
        """INSERT INTO user_submissions (city, housing_type, lifestyle, trips_per_month,
                                         monthly_cost_chf, submitted_on)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (city, housing_type, lifestyle, int(trips_per_month), float(monthly_cost_chf), str(date.today())),
    )


def count_submissions_per_city():
    """GROUP BY: number of app submissions and their average cost, per city."""
    return run_query("""
        SELECT city,
               COUNT(*) AS number_of_submissions,
               ROUND(AVG(monthly_cost_chf), 0) AS average_monthly_cost_chf
        FROM user_submissions
        GROUP BY city
        ORDER BY number_of_submissions DESC, city
    """)
