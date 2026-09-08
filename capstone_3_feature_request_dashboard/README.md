# Capstone 3: Feature Request Intelligence Dashboard

**Build order: 2nd**

## Goal
Agent pulls in feedback from multiple sources (support tickets, reviews, surveys),
classifies each item by feature area, sentiment, and urgency, and feeds a dashboard
showing top requested features and trends over time.

## Dataset
AI-generated tickets, reviews, and surveys (to be generated as part of this project).

## Deliverables
1. Custom pipeline (Python, replacing the originally suggested n8n/Cowork workflow)
   that reads feedback from the three sources and classifies by feature area,
   sentiment, and urgency.
2. A dashboard (React frontend) showing top requested features and trends over time.

## Stack
- Backend: Python (FastAPI)
- Frontend: React (Vite)
- Storage: SQLite
- LLM: OpenRouter API (`OPENROUTER_API_KEY` via `.env`)

## Status
Not started. Scaffold only.

## Resources needed from you
- OpenRouter API key (see `.env.example`)
- Confirm the feature-area taxonomy (fixed list vs. open-ended/LLM-discovered)
