# Fieldwise crop recommendation system

A small Flask + scikit-learn application that recommends a crop from temperature, rainfall, humidity, and soil type.

## Run locally

```powershell
cd ML_MODEL
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
py app.py
```

Open http://127.0.0.1:5000.

## Dataset

The model reads `data/crop_weather.csv` at startup. Replace it with a larger Kaggle or Google dataset as long as it keeps these columns:

- `Temperature`
- `Rainfall`
- `Humidity`
- `Soil_Type`
- `Crop`

The pipeline one-hot encodes soil type and trains a random forest classifier on every startup.

## API

`POST /api/recommend` accepts JSON such as:

```json
{"Temperature": 26, "Rainfall": 145, "Humidity": 72, "Soil_Type": "Loamy"}
```
