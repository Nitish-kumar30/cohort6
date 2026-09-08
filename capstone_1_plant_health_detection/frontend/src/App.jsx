import { useCallback, useRef, useState } from "react";

const SAMPLE_IMAGES = [
  { label: "Try healthy sample", file: "/samples/healthy_leaf.png" },
  { label: "Try spotted sample", file: "/samples/spotted_leaf.png" },
];

function ConfidenceBadge({ confidence }) {
  return <span className="badge confidence">{confidence} confidence</span>;
}

function HealthBadge({ isHealthy }) {
  return (
    <span className={`badge ${isHealthy ? "healthy" : "unhealthy"}`}>
      {isHealthy ? "Looks healthy" : "Needs attention"}
    </span>
  );
}

export default function App() {
  const [file, setFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [dragging, setDragging] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);

  function setImage(f) {
    setFile(f);
    setPreviewUrl(URL.createObjectURL(f));
    setResult(null);
    setError(null);
  }

  function handleFileSelect(e) {
    const f = e.target.files?.[0];
    if (f) setImage(f);
  }

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    setDragging(false);
    const f = e.dataTransfer.files?.[0];
    if (f) setImage(f);
  }, []);

  async function loadSample(path) {
    const res = await fetch(path);
    const blob = await res.blob();
    const f = new File([blob], path.split("/").pop(), { type: blob.type || "image/png" });
    setImage(f);
  }

  async function handleAnalyze() {
    if (!file) return;
    setAnalyzing(true);
    setError(null);
    setResult(null);
    try {
      const formData = new FormData();
      formData.append("image", file);
      const res = await fetch("/api/analyze", { method: "POST", body: formData });
      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.detail || `Request failed (${res.status})`);
      }
      const data = await res.json();
      setResult(data);
    } catch (e) {
      setError(e.message || "Something went wrong analyzing this image.");
    } finally {
      setAnalyzing(false);
    }
  }

  function handleClear() {
    setFile(null);
    setPreviewUrl(null);
    setResult(null);
    setError(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  }

  return (
    <div className="app">
      <div className="app-header">
        <h1>Plant Health Detective</h1>
        <div className="subtitle">
          Upload a photo of your plant to identify it and get friendly, plain-language
          guidance on watering, current condition, and how to treat any issues.
        </div>
      </div>

      <div className="panel">
        {!previewUrl && (
          <div
            className={`dropzone ${dragging ? "dragging" : ""}`}
            onClick={() => fileInputRef.current?.click()}
            onDragOver={(e) => {
              e.preventDefault();
              setDragging(true);
            }}
            onDragLeave={() => setDragging(false)}
            onDrop={handleDrop}
          >
            <div style={{ fontSize: 28 }}>🌿</div>
            <p>Click to upload, or drag and drop a JPEG, PNG, or WebP photo</p>
            <input
              ref={fileInputRef}
              type="file"
              accept="image/jpeg,image/png,image/webp"
              onChange={handleFileSelect}
            />
          </div>
        )}

        {previewUrl && (
          <div className="preview-row">
            <img src={previewUrl} alt="Uploaded plant" className="preview-img" />
            <div className="preview-meta">
              <div>{file?.name}</div>
              <div>{file ? `${(file.size / 1024).toFixed(0)} KB` : ""}</div>
            </div>
          </div>
        )}

        {!previewUrl && (
          <div className="sample-row">
            {SAMPLE_IMAGES.map((s) => (
              <button key={s.file} className="sample-btn" onClick={() => loadSample(s.file)}>
                {s.label}
              </button>
            ))}
          </div>
        )}

        {previewUrl && (
          <div>
            <button className="analyze-btn" onClick={handleAnalyze} disabled={analyzing}>
              {analyzing && <span className="spinner" />}
              {analyzing ? "Analyzing..." : "Analyze this plant"}
            </button>
            <button className="clear-btn" onClick={handleClear} disabled={analyzing}>
              Choose a different photo
            </button>
          </div>
        )}

        {error && <div className="error-box">{error}</div>}
      </div>

      {result && (
        <div className="panel">
          <div className="result-header">
            <h2>{result.plant_name}</h2>
            <div>
              <ConfidenceBadge confidence={result.confidence} />{" "}
              <HealthBadge isHealthy={result.is_healthy} />
            </div>
          </div>
          <p style={{ color: "var(--text-secondary)", fontSize: 13 }}>
            {result.condition_summary}
          </p>

          <div className="result-section">
            <h3>What's going on</h3>
            <p>{result.friendly_explanation}</p>
          </div>

          {result.likely_issue && (
            <div className="result-section">
              <h3>Likely issue</h3>
              <p>{result.likely_issue}</p>
            </div>
          )}

          <div className="result-section">
            <h3>Watering &amp; light</h3>
            <p>{result.watering_guidance}</p>
          </div>

          {result.treatment_recommendations?.length > 0 && (
            <div className="result-section">
              <h3>Recommended steps</h3>
              <ul className="treatment-list">
                {result.treatment_recommendations.map((step, i) => (
                  <li key={i}>{step}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {!result && !error && !previewUrl && (
        <div className="empty-state">
          No photo yet — upload one above or try a sample to see how it works.
        </div>
      )}
    </div>
  );
}
