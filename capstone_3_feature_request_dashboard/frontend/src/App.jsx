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

const FEATURE_COLORS = {
  "Integrations": "#2a78d6",
  "Mobile App": "#eb6834",
  "Reporting & Analytics": "#1baf7a",
  "Security & Access": "#eda100",
  "Billing": "#e87ba4",
  "Onboarding": "#008300",
  "UI/UX": "#4a3aa7",
  "Performance": "#e34948",
};
const FALLBACK_COLOR = "#898781";

function featureColor(name) {
  return FEATURE_COLORS[name] || FALLBACK_COLOR;
}

const URGENCY_ORDER = ["low", "medium", "high", "critical"];
const URGENCY_COLORS = {
  low: "#898781",
  medium: "#fab219",
  high: "#ec835a",
  critical: "#d03b3b",
};

function StatTile({ label, value }) {
  return (
    <div className="stat-tile">
      <div className="label">{label}</div>
      <div className="value">{value}</div>
    </div>
  );
}

function SentimentBadge({ sentiment }) {
  return <span className={`badge ${sentiment}`}>{sentiment}</span>;
}

function UrgencyBadge({ urgency }) {
  return <span className={`badge urgency-${urgency}`}>{urgency}</span>;
}

function ChartTooltip({ active, payload, label, colorFor }) {
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
        <div key={p.dataKey} style={{ color: colorFor ? colorFor(p.dataKey) : p.color }}>
          {p.dataKey}: {p.value}
        </div>
      ))}
    </div>
  );
}

