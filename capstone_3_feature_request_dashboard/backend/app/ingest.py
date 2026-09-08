import json
import os
from sqlalchemy.orm import Session

from app.db import FeedbackItem
from app.pipeline import analyze_feedback, PipelineError

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")
SOURCE_FILES = ["support_tickets.json", "reviews.json", "surveys.json"]


def load_raw_feedback() -> list[dict]:
    items = []
    for filename in SOURCE_FILES:
        path = os.path.join(DATA_DIR, filename)
        with open(path, "r", encoding="utf-8") as f:
            items.extend(json.load(f))
    return items


def ingest_feedback(db: Session) -> dict:
    raw_items = load_raw_feedback()

    existing_ids = {row.id for row in db.query(FeedbackItem.id).all()}
    processed = 0
    errors = []

    for raw in raw_items:
        if raw["id"] in existing_ids:
            continue

        try:
            result = analyze_feedback(raw["text"])
        except PipelineError as e:
            errors.append({"id": raw["id"], "error": str(e)})
            continue

        db.add(
            FeedbackItem(
                id=raw["id"],
                source=raw["source"],
                user=raw.get("user", ""),
                feedback_date=raw["date"],
                text=raw["text"],
                feature_area=result["feature_area"],
                sentiment=result["sentiment"],
                urgency=result["urgency"],
                summary=result["summary"],
            )
        )
        processed += 1

    db.commit()
    return {
        "processed": processed,
        "skipped_existing": len(raw_items) - processed - len(errors),
        "errors": errors,
    }
