# Crop recommendation project

The project keeps the frontend and backend separate:

- `frontend/` contains the browser client.
- `backend/` contains the Flask API, R model, and dataset.

## Setup

```powershell
cd backend
pip install -r requirements.txt
Rscript -e "install.packages(c('jsonlite', 'randomForest'), repos='https://cloud.r-project.org')"
py app.py
```

The API reads `backend/data/crop_weather.csv`. Flask validates requests and calls `backend/model.R`, which trains a random forest in R and returns the recommended crop with confidence and alternatives.

`POST /api/recommend` expects:

```json
{"Temperature": 26, "Rainfall": 141, "Humidity": 72, "Soil_Type": "Loamy"}
```