export default function App() {
  const [summary, setSummary] = useState(null);
  const [topFeatures, setTopFeatures] = useState([]);
  const [trends, setTrends] = useState({ series_keys: [], data: [] });
  const [feedback, setFeedback] = useState([]);
  const [sourceFilter, setSourceFilter] = useState("all");
  const [urgencyFilter, setUrgencyFilter] = useState("all");
  const [featureFilter, setFeatureFilter] = useState("all");
  const [loading, setLoading] = useState(true);
  const [ingesting, setIngesting] = useState(false);

  async function loadAll() {
    setLoading(true);
    const [summaryRes, topRes, trendsRes, feedbackRes] = await Promise.all([
      fetch("/api/summary").then((r) => r.json()),
      fetch("/api/top-features").then((r) => r.json()),
      fetch("/api/trends").then((r) => r.json()),
      fetch("/api/feedback").then((r) => r.json()),
    ]);
    setSummary(summaryRes);
    setTopFeatures(topRes);
    setTrends(trendsRes);
    setFeedback(feedbackRes);
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

  const urgencyChartData = useMemo(() => {
    if (!summary) return [];
    return URGENCY_ORDER.map((u) => ({
      urgency: u,
      count: summary.by_urgency?.[u] || 0,
    }));
  }, [summary]);

  const featureOptions = useMemo(
    () => ["all", ...topFeatures.map((f) => f.feature_area)],
    [topFeatures]
  );

  const filteredFeedback = useMemo(() => {
    return feedback.filter((item) => {
      if (sourceFilter !== "all" && item.source !== sourceFilter) return false;
      if (urgencyFilter !== "all" && item.urgency !== urgencyFilter) return false;
      if (featureFilter !== "all" && item.feature_area !== featureFilter) return false;
      return true;
    });
  }, [feedback, sourceFilter, urgencyFilter, featureFilter]);

  return (
    <div className="app">
      <div className="app-header">
        <div>
          <h1>Feature Request Intelligence</h1>
          <div className="subtitle">
            Support tickets, reviews, and surveys classified by feature area,
            sentiment, and urgency
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
            <StatTile label="Total feedback" value={summary.total_feedback} />
            <StatTile label="Support tickets" value={summary.by_source?.support_ticket || 0} />
            <StatTile label="Reviews" value={summary.by_source?.review || 0} />
            <StatTile label="Surveys" value={summary.by_source?.survey || 0} />
          </div>

          <div className="charts-row">
            <div className="panel">
              <h2>Top requested features</h2>
              <ResponsiveContainer width="100%" height={280}>
                <BarChart
                  data={topFeatures}
                  layout="vertical"
                  margin={{ left: 24, right: 16 }}
                >
                  <CartesianGrid stroke="var(--gridline)" horizontal={false} />
                  <XAxis
                    type="number"
                    allowDecimals={false}
                    tick={{ fontSize: 11, fill: "var(--text-muted)" }}
                    axisLine={false}
                    tickLine={false}
                  />
                  <YAxis
                    type="category"
                    dataKey="feature_area"
                    width={140}
                    tick={{ fontSize: 11, fill: "var(--text-secondary)" }}
                    axisLine={{ stroke: "var(--baseline)" }}
                    tickLine={false}
                  />
                  <Tooltip content={<ChartTooltip colorFor={featureColor} />} />
                  <Bar dataKey="count" radius={[0, 4, 4, 0]} maxBarSize={20}>
                    {topFeatures.map((f) => (
                      <Cell key={f.feature_area} fill={featureColor(f.feature_area)} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div className="panel">
              <h2>Feedback by urgency</h2>
              <ResponsiveContainer width="100%" height={280}>
                <BarChart data={urgencyChartData} margin={{ left: -20 }}>
                  <CartesianGrid stroke="var(--gridline)" vertical={false} />
                  <XAxis
                    dataKey="urgency"
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
                  <Tooltip content={<ChartTooltip colorFor={() => "var(--text-primary)"} />} />
                  <Bar dataKey="count" radius={[4, 4, 0, 0]} maxBarSize={64}>
                    {urgencyChartData.map((d) => (
                      <Cell key={d.urgency} fill={URGENCY_COLORS[d.urgency]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="panel">
            <h2>Feature request trends over time (weekly)</h2>
            <ResponsiveContainer width="100%" height={260}>
              <LineChart data={trends.data} margin={{ left: -20 }}>
                <CartesianGrid stroke="var(--gridline)" vertical={false} />
                <XAxis
                  dataKey="week"
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
                <Tooltip content={<ChartTooltip colorFor={featureColor} />} />
                {trends.series_keys.map((key) => (
                  <Line
                    key={key}
                    type="monotone"
                    dataKey={key}
                    stroke={featureColor(key)}
                    strokeWidth={2}
                    dot={{ r: 3 }}
                  />
                ))}
              </LineChart>
            </ResponsiveContainer>
            <div className="legend-row">
              {trends.series_keys.map((key) => (
                <span className="legend-item" key={key}>
                  <span className="legend-dot" style={{ background: featureColor(key) }} />
                  {key}
                </span>
              ))}
            </div>
          </div>

          <div className="panel">
            <h2>Feedback ({filteredFeedback.length})</h2>
            <div className="filter-row">
              {["all", "support_ticket", "review", "survey"].map((f) => (
                <button
                  key={f}
                  className={`filter-chip ${sourceFilter === f ? "active" : ""}`}
                  onClick={() => setSourceFilter(f)}
                >
                  {f === "all" ? "all sources" : f.replace("_", " ")}
                </button>
              ))}
            </div>
            <div className="filter-row">
              {["all", ...URGENCY_ORDER].map((u) => (
                <button
                  key={u}
                  className={`filter-chip ${urgencyFilter === u ? "active" : ""}`}
                  onClick={() => setUrgencyFilter(u)}
                >
                  {u === "all" ? "all urgency" : u}
                </button>
              ))}
            </div>
            <div className="filter-row">
              <select
                value={featureFilter}
                onChange={(e) => setFeatureFilter(e.target.value)}
                style={{
                  padding: "6px 10px",
                  borderRadius: 8,
                  border: "1px solid var(--border)",
                  background: "var(--surface-1)",
                  color: "var(--text-primary)",
                  fontSize: 12,
                }}
              >
                {featureOptions.map((f) => (
                  <option key={f} value={f}>
                    {f === "all" ? "All feature areas" : f}
                  </option>
                ))}
              </select>
            </div>
            <div className="table-scroll">
              <table>
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Source</th>
                    <th>Feature area</th>
                    <th>Sentiment</th>
                    <th>Urgency</th>
                    <th>Summary</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredFeedback.map((item) => (
                    <tr key={item.id}>
                      <td>{item.date}</td>
                      <td>{item.source.replace("_", " ")}</td>
                      <td>
                        <span
                          className="legend-dot"
                          style={{
                            background: featureColor(item.feature_area),
                            display: "inline-block",
                            marginRight: 6,
                          }}
                        />
                        {item.feature_area}
                      </td>
                      <td>
                        <SentimentBadge sentiment={item.sentiment} />
                      </td>
                      <td>
                        <UrgencyBadge urgency={item.urgency} />
                      </td>
                      <td>{item.summary}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {filteredFeedback.length === 0 && (
                <div className="empty-state">No feedback matches this filter.</div>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
