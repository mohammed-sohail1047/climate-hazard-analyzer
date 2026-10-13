
from app.hazards import (
    analyze_heatwaves,
    analyze_heatwave_trends,
    summarize_weather,
)


def create_baseline_data():
    """Create 30 baseline temperature observations for testing."""
    temperatures = [
        20, 22, 24, 26, 28, 30, 32, 34, 36, 38,
        20, 22, 24, 26, 28, 30, 32, 34, 36, 38,
        20, 22, 24, 26, 28, 30, 32, 34, 36, 38,
    ]

    return {
        "daily": {
            "temperature_2m_max": temperatures,
        }
    }



def test_heatwave_events_have_at_least_three_consecutive_days():
    weather_data = {
        "daily": {
            "time": [
                f"2024-01-{day:02d}" for day in range(1, 11)
            ],
            "temperature_2m_max": [
                20, 21, 20, 39, 39, 39, 22, 21, 23, 40
            ],
        }
    }

    result = analyze_heatwaves(
        weather_data,
        create_baseline_data(),
    )

    assert len(result["heatwave_events"]) == 1
    assert result["heatwave_events"][0]["duration_days"] == 3
    assert result["heatwave_events"][0]["start_date"] == "2024-01-04"
    assert result["heatwave_events"][0]["end_date"] == "2024-01-06"



def test_missing_calendar_date_does_not_join_events():
    weather_data = {
        "daily": {
            "time": [
                "2024-01-01",
                "2024-01-02",
                "2024-01-04",
                "2024-01-05",
                "2024-01-06",
            ],
            "temperature_2m_max": [35, 39, 39, 39, 39],
        }
    }

    result = analyze_heatwaves(
        weather_data,
        create_baseline_data(),
    )

    assert result["threshold_celsius"] == 38.0
    assert result["heatwave_events"] == [
        {
            "start_date": "2024-01-04",
            "end_date": "2024-01-06",
            "duration_days": 3,
            "max_temperature_celsius": 39.0,
        }
    ]
    assert result["heatwave_days"] == 3


def test_heatwave_threshold_uses_baseline_temperatures():
    weather_data = {
        "daily": {
            "time": [
                "2024-01-01",
                "2024-01-02",
                "2024-01-03",
                "2024-01-04",
            ],
            "temperature_2m_max": [35, 39, 40, 41],
        }
    }

    result = analyze_heatwaves(
        weather_data,
        create_baseline_data(),
    )

    assert result["threshold_celsius"] == 38.0


def test_duplicate_dates_do_not_create_false_heatwave():
    weather_data = {
        "daily": {
            "time": [
                "2024-01-01",
                "2024-01-02",
                "2024-01-02",
                "2024-01-03",
            ],
            "temperature_2m_max": [20, 39, 40, 39],
        }
    }

    result = analyze_heatwaves(
        weather_data,
        create_baseline_data(),
    )

    assert result["threshold_celsius"] == 38.0
    assert result["heatwave_events"] == []
    assert result["heatwave_days"] == 0


def test_summarize_weather_calculates_temperature_statistics():
    weather_data = {
        "daily": {
            "time": [
                "2024-01-01",
                "2024-01-02",
                "2024-01-03",
            ],
            "temperature_2m_max": [30, 35, 40],
        }
    }

    result = summarize_weather(weather_data)

    assert result["days_analyzed"] == 3
    assert result["average_max_temperature_celsius"] == 35.0
    assert result["highest_max_temperature_celsius"] == 40.0
    assert result["lowest_max_temperature_celsius"] == 30.0


def test_summarize_weather_handles_missing_temperatures():
    weather_data = {
        "daily": {
            "time": [
                "2024-01-01",
                "2024-01-02",
            ],
            "temperature_2m_max": [None, None],
        }
    }

    result = summarize_weather(weather_data)

    assert result["days_analyzed"] == 0
    assert result["average_max_temperature_celsius"] is None
    assert result["highest_max_temperature_celsius"] is None
    assert result["lowest_max_temperature_celsius"] is None


baseline_data = {
    "daily": {
        "time": [
            f"2010-01-{day:02d}"
            for day in range(1, 32)
        ],
        "temperature_2m_max": [30.0] * 31,
    }
}


def test_analyze_heatwave_trends_returns_annual_data():
    baseline_data = {
        "daily": {
            "time": [
                f"2010-01-{day:02d}"
                for day in range(1, 32)
            ],
            "temperature_2m_max": [30.0] * 31,
        }
    }

    weather_data = {
        "daily": {
            "time": [
                "2020-01-01",
                "2020-01-02",
                "2020-01-03",
                "2020-01-04",
                "2021-01-01",
                "2021-01-02",
                "2021-01-03",
                "2021-01-04",
            ],
            "temperature_2m_max": [
                40.0, 40.0, 40.0, 30.0,
                40.0, 40.0, 30.0, 30.0,
            ],
        }
    }

    result = analyze_heatwave_trends(weather_data, baseline_data)

    assert len(result["annual_trends"]) == 2
    assert result["annual_trends"][0]["year"] == 2020
    assert result["annual_trends"][0]["heatwave_events"] == 1
    assert result["annual_trends"][0]["heatwave_days"] == 3
    assert result["annual_trends"][1]["year"] == 2021
    assert result["annual_trends"][1]["heatwave_events"] == 0
    assert result["annual_trends"][1]["heatwave_days"] == 0



def test_heatwave_trend_includes_regression_slope():
    from datetime import date, timedelta

    from app.hazards import analyze_heatwave_trends

    baseline_data = {
        "daily": {
            "temperature_2m_max": [30.0] * 31
        }
    }

    dates = []
    temperatures = []

    # Generate complete calendar years.
    # 2020: two heatwave events.
    # 2021: one heatwave event.
    yearly_event_starts = {
        2020: ["2020-01-01", "2020-02-01"],
        2021: ["2021-01-01"],
    }

    for year in (2020, 2021):
        current_date = date(year, 1, 1)
        next_year = date(year + 1, 1, 1)
        hot_days = set()

        for start in yearly_event_starts[year]:
            start_date = date.fromisoformat(start)
            for offset in range(3):
                hot_days.add(start_date + timedelta(days=offset))

        while current_date < next_year:
            dates.append(current_date.isoformat())
            temperatures.append(
                40.0 if current_date in hot_days else 30.0
            )
            current_date += timedelta(days=1)

    weather_data = {
        "daily": {
            "time": dates,
            "temperature_2m_max": temperatures,
        }
    }

    result = analyze_heatwave_trends(weather_data, baseline_data)

    assert result["trend_direction"] == "decreasing"
    assert result["trend_slope_events_per_year"] < 0
    assert len(result["annual_trends"]) == 2
    assert all(
        item["is_complete_year"]
        for item in result["annual_trends"]
    )

