from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime, timezone

from app.config import DATABASE_URL

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True)
    product = Column(String, index=True)
    customer_name = Column(String)
    rating = Column(Integer)
    review_date = Column(String, index=True)
    review_text = Column(String)

    sentiment = Column(String, index=True)  # positive | negative | neutral
    summary = Column(String)
    negative_reason = Column(String, nullable=True)
    is_alert = Column(Boolean, default=False)
    processed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True)
    review_id = Column(Integer, index=True)
    product = Column(String)
    message = Column(String)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    acknowledged = Column(Boolean, default=False)


def init_db():
    Base.metadata.create_all(bind=engine)


def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
