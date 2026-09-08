# Capstone 1: AI-Powered Plant Health Detection

**Build order: 4th (highest effort)**

## Goal
Identify a plant and detect leaf diseases from an uploaded image, then use
Generative AI to give friendly explanations: what the plant is, watering needs,
why it might be dying, and treatment recommendations.

## Dataset
https://www.kaggle.com/datasets/vipoooool/new-plant-diseases-dataset (or personal
home plant photos).

## Deliverables
A web app where a user can upload a leaf/plant image, get it analyzed, and receive
a natural-language explanation (plant identity, watering requirements, current
condition, cure/treatment).

## Approach taken
No GPU/Kaggle credentials in this sandbox, so instead of training a CNN, plant ID +
disease detection is done in one call to a **vision-capable LLM via OpenRouter**
(`openai/gpt-4o-mini`, which accepts image input). The uploaded photo is sent
directly to the model along with a prompt asking for identification, health
assessment, and friendly guidance — no training pipeline or dataset download
needed, and it generalizes to plants/diseases outside any fixed training set.

## Stack
- Backend: Python (FastAPI) — single `/api/analyze` endpoint, stateless (no DB)
- Vision + explanation: OpenRouter vision model in one call (identification,
  health assessment, and friendly explanation all come from the same response)
- Frontend: React (Vite) with drag-and-drop image upload

## Status
Built and working end-to-end (backend + frontend), verified with two synthetic
test images (`data/sample_images/healthy_leaf.png`, `spotted_leaf.png`) also
available as one-click "try a sample" buttons in the app. Verified with
`USE_MOCK_LLM=true` in this sandbox since its network policy blocks
`openrouter.ai`; switch that off to use the real OpenRouter API key locally.

**Mock mode caveat:** the mock fallback only estimates health from color
statistics (green vs. brown/yellow pixel ratio) — it cannot identify plant
species. Real species identification and disease diagnosis require the actual
OpenRouter vision call (`USE_MOCK_LLM=false`).

## How to run

### Backend
```bash
cd backend
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
cp .env.example .env   # then fill in OPENROUTER_API_KEY
.venv/bin/uvicorn app.main:app --reload --port 8003
```
Endpoint: `POST /api/analyze` (multipart form field `image`).

### Frontend
```bash
cd frontend
npm install
npm run dev -- --port 5176
```
Open http://localhost:5176 — upload a photo or click a sample button.

## Resources needed from you
- Real OpenRouter API key for use outside this sandbox (set `USE_MOCK_LLM=false`
  in `backend/.env`) — a key was provided and stored locally in `backend/.env`,
  which is gitignored and never committed
- Confirmed model: `openai/gpt-4o-mini` (vision-capable) via OpenRouter
- Your own home plant photos (or the Kaggle dataset) for more realistic testing
  than the synthetic sample images included here
