"""Auth dependency. © 2026 Lamya F. H. Ali"""
from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from app.core.database import get_db, User
from app.core.security import read_token


def get_current_user(authorization: str = Header(default=""),
                     db: Session = Depends(get_db)) -> User:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = read_token(authorization[7:])
    if not payload or payload.get("kind") != "access":
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.id == payload["sub"]).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user
