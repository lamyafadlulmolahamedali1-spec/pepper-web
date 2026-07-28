"""Stripe billing routes. © 2026 Lamya F. H. Ali"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.database import get_db, User
from app.core.billing import create_checkout_session, verify_webhook, parse_event
from app.core.licensing import PlanKey, expiry_for, issue_license_key, seats_for
from app.models.schemas import CheckoutReq

router = APIRouter(prefix="/api/billing", tags=["Billing"])


@router.get("/plans")
def plans():
    return {
        "individual_monthly": {"price_gbp": 49, "interval": "month", "seats": 1},
        "individual_yearly": {"price_gbp": 399, "interval": "year", "seats": 1},
        "institution_monthly": {"price_gbp": 399, "interval": "month", "seats": 10},
        "institution_yearly": {"price_gbp": 3990, "interval": "year", "seats": 10},
    }


@router.post("/checkout")
def checkout(body: CheckoutReq):
    try:
        plan = PlanKey(body.plan)
    except ValueError:
        raise HTTPException(status_code=400, detail="Unknown plan")
    if plan == PlanKey.TRIAL:
        raise HTTPException(status_code=400, detail="Trial is free")
    try:
        s = create_checkout_session(
            plan, body.email,
            success_url="https://your-domain.com/success",
            cancel_url="https://your-domain.com/cancel")
        return {"checkout_url": s.url, "session_id": s.id}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Stripe error: {e}")


@router.post("/webhook")
async def webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig = request.headers.get("stripe-signature", "")
    try:
        event = verify_webhook(payload, sig)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid signature")
    action, email, plan_str = parse_event(event)
    if action == "ignore" or not email:
        return {"ok": True}
    u = db.query(User).filter(User.email == email).first()
    if not u:
        return {"ok": True}
    try:
        plan = PlanKey(plan_str) if plan_str else PlanKey(u.plan)
    except ValueError:
        plan = PlanKey.INDIVIDUAL_MONTHLY
    if action in ("activate", "renew"):
        u.plan = plan.value
        u.expiry = expiry_for(plan)
        u.seats = seats_for(plan)
        if not u.license_key:
            u.license_key = issue_license_key()
    elif action == "cancel":
        # leave expiry as-is; grace period (2 days) handled by license_status
        pass
    # "fail" → do nothing; subscription stays until expiry + 2-day grace
    db.commit()
    return {"ok": True}
