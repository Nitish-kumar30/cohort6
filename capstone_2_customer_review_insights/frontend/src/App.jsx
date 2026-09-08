import { useEffect, useMemo, useState } from "react";
import {
  BarChart,
  Bar,
  Cell,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

const STATUS_COLORS = {
  positive: "var(--status-good)",
  negative: "var(--status-critical)",
  neutral: "var(--status-neutral)",
};

// recharts needs resolved hex, not CSS vars, for fills
const STATUS_HEX = {
  positive: "#0ca30c",
  negative: "#d03b3b",
  neutral: "#898781",
};

function StatTile({ label, value, tone }) {
  return (
    <div className={`stat-tile ${tone || ""}`}>
      <div className="label">{label}</div>
      <div className="value">{value}</div>
    </div>
  );
}

function SentimentBadge({ sentiment }) {
  return <span className={`badge ${sentiment}`}>{sentiment}</span>;
}

function ChartTooltip({ active, payload, label }) {
  if (!active || !payload || !payload.length) return null;
  return (
    <div
      style={{
        background: "var(--surface-1)",
        border: "1px solid var(--border)",
        borderRadius: 8,
        padding: "8px 12px",
        fontSize: 12,
        color: "var(--text-primary)",
      }}
    >
      <div style={{ color: "var(--text-muted)", marginBottom: 4 }}>{label}</div>
      {payload.map((p) => (
        <div key={p.dataKey} style={{ color: STATUS_HEX[p.dataKey] || p.color }}>
          {p.dataKey}: {p.value}
        </div>
      ))}
    </div>
  );
}

export default function App() {
  const [summary, setSummary] = useState(null);
  const [trends, setTrends] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [reviews, setReviews] = useState([]);
  const [sentimentFilter, setSentimentFilter] = useState("all");
  const [loading, setLoading] = useState(true);
  const [ingesting, setIngesting] = useState(false);

  async function loadAll() {
    setLoading(true);
    const [summaryRes, trendsRes, alertsRes, reviewsRes] = await Promise.all([
      fetch("/api/summary").then((r) => r.json()),
      fetch("/api/trends").then((r) => r.json()),
      fetch("/api/alerts").then((r) => r.json()),
      fetch("/api/reviews").then((r) => r.json()),
    ]);
    setSummary(summaryRes);
    setTrends(trendsRes);
    setAlerts(alertsRes);
    setReviews(reviewsRes);
    setLoading(false);
  }

  useEffect(() => {
    loadAll();
  }, []);

  async function handleIngest() {
    setIngesting(true);
    await fetch("/api/ingest", { method: "POST" });
    await loadAll();
    setIngesting(false);
  }

  const distribution = useMemo(() => {
    if (!summary) return [];
    return [
      { sentiment: "positive", count: summary.positive },
      { sentiment: "neutral", count: summary.neutral },
      { sentiment: "negative", count: summary.negative },
    ];
  }, [summary]);

  const filteredReviews = useMemo(() => {
    if (sentimentFilter === "all") return reviews;
    return reviews.filter((r) => r.sentiment === sentimentFilter);
  }, [reviews, sentimentFilter]);

  return (
    <div className="app">
      <div className="app-header">
        <div>
          <h1>Customer Review Insights</h1>
          <div className="subtitle">
            Sentiment, summaries, and trend monitoring across products
          </div>
        </div>
        <button className="refresh-btn" onClick={handleIngest} disabled={ingesting}>
          {ingesting ? "Processing..." : "Run pipeline"}
        </button>
      </div>

      {loading && <div className="empty-state">Loading...</div>}

      {!loading && summary && (
        <>
          <div className="stat-grid">
            <StatTile label="Total reviews" value={summary.total_reviews} />
            <StatTile label="Positive" value={summary.positive} tone="good" />
            <StatTile label="Neutral" value={summary.neutral} tone="neutral" />
            <StatTile label="Negative" value={summary.negative} tone="critical" />
            <StatTile label="Alerts" value={summary.alerts} tone="critical" />
          </div>

          <div className="charts-row">
            <div className="panel">
              <h2>Sentiment trend over time</h2>
              <ResponsiveContainer width="100%" height={240}>
                <LineChart data={trends} margin={{ left: -20 }}>
                  <CartesianGrid stroke="var(--gridline)" vertical={false} />
                  <XAxis
                    dataKey="date"
                    tick={{ fontSize: 11, fill: "var(--text-muted)" }}
                    axisLine={{ stroke: "var(--baseline)" }}
                    tickLine={false}
                  />
                  <YAxis
                    allowDecimals={false}
                    tick={{ fontSize: 11, fill: "var(--text-muted)" }}
                    axisLine={false}
                    tickLine={false}
                  />
                  <Tooltip content={<ChartTooltip />} />
                  <Line
                    type="monotone"
                    dataKey="positive"
                    stroke={STATUS_HEX.positive}
                    strokeWidth={2}
                    dot={{ r: 3 }}
                  />
                  <Line
                    type="monotone"
                    dataKey="neutral"
                    stroke={STATUS_HEX.neutral}
                    strokeWidth={2}
                    dot={{ r: 3 }}
                  />
                  <Line
                    type="monotone"
                    dataKey="negative"
                    stroke={STATUS_HEX.negative}
                    strokeWidth={2}
                    dot={{ r: 3 }}
                  />
                </LineChart>
              </ResponsiveContainer>
              <div className="legend-row">
                {Object.entries(STATUS_HEX).map(([k, hex]) => (
                  <span className="legend-item" key={k}>
                    <span className="legend-dot" style={{ background: hex }} />
                    {k}
                  </span>
                ))}
              </div>
            </div>

            <div className="panel">
              <h2>Sentiment distribution</h2>
              <ResponsiveContainer width="100%" height={240}>
                <BarChart data={distribution} margin={{ left: -20 }}>
                  <CartesianGrid stroke="var(--gridline)" vertical={false} />
                  <XAxis
                    dataKey="sentiment"
                    tick={{ fontSize: 11, fill: "var(--text-muted)" }}
                    axisLine={{ stroke: "var(--baseline)" }}
                    tickLine={false}
                  />
                  <YAxis
                    allowDecimals={false}
                    tick={{ fontSize: 11, fill: "var(--text-muted)" }}
                    axisLine={false}
                    tickLine={false}
                  />
                  <Tooltip content={<ChartTooltip />} />
                  <Bar dataKey="count" radius={[4, 4, 0, 0]} maxBarSize={64}>
                    {distribution.map((d) => (
                      <Cell key={d.sentiment} fill={STATUS_HEX[d.sentiment]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="panel">
            <h2>Negative review alerts ({alerts.length})</h2>
            {alerts.length === 0 && (
              <div className="empty-state">No alerts yet.</div>
            )}
            {alerts.slice(0, 8).map((a) => (
              <div className="alert-item" key={a.id}>
                <div>{a.message}</div>
                <div className="meta">
                  {a.product} &middot; review #{a.review_id}
                </div>
              </div>
            ))}
          </div>

          <div className="panel">
            <h2>Reviews</h2>
            <div className="filter-row">
              {["all", "positive", "neutral", "negative"].map((f) => (
                <button
                  key={f}
                  className={`filter-chip ${sentimentFilter === f ? "active" : ""}`}
                  onClick={() => setSentimentFilter(f)}
                >
                  {f}
                </button>
              ))}
            </div>
            <div className="table-scroll">
              <table>
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Product</th>
                    <th>Rating</th>
                    <th>Sentiment</th>
                    <th>Summary</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredReviews.map((r) => (
                    <tr key={r.id}>
                      <td>{r.date}</td>
                      <td>{r.product}</td>
                      <td>{r.rating}/5</td>
                      <td>
                        <SentimentBadge sentiment={r.sentiment} />
                      </td>
                      <td>{r.summary}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {filteredReviews.length === 0 && (
                <div className="empty-state">No reviews match this filter.</div>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
