\# Climate Hazard Trend Analyzer



A full-stack web application that analyzes historical weather data to identify heatwave events and explore annual heatwave trends for selected geographic locations.



\*\*Built for:\*\* Dygnify Ventures Pvt Ltd — Full-Stack Developer Case Study



\## Overview



The Climate Hazard Trend Analyzer retrieves historical daily maximum temperatures, caches weather data, detects heatwave events, and presents climate statistics through an interactive dashboard.



Users can select a city or enter geographic coordinates, choose a date range, view temperature charts, inspect detected heatwaves, and download annual trend data as a CSV file.



\## Features



\- \*\*Location selection:\*\* Choose from supported cities or enter custom latitude and longitude.

\- \*\*Historical weather data:\*\* Retrieve daily maximum temperatures from the Open-Meteo Archive API.

\- \*\*MongoDB caching:\*\* Store retrieved weather data to reduce repeated external API requests.

\- \*\*Heatwave detection:\*\* Identify periods of at least three consecutive days exceeding a regional temperature threshold.

\- \*\*Climate dashboard:\*\* Display temperature summaries, historical charts, heatwave events, and annual trend analysis.

\- \*\*Trend analysis:\*\* Estimate changes in annual heatwave-event counts using linear regression.

\- \*\*CSV export:\*\* Download annual heatwave statistics for further analysis.

\- \*\*Input validation:\*\* Validate geographic coordinates and date ranges before requesting analysis.

\- \*\*Automated tests:\*\* Test heatwave detection, missing dates, duplicate dates, temperature thresholds, and trend calculations.



\## Technology Stack



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



\## Architecture



```text

User

&#x20;|

&#x20;v

React Dashboard

&#x20;|

&#x20;| HTTP requests

&#x20;v

FastAPI Backend

&#x20;|

&#x20;+---- Weather Service

&#x20;|       |

&#x20;|       +---- Open-Meteo Archive API

&#x20;|       |

&#x20;|       +---- MongoDB Weather Cache

&#x20;|

&#x20;+---- Heatwave Detection

&#x20;|

&#x20;+---- Annual Trend Analysis

&#x20;|

&#x20;v

JSON Responses

&#x20;|

&#x20;v

Charts, Statistics, Insights and CSV Export

```



\## How Heatwave Detection Works



The application uses daily maximum temperatures to identify potential heatwave events.



1\. Retrieve historical daily maximum temperatures for the selected coordinates and date range.

2\. Retrieve baseline temperature data for the same coordinates when needed.

3\. Calculate the 95th-percentile maximum-temperature threshold using the baseline data.

4\. Identify days whose maximum temperatures exceed that threshold.

5\. Group consecutive qualifying calendar days into events.

6\. Count an event only when it lasts at least three consecutive days.

7\. Calculate heatwave-event counts, heatwave days, average event duration, and annual trends.



\### Baseline assumption



The current implementation uses \*\*2004–2013\*\* as its baseline period. This is a project assumption and should not be interpreted as an official 30-year climate normal.



When baseline data is unavailable, the heatwave detector may use a percentile calculated from the selected period. Results obtained using this fallback may not be directly comparable with baseline-based results.



\## Trend Analysis



The backend aggregates detected heatwave events by year and calculates annual event counts, heatwave days, and average event duration.



A least-squares linear regression estimates the slope of annual event counts:



\- \*\*Increasing:\*\* Positive slope greater than 0.01 events per year.

\- \*\*Decreasing:\*\* Negative slope less than -0.01 events per year.

\- \*\*Stable:\*\* Slope between these thresholds.

\- \*\*Insufficient data:\*\* Fewer than two complete calendar years are available for the trend calculation.



The slope is descriptive, not a statistical significance test. An increasing or decreasing trend does not by itself establish statistical significance or prove that climate change caused the observed pattern.



Events spanning calendar years are attributed to the year in which the event begins.



\## Getting Started



\### Prerequisites



Install the following before running the project:



\- Python 3.12 or a compatible Python version

\- Node.js and npm

\- MongoDB Atlas account or an accessible MongoDB deployment

\- Git



\### 1. Clone the repository



```bash

git clone https://github.com/mohammed-sohail1047/climate-hazard-analyzer.git

cd climate-hazard-analyzer

```



\### 2. Set up the backend



From the project root:



```powershell

cd backend

python -m venv venv

.\\venv\\Scripts\\Activate.ps1

pip install -r requirements.txt

```



Create your local environment file by copying the example:



```powershell

Copy-Item .env.example .env

```



Update `backend/.env` with your own MongoDB connection details:



```dotenv

MONGODB\_URI=your\_mongodb\_connection\_string

DATABASE\_NAME=climate\_hazard\_analyzer

```



Do not commit `.env` or publish database credentials.



Start the backend from the `backend` directory:



```powershell

uvicorn app.main:app --reload

```



The API should be available at:



\- API base URL: `http://127.0.0.1:8000`

\- Interactive API documentation: `http://127.0.0.1:8000/docs`



\### 3. Set up the frontend



Open a second terminal from the project root:



```powershell

cd frontend

npm install

npm run dev

```



Open the local URL printed by Vite, normally `http://localhost:5173`.



The frontend uses `VITE\_API\_URL` when configured and otherwise defaults to `http://127.0.0.1:8000`.



For a local deployment, ensure the frontend can reach the backend and the backend CORS configuration allows the frontend origin.



\## API Endpoints



The dashboard uses the following backend endpoints:



| Endpoint | Purpose |

|---|---|

| `GET /weather/summary` | Return summary statistics for the selected weather period |

| `GET /weather/history` | Return historical daily weather data |

| `GET /hazards/heatwaves` | Return detected heatwave events and related statistics |

| `GET /hazards/heatwave-trends` | Return annual heatwave statistics and trend estimates |



The dashboard sends location coordinates and the selected start and end dates to the API. See `/docs` while the backend is running for the actual endpoint parameters and response schemas.



\## Running Tests



From the project root, activate the backend virtual environment and run:



```powershell

cd backend

python -m pytest -v

```



The current automated test suite contains eight tests covering heatwave-event detection, missing calendar dates, baseline thresholds, duplicate dates, temperature summaries, missing temperature values, annual trends, and regression slopes.



\## Data Source



Historical weather data is provided by the \[Open-Meteo Archive API](https://open-meteo.com/en/docs/historical-weather-api).



Weather observations are cached in MongoDB to reduce repeated requests for matching coordinates and date ranges.



Weather data and derived metrics should be interpreted in the context of the selected location, period, baseline assumptions, and available observations.



\## Limitations and Future Improvements



\- The current hazard-analysis interface focuses on heatwaves.

\- The baseline period is a project assumption rather than an official climate normal.

\- The linear regression slope does not include a statistical significance test.

\- Events crossing calendar years are assigned to their starting year.

\- Additional quality checks could improve handling of incomplete weather observations.

\- Future versions could include interactive maps, additional hazards, more formal trend tests such as Mann–Kendall, downloadable PDF reports, and expanded data-quality reporting.

\- Production deployment should include appropriate CORS restrictions, secret management, API error handling, caching policies, and resource limits.



\## AI Assistance Disclosure



AI tools were used as development aids during implementation and documentation. The application code, climate-analysis assumptions, automated tests, and deployment behavior should be reviewed and validated by the project author before production use.



\## Author



\*\*Mohammed Sohail\*\*



GitHub: \[mohammed-sohail1047](https://github.com/mohammed-sohail1047)



\## License



No license has been specified yet. All rights are reserved by default unless a license is added to this repository.



