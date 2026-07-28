"""
Pepper Clinical Infinity V6 — Licensing & Subscription state
© 2026 Lamya F. H. Ali — All Rights Reserved
"""
import secrets
from datetime import datetime, timedelta, timezone
from enum import Enum

GRACE_DAYS = 2  # فترة سماح يومين بعد انتهاء الاشتراك


class PlanKey(str, Enum):
    INDIVIDUAL_MONTHLY = "individual_monthly"
    INDIVIDUAL_YEARLY = "individual_yearly"
    INSTITUTION_MONTHLY = "institution_monthly"
    INSTITUTION_YEARLY = "institution_yearly"
    TRIAL = "trial"


PLAN_SEATS = {
    PlanKey.INDIVIDUAL_MONTHLY: 1,
    PlanKey.INDIVIDUAL_YEARLY: 1,
    PlanKey.INSTITUTION_MONTHLY: 10,
    PlanKey.INSTITUTION_YEARLY: 10,
    PlanKey.TRIAL: 1,
}

PLAN_DAYS = {
    PlanKey.INDIVIDUAL_MONTHLY: 30,
    PlanKey.INDIVIDUAL_YEARLY: 365,
    PlanKey.INSTITUTION_MONTHLY: 30,
    PlanKey.INSTITUTION_YEARLY: 365,
    PlanKey.TRIAL: 15,
}

PLAN_PRICE_GBP = {
    PlanKey.INDIVIDUAL_MONTHLY: 49,
    PlanKey.INDIVIDUAL_YEARLY: 399,
    PlanKey.INSTITUTION_MONTHLY: 399,
    PlanKey.INSTITUTION_YEARLY: 3990,
    PlanKey.TRIAL: 0,
}


def issue_license_key() -> str:
    """PEPPER-XXXX-XXXX-XXXX-XXXX"""
    blocks = ["".join(secrets.choice("ABCDEFGHJKLMNPQRSTUVWXYZ23456789")
                      for _ in range(4)) for _ in range(4)]
    return "PEPPER-" + "-".join(blocks)


def expiry_for(plan: PlanKey, start=None) -> datetime:
    start = start or datetime.now(timezone.utc)
    return start + timedelta(days=PLAN_DAYS[plan])


def grace_end(expiry: datetime) -> datetime:
    return expiry + timedelta(days=GRACE_DAYS)


def license_status(expiry: datetime) -> str:
    """active | grace | expired"""
    now = datetime.now(timezone.utc)
    if now < expiry:
        return "active"
    if now < grace_end(expiry):
        return "grace"
    return "expired"


def is_usable(expiry: datetime) -> bool:
    """التطبيق يشتغل في active أو grace فقط"""
    return license_status(expiry) in ("active", "grace")


def seats_for(plan: PlanKey) -> int:
    return PLAN_SEATS.get(plan, 1)
