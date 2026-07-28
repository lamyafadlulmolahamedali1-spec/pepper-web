"""Pydantic schemas. © 2026 Lamya F. H. Ali"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr


class TrialReq(BaseModel):
    full_name: str
    email: EmailStr
    child_name: str
    child_age: int = 6


class LoginReq(BaseModel):
    email: EmailStr
    pin: str


class TokenOut(BaseModel):
    access_token: str
    refresh_token: str
    user: dict


class ChildIn(BaseModel):
    name: str
    age: int = 6
    diagnosis: str = ""


class CheckoutReq(BaseModel):
    plan: str
    email: EmailStr


class SessionStart(BaseModel):
    child_id: str
    protocol: str = "ABA-DTT"


class SessionEnd(BaseModel):
    session_id: str
    duration_sec: int = 0
    score: int = 0
    tasks_total: int = 0
    tasks_success: int = 0
    tasks_fail: int = 0
    tasks_mastered: int = 0
    avg_attention: float = 0
    dominant_emotion: str = ""
