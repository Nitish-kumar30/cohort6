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

const ROLE_PALETTE = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"];
const FALLBACK_ROLE_COLOR = "#898781";

const SHORT_ROLE_NAME = {
  "Backend Engineer": "Backend Eng.",
  "Frontend Engineer": "Frontend Eng.",
  "Data Analyst": "Data Analyst",
  "Product Marketing Manager": "Product Mktg.",
};

function shortRoleName(title) {
  return SHORT_ROLE_NAME[title] || title;
}

const VERDICT_COLORS = {
  strong_fit: "#0ca30c",
  potential_fit: "#fab219",
  weak_fit: "#d03b3b",
};
const VERDICT_LABELS = {
  strong_fit: "Strong fit",
  potential_fit: "Potential fit",
  weak_fit: "Weak fit",
};

function StatTile({ label, value }) {
  return (
    <div className="stat-tile">
      <div className="label">{label}</div>
      <div className="value">{value}</div>
    </div>
  );
}

function VerdictBadge({ verdict }) {
  return <span className={`badge ${verdict}`}>{VERDICT_LABELS[verdict] || verdict}</span>;
}

function ChartTooltip({ active, payload, label, colorFor, labelFor }) {
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
          {labelFor ? labelFor(p.dataKey) : p.dataKey}: {p.value}
        </div>
      ))}
    </div>
  );
}

