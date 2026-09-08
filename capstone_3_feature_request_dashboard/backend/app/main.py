from collections import defaultdict
from datetime import datetime, timedelta
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db import init_db, get_session, FeedbackItem
from app.ingest import ingest_feedback

app = FastAPI(title="Feature Request Intelligence API")

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
    return ingest_feedback(db)


@app.get("/api/feedback")
def list_feedback(
    source: str | None = None,
    feature_area: str | None = None,
    sentiment: str | None = None,
    urgency: str | None = None,
    db: Session = Depends(get_session),
):
    query = db.query(FeedbackItem)
    if source:
        query = query.filter(FeedbackItem.source == source)
    if feature_area:
        query = query.filter(FeedbackItem.feature_area == feature_area)
    if sentiment:
        query = query.filter(FeedbackItem.sentiment == sentiment)
    if urgency:
        query = query.filter(FeedbackItem.urgency == urgency)

    items = query.order_by(FeedbackItem.feedback_date.desc()).all()
    return [
        {
            "id": i.id,
            "source": i.source,
            "user": i.user,
            "date": i.feedback_date,
            "text": i.text,
            "feature_area": i.feature_area,
            "sentiment": i.sentiment,
            "urgency": i.urgency,
            "summary": i.summary,
        }
        for i in items
    ]


@app.get("/api/summary")
def summary(db: Session = Depends(get_session)):
    total = db.query(func.count(FeedbackItem.id)).scalar() or 0
    by_source = dict(
        db.query(FeedbackItem.source, func.count(FeedbackItem.id)).group_by(FeedbackItem.source).all()
    )
    by_urgency = dict(
        db.query(FeedbackItem.urgency, func.count(FeedbackItem.id)).group_by(FeedbackItem.urgency).all()
    )
    by_sentiment = dict(
        db.query(FeedbackItem.sentiment, func.count(FeedbackItem.id)).group_by(FeedbackItem.sentiment).all()
    )
    return {
        "total_feedback": total,
        "by_source": by_source,
        "by_urgency": by_urgency,
        "by_sentiment": by_sentiment,
    }


@app.get("/api/top-features")
def top_features(db: Session = Depends(get_session)):
    rows = (
        db.query(FeedbackItem.feature_area, func.count(FeedbackItem.id))
        .group_by(FeedbackItem.feature_area)
        .order_by(func.count(FeedbackItem.id).desc())
        .all()
    )
    return [{"feature_area": area, "count": count} for area, count in rows]


def _week_start(date_str: str) -> str:
    d = datetime.strptime(date_str, "%Y-%m-%d")
    monday = d - timedelta(days=d.weekday())
    return monday.strftime("%Y-%m-%d")


@app.get("/api/trends")
def trends(db: Session = Depends(get_session)):
    top_areas = [
        row[0]
        for row in db.query(FeedbackItem.feature_area, func.count(FeedbackItem.id))
        .group_by(FeedbackItem.feature_area)
        .order_by(func.count(FeedbackItem.id).desc())
        .limit(4)
        .all()
    ]

    rows = db.query(FeedbackItem.feedback_date, FeedbackItem.feature_area).all()
    by_week = defaultdict(lambda: defaultdict(int))
    for date_str, feature_area in rows:
        week = _week_start(date_str)
        key = feature_area if feature_area in top_areas else "Other"
        by_week[week][key] += 1

    series_keys = top_areas + ["Other"]
    result = []
    for week in sorted(by_week.keys()):
        row = {"week": week}
        for key in series_keys:
            row[key] = by_week[week].get(key, 0)
        result.append(row)

    return {"series_keys": series_keys, "data": result}
