
from datetime import date

import httpx
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from app.hazards import (
    analyze_heatwaves,
    analyze_heatwave_trends,
    summarize_weather,
)
from app.weather import fetch_historical_weather, fetch_baseline_weather


app = FastAPI(
    title="Climate Hazard Trend Analyzer",
    description="Analyze historical weather data and climate hazards.",
    version="1.0.0",
)





from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://climate-hazard-analyzer-brown.vercel.app",
        "https://climate-hazard-analyzer-qo9vik1nv-mohammed-sohail-s-projects1.vercel.app",
    ],
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)





@app.get("/")
def home():
    return {
        "message": "Climate Hazard Trend Analyzer API is running!",
        "status": "success",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/weather/history")
async def historical_weather(
    latitude: float = Query(17.385, ge=-90, le=90),
    longitude: float = Query(78.4867, ge=-180, le=180),
    start_date: date = Query(...),
    end_date: date = Query(...),
):
    if start_date > end_date:
        raise HTTPException(
            status_code=400,
            detail="start_date must be before or equal to end_date",
        )

    try:
        return await fetch_historical_weather(
            latitude=latitude,
            longitude=longitude,
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat(),
        )
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502,
            detail="Unable to retrieve historical weather data",
        ) from exc


@app.get("/hazards/heatwaves")
async def detect_heatwaves(
    latitude: float = Query(17.385, ge=-90, le=90),
    longitude: float = Query(78.4867, ge=-180, le=180),
    start_date: date = Query(...),
    end_date: date = Query(...),
):
    if start_date > end_date:
        raise HTTPException(
            status_code=400,
            detail="start_date must be before or equal to end_date",
        )

    try:
        
        weather_data = await fetch_historical_weather(
            latitude=latitude,
            longitude=longitude,
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat(),
        )

        baseline_data = await fetch_baseline_weather(
            latitude=latitude,
            longitude=longitude,
        )

        return {
            "location": {
                "latitude": latitude,
                "longitude": longitude,
            },
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "hazard": "heatwave",
            "analysis": analyze_heatwaves(weather_data, baseline_data),
        }

    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502,
            detail="Unable to retrieve historical weather data",
        ) from exc


@app.get("/weather/summary")
async def weather_summary(
    latitude: float = Query(17.385, ge=-90, le=90),
    longitude: float = Query(78.4867, ge=-180, le=180),
    start_date: date = Query(...),
    end_date: date = Query(...),
):
    if start_date > end_date:
        raise HTTPException(
            status_code=400,
            detail="start_date must be before or equal to end_date",
        )

    try:
        weather_data = await fetch_historical_weather(
            latitude=latitude,
            longitude=longitude,
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat(),
        )

        return {
            "location": {
                "latitude": latitude,
                "longitude": longitude,
            },
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "summary": summarize_weather(weather_data),
        }

    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502,
            detail="Unable to retrieve historical weather data",
        ) from exc


@app.get("/hazards/heatwave-trends")
async def heatwave_trends(
    latitude: float = Query(17.385, ge=-90, le=90),
    longitude: float = Query(78.4867, ge=-180, le=180),
    start_date: date = Query(...),
    end_date: date = Query(...),
):
    if start_date > end_date:
        raise HTTPException(
            status_code=400,
            detail="start_date must be before or equal to end_date",
        )

    try:
        weather_data = await fetch_historical_weather(
            latitude=latitude,
            longitude=longitude,
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat(),
        )

        baseline_data = await fetch_baseline_weather(
            latitude=latitude,
            longitude=longitude,
        )

        analysis = analyze_heatwave_trends(
            weather_data,
            baseline_data,
        )

        return {
            "location": {
                "latitude": latitude,
                "longitude": longitude,
            },
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "hazard": "heatwave",
            "analysis": analysis,
        }

    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502,
            detail="Unable to retrieve historical weather data",
        ) from exc
