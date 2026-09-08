from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import DATABASE_URL

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Role(Base):
    __tablename__ = "roles"

    id = Column(String, primary_key=True)  # e.g. ROLE-BE
    title = Column(String)
    department = Column(String)
    seniority = Column(String)


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(String, primary_key=True)  # e.g. CAND-001
    name = Column(String)
    role_id = Column(String, index=True)
    role_title = Column(String)
    applied_date = Column(String, index=True)
    resume_text = Column(String)

    score = Column(Float)  # 0-100
    verdict = Column(String, index=True)  # strong_fit | potential_fit | weak_fit
    matched_skills = Column(String)  # comma-separated
    missing_skills = Column(String)  # comma-separated
    summary = Column(String)


def init_db():
    Base.metadata.create_all(bind=engine)


def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
