
import pandas as pd


def analyze_heatwaves(
    weather_data: dict,
    baseline_data: dict | None = None,
) -> dict:
    """Detect heatwave events lasting at least three consecutive hot days."""

    daily_data = weather_data.get("daily", {})
    dates = daily_data.get("time", [])
    temperatures = daily_data.get("temperature_2m_max", [])

    if not dates or not temperatures or len(dates) != len(temperatures):
        return {
            "threshold_celsius": None,
            "heatwave_days": 0,
            "heatwave_events": [],
            "message": "No valid daily temperature data available.",
        }

    df = pd.DataFrame({
        "date": pd.to_datetime(dates, errors="coerce"),
        "temperature": pd.to_numeric(temperatures, errors="coerce"),
    })

    # Remove invalid dates and missing temperatures.
    df = df.dropna(subset=["date", "temperature"])
    df = df.sort_values("date").reset_index(drop=True)

# Keep one record per calendar date.
    df = df.drop_duplicates(subset=["date"], keep="last")
    df = df.reset_index(drop=True)

    if len(df) < 3:
        return {
            "threshold_celsius": None,
            "heatwave_days": 0,
            "heatwave_events": [],
            "message": "At least 3 days of valid data are required.",
        }

    # Calculate the preliminary threshold for the selected period.
    if baseline_data is not None:
        baseline_daily = baseline_data.get("daily", {})
        baseline_temperatures = pd.to_numeric(
            pd.Series(baseline_daily.get("temperature_2m_max", [])),
            errors="coerce",
        ).dropna()

        if len(baseline_temperatures) < 30:
            return {
                "threshold_celsius": None,
                "heatwave_days": 0,
                "heatwave_events": [],
                "message": (
                    "At least 30 valid baseline temperature "
                    "observations are required."
                ),
            }

        threshold = float(baseline_temperatures.quantile(0.95))
    else:
        # Temporary fallback until the API passes baseline data.
        threshold = float(df["temperature"].quantile(0.95))

    df["is_hot"] = df["temperature"] > threshold

    # Start a new group when dates have a gap or hot status changes.
    previous_date = df["date"].shift(1)
    date_gap = (df["date"] - previous_date).dt.days.ne(1)
    status_change = df["is_hot"].ne(df["is_hot"].shift(1))

    df["group"] = (date_gap | status_change).cumsum()

    events = []

    for _, group in df[df["is_hot"]].groupby("group"):
        if len(group) >= 3:
            events.append({
                "start_date": group["date"].iloc[0].strftime("%Y-%m-%d"),
                "end_date": group["date"].iloc[-1].strftime("%Y-%m-%d"),
                "duration_days": len(group),
                "max_temperature_celsius": round(
                    float(group["temperature"].max()), 2
                ),
            })

    return {
        "threshold_celsius": round(threshold, 2),
        "heatwave_days": sum(
            event["duration_days"] for event in events
        ),
        "heatwave_events": events,
        "message": "Heatwave analysis completed.",
    }


def summarize_weather(weather_data: dict) -> dict:
    """Calculate summary statistics for daily maximum temperatures."""

    daily_data = weather_data.get("daily", {})
    dates = daily_data.get("time", [])
    temperatures = daily_data.get("temperature_2m_max", [])

    df = pd.DataFrame({
        "date": dates,
        "temperature": pd.to_numeric(
            pd.Series(temperatures), errors="coerce"
        ),
    })

    df = df.dropna(subset=["temperature"])

    if df.empty:
        return {
            "days_analyzed": 0,
            "average_max_temperature_celsius": None,
            "highest_max_temperature_celsius": None,
            "lowest_max_temperature_celsius": None,
            "message": "No valid temperature data available.",
        }

    return {
        "days_analyzed": len(df),
        "average_max_temperature_celsius": round(
            float(df["temperature"].mean()), 2
        ),
        "highest_max_temperature_celsius": round(
            float(df["temperature"].max()), 2
        ),
        "lowest_max_temperature_celsius": round(
            float(df["temperature"].min()), 2
        ),
        "message": "Weather summary generated successfully.",
    }


