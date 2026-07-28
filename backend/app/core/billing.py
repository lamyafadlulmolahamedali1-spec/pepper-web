"""
Pepper Clinical Infinity V6 — Stripe Billing
© 2026 Lamya F. H. Ali — All Rights Reserved
"""
import os
import stripe
from app.core.licensing import PlanKey, PLAN_PRICE_GBP, PLAN_DAYS

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
CURRENCY = "gbp"

PLAN_INTERVAL = {
    PlanKey.INDIVIDUAL_MONTHLY: "month",
    PlanKey.INDIVIDUAL_YEARLY: "year",
    PlanKey.INSTITUTION_MONTHLY: "month",
    PlanKey.INSTITUTION_YEARLY: "year",
}

PLAN_LABEL = {
    PlanKey.INDIVIDUAL_MONTHLY: "Individual — Monthly (£49)",
    PlanKey.INDIVIDUAL_YEARLY: "Individual — Yearly (£399)",
    PlanKey.INSTITUTION_MONTHLY: "Institution 10 — Monthly (£399)",
    PlanKey.INSTITUTION_YEARLY: "Institution 10 — Yearly (£3990)",
}


def create_checkout_session(plan: PlanKey, email: str, success_url: str, cancel_url: str):
    return stripe.checkout.Session.create(
        mode="subscription",
        customer_email=email,
        line_items=[{
            "price_data": {
                "currency": CURRENCY,
                "product_data": {"name": "Pepper Clinical V6 — " + PLAN_LABEL[plan]},
                "unit_amount": PLAN_PRICE_GBP[plan] * 100,
                "recurring": {"interval": PLAN_INTERVAL[plan]},
            },
            "quantity": 1,
        }],
        metadata={"plan": plan.value},
        success_url=success_url + "?session_id={CHECKOUT_SESSION_ID}",
        cancel_url=cancel_url,
    )


def verify_webhook(payload: bytes, sig_header: str):
    return stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)


def parse_event(event: dict):
    """يرجّع (action, email, plan) — action: activate | renew | fail | cancel"""
    t = event.get("type", "")
    obj = event.get("data", {}).get("object", {})
    email = obj.get("customer_email") or obj.get("customer_details", {}).get("email", "")
    plan = obj.get("metadata", {}).get("plan", "")
    if t == "checkout.session.completed":
        return ("activate", email, plan)
    if t == "invoice.paid":
        return ("renew", email, plan)
    if t == "invoice.payment_failed":
        return ("fail", email, plan)
    if t == "customer.subscription.deleted":
        return ("cancel", email, plan)
    return ("ignore", email, plan)
