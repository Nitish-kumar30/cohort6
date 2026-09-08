# Capstone 2: AI-Powered Customer Review Insights Pipeline

**Build order: 1st (lowest effort)**

## Goal
Automated pipeline that ingests customer reviews, summarizes them, runs sentiment
analysis, logs results for trend monitoring, and alerts on negative reviews.

## Dataset
AI-generated customer reviews — see `data/reviews.json` (35 reviews across 10
fictional products, mix of positive/negative/neutral, includes rating, date,
product, and review text).

## Deliverables
1. Custom pipeline (Python, replacing the originally suggested n8n workflow) that
   reads reviews and writes sentiment/summary results to a database.
2. A web app (React frontend) that displays sentiment analysis and trends over time.

## Stack
- Backend: Python (FastAPI)
- Frontend: React (Vite)
- Storage: SQLite (swap for Postgres later if needed)
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
.venv/bin/uvicorn app.main:app --reload --port 8000
```
Then trigger ingestion once: `curl -X POST http://127.0.0.1:8000/api/ingest`

Endpoints: `POST /api/ingest`, `GET /api/reviews`, `GET /api/summary`,
`GET /api/trends`, `GET /api/alerts`, `POST /api/alerts/{id}/acknowledge`.

### Frontend
```bash
cd frontend
npm install
npm run dev
```
Open http://localhost:5173 — the "Run pipeline" button re-triggers ingestion for
any new rows in `data/reviews.json`.

## Resources needed from you
- Real OpenRouter API key for use outside this sandbox (set `USE_MOCK_LLM=false`
  in `backend/.env`) — a key was provided and stored locally in `backend/.env`,
  which is gitignored and never committed
- Confirmed model: `openai/gpt-4o-mini` via OpenRouter
