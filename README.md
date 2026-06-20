# World Cup 2026 Match Predictor

A web platform that predicts FIFA World Cup 2026 match results using **Poisson regression** and **XGBoost** models, with a live-updating scoreboard.

## Data Sources

| Source | Description |
|--------|-------------|
| [openfootball/worldcup.json](https://github.com/openfootball/worldcup.json) | 2026 World Cup fixtures, live scores, and goal scorers |
| [martj42/international_results](https://github.com/martj42/international_results) | 49,000+ international match results (1872–2026) for model training |

## Models

- **Poisson**: Estimates expected goals from team attack/defense strengths, then computes scoreline probabilities via the Poisson distribution.
- **XGBoost**: Gradient-boosted classifier trained on ELO ratings, recent form, and match context to predict home win / draw / away win.

## Quick Start

### 1. Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173** in your browser.

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/scoreboard` | Recent results, upcoming fixtures, group standings |
| GET | `/api/predictions/upcoming` | Predictions for next matches |
| GET | `/api/predict/{home}/{away}` | Single match prediction |
| GET | `/api/standings` | Group tables |
| POST | `/api/refresh` | Re-fetch live data from openfootball |

## Project Structure

```
Predict/
├── backend/          # FastAPI + ML models
├── frontend/         # React + Vite UI
└── data/             # Cached datasets
    ├── worldcup2026.json
    └── results.csv
```
