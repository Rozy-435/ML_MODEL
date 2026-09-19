# Fieldwise crop recommendation system

Full-stack crop recommendation project.

- Flask and scikit-learn backend: `app.py`
- Standalone frontend: `frontend/index.html`
- Training data: `data/crop_weather.csv`

## Run the backend

```powershell
pip install -r requirements.txt
py app.py
```

The frontend in `frontend/` calls `http://127.0.0.1:5000/api/recommend`. Open `frontend/index.html` with a static server while the backend is running.
