# Climate Hazard Trend Analyzer

A full-stack web application that analyzes historical weather data to identify heatwave events and explore annual heatwave trends for selected geographic locations.

**Built for:** Dygnify Ventures Pvt Ltd — Full-Stack Developer Case Study

## Overview

The Climate Hazard Trend Analyzer retrieves historical daily maximum temperatures, caches weather data in MongoDB, detects heatwave events, and presents climate statistics through an interactive dashboard.

Users can select a supported city or enter custom geographic coordinates, choose a date range, view temperature charts, inspect heatwave events, and download annual trend data as CSV.

## Features

- **Location selection:** Choose supported cities or enter custom latitude and longitude.
- **Historical weather data:** Retrieve daily maximum temperatures from the Open-Meteo Archive API.
- **MongoDB caching:** Cache weather data to reduce repeated external API requests.
- **Heatwave detection:** Identify events lasting at least three consecutive days above a regional temperature threshold.
- **Climate dashboard:** View temperature summaries, charts, heatwave events, and annual trends.
- **Trend analysis:** Estimate changes in annual heatwave-event counts using linear regression.
- **CSV export:** Download annual heatwave statistics.
- **Input validation:** Validate coordinates and date ranges.
- **Automated tests:** Test heatwave detection, missing dates, duplicate dates, thresholds, and trend calculations.

## Technology Stack

| Layer | Technologies |
|---|---|
| Frontend | React, Vite, JavaScript, CSS |
| Charts | Recharts |
| API communication | Axios |
| Backend | Python, FastAPI |
| Data processing | Pandas, NumPy |
| Database | MongoDB Atlas, PyMongo |
| Weather data | Open-Meteo Archive API |
| Testing | Pytest |

## Architecture

```text
User
  |
  v
React Dashboard
  |
  | HTTP requests
  v
FastAPI Backend
  |
  +---- Weather Service
  |       |
  |       +---- Open-Meteo Archive API
  |       |
  |       +---- MongoDB Weather Cache
  |
  +---- Heatwave Detection
  |
  +---- Annual Trend Analysis
  |
  v
JSON Responses
  |
  v
Charts, Statistics, Insights and CSV Export
```

## Heatwave Detection Logic

1. Retrieve historical daily maximum temperatures for the selected location and period.
2. Retrieve baseline temperature data for the same coordinates when needed.
3. Calculate the 95th-percentile maximum-temperature threshold from the baseline data.
4. Identify days with maximum temperatures above the threshold.
5. Group consecutive qualifying calendar days into events.
6. Count an event only if it lasts at least three consecutive days.
7. Calculate heatwave-event counts, heatwave days, average duration, and annual trends.

### Baseline assumption

The current implementation uses **2004–2013** as its baseline period. This is a project assumption, not an official 30-year climate normal.

When baseline data is unavailable, the detector may use a percentile calculated from the selected period. Results from this fallback may not be directly comparable with baseline-based results.

## Trend Analysis

The backend aggregates heatwave events by year and calculates annual event counts, heatwave days, and average event duration.

A least-squares linear regression estimates the slope of annual event counts:

- **Increasing:** Slope greater than 0.01 events per year.
- **Decreasing:** Slope less than -0.01 events per year.
- **Stable:** Slope between these thresholds.
- **Insufficient data:** Fewer than two complete calendar years are available.

The slope is descriptive and is not a statistical significance test. It does not independently establish causation or prove that climate change caused an observed trend.

Events spanning calendar years are attributed to the year in which the event begins.

## Getting Started

### Prerequisites

- Python 3.12 or a compatible Python version
- Node.js and npm
- MongoDB Atlas account or another accessible MongoDB deployment
- Git

### 1. Clone the repository

```bash
git clone https://github.com/mohammed-sohail1047/climate-hazard-analyzer.git
cd climate-hazard-analyzer
```

### 2. Configure the backend

From the project root, run:

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `backend/.env` with your MongoDB connection details:

```dotenv
MONGODB_URI=your_mongodb_connection_string
DATABASE_NAME=climate_hazard_analyzer
```

Keep your actual `.env` file private. Never commit database credentials.

Start the backend from the `backend` directory:

```powershell
uvicorn app.main:app --reload
```

The API and interactive documentation should be available at:

- API: http://127.0.0.1:8000
- API documentation: http://127.0.0.1:8000/docs

### 3. Configure the frontend

Open a second terminal from the project root:

```powershell
cd frontend
npm install
npm run dev
```

Open the local URL printed by Vite, normally http://localhost:5173.

The frontend uses `VITE_API_URL` when configured; otherwise, it defaults to `http://127.0.0.1:8000`.

For local development, ensure the backend CORS configuration permits requests from the frontend origin.

## API Endpoints

| Endpoint | Purpose |
|---|---|
| `GET /weather/summary` | Return weather summary statistics |
| `GET /weather/history` | Return historical daily weather data |
| `GET /hazards/heatwaves` | Return detected heatwave events and related statistics |
| `GET /hazards/heatwave-trends` | Return annual heatwave statistics and trend estimates |

See `/docs` while the backend is running for the actual endpoint parameters and response schemas.

## Running Tests

From the project root:

```powershell
cd backend
python -m pytest -v
```

The current test suite contains eight tests covering event detection, missing calendar dates, baseline thresholds, duplicate dates, temperature summaries, missing temperatures, annual trends, and regression slopes.

## Data Source

Historical weather data is provided by the [Open-Meteo Archive API](https://open-meteo.com/en/docs/historical-weather-api).

Weather observations are cached in MongoDB to reduce repeated requests for matching coordinates and date ranges.

Results should be interpreted in the context of the selected location, period, baseline assumptions, and available observations.

## Limitations and Future Improvements

- The current hazard-analysis interface focuses on heatwaves.
- The baseline period is a project assumption rather than an official climate normal.
- The regression slope does not include a statistical significance test.
- Events crossing calendar years are assigned to their starting year.
- Additional data-quality checks could improve handling of incomplete observations.
- Future improvements could include interactive maps, additional hazards, Mann–Kendall trend testing, PDF reports, and expanded data-quality reporting.
- Production deployment requires appropriate CORS restrictions, secret management, error handling, caching policies, and resource limits.

## AI Assistance Disclosure

AI tools were used as development aids during implementation and documentation. The application code, climate-analysis assumptions, automated tests, and deployment behavior should be reviewed and validated by the project author before production use.

## Author

**Mohammed Sohail**

GitHub: [mohammed-sohail1047](https://github.com/mohammed-sohail1047)

## License

No license has been specified. All rights are reserved by default unless a license is added to this repository.