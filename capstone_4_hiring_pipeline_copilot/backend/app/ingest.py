import json
import os
from sqlalchemy.orm import Session

from app.db import Role, Candidate
from app.pipeline import analyze_candidate, PipelineError

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")


def load_roles() -> list[dict]:
    with open(os.path.join(DATA_DIR, "job_descriptions.json"), "r", encoding="utf-8") as f:
        return json.load(f)


def load_resumes() -> list[dict]:
    with open(os.path.join(DATA_DIR, "resumes.json"), "r", encoding="utf-8") as f:
        return json.load(f)


def ingest_pipeline(db: Session) -> dict:
    roles = load_roles()
    roles_by_id = {r["id"]: r for r in roles}

    existing_role_ids = {r.id for r in db.query(Role.id).all()}
    for role in roles:
        if role["id"] in existing_role_ids:
            continue
        db.add(
            Role(
                id=role["id"],
                title=role["title"],
                department=role["department"],
                seniority=role["seniority"],
            )
        )
    db.commit()

    resumes = load_resumes()
    existing_candidate_ids = {c.id for c in db.query(Candidate.id).all()}
    processed = 0
    errors = []

    for resume in resumes:
        if resume["id"] in existing_candidate_ids:
            continue

        job = roles_by_id.get(resume["role_id"])
        if not job:
            errors.append({"id": resume["id"], "error": f"unknown role_id {resume['role_id']}"})
            continue

        try:
            result = analyze_candidate(resume["resume_text"], job)
        except PipelineError as e:
            errors.append({"id": resume["id"], "error": str(e)})
            continue

        db.add(
            Candidate(
                id=resume["id"],
                name=resume["name"],
                role_id=resume["role_id"],
                role_title=job["title"],
                applied_date=resume["applied_date"],
                resume_text=resume["resume_text"],
                score=result["score"],
                verdict=result["verdict"],
                matched_skills=", ".join(result["matched_skills"]),
                missing_skills=", ".join(result["missing_skills"]),
                summary=result["summary"],
            )
        )
        processed += 1

    db.commit()
    return {
        "processed": processed,
        "skipped_existing": len(resumes) - processed - len(errors),
        "errors": errors,
    }
