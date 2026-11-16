"""
ml_model.py - Exchange Cost Planner

Role: "Machine Learning"

We train our OWN model that predicts the monthly cost (CHF) of an exchange
student. The training data are the reported monthly costs of former
exchange students (tables experiences + user_submissions), combined with
the price data of their city.

Functions:
- create_features():        turn the training table into numbers
- train_models():           train LinearRegression and RandomForest, compare them with MAE
- predict_monthly_cost():   use the chosen model for the user's plan
"""

# AI assistance:
# Initial implementation developed with assistance from Claude.
# Students reviewed, tested, adapted and must document the exact use
# according to HSG course requirements.

import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split

from calculation import HOUSING_COLUMNS

# Price columns of the city that the model uses as inputs
CITY_PRICE_COLUMNS = ["groceries_month", "restaurant_meal", "evening_out", "transport_pass"]

# With fewer rows than this we do not train a model (the result would be meaningless)
MINIMUM_TRAINING_ROWS = 30


def create_features(data):
    """Return a table with only numbers - the inputs (features) of the model.

    `data` needs the columns housing_type, lifestyle, trips_per_month and
    the city price columns. Works for the whole training table and for a
    single row (the user's plan).
    """
    features = pd.DataFrame(index=data.index)

    # The rent that matters depends on the housing type of each person:
    # e.g. "Shared flat room" -> column rent_shared_room
    rents = []
    for index, row in data.iterrows():
        rent_column = HOUSING_COLUMNS[row["housing_type"]]
        rents.append(row[rent_column])
    features["rent"] = rents

    for column in CITY_PRICE_COLUMNS:
        features[column] = data[column]
    features["trips_per_month"] = data["trips_per_month"]

    # Data cleaning: missing prices count as 0, so the model can still calculate
    features = features.astype(float).fillna(0)

    # Text columns -> 0/1 columns ("one-hot encoding"),
    # e.g. lifestyle_frugal = 1 if the person lives frugally, otherwise 0
    dummies = pd.get_dummies(data[["lifestyle", "housing_type"]], dtype=int)
    features = pd.concat([features, dummies], axis=1)
    return features


def train_models(training_data):
    """Train two models and choose one. Returns a dictionary, or None if
    there is not enough training data.

    Keys of the result: model, model_name, feature_columns, mae (of the chosen
    model), mae_linear, mae_forest, test_results, number_of_rows
    """
    if len(training_data) < MINIMUM_TRAINING_ROWS:
        return None

    X = create_features(training_data)
    y = training_data["monthly_cost_chf"]

    # 80 % of the reports are used for training, 20 % are kept aside.
    # The models never see the test rows, so they show how well the
    # models work for new students.
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # --- Model 1: linear regression (one coefficient per input) ---
    linear_model = LinearRegression()
    linear_model.fit(X_train, y_train)
    linear_predictions = linear_model.predict(X_test)
    mae_linear = mean_absolute_error(y_test, linear_predictions)

    # --- Model 2: random forest (100 decision trees, their answers are averaged) ---
    forest_model = RandomForestRegressor(n_estimators=100, random_state=42)
    forest_model.fit(X_train, y_train)
    forest_predictions = forest_model.predict(X_test)
    mae_forest = mean_absolute_error(y_test, forest_predictions)

    # --- Choose: the linear model is easier to explain, so the random forest
    # is only used if it is clearly better (at least 10 % smaller error) ---
    if mae_forest < 0.9 * mae_linear:
        chosen_model = forest_model
        model_name = "Random forest"
        chosen_predictions = forest_predictions
        chosen_mae = mae_forest
    else:
        chosen_model = linear_model
        model_name = "Linear regression"
        chosen_predictions = linear_predictions
        chosen_mae = mae_linear

    test_results = pd.DataFrame({
        "actual_cost": y_test,
        "predicted_cost": chosen_predictions,
    })

    return {
        "model": chosen_model,
        "model_name": model_name,
        "feature_columns": list(X.columns),
        "mae_linear": mae_linear,
        "mae_forest": mae_forest,
        "mae": chosen_mae,
        "test_results": test_results,
        "number_of_rows": len(training_data),
    }


def predict_monthly_cost(trained, city, housing_type, lifestyle, trips_per_month):
    """Predict the monthly cost in CHF for ONE plan.

    trained - the dictionary returned by train_models()
    city    - one row of the cities table (pandas Series or dict)
    """
    # Build a table with one row that looks like the training data
    plan = {
        "housing_type": housing_type,
        "lifestyle": lifestyle,
        "trips_per_month": trips_per_month,
    }
    for column in list(HOUSING_COLUMNS.values()) + CITY_PRICE_COLUMNS:
        plan[column] = city[column]
    plan_table = pd.DataFrame([plan])

    features = create_features(plan_table)

    # For one row, get_dummies only creates the columns for ITS values
    # (e.g. only lifestyle_frugal). reindex adds the other training columns
    # filled with 0, so the columns match exactly what the model learned.
    features = features.reindex(columns=trained["feature_columns"], fill_value=0)

    prediction = trained["model"].predict(features)[0]
    return max(0, round(prediction))
