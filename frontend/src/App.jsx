import { useState } from "react";
import axios from "axios";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from "recharts";
import "./App.css";

const API_URL =
  import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";


const CITIES = [
  {
    name: "Hyderabad",
    latitude: "17.385",
    longitude: "78.4867",
  },
  {
    name: "Mumbai",
    latitude: "19.076",
    longitude: "72.8777",
  },
  {
    name: "Delhi",
    latitude: "28.6139",
    longitude: "77.209",
  },
  {
    name: "Bengaluru",
    latitude: "12.9716",
    longitude: "77.5946",
  },
  {
    name: "Chennai",
    latitude: "13.0827",
    longitude: "80.2707",
  },
];


function downloadAnnualTrendsCSV(annualTrends) {
  if (!annualTrends || annualTrends.length === 0) {
    alert("No annual trend data available to export.");
    return;
  }

  const headers = [
    "Year",
    "Heatwave Events",
    "Heatwave Days",
    "Average Duration (Days)",
    "Complete Year",
  ];

  const rows = annualTrends.map((item) => [
    item.year,
    item.heatwave_events,
    item.heatwave_days,
    item.average_duration_days,
    item.is_complete_year ? "Yes" : "No",
  ]);

  const csvContent = [headers, ...rows]
    .map((row) =>
      row
        .map((value) => `"${String(value ?? "").replace(/"/g, '""')}"`)
        .join(",")
    )
    .join("\r\n");

  const blob = new Blob(["\uFEFF", csvContent], {
    type: "text/csv;charset=utf-8;",
  });

  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");

  link.href = url;
  link.download = "annual-heatwave-trends.csv";
  document.body.appendChild(link);
  link.click();
  link.remove();

  // Delay URL cleanup to allow the browser to begin the download.
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

function App() {
  const [latitude, setLatitude] = useState("17.385");
  const [longitude, setLongitude] = useState("78.4867");
  const [selectedCity, setSelectedCity] = useState("Hyderabad");
  const [startDate, setStartDate] = useState("2024-01-01");
  const [endDate, setEndDate] = useState("2024-01-31");

  const [summary, setSummary] = useState(null);
  const [weatherData, setWeatherData] = useState([]);
  const [heatwaves, setHeatwaves] = useState(null);
  const [heatwaveTrends, setHeatwaveTrends] = useState(null);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  
async function loadClimateData(event) {
  event.preventDefault();

  const lat = Number(latitude);
  const lon = Number(longitude);

  if (
    latitude.trim() === "" ||
    !Number.isFinite(lat) ||
    lat < -90 ||
    lat > 90
  ) {
    setError("Latitude must be a valid number between -90 and 90.");
    return;
  }

  if (
    longitude.trim() === "" ||
    !Number.isFinite(lon) ||
    lon < -180 ||
    lon > 180
  ) {
    setError("Longitude must be a valid number between -180 and 180.");
    return;
  }

  if (!startDate || !endDate) {
    setError("Please select both a start date and an end date.");
    return;
  }

  if (startDate > endDate) {
    setError("Start date must be before or equal to end date.");
    return;
  }

  setLoading(true);
  setError("");
  setSummary(null);
  setWeatherData([]);
  setHeatwaves(null);
  setHeatwaveTrends(null);


    const params = {
      latitude: lat,
      longitude: lon  ,
      start_date: startDate,
      end_date: endDate,
    };

    try {
      const [
        summaryResponse,
        weatherResponse,
        heatwaveResponse,
        trendResponse,
      ] = await Promise.all([
        axios.get(`${API_URL}/weather/summary`, { params }),
        axios.get(`${API_URL}/weather/history`, { params }),
        axios.get(`${API_URL}/hazards/heatwaves`, { params }),
        axios.get(`${API_URL}/hazards/heatwave-trends`, { params }),
      ]);

      setSummary(summaryResponse.data.summary);
      setHeatwaves(heatwaveResponse.data.analysis);
      setHeatwaveTrends(trendResponse.data.analysis);

      const daily = weatherResponse.data.daily ?? {};
      const temperatures = daily.temperature_2m_max ?? [];
      const dates = daily.time ?? [];

      setWeatherData(
        dates
          .map((date, index) => ({
            date,
            temperature: temperatures[index],
          }))
          .filter(
            (item) =>
              item.temperature !== null &&
              item.temperature !== undefined &&
              Number.isFinite(Number(item.temperature))
          )
      );
    } catch (err) {
      console.error("Climate analysis failed:", err);

      setError(
        err.response?.data?.detail ||
          "Could not load climate data. Check that the backend is running and try again."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="dashboard">
      <header className="page-header">
        <div>
          <p className="eyebrow">CLIMATE INTELLIGENCE</p>
          <h1>Climate Hazard Trend Analyzer</h1>
          
<p className="subtitle">
  Explore historical temperatures and identify potential
  heatwave events for your selected location.
</p>

<p className="analysis-context">
  Location: {Number(latitude).toFixed(4)},{" "}
  {Number(longitude).toFixed(4)}
  {" · "}
  Period: {startDate} to {endDate}
</p>

        </div>

        <span className="status-pill">Historical analysis</span>
      </header>

      <section className="panel">
        <h2>Analysis settings</h2>

        <form onSubmit={loadClimateData} className="filters">
        <label>
  City / Location
  <select
    value={selectedCity}
    onChange={(event) => {
      const cityName = event.target.value;
      setSelectedCity(cityName);

      const city = CITIES.find(
        (item) => item.name === cityName
      );

      if (city) {
        setLatitude(city.latitude);
        setLongitude(city.longitude);
      }
    }}
  >
    {CITIES.map((city) => (
      <option key={city.name} value={city.name}>
        {city.name}
      </option>
    ))}
    <option value="Custom">Custom coordinates</option>
  </select>
</label>
          <label>
            Latitude
            <input
              type="number"
              min="-90"
              max="90"
              step="any"
              required
              value={latitude}
              
onChange={(event) => {
  setLatitude(event.target.value);
  setSelectedCity("Custom");
}}

            />
          </label>

          <label>
            Longitude
            <input
              type="number"
              min="-180"
              max="180"
              step="any"
              required
              value={longitude}
              
onChange={(event) => {
  setLongitude(event.target.value);
  setSelectedCity("Custom");
}}

            />
          </label>

          <label>
            Start date
            <input
              type="date"
              required
              max={endDate}
              value={startDate}
              onChange={(event) => setStartDate(event.target.value)}
            />
          </label>

          <label>
            End date
            <input
              type="date"
              required
              min={startDate}
              value={endDate}
              onChange={(event) => setEndDate(event.target.value)}
            />
          </label>

          <button type="submit" disabled={loading}>
            {loading ? "Analyzing..." : "Analyze climate"}
          </button>
        </form>

        {error && (
          <p className="error-message" role="alert">
            {error}
          </p>
        )}
      </section>

      <section className="metrics">
        <article className="metric-card">
          <p>Average maximum temperature</p>
          <strong>
            {summary
              ? `${summary.average_max_temperature_celsius}°C`
              : "—"}
          </strong>
          <span>Across valid days</span>
        </article>

        <article className="metric-card">
          <p>Highest maximum temperature</p>
          <strong>
            {summary
              ? `${summary.highest_max_temperature_celsius}°C`
              : "—"}
          </strong>
          <span>Peak daily maximum</span>
        </article>

        <article className="metric-card">
          <p>Lowest maximum temperature</p>
          <strong>
            {summary
              ? `${summary.lowest_max_temperature_celsius}°C`
              : "—"}
          </strong>
          <span>Minimum daily maximum</span>
        </article>

        <article className="metric-card">
          <p>Heatwave days</p>
          <strong>
            {heatwaves ? heatwaves.heatwave_days : "—"}
          </strong>
          <span>Based on the current detection rule</span>
        </article>
      </section>

      <section className="panel chart-panel">
        <div className="section-heading">
          <div>
            <h2>Daily maximum temperature</h2>
            <p>Temperature in degrees Celsius</p>
          </div>

          <span className="chart-count">
            {weatherData.length} days
          </span>
        </div>

        {weatherData.length > 0 ? (
          <div className="chart">
            <ResponsiveContainer width="100%" height={320}>
              <LineChart data={weatherData}>
                <CartesianGrid strokeDasharray="3 3" />

                <XAxis
                  dataKey="date"
                  tick={{ fontSize: 11 }}
                  minTickGap={25}
                />

                <YAxis
                  domain={["auto", "auto"]}
                  tick={{ fontSize: 12 }}
                  unit="°C"
                />

                <Tooltip />
                <Legend />

                <Line
                  type="monotone"
                  dataKey="temperature"
                  name="Maximum temperature"
                  stroke="#287d74"
                  strokeWidth={2.5}
                  dot={false}
                  connectNulls={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        ) : (
          <div className="empty-state">
            <p>Temperature chart will appear here.</p>
            <span>
              Choose a location and date range, then analyze.
            </span>
          </div>
        )}
      </section>

      {heatwaveTrends && (
        <section className="panel chart-panel">
          <div className="section-heading">
            <div>
              <h2>Annual Heatwave Trends</h2>
              <p>Year-by-year frequency and duration</p>
            </div>

            {heatwaveTrends.annual_trends?.length > 0 && (
              <button
                type="button"
                onClick={() =>
                  downloadAnnualTrendsCSV(
                    heatwaveTrends.annual_trends
                  )
                }
              >
                Export Annual Trends CSV
              </button>
            )}
          </div>

          <p>
            Trend direction:{" "}
            <strong>{heatwaveTrends.trend_direction}</strong>
          </p>

          {heatwaveTrends.message && (
            <p>{heatwaveTrends.message}</p>
          )}

          {heatwaveTrends.annual_trends?.length > 0 ? (
            <div className="chart">
              <ResponsiveContainer width="100%" height={320}>
                <LineChart data={heatwaveTrends.annual_trends}>
                  <CartesianGrid strokeDasharray="3 3" />

                  <XAxis
                    dataKey="year"
                    tick={{ fontSize: 12 }}
                  />

                  <YAxis
                    yAxisId="events"
                    allowDecimals={false}
                  />

                  <YAxis
                    yAxisId="days"
                    orientation="right"
                    allowDecimals={false}
                  />

                  <Tooltip />
                  <Legend />

                  <Line
                    yAxisId="events"
                    type="monotone"
                    dataKey="heatwave_events"
                    name="Heatwave events"
                    stroke="#e85d04"
                    strokeWidth={2}
                  />

                  <Line
                    yAxisId="days"
                    type="monotone"
                    dataKey="heatwave_days"
                    name="Heatwave days"
                    stroke="#0077b6"
                    strokeWidth={2}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <p>No annual trend data is available for this period.</p>
          )}
        </section>
      )}

      <section className="panel">
        <h2>Heatwave analysis</h2>

        {heatwaves ? (
          <>
            <p>{heatwaves.message}</p>

            <p>
              Detection threshold:{" "}
              {heatwaves.threshold_celsius == null
                ? "Not available"
                : `${heatwaves.threshold_celsius}°C`}
            </p>

            {heatwaves.heatwave_events?.length > 0 ? (
              <div className="event-list">
                {heatwaves.heatwave_events.map((event) => (
                  <article
                    className="event-card"
                    key={`${event.start_date}-${event.end_date}`}
                  >
                    <strong>
                      {event.start_date} – {event.end_date}
                    </strong>

                    <span>{event.duration_days} days</span>

                    <span>
                      Peak: {event.max_temperature_celsius}°C
                    </span>
                  </article>
                ))}
              </div>
            ) : (
              <p>No qualifying heatwave events were detected.</p>
            )}
          </>
        ) : (
          <p className="muted">
            Run an analysis to view detected heatwave events.
          </p>
        )}
      </section>

      <section className="panel">
        <h2>Climate Insights</h2>

        {summary && heatwaves && heatwaveTrends ? (
          <>
            <article className="event-card">
              <strong>Temperature overview</strong>
              
<p>
  The average maximum temperature during the selected
  period was{" "}
  {summary.average_max_temperature_celsius == null
    ? "Not available"
    : `${Number(summary.average_max_temperature_celsius).toFixed(1)}°C`}.
</p>

            </article>

            <article className="event-card">
              <strong>Heatwave activity</strong>
              <p>
                {heatwaves.heatwave_events?.length > 0
                  ? `${heatwaves.heatwave_events.length} qualifying heatwave event(s) were detected.`
                  : "No qualifying heatwave events were detected during the selected period."}
              </p>
            </article>

            <article className="event-card">
              <strong>Long-term trend</strong>
              <p>
                {heatwaveTrends.trend_direction === "increasing"
                  ? "Annual heatwave frequency shows an increasing trend."
                  : heatwaveTrends.trend_direction === "decreasing"
                  ? "Annual heatwave frequency shows a decreasing trend."
                  : heatwaveTrends.trend_direction === "stable"
                  ? "Annual heatwave frequency shows a relatively stable trend."
                  : "There is insufficient complete annual data to assess the long-term trend."}
              </p>
            </article>
          </>
        ) : (
          <p className="muted">
            Run an analysis to generate climate insights.
          </p>
        )}
      </section>

      <footer>
        Climate Hazard Trend Analyzer · Historical weather powered by
        Open-Meteo
      </footer>
    </main>
  );
}

export default App;