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

## Stack
- Image classification: pretrained/fine-tuned CNN on the Kaggle dataset (or a
  pretrained plant-ID model) — this is the one component that is genuine ML work,
  not just LLM orchestration
- Backend: Python (FastAPI)
- Frontend: React (Vite) with image upload
- LLM: OpenRouter API (`OPENROUTER_API_KEY` via `.env`) for the explanation layer

## Status
Not started. Scaffold only.

## Resources needed from you
- OpenRouter API key (see `.env.example`)
- Decide: train a small CNN ourselves on the Kaggle dataset, or use an existing
  pretrained plant-ID/disease-classification model/API (faster, less effort)
- If training locally: confirm GPU availability, since this environment may be
  CPU-only