def analyze_heatwave_trends(
    weather_data: dict,
    baseline_data: dict,
) -> dict:
    """Summarize annual heatwave frequency and duration trends."""

    daily_data = weather_data.get("daily", {})
    dates = daily_data.get("time", [])
    temperatures = daily_data.get("temperature_2m_max", [])

    if not dates or len(dates) != len(temperatures):
        return {
            "annual_trends": [],
            "trend_direction": "insufficient_data",
            "message": "No valid daily weather data available.",
        }

    # Reuse the existing heatwave detection logic.
    analysis = analyze_heatwaves(weather_data, baseline_data)

    if analysis["threshold_celsius"] is None:
        return {
            "annual_trends": [],
            "trend_direction": "insufficient_data",
            "message": analysis["message"],
        }

    df = pd.DataFrame({
        "date": pd.to_datetime(dates, errors="coerce"),
        "temperature": pd.to_numeric(temperatures, errors="coerce"),
    })

    df = df.dropna(subset=["date", "temperature"])
    df = df.sort_values("date").reset_index(drop=True)
    df = df.drop_duplicates(subset=["date"], keep="last")

    threshold = analysis["threshold_celsius"]
    df["is_hot"] = df["temperature"] > threshold

    previous_date = df["date"].shift(1)
    date_gap = (df["date"] - previous_date).dt.days.ne(1)
    status_change = df["is_hot"].ne(df["is_hot"].shift(1))
    df["group"] = (date_gap | status_change).cumsum()

    events = []

    for _, group in df[df["is_hot"]].groupby("group"):
        if len(group) >= 3:
            events.append({
                "year": int(group["date"].iloc[0].year),
                "duration_days": len(group),
                "start_date": group["date"].iloc[0].strftime("%Y-%m-%d"),
                "end_date": group["date"].iloc[-1].strftime("%Y-%m-%d"),
            })

    
    annual_trends = []

    # Count the number of valid weather observations in each year.
    df["year"] = df["date"].dt.year
    df["day_of_year"] = df["date"].dt.dayofyear

    for year, year_data in df.groupby("year"):
        year_events = [
            event for event in events if event["year"] == int(year)
        ]

        event_count = len(year_events)
        heatwave_days = sum(
            event["duration_days"] for event in year_events
        )

        # A year is complete only if all calendar days are present.
        expected_days = 366 if pd.Timestamp(
            year=int(year), month=12, day=31
        ).dayofyear == 366 else 365

        observed_days = year_data["date"].dt.normalize().nunique()
        is_complete = observed_days == expected_days

        annual_trends.append({
            "year": int(year),
            "heatwave_events": event_count,
            "heatwave_days": heatwave_days,
            "average_duration_days": (
                round(heatwave_days / event_count, 2)
                if event_count else 0
            ),
            "is_complete_year": is_complete,
        })

    # Use only complete calendar years to calculate the regression trend.
    complete_years = [
        item for item in annual_trends if item["is_complete_year"]
    ]

    trend_slope = None

    if len(complete_years) < 2:
        trend_direction = "insufficient_data"
        message = (
            "At least two complete calendar years are required "
            "to calculate a reliable annual trend."
        )
    else:
        years = [item["year"] for item in complete_years]
        event_counts = [
            item["heatwave_events"] for item in complete_years
        ]

        mean_year = sum(years) / len(years)
        mean_count = sum(event_counts) / len(event_counts)

        numerator = sum(
            (year - mean_year) * (count - mean_count)
            for year, count in zip(years, event_counts)
        )
        denominator = sum(
            (year - mean_year) ** 2 for year in years
        )

        slope = numerator / denominator if denominator else 0.0

        if slope > 0.01:
            trend_direction = "increasing"
        elif slope < -0.01:
            trend_direction = "decreasing"
        else:
            trend_direction = "stable"

        trend_slope = round(slope, 4)
        message = (
            "Annual heatwave trends calculated using complete "
            "calendar years."
        )

    return {
        "threshold_celsius": round(float(threshold), 2),
        "annual_trends": annual_trends,
        "trend_direction": trend_direction,
        "trend_slope_events_per_year": trend_slope,
        "message": message,
    }

