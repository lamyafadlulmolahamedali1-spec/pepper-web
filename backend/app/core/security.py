"""
Pepper Clinical Infinity V6 — Security (bcrypt · JWT · Fernet)
© 2026 Lamya F. H. Ali — All Rights Reserved
"""
import base64
import hashlib
from datetime import datetime, timedelta, timezone

import bcrypt
from jose import jwt, JWTError
from cryptography.fernet import Fernet

from app.core.config import settings


def hash_secret(plain: str) -> str:
    pw = plain.encode("utf-8")[:72]
    return bcrypt.hashpw(pw, bcrypt.gensalt(rounds=settings.BCRYPT_ROUNDS)).decode("utf-8")


def verify_secret(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode("utf-8")[:72], hashed.encode("utf-8"))
    except Exception:
        return False


def _fernet() -> Fernet:
    key = hashlib.sha256(settings.ENCRYPTION_KEY.encode()).digest()
    return Fernet(base64.urlsafe_b64encode(key))


def encrypt_field(value: str) -> str:
    if value is None:
        return ""
    return _fernet().encrypt(value.encode("utf-8")).decode("utf-8")


def decrypt_field(token: str) -> str:
    if not token:
        return ""
    try:
        return _fernet().decrypt(token.encode("utf-8")).decode("utf-8")
    except Exception:
        return ""


def make_token(sub: str, kind: str = "access", extra: dict | None = None) -> str:
    now = datetime.now(timezone.utc)
    exp = now + (timedelta(minutes=settings.ACCESS_MIN) if kind == "access"
                 else timedelta(days=settings.REFRESH_DAYS))
    payload = {"sub": sub, "kind": kind, "iat": now, "exp": exp}
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)


def read_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALG])
    except JWTError:
        return None
