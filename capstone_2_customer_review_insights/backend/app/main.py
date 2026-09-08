from collections import defaultdict
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db import init_db, get_session, Review, Alert
from app.ingest import ingest_reviews

app = FastAPI(title="Customer Review Insights API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()


@app.post("/api/ingest")
def run_ingest(db: Session = Depends(get_session)):
    return ingest_reviews(db)


@app.get("/api/reviews")
def list_reviews(sentiment: str | None = None, product: str | None = None,
                  db: Session = Depends(get_session)):
    query = db.query(Review)
    if sentiment:
        query = query.filter(Review.sentiment == sentiment)
    if product:
        query = query.filter(Review.product == product)
    reviews = query.order_by(Review.review_date.desc()).all()
    return [
        {
            "id": r.id,
            "product": r.product,
            "customer_name": r.customer_name,
            "rating": r.rating,
            "date": r.review_date,
            "review_text": r.review_text,
            "sentiment": r.sentiment,
            "summary": r.summary,
            "negative_reason": r.negative_reason,
            "is_alert": r.is_alert,
        }
        for r in reviews
    ]


@app.get("/api/summary")
def summary(db: Session = Depends(get_session)):
    total = db.query(func.count(Review.id)).scalar() or 0
    counts = dict(
        db.query(Review.sentiment, func.count(Review.id))
        .group_by(Review.sentiment)
        .all()
    )
    alert_count = db.query(func.count(Review.id)).filter(Review.is_alert.is_(True)).scalar() or 0
    return {
        "total_reviews": total,
        "positive": counts.get("positive", 0),
        "negative": counts.get("negative", 0),
        "neutral": counts.get("neutral", 0),
        "alerts": alert_count,
    }


@app.get("/api/trends")
def trends(db: Session = Depends(get_session)):
    reviews = db.query(Review.review_date, Review.sentiment).all()
    by_date = defaultdict(lambda: {"positive": 0, "negative": 0, "neutral": 0})
    for date, sentiment in reviews:
        if sentiment in by_date[date]:
            by_date[date][sentiment] += 1

    return [
        {"date": date, **counts}
        for date, counts in sorted(by_date.items())
    ]


@app.get("/api/alerts")
def list_alerts(db: Session = Depends(get_session)):
    alerts = db.query(Alert).order_by(Alert.created_at.desc()).all()
    return [
        {
            "id": a.id,
            "review_id": a.review_id,
            "product": a.product,
            "message": a.message,
            "created_at": a.created_at.isoformat(),
            "acknowledged": a.acknowledged,
        }
        for a in alerts
    ]


@app.post("/api/alerts/{alert_id}/acknowledge")
def acknowledge_alert(alert_id: int, db: Session = Depends(get_session)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        return {"error": "not found"}
    alert.acknowledged = True
    db.commit()
    return {"ok": True}
