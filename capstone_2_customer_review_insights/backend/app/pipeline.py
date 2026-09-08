import json
import re
import requests

from app.config import OPENROUTER_API_KEY, OPENROUTER_MODEL, USE_MOCK_LLM

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

SYSTEM_PROMPT = (
    "You are a customer feedback analyst. Given a single product review, "
    "respond with ONLY a JSON object (no markdown, no extra text) with these keys:\n"
    '  "sentiment": one of "positive", "negative", "neutral"\n'
    '  "summary": a single short sentence (max 20 words) summarizing the review\n'
    '  "negative_reason": if sentiment is "negative", a short phrase naming the root '
    'cause (e.g. "product defect", "shipping damage", "poor support response"); '
    "otherwise null"
)


class PipelineError(Exception):
    pass


def _extract_json(text: str) -> dict:
    text = text.strip()
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise PipelineError(f"No JSON object found in model response: {text[:200]}")
    return json.loads(match.group(0))


_NEGATIVE_REASON_KEYWORDS = {
    "support": "poor support response",
    "customer service": "poor support response",
    "broke": "product defect",
    "broken": "product defect",
    "crack": "product defect",
    "defect": "product defect",
    "stopped": "product defect",
    "leak": "product defect",
    "damaged": "shipping damage",
    "arrived": "shipping damage",
    "missing": "shipping/fulfillment issue",
    "loud": "quality below expectations",
    "smell": "quality below expectations",
    "slow": "performance below expectations",
    "warm": "safety concern",
}


def _mock_analyze_review(review_text: str, rating: int) -> dict:
    if rating <= 2:
        sentiment = "negative"
    elif rating == 3:
        sentiment = "neutral"
    else:
        sentiment = "positive"

    words = review_text.strip().split()
    summary = " ".join(words[:18]) + ("..." if len(words) > 18 else "")

    negative_reason = None
    if sentiment == "negative":
        lower = review_text.lower()
        negative_reason = "general dissatisfaction"
        for keyword, reason in _NEGATIVE_REASON_KEYWORDS.items():
            if keyword in lower:
                negative_reason = reason
                break

    return {
        "sentiment": sentiment,
        "summary": summary,
        "negative_reason": negative_reason,
    }


def analyze_review(review_text: str, product: str, rating: int) -> dict:
    if USE_MOCK_LLM:
        return _mock_analyze_review(review_text, rating)

    if not OPENROUTER_API_KEY:
        raise PipelineError("OPENROUTER_API_KEY is not set")

    user_prompt = (
        f"Product: {product}\n"
        f"Star rating: {rating}/5\n"
        f"Review: {review_text}"
    )

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
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.2,
        },
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()
    content = data["choices"][0]["message"]["content"]
    parsed = _extract_json(content)

    sentiment = parsed.get("sentiment", "neutral").lower().strip()
    if sentiment not in {"positive", "negative", "neutral"}:
        sentiment = "neutral"

    return {
        "sentiment": sentiment,
        "summary": parsed.get("summary", "").strip(),
        "negative_reason": parsed.get("negative_reason"),
    }
