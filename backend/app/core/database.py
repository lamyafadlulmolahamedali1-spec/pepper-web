"""
Pepper Clinical Infinity V6 — Database (SQLAlchemy)
© 2026 Lamya F. H. Ali — All Rights Reserved
"""
import os
import secrets
from datetime import datetime, timezone

from sqlalchemy import (create_engine, Column, String, Integer, Float,
                        DateTime, Boolean, Index)
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

os.makedirs("data", exist_ok=True)
os.makedirs("logs", exist_ok=True)

engine = create_engine(settings.DATABASE_URL,
                       connect_args={"check_same_thread": False}
                       if settings.DATABASE_URL.startswith("sqlite") else {},
                       pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def _uuid():
    return secrets.token_hex(16)


def _now():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=_uuid)
    full_name = Column(String, default="")
    email = Column(String, unique=True, index=True)
    pin_hash = Column(String, default="")
    created_at = Column(DateTime, default=_now)
    # licensing
    plan = Column(String, default="trial")
    license_key = Column(String, default="")
    expiry = Column(DateTime, default=_now)
    seats = Column(Integer, default=1)
    stripe_customer = Column(String, default="")


class Child(Base):
    __tablename__ = "children"
    id = Column(String, primary_key=True, default=_uuid)
    parent_id = Column(String, index=True)
    name_enc = Column(String, default="")        # encrypted
    diagnosis_enc = Column(String, default="")   # encrypted
    age = Column(Integer, default=6)
    pin = Column(String, default="")
    created_at = Column(DateTime, default=_now)
    skill_motor = Column(Float, default=50)
    skill_cognitive = Column(Float, default=50)
    skill_verbal = Column(Float, default=50)
    skill_math = Column(Float, default=50)
    skill_social = Column(Float, default=50)
    total_sessions = Column(Integer, default=0)
    total_score = Column(Integer, default=0)


class TherapySession(Base):
    __tablename__ = "sessions"
    id = Column(String, primary_key=True, default=_uuid)
    user_id = Column(String, index=True)
    child_id = Column(String, index=True)
    started_at = Column(DateTime, default=_now)
    ended_at = Column(DateTime, nullable=True)
    duration_sec = Column(Integer, default=0)
    score = Column(Integer, default=0)
    tasks_total = Column(Integer, default=0)
    tasks_success = Column(Integer, default=0)
    tasks_fail = Column(Integer, default=0)
    tasks_mastered = Column(Integer, default=0)
    avg_attention = Column(Float, default=0)
    dominant_emotion = Column(String, default="")
    protocol = Column(String, default="ABA-DTT")


class TaskEvent(Base):
    __tablename__ = "task_events"
    id = Column(String, primary_key=True, default=_uuid)
    session_id = Column(String, index=True)
    child_id = Column(String, index=True)
    ts = Column(DateTime, default=_now)
    domain = Column(String, default="")
    task_type = Column(String, default="")
    success = Column(Integer, default=0)
    attention = Column(Float, default=0)
    emotion = Column(String, default="")


Index("ix_sessions_child_ended", TherapySession.child_id, TherapySession.ended_at)


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
