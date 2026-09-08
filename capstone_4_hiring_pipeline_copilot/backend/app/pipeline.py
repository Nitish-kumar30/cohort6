import json
import re
import requests

from app.config import OPENROUTER_API_KEY, OPENROUTER_MODEL, USE_MOCK_LLM, VERDICTS

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

SYSTEM_PROMPT = (
    "You are a technical recruiter screening a resume against a job description. "
    "Respond with ONLY a JSON object (no markdown, no extra text) with these keys:\n"
    '  "score": an integer 0-100 rating overall fit for the role\n'
    f'  "verdict": exactly one of {VERDICTS}\n'
    '  "matched_skills": a list of skills/requirements from the job description '
    "the candidate clearly demonstrates\n"
    '  "missing_skills": a list of must-have skills from the job description the '
    "candidate does not demonstrate\n"
    '  "summary": a single short sentence (max 20 words) on overall fit'
)


class PipelineError(Exception):
    pass


def _extract_json(text: str) -> dict:
    text = text.strip()
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise PipelineError(f"No JSON object found in model response: {text[:200]}")
    return json.loads(match.group(0))


def _verdict_for_score(score: float) -> str:
    if score >= 75:
        return "strong_fit"
    if score >= 45:
        return "potential_fit"
    return "weak_fit"


_NEGATION_MARKERS = [
    "no ", "not ", "none ", "without ", "haven't", "hasn't", "n't have",
    "limited", "no formal", "no professional",
]


def _sentence_has_skill_without_negation(sentences: list[str], skill: str) -> bool:
    """A skill only counts as matched if at least one sentence mentioning it
    has no negation marker before the mention (avoids 'no experience with X'
    being read as a positive match for X)."""
    for sentence in sentences:
        idx = sentence.find(skill)
        if idx == -1:
            continue
        prefix = sentence[:idx]
        if not any(marker in prefix for marker in _NEGATION_MARKERS):
            return True
    return False


def _mock_analyze(resume_text: str, job: dict) -> dict:
    lower_resume = resume_text.lower()
    sentences = re.split(r"(?<=[.!?])\s+", lower_resume)

    must_have = job["must_have_skills"]
    nice_to_have = job.get("nice_to_have_skills", [])

    matched_must = [
        s for s in must_have if _sentence_has_skill_without_negation(sentences, s.lower())
    ]
    matched_nice = [
        s for s in nice_to_have if _sentence_has_skill_without_negation(sentences, s.lower())
    ]
    missing_must = [s for s in must_have if s not in matched_must]

    must_ratio = len(matched_must) / len(must_have) if must_have else 0
    nice_ratio = len(matched_nice) / len(nice_to_have) if nice_to_have else 0
    score = round(must_ratio * 80 + nice_ratio * 20)

    verdict = _verdict_for_score(score)

    if verdict == "strong_fit":
        summary = f"Strong match on {len(matched_must)}/{len(must_have)} must-have skills."
    elif verdict == "potential_fit":
        summary = f"Partial match, missing {', '.join(missing_must[:2]) or 'some'} skills."
    else:
        summary = "Limited overlap with required skills for this role."

    return {
        "score": score,
        "verdict": verdict,
        "matched_skills": matched_must + matched_nice,
        "missing_skills": missing_must,
        "summary": summary,
    }


def analyze_candidate(resume_text: str, job: dict) -> dict:
    if USE_MOCK_LLM:
        return _mock_analyze(resume_text, job)

    if not OPENROUTER_API_KEY:
        raise PipelineError("OPENROUTER_API_KEY is not set")

    user_prompt = (
        f"Job title: {job['title']}\n"
        f"Job description: {job['description']}\n"
        f"Must-have skills: {', '.join(job['must_have_skills'])}\n"
        f"Nice-to-have skills: {', '.join(job.get('nice_to_have_skills', []))}\n\n"
        f"Candidate resume: {resume_text}"
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

    score = max(0, min(100, int(parsed.get("score", 0))))
    verdict = parsed.get("verdict", "").strip()
    if verdict not in VERDICTS:
        verdict = _verdict_for_score(score)

    return {
        "score": score,
        "verdict": verdict,
        "matched_skills": parsed.get("matched_skills", []),
        "missing_skills": parsed.get("missing_skills", []),
        "summary": parsed.get("summary", "").strip(),
    }
