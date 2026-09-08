from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import DATABASE_URL

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class FeedbackItem(Base):
    __tablename__ = "feedback_items"

    id = Column(String, primary_key=True)  # e.g. TCK-101, REV-201, SUR-301
    source = Column(String, index=True)  # support_ticket | review | survey
    user = Column(String)
    feedback_date = Column(String, index=True)
    text = Column(String)

    feature_area = Column(String, index=True)
    sentiment = Column(String, index=True)  # positive | negative | neutral
    urgency = Column(String, index=True)  # low | medium | high | critical
    summary = Column(String)


def init_db():
    Base.metadata.create_all(bind=engine)


def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
