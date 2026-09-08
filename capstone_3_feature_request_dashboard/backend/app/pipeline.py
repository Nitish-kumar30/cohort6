import json
import re
import requests

from app.config import (
    OPENROUTER_API_KEY,
    OPENROUTER_MODEL,
    USE_MOCK_LLM,
    FEATURE_AREAS,
    URGENCY_LEVELS,
)

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

SYSTEM_PROMPT = (
    "You are a product feedback analyst. Given a single piece of customer "
    "feedback (a support ticket, review, or survey response), respond with "
    "ONLY a JSON object (no markdown, no extra text) with these keys:\n"
    f'  "feature_area": exactly one of {FEATURE_AREAS}\n'
    '  "sentiment": one of "positive", "negative", "neutral"\n'
    f'  "urgency": exactly one of {URGENCY_LEVELS}\n'
    '  "summary": a single short sentence (max 20 words) summarizing the feedback'
)


class PipelineError(Exception):
    pass


def _extract_json(text: str) -> dict:
    text = text.strip()
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise PipelineError(f"No JSON object found in model response: {text[:200]}")
    return json.loads(match.group(0))


_FEATURE_KEYWORDS = [
    ("Integrations", ["slack", "teams integration", "zapier", "webhook", "calendar sync", "integration", "connector"]),
    ("Mobile App", ["mobile app", "android", "ios app", "the app crashes", "app crash"]),
    ("Reporting & Analytics", ["report", "export", "dashboard", "analytics", "breakdown", "date range"]),
    ("Security & Access", ["2fa", "two-factor", "security", "password", "locked", "authentication", "compliance"]),
    ("Billing", ["billing", "charge", "invoice", "refund", "plan tier", "upgrade"]),
    ("Onboarding", ["onboarding", "tutorial", "walkthrough", "new hires", "new users", "ramp-up", "docs are out of date"]),
    ("UI/UX", ["dark mode", "confusing", "clean ui", "ui ", "design"]),
    ("Performance", ["slow", "laggy", "lag", "sluggish", "crash", "load", "battery"]),
    ("Notifications", ["notification", "push notification", "reminder", "miss assignments", "alert"]),
]

_URGENT_WORDS = ["asap", "urgent", "blocking", "affecting our invoicing", "security gap", "double charged", "refund"]
_HIGH_WORDS = ["crash", "locked", "security", "24 hours", "4 days"]
_LOW_WORDS = ["would love", "would be amazing", "wish", "nice to have", "no major complaints", "very happy"]

_NEGATIVE_WORDS = ["frustrat", "crash", "confusing", "headache", "rough", "blocking", "disappointed", "slow", "laggy", "locked"]
_POSITIVE_WORDS = ["love", "great", "excellent", "happy", "solid", "amazing"]


def _mock_analyze(text: str) -> dict:
    lower = text.lower()

    feature_area = "Other"
    for area, keywords in _FEATURE_KEYWORDS:
        if any(k in lower for k in keywords):
            feature_area = area
            break

    if any(w in lower for w in _URGENT_WORDS):
        urgency = "critical"
    elif any(w in lower for w in _HIGH_WORDS):
        urgency = "high"
    elif any(w in lower for w in _LOW_WORDS):
        urgency = "low"
    else:
        urgency = "medium"

    if any(w in lower for w in _NEGATIVE_WORDS):
        sentiment = "negative"
    elif any(w in lower for w in _POSITIVE_WORDS):
        sentiment = "positive"
    else:
        sentiment = "neutral"

    words = text.strip().split()
    summary = " ".join(words[:18]) + ("..." if len(words) > 18 else "")

    return {
        "feature_area": feature_area,
        "sentiment": sentiment,
        "urgency": urgency,
        "summary": summary,
    }


def analyze_feedback(text: str) -> dict:
    if USE_MOCK_LLM:
        return _mock_analyze(text)

    if not OPENROUTER_API_KEY:
        raise PipelineError("OPENROUTER_API_KEY is not set")

    response = requests.post(
        OPENROUTER_URL,
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": OPENROUTER_MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Feedback: {text}"},
            ],
            "temperature": 0.2,
        },
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()
    content = data["choices"][0]["message"]["content"]
    parsed = _extract_json(content)

    feature_area = parsed.get("feature_area", "Other")
    if feature_area not in FEATURE_AREAS:
        feature_area = "Other"

    sentiment = parsed.get("sentiment", "neutral").lower().strip()
    if sentiment not in {"positive", "negative", "neutral"}:
        sentiment = "neutral"

    urgency = parsed.get("urgency", "medium").lower().strip()
    if urgency not in URGENCY_LEVELS:
        urgency = "medium"

    return {
        "feature_area": feature_area,
        "sentiment": sentiment,
        "urgency": urgency,
        "summary": parsed.get("summary", "").strip(),
    }
