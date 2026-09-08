# Capstone 4: Hiring Pipeline Copilot

**Build order: 3rd**

## Goal
Agent screens incoming resumes against a job description, scores and tags
candidates, and feeds a dashboard tracking pipeline health (volume, quality) by role.

## Dataset
AI-generated job descriptions and resumes for a fictional company, in `data/`:
- `job_descriptions.json` — 4 open roles (Backend Engineer, Frontend Engineer, Data
  Analyst, Product Marketing Manager), each with must-have and nice-to-have skills.
- `resumes.json` — 24 candidates (6 per role) applied over ~4 weeks, deliberately
  spanning strong/partial/weak fits so the pipeline health dashboard has a realistic
  spread.

## Scoring approach
Score 0-100 = 80% weight on must-have skill coverage + 20% on nice-to-have coverage.
Verdict thresholds: `strong_fit` ≥75, `potential_fit` ≥45, else `weak_fit`. The mock
heuristic also checks for negation ("no experience with X") so a resume stating it
lacks a skill isn't miscounted as a match.

## Deliverables
1. Custom pipeline (Python, replacing the originally suggested n8n/Cowork workflow)
   that reads resumes and job descriptions, scores/tags candidates against the JD.
2. A web app (React frontend) that displays candidate pipeline health by role.

## Stack
- Backend: Python (FastAPI)
- Frontend: React (Vite + recharts)
- Storage: SQLite
- LLM: OpenRouter API (`OPENROUTER_API_KEY` via `.env`)

## Status
Built and working end-to-end (backend + frontend). Verified with `USE_MOCK_LLM=true`
in this sandbox since its network policy blocks `openrouter.ai`; switch that off to
use the real OpenRouter API key locally.

## How to run

### Backend
```bash
cd backend
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
cp .env.example .env   # then fill in OPENROUTER_API_KEY
.venv/bin/uvicorn app.main:app --reload --port 8002
```
Then trigger ingestion once: `curl -X POST http://127.0.0.1:8002/api/ingest`

Endpoints: `POST /api/ingest`, `GET /api/roles`, `GET /api/candidates`,
`GET /api/summary`, `GET /api/pipeline-health`, `GET /api/trends`.

### Frontend
```bash
cd frontend
npm install
npm run dev -- --port 5175
```
Open http://localhost:5175 — the "Run pipeline" button re-triggers ingestion for
any new rows in the `data/` files.

## Resources needed from you
- Real OpenRouter API key for use outside this sandbox (set `USE_MOCK_LLM=false`
  in `backend/.env`) — a key was provided and stored locally in `backend/.env`,
  which is gitignored and never committed
- Confirmed model: `openai/gpt-4o-mini` via OpenRouter
