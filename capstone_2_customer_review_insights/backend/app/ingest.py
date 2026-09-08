import json
import os
from sqlalchemy.orm import Session

from app.db import Review, Alert
from app.pipeline import analyze_review, PipelineError

DATA_FILE = os.path.join(
    os.path.dirname(__file__), "..", "..", "data", "reviews.json"
)


def load_raw_reviews(path: str = DATA_FILE) -> list[dict]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def ingest_reviews(db: Session, path: str = DATA_FILE) -> dict:
    raw_reviews = load_raw_reviews(path)

    existing_ids = {r.id for r in db.query(Review.id).all()}
    processed = 0
    alerts_created = 0
    errors = []

    for raw in raw_reviews:
        if raw["id"] in existing_ids:
            continue

        try:
            result = analyze_review(
                review_text=raw["review_text"],
                product=raw["product"],
                rating=raw["rating"],
            )
        except PipelineError as e:
            errors.append({"id": raw["id"], "error": str(e)})
            continue

        is_alert = result["sentiment"] == "negative" and raw["rating"] <= 2

        review = Review(
            id=raw["id"],
            product=raw["product"],
            customer_name=raw.get("customer_name", ""),
            rating=raw["rating"],
            review_date=raw["date"],
            review_text=raw["review_text"],
            sentiment=result["sentiment"],
            summary=result["summary"],
            negative_reason=result.get("negative_reason"),
            is_alert=is_alert,
        )
        db.add(review)
        processed += 1

        if is_alert:
            db.add(
                Alert(
                    review_id=raw["id"],
                    product=raw["product"],
                    message=(
                        f"Negative review for {raw['product']} "
                        f"({raw['rating']}/5): {result['summary']}"
                    ),
                )
            )
            alerts_created += 1

    db.commit()
    return {
        "processed": processed,
        "skipped_existing": len(raw_reviews) - processed - len(errors),
        "alerts_created": alerts_created,
        "errors": errors,
    }
