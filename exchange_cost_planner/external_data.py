"""
external_data.py - Exchange Cost Planner

Data that we load live from two free online APIs (no API key needed):

1. Open-Meteo archive API  -> climate during the exchange semester
2. OpenStreetMap Overpass API -> excursion destinations near the city

Both functions return None if the request fails (no internet, server
down, timeout). The app then shows a warning instead of crashing.
"""

# AI assistance:
# Initial implementation developed with assistance from Claude.
# Students reviewed, tested, adapted and must document the exact use
# according to HSG course requirements.

import math
from datetime import date

import pandas as pd
import requests

MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

NUMBER_OF_CLIMATE_YEARS = 3   # we average the weather of the last 3 complete years
MAXIMUM_PLACES = 150          # do not load more excursion destinations than this


# ---------------------------------------------------------------------------
# 1. Climate (Open-Meteo)
# ---------------------------------------------------------------------------
def get_monthly_climate(latitude, longitude):
    """Average temperature and rain per month for a place.

    A real weather forecast for a semester that starts in several months
    does not exist. Instead we look at what the weather was like in the
    last 3 complete years and average it per month ("climate").

    How it works:
    1. Our app sends an HTTP GET request with the coordinates and dates.
    2. The Open-Meteo server answers with JSON: one value per day.
    3. response.json() turns the JSON text into a Python dictionary,
       which we put into a pandas DataFrame and summarise per month.

    Returns a DataFrame with 12 rows (month, month_name, temperature_c,
    rain_mm) or None if the request fails.
    """
    last_complete_year = date.today().year - 1
    first_year = last_complete_year - NUMBER_OF_CLIMATE_YEARS + 1

    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": f"{first_year}-01-01",
        "end_date": f"{last_complete_year}-12-31",
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
        "timezone": "auto",
    }

    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()  # error if the status code is 4xx or 5xx
        data = response.json()
        daily = pd.DataFrame({
            "date": pd.to_datetime(data["daily"]["time"]),
            "temp_max": data["daily"]["temperature_2m_max"],
            "temp_min": data["daily"]["temperature_2m_min"],
            "rain_mm": data["daily"]["precipitation_sum"],
        })
    except Exception:
        return None

    # Daily mean temperature = average of the daily maximum and minimum
    daily["temperature_c"] = (daily["temp_max"] + daily["temp_min"]) / 2
    daily["month"] = daily["date"].dt.month

    # Data wrangling: about 1,100 daily rows -> 12 monthly rows
    temperature_per_month = daily.groupby("month")["temperature_c"].mean()
    # Rain: total of all days of that month over 3 years, divided by 3 = rain in an average month
    rain_per_month = daily.groupby("month")["rain_mm"].sum() / NUMBER_OF_CLIMATE_YEARS

    climate = pd.DataFrame({
        "month": temperature_per_month.index,
        "temperature_c": temperature_per_month.values.round(1),
        "rain_mm": rain_per_month.values.round(0),
    })
    climate["month_name"] = [MONTH_NAMES[number - 1] for number in climate["month"]]
    return climate


# ---------------------------------------------------------------------------
# 2. Excursion destinations (OpenStreetMap)
# ---------------------------------------------------------------------------
def distance_km(latitude_1, longitude_1, latitude_2, longitude_2):
    """Distance between two places on Earth in km ("haversine" formula).

    The Earth is a sphere, so we cannot simply use Pythagoras with the
    coordinates. This standard formula gives the distance as the crow flies.
    """
    earth_radius_km = 6371
    lat_1 = math.radians(latitude_1)
    lat_2 = math.radians(latitude_2)
    difference_lat = math.radians(latitude_2 - latitude_1)
    difference_lon = math.radians(longitude_2 - longitude_1)

    a = math.sin(difference_lat / 2) ** 2 + math.cos(lat_1) * math.cos(lat_2) * math.sin(difference_lon / 2) ** 2
    return 2 * earth_radius_km * math.asin(math.sqrt(a))


def find_category(tags):
    """Translate the OpenStreetMap tags of a place into one of our categories."""
    if tags.get("tourism") == "museum":
        return "Museum"
    if tags.get("tourism") == "viewpoint":
        return "Viewpoint"
    if tags.get("natural") in ["peak", "beach"] or tags.get("leisure") == "nature_reserve":
        return "Nature"
    return "Sight"


def get_nearby_places(latitude, longitude, radius_km):
    """Sights, museums, viewpoints and nature within radius_km of a place.

    We ask the Overpass API, a free search service for OpenStreetMap data.
    The request contains a small query text: "give me all places with these
    tags around this point". To get only well-known places we ask for
    places that have a Wikipedia article (the tag "wikipedia").

    Returns a DataFrame (name, category, latitude, longitude, distance_km),
    which can be empty, or None if the request fails.
    """
    radius_m = int(radius_km * 1000)
    around = f"(around:{radius_m},{latitude},{longitude})"

    # nwr = nodes, ways and relations (points, outlines and groups on the map)
    query = f"""
        [out:json][timeout:25];
        (
          nwr["tourism"~"^(attraction|museum|viewpoint)$"]["wikipedia"]["name"]{around};
          nwr["natural"~"^(peak|beach)$"]["wikipedia"]["name"]{around};
          nwr["leisure"="nature_reserve"]["wikipedia"]["name"]{around};
        );
        out center {MAXIMUM_PLACES};
    """

    try:
        response = requests.get(
            "https://overpass-api.de/api/interpreter",
            params={"data": query},
            headers={"User-Agent": "ExchangeCostPlanner (university student project)"},
            timeout=30,
        )
        response.raise_for_status()
        elements = response.json()["elements"]
    except Exception:
        return None

    # Convert the JSON list into rows for a table
    rows = []
    for element in elements:
        tags = element.get("tags", {})

        # Points have "lat"/"lon" directly; outlines have them inside "center"
        if "lat" in element:
            place_latitude = element["lat"]
            place_longitude = element["lon"]
        elif "center" in element:
            place_latitude = element["center"]["lat"]
            place_longitude = element["center"]["lon"]
        else:
            continue  # no position -> we cannot show it on the map

        rows.append({
            "name": tags.get("name", "unknown"),
            "category": find_category(tags),
            "latitude": place_latitude,
            "longitude": place_longitude,
            "distance_km": round(distance_km(latitude, longitude, place_latitude, place_longitude), 1),
        })

    places = pd.DataFrame(rows, columns=["name", "category", "latitude", "longitude", "distance_km"])

    # Data cleaning: the same place can appear twice (as point and as outline)
    places = places.drop_duplicates(subset="name")
    places = places.sort_values("distance_km")
    return places

def get_inflation_factor(iso3):
    """How much consumer prices rose from Dec 2022 to 2026 (IMF DataMapper API, no key).
    Returns e.g. 1.12 for +12 %, or None if the API cannot be reached."""
    try:
        url = f"https://www.imf.org/external/datamapper/api/v1/PCPIPCH/{iso3}"
        rates = requests.get(url, timeout=5).json()["values"]["PCPIPCH"][iso3]
        factor = 1.0
        for year in ["2023", "2024", "2025", "2026"]:
            factor = factor * (1 + rates.get(year, 0) / 100)
        return factor
    except Exception:
        return None

