# Crop recommendation API

This branch contains the Flask API and the R machine-learning model.

## Setup

```powershell
pip install -r requirements.txt
Rscript -e "install.packages(c('jsonlite', 'randomForest'), repos='https://cloud.r-project.org')"
py app.py
```

The API reads `data/crop_weather.csv`. Flask validates requests and calls `model.R`, which trains a random forest in R and returns the recommended crop with confidence and alternatives.

`POST /api/recommend` expects:

```json
{"Temperature": 26, "Rainfall": 141, "Humidity": 72, "Soil_Type": "Loamy"}
```
