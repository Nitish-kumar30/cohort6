# Capstone 3: Feature Request Intelligence Dashboard

**Build order: 2nd**

## Goal
Agent pulls in feedback from multiple sources (support tickets, reviews, surveys),
classifies each item by feature area, sentiment, and urgency, and feeds a dashboard
showing top requested features and trends over time.

## Dataset
AI-generated feedback for a fictional SaaS product ("TaskFlow"), across three
source files in `data/`: `support_tickets.json` (15), `reviews.json` (12), and
`surveys.json` (10) — 37 items total spanning support/security/billing issues and
feature requests (integrations, mobile, reporting, notifications, etc.).

## Feature-area taxonomy (fixed list)
Integrations, Mobile App, Reporting & Analytics, Security & Access, Billing,
Onboarding, UI/UX, Performance, Notifications, Other (see `backend/app/config.py`).

## Deliverables
1. Custom pipeline (Python, replacing the originally suggested n8n/Cowork workflow)
   that reads feedback from the three sources and classifies each item by feature
   area, sentiment, and urgency (low/medium/high/critical).
2. A dashboard (React frontend) showing top requested features, urgency
   breakdown, and weekly trends for the top feature areas over time.

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
.venv/bin/uvicorn app.main:app --reload --port 8001
```
Then trigger ingestion once: `curl -X POST http://127.0.0.1:8001/api/ingest`

Endpoints: `POST /api/ingest`, `GET /api/feedback`, `GET /api/summary`,
`GET /api/top-features`, `GET /api/trends`.

### Frontend
```bash
cd frontend
npm install
npm run dev -- --port 5174
```
Open http://localhost:5174 — the "Run pipeline" button re-triggers ingestion for
any new rows in the `data/` files.

## Resources needed from you
- Real OpenRouter API key for use outside this sandbox (set `USE_MOCK_LLM=false`
  in `backend/.env`) — a key was provided and stored locally in `backend/.env`,
  which is gitignored and never committed
- Confirmed model: `openai/gpt-4o-mini` via OpenRouter
