import csv
import json
import os
import subprocess
from pathlib import Path

from flask import Flask, jsonify, request

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "crop_weather.csv"
REQUIRED_COLUMNS = ["Temperature", "Rainfall", "Humidity", "Soil_Type", "Crop"]
FEATURE_COLUMNS = REQUIRED_COLUMNS[:-1]
RSCRIPT_PATH = os.environ.get("RSCRIPT_PATH", "Rscript")

app = Flask(__name__)
model = None


@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response


def load_dataset():
    with DATA_PATH.open(newline="", encoding="utf-8") as data_file:
        rows = list(csv.DictReader(data_file))
    missing_columns = set(REQUIRED_COLUMNS) - set(rows[0])
    if missing_columns:
        raise ValueError(f"Dataset is missing columns: {sorted(missing_columns)}")
    return rows


dataset = load_dataset()
soil_types = sorted({row["Soil_Type"] for row in dataset})


@app.get("/")
def home():
    return jsonify({
        "service": "crop recommendation API",
        "status": "ok",
        "recommendation_endpoint": "/api/recommend",
        "model": "R randomForest",
    })


@app.get("/api/health")
def health():
    return jsonify({"status": "ok", "rows": len(dataset), "crops": len({row['Crop'] for row in dataset}), "model": "R randomForest"})


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

    if soil_type not in soil_types:
        return jsonify({"error": f"Choose one of these soil types: {', '.join(soil_types)}"}), 400

    payload = json.dumps({
        "Temperature": temperature,
        "Rainfall": rainfall,
        "Humidity": humidity,
        "Soil_Type": soil_type,
    })
    try:
        prediction = subprocess.run(
            [RSCRIPT_PATH, str(BASE_DIR / "model.R"), str(DATA_PATH)],
            input=payload,
            text=True,
            capture_output=True,
            check=True,
        )
        return jsonify(json.loads(prediction.stdout))
    except (OSError, subprocess.CalledProcessError, json.JSONDecodeError) as error:
        return jsonify({"error": f"R model could not make a prediction: {error}"}), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
