# Capstone 4: Hiring Pipeline Copilot

**Build order: 3rd**

## Goal
Agent screens incoming resumes against a job description, scores and tags
candidates, and feeds a dashboard tracking pipeline health (volume, quality) by role.

## Dataset
AI-generated resumes and job descriptions (to be generated as part of this project).

## Deliverables
1. Custom pipeline (Python, replacing the originally suggested n8n/Cowork workflow)
   that reads resumes and job descriptions, scores/tags candidates against the JD.
2. A web app (React frontend) that displays candidate pipeline health by role.

## Stack
- Backend: Python (FastAPI) — includes resume text/PDF extraction
- Frontend: React (Vite)
- Storage: SQLite
- LLM: OpenRouter API (`OPENROUTER_API_KEY` via `.env`)

## Status
Not started. Scaffold only.

## Resources needed from you
- OpenRouter API key (see `.env.example`)
- Sample job description(s) and desired scoring criteria (skills match, experience,
  etc.) — or confirm the LLM should design the rubric itself
