"""Auth + licensing. © 2026 Lamya F. H. Ali"""
from datetime import datetime, timezone
import secrets
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db, User, Child
from app.core.security import (hash_secret, verify_secret, make_token,
                               read_token, encrypt_field)
from app.core.licensing import (PlanKey, issue_license_key, expiry_for,
                                license_status, seats_for)
from app.models.schemas import TrialReq, LoginReq, TokenOut

router = APIRouter(prefix="/api/auth", tags=["Auth"])


def _user_dict(u: User):
    return {"id": u.id, "full_name": u.full_name, "email": u.email,
            "plan": u.plan, "license_key": u.license_key,
            "expiry": u.expiry.isoformat() if u.expiry else None,
            "status": license_status(u.expiry) if u.expiry else "expired",
            "seats": u.seats}


@router.post("/trial", status_code=201)
def trial(body: TrialReq, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == body.email).first():
        raise HTTPException(status_code=409, detail="Email already registered")
    pin = "".join(secrets.choice("0123456789") for _ in range(6))
    u = User(full_name=body.full_name, email=body.email,
             pin_hash=hash_secret(pin), plan=PlanKey.TRIAL.value,
             license_key=issue_license_key(),
             expiry=expiry_for(PlanKey.TRIAL), seats=1)
    db.add(u); db.commit(); db.refresh(u)
    c = Child(parent_id=u.id, name_enc=encrypt_field(body.child_name),
              age=body.child_age, pin="".join(secrets.choice("0123456789") for _ in range(4)))
    db.add(c); db.commit()
    return {"user_id": u.id, "pin": pin, "license_key": u.license_key,
            "expiry": u.expiry.isoformat(),
            "message": "Trial created. Save your PIN — it will not be shown again."}


@router.post("/login", response_model=TokenOut)
def login(body: LoginReq, db: Session = Depends(get_db)):
    u = db.query(User).filter(User.email == body.email).first()
    if not u or not verify_secret(body.pin, u.pin_hash):
        raise HTTPException(status_code=401, detail="Invalid email or PIN")
    return TokenOut(access_token=make_token(u.id, "access"),
                    refresh_token=make_token(u.id, "refresh"),
                    user=_user_dict(u))


@router.post("/refresh", response_model=TokenOut)
def refresh(refresh_token: str, db: Session = Depends(get_db)):
    p = read_token(refresh_token)
    if not p or p.get("kind") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    u = db.query(User).filter(User.id == p["sub"]).first()
    if not u:
        raise HTTPException(status_code=401, detail="User not found")
    return TokenOut(access_token=make_token(u.id, "access"),
                    refresh_token=make_token(u.id, "refresh"),
                    user=_user_dict(u))