export default function App() {
  const [summary, setSummary] = useState(null);
  const [roles, setRoles] = useState([]);
  const [pipelineHealth, setPipelineHealth] = useState([]);
  const [trends, setTrends] = useState({ series_keys: [], data: [] });
  const [candidates, setCandidates] = useState([]);
  const [roleFilter, setRoleFilter] = useState("all");
  const [verdictFilter, setVerdictFilter] = useState("all");
  const [loading, setLoading] = useState(true);
  const [ingesting, setIngesting] = useState(false);

  async function loadAll() {
    setLoading(true);
    const [summaryRes, rolesRes, healthRes, trendsRes, candidatesRes] = await Promise.all([
      fetch("/api/summary").then((r) => r.json()),
      fetch("/api/roles").then((r) => r.json()),
      fetch("/api/pipeline-health").then((r) => r.json()),
      fetch("/api/trends").then((r) => r.json()),
      fetch("/api/candidates").then((r) => r.json()),
    ]);
    setSummary(summaryRes);
    setRoles(rolesRes);
    setPipelineHealth(healthRes);
    setTrends(trendsRes);
    setCandidates(candidatesRes);
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

  const roleColor = useMemo(() => {
    const map = {};
    roles.forEach((r, i) => {
      map[r.title] = ROLE_PALETTE[i % ROLE_PALETTE.length] || FALLBACK_ROLE_COLOR;
    });
    return (title) => map[title] || FALLBACK_ROLE_COLOR;
  }, [roles]);

  const filteredCandidates = useMemo(() => {
    return candidates.filter((c) => {
      if (roleFilter !== "all" && c.role_id !== roleFilter) return false;
      if (verdictFilter !== "all" && c.verdict !== verdictFilter) return false;
      return true;
    });
  }, [candidates, roleFilter, verdictFilter]);

  return (
    <div className="app">
      <div className="app-header">
        <div>
          <h1>Hiring Pipeline Copilot</h1>
          <div className="subtitle">
            Resumes screened against job descriptions, scored and tagged by fit
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
            <StatTile label="Open roles" value={summary.open_roles} />
            <StatTile label="Total candidates" value={summary.total_candidates} />
            <StatTile label="Avg score" value={summary.avg_score} />
            <StatTile label="Strong fits" value={summary.by_verdict?.strong_fit || 0} />
          </div>

          <div className="charts-row">
            <div className="panel">
              <h2>Pipeline health by role (volume &amp; quality)</h2>
              <ResponsiveContainer width="100%" height={280}>
                <BarChart data={pipelineHealth} margin={{ left: -20 }}>
                  <CartesianGrid stroke="var(--gridline)" vertical={false} />
                  <XAxis
                    dataKey="role_title"
                    tickFormatter={shortRoleName}
                    interval={0}
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
                  <Tooltip
                    content={
                      <ChartTooltip
                        colorFor={(k) => VERDICT_COLORS[k]}
                        labelFor={(k) => VERDICT_LABELS[k] || k}
                      />
                    }
                  />
                  <Bar dataKey="strong_fit" stackId="a" fill={VERDICT_COLORS.strong_fit} radius={[0, 0, 0, 0]} />
                  <Bar dataKey="potential_fit" stackId="a" fill={VERDICT_COLORS.potential_fit} />
                  <Bar dataKey="weak_fit" stackId="a" fill={VERDICT_COLORS.weak_fit} radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
              <div className="legend-row">
                {Object.entries(VERDICT_COLORS).map(([k, hex]) => (
                  <span className="legend-item" key={k}>
                    <span className="legend-dot" style={{ background: hex }} />
                    {VERDICT_LABELS[k]}
                  </span>
                ))}
              </div>
            </div>

            <div className="panel">
              <h2>Average fit score by role</h2>
              <ResponsiveContainer width="100%" height={280}>
                <BarChart data={pipelineHealth} margin={{ left: -20 }}>
                  <CartesianGrid stroke="var(--gridline)" vertical={false} />
                  <XAxis
                    dataKey="role_title"
                    tickFormatter={shortRoleName}
                    interval={0}
                    tick={{ fontSize: 11, fill: "var(--text-muted)" }}
                    axisLine={{ stroke: "var(--baseline)" }}
                    tickLine={false}
                  />
                  <YAxis
                    domain={[0, 100]}
                    tick={{ fontSize: 11, fill: "var(--text-muted)" }}
                    axisLine={false}
                    tickLine={false}
                  />
                  <Tooltip content={<ChartTooltip colorFor={(k, d) => roleColor(k)} />} />
                  <Bar dataKey="avg_score" radius={[4, 4, 0, 0]} maxBarSize={56}>
                    {pipelineHealth.map((r) => (
                      <Cell key={r.role_id} fill={roleColor(r.role_title)} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="panel">
            <h2>Applications over time by role (weekly)</h2>
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
                <Tooltip content={<ChartTooltip colorFor={roleColor} />} />
                {trends.series_keys.map((key) => (
                  <Line
                    key={key}
                    type="monotone"
                    dataKey={key}
                    stroke={roleColor(key)}
                    strokeWidth={2}
                    dot={{ r: 3 }}
                  />
                ))}
              </LineChart>
            </ResponsiveContainer>
            <div className="legend-row">
              {trends.series_keys.map((key) => (
                <span className="legend-item" key={key}>
                  <span className="legend-dot" style={{ background: roleColor(key) }} />
                  {key}
                </span>
              ))}
            </div>
          </div>

          <div className="panel">
            <h2>Candidates ({filteredCandidates.length})</h2>
            <div className="filter-row">
              <button
                className={`filter-chip ${roleFilter === "all" ? "active" : ""}`}
                onClick={() => setRoleFilter("all")}
              >
                all roles
              </button>
              {roles.map((r) => (
                <button
                  key={r.id}
                  className={`filter-chip ${roleFilter === r.id ? "active" : ""}`}
                  onClick={() => setRoleFilter(r.id)}
                >
                  {r.title}
                </button>
              ))}
            </div>
            <div className="filter-row">
              {["all", "strong_fit", "potential_fit", "weak_fit"].map((v) => (
                <button
                  key={v}
                  className={`filter-chip ${verdictFilter === v ? "active" : ""}`}
                  onClick={() => setVerdictFilter(v)}
                >
                  {v === "all" ? "all verdicts" : VERDICT_LABELS[v]}
                </button>
              ))}
            </div>
            <div className="table-scroll">
              <table>
                <thead>
                  <tr>
                    <th>Applied</th>
                    <th>Candidate</th>
                    <th>Role</th>
                    <th>Score</th>
                    <th>Verdict</th>
                    <th>Skills</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredCandidates.map((c) => (
                    <tr key={c.id}>
                      <td>{c.applied_date}</td>
                      <td>{c.name}</td>
                      <td>{c.role_title}</td>
                      <td className="score-cell">{c.score}</td>
                      <td>
                        <VerdictBadge verdict={c.verdict} />
                      </td>
                      <td>
                        {c.matched_skills.map((s) => (
                          <span className="skill-tag" key={`m-${s}`}>
                            {s}
                          </span>
                        ))}
                        {c.missing_skills.map((s) => (
                          <span className="skill-tag missing" key={`x-${s}`}>
                            missing: {s}
                          </span>
                        ))}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {filteredCandidates.length === 0 && (
                <div className="empty-state">No candidates match this filter.</div>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
