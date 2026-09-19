from pathlib import Path

import pandas as pd
from flask import Flask, jsonify, request
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "crop_weather.csv"
REQUIRED_COLUMNS = ["Temperature", "Rainfall", "Humidity", "Soil_Type", "Crop"]
FEATURE_COLUMNS = REQUIRED_COLUMNS[:-1]

app = Flask(__name__)
model = None


@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response


def train_model():
    dataset = pd.read_csv(DATA_PATH)
    missing_columns = set(REQUIRED_COLUMNS) - set(dataset.columns)
    if missing_columns:
        raise ValueError(f"Dataset is missing columns: {sorted(missing_columns)}")

    dataset = dataset.dropna(subset=REQUIRED_COLUMNS)
    preprocessor = ColumnTransformer(
        transformers=[
            ("soil", OneHotEncoder(handle_unknown="ignore"), ["Soil_Type"]),
            ("weather", "passthrough", ["Temperature", "Rainfall", "Humidity"]),
        ]
    )
    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", RandomForestClassifier(n_estimators=240, random_state=42)),
        ]
    )
    pipeline.fit(dataset[FEATURE_COLUMNS], dataset["Crop"])
    return pipeline, dataset


model, dataset = train_model()


@app.get("/")
def home():
    return jsonify({
        "service": "crop recommendation API",
        "status": "ok",
        "recommendation_endpoint": "/api/recommend",
    })


@app.get("/api/health")
def health():
    return jsonify({"status": "ok", "rows": len(dataset), "crops": dataset["Crop"].nunique()})


@app.post("/api/recommend")
def recommend():
    payload = request.get_json(silent=True) or {}
    try:
        temperature = float(payload["Temperature"])
        rainfall = float(payload["Rainfall"])
        humidity = float(payload["Humidity"])
        soil_type = str(payload["Soil_Type"]).strip()
        if not soil_type:
            raise ValueError("Soil type is required")
    except (KeyError, TypeError, ValueError) as error:
        return jsonify({"error": f"Please enter valid weather values and soil type. {error}"}), 400

    if not -20 <= temperature <= 60 or not 0 <= rainfall <= 1000 or not 0 <= humidity <= 100:
        return jsonify({"error": "Use realistic ranges: temperature -20 to 60 C, rainfall 0 to 1000 mm, humidity 0 to 100%."}), 400

    features = pd.DataFrame(
        [{
            "Temperature": temperature,
            "Rainfall": rainfall,
            "Humidity": humidity,
            "Soil_Type": soil_type,
        }]
    )
    probabilities = model.predict_proba(features)[0]
    best_index = probabilities.argmax()
    crop = model.classes_[best_index]
    confidence = round(float(probabilities[best_index]) * 100, 1)
    alternatives = sorted(
        zip(model.classes_, probabilities), key=lambda item: item[1], reverse=True
    )[1:4]

    return jsonify({
        "crop": crop,
        "confidence": confidence,
        "alternatives": [
            {"crop": name, "confidence": round(float(score) * 100, 1)}
            for name, score in alternatives
        ],
    })


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
