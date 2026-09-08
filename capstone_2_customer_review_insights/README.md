# Capstone 2: AI-Powered Customer Review Insights Pipeline

**Build order: 1st (lowest effort)**

## Goal
Automated pipeline that ingests customer reviews, summarizes them, runs sentiment
analysis, logs results for trend monitoring, and alerts on negative reviews.

## Dataset
AI-generated customer reviews (to be generated as part of this project — no external
download needed).

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
Not started. Scaffold only.

## Resources needed from you
- OpenRouter API key (add to `.env` when ready to run — see `.env.example`)
- Confirm which model on OpenRouter to use (e.g. a cheap fast model for
  summarization/sentiment classification)
