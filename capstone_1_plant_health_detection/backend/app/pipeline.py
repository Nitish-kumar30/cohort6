import base64
import io
import json
import re

import requests
from PIL import Image

from app.config import OPENROUTER_API_KEY, OPENROUTER_VISION_MODEL, USE_MOCK_LLM

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

SYSTEM_PROMPT = (
    "You are a friendly plant-care expert helping a home gardener understand a "
    "photo of their plant. Look closely at the leaves, stems, and any visible "
    "soil. Respond with ONLY a JSON object (no markdown, no extra text) with "
    "these keys:\n"
    '  "plant_name": your best guess at the plant\'s common name and species '
    '(e.g. "Fiddle Leaf Fig (Ficus lyrata)"), or "Unable to identify" if unclear\n'
    '  "confidence": "high", "medium", or "low" - your confidence in the '
    "identification\n"
    '  "is_healthy": true or false - overall health assessment\n'
    '  "condition_summary": one short friendly sentence describing what you see '
    "(discoloration, spots, wilting, healthy growth, etc.)\n"
    '  "likely_issue": the most likely disease, pest, or care issue if unhealthy '
    '(e.g. "Early blight", "Overwatering / root stress", "Spider mites"), or '
    'null if healthy\n'
    '  "watering_guidance": one or two friendly sentences on watering frequency '
    "and light needs for this type of plant\n"
    '  "treatment_recommendations": a list of 2-4 short, concrete, actionable '
    "steps to treat the issue or maintain health\n"
    '  "friendly_explanation": a warm, conversational paragraph (3-5 sentences) '
    "explaining the diagnosis to a home gardener in plain language, as if "
    "talking to a friend"
)


class PipelineError(Exception):
    pass


def _extract_json(text: str) -> dict:
    text = text.strip()
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise PipelineError(f"No JSON object found in model response: {text[:200]}")
    return json.loads(match.group(0))


def _mock_analyze(image_bytes: bytes) -> dict:
    """Color-heuristic fallback. Cannot identify plant species - only gives a
    rough health signal from color statistics, to exercise the app's flow
    when a real vision-capable LLM call isn't available (offline/sandboxed)."""
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img = img.resize((64, 64))
    pixels = list(img.getdata())

    green_dominant = 0
    brown_or_yellow = 0
    for r, g, b in pixels:
        if g > r and g > b and g > 60:
            green_dominant += 1
        elif r > 100 and g > 60 and b < 90 and r >= g:
            brown_or_yellow += 1

    total = len(pixels)
    green_ratio = green_dominant / total
    spot_ratio = brown_or_yellow / total

    is_healthy = green_ratio > 0.35 and spot_ratio < 0.08

    if is_healthy:
        condition_summary = "Leaves look predominantly green and vibrant in this photo."
        likely_issue = None
        treatment = [
            "Keep up the current watering and light routine.",
            "Rotate the pot occasionally so growth stays even.",
            "Wipe leaves gently to keep dust off and support photosynthesis.",
        ]
        friendly = (
            "Good news - based on the color and coverage in this photo, your plant "
            "looks like it's in decent shape right now! There's a healthy amount of "
            "green visible with no major discoloration jumping out. Keep an eye on "
            "the soil moisture and light exposure, and it should keep doing well. "
            "If you notice any new spots or wilting, that'd be a good time to take "
            "another photo and check again."
        )
    else:
        condition_summary = "This photo shows noticeable discoloration or brown/yellow patches."
        likely_issue = "Possible leaf discoloration (could be over/under-watering, nutrient stress, or early disease)"
        treatment = [
            "Check soil moisture before watering again - avoid both bone-dry and soggy soil.",
            "Trim off any clearly dead or badly spotted leaves.",
            "Move the plant to a spot with appropriate indirect light for its type.",
            "Monitor for a few days and re-photograph to see if it's improving.",
        ]
        friendly = (
            "Looking at this photo, I'm seeing some brown or yellow patches mixed in "
            "with the green, which usually points to some kind of stress - most often "
            "watering issues, nutrient deficiency, or the early stages of a leaf disease. "
            "It's not necessarily an emergency, but it's worth investigating soon. Start "
            "with the basics: check the soil isn't staying too wet or drying out "
            "completely, and trim off the most affected leaves so the plant can focus "
            "energy on healthy growth."
        )

    return {
        "plant_name": "Unable to identify (mock mode - species ID requires a real vision model call)",
        "confidence": "low",
        "is_healthy": is_healthy,
        "condition_summary": condition_summary,
        "likely_issue": likely_issue,
        "watering_guidance": (
            "General rule of thumb: water most houseplants when the top inch of soil "
            "feels dry, and provide bright, indirect light unless your species prefers "
            "otherwise."
        ),
        "treatment_recommendations": treatment,
        "friendly_explanation": friendly,
    }


def analyze_plant_image(image_bytes: bytes, content_type: str) -> dict:
    if USE_MOCK_LLM:
        return _mock_analyze(image_bytes)

    if not OPENROUTER_API_KEY:
        raise PipelineError("OPENROUTER_API_KEY is not set")

    encoded = base64.b64encode(image_bytes).decode("utf-8")
    data_url = f"data:{content_type};base64,{encoded}"

    response = requests.post(
        OPENROUTER_URL,
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": OPENROUTER_VISION_MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Here is a photo of my plant. What can you tell me about it?",
                        },
                        {"type": "image_url", "image_url": {"url": data_url}},
                    ],
                },
            ],
            "temperature": 0.3,
        },
        timeout=60,
    )
    response.raise_for_status()
    data = response.json()
    content = data["choices"][0]["message"]["content"]
    parsed = _extract_json(content)

    return {
        "plant_name": parsed.get("plant_name", "Unable to identify"),
        "confidence": parsed.get("confidence", "low"),
        "is_healthy": bool(parsed.get("is_healthy", True)),
        "condition_summary": parsed.get("condition_summary", ""),
        "likely_issue": parsed.get("likely_issue"),
        "watering_guidance": parsed.get("watering_guidance", ""),
        "treatment_recommendations": parsed.get("treatment_recommendations", []),
        "friendly_explanation": parsed.get("friendly_explanation", ""),
    }
