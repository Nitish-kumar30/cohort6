from collections import defaultdict
from datetime import datetime, timedelta
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db import init_db, get_session, Role, Candidate
from app.ingest import ingest_pipeline

app = FastAPI(title="Hiring Pipeline Copilot API")

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
    return ingest_pipeline(db)


@app.get("/api/roles")
def list_roles(db: Session = Depends(get_session)):
    roles = db.query(Role).all()
    return [
        {"id": r.id, "title": r.title, "department": r.department, "seniority": r.seniority}
        for r in roles
    ]


@app.get("/api/candidates")
def list_candidates(
    role_id: str | None = None,
    verdict: str | None = None,
    db: Session = Depends(get_session),
):
    query = db.query(Candidate)
    if role_id:
        query = query.filter(Candidate.role_id == role_id)
    if verdict:
        query = query.filter(Candidate.verdict == verdict)

    candidates = query.order_by(Candidate.score.desc()).all()
    return [
        {
            "id": c.id,
            "name": c.name,
            "role_id": c.role_id,
            "role_title": c.role_title,
            "applied_date": c.applied_date,
            "score": c.score,
            "verdict": c.verdict,
            "matched_skills": [s for s in c.matched_skills.split(", ") if s],
            "missing_skills": [s for s in c.missing_skills.split(", ") if s],
            "summary": c.summary,
        }
        for c in candidates
    ]


@app.get("/api/summary")
def summary(db: Session = Depends(get_session)):
    total = db.query(func.count(Candidate.id)).scalar() or 0
    by_verdict = dict(
        db.query(Candidate.verdict, func.count(Candidate.id)).group_by(Candidate.verdict).all()
    )
    avg_score = db.query(func.avg(Candidate.score)).scalar() or 0
    return {
        "total_candidates": total,
        "by_verdict": by_verdict,
        "avg_score": round(avg_score, 1),
        "open_roles": db.query(func.count(Role.id)).scalar() or 0,
    }


@app.get("/api/pipeline-health")
def pipeline_health(db: Session = Depends(get_session)):
    roles = db.query(Role).all()
    result = []
    for role in roles:
        candidates = db.query(Candidate).filter(Candidate.role_id == role.id).all()
        total = len(candidates)
        avg_score = round(sum(c.score for c in candidates) / total, 1) if total else 0
        by_verdict = defaultdict(int)
        for c in candidates:
            by_verdict[c.verdict] += 1

        result.append(
            {
                "role_id": role.id,
                "role_title": role.title,
                "department": role.department,
                "total_candidates": total,
                "avg_score": avg_score,
                "strong_fit": by_verdict.get("strong_fit", 0),
                "potential_fit": by_verdict.get("potential_fit", 0),
                "weak_fit": by_verdict.get("weak_fit", 0),
            }
        )
    return result


def _week_start(date_str: str) -> str:
    d = datetime.strptime(date_str, "%Y-%m-%d")
    monday = d - timedelta(days=d.weekday())
    return monday.strftime("%Y-%m-%d")


@app.get("/api/trends")
def trends(db: Session = Depends(get_session)):
    roles = db.query(Role).all()
    role_titles = [r.title for r in roles]

    rows = db.query(Candidate.applied_date, Candidate.role_title).all()
    by_week = defaultdict(lambda: defaultdict(int))
    for date_str, role_title in rows:
        week = _week_start(date_str)
        by_week[week][role_title] += 1

    result = []
    for week in sorted(by_week.keys()):
        row = {"week": week}
        for title in role_titles:
            row[title] = by_week[week].get(title, 0)
        result.append(row)

    return {"series_keys": role_titles, "data": result}
