"""PayPal subscription checkout confirmation and webhook routes."""

import time

from flask import abort, g, jsonify, redirect, request

from files.__main__ import app, limiter
from files.classes import PaypalSubscription, PaypalWebhookEvent
from files.helpers.config.const import DEFAULT_RATELIMIT_SLOWER
from files.helpers.patron_extras import ensure_patron_extras
from files.helpers.paypal import (
    PayPalError,
    cancel_paypal_subscription,
    get_paypal_subscription,
    recalculate_paypal_patron,
    reverse_paypal_payment,
    sync_paypal_transactions,
    upsert_paypal_subscription,
    verify_paypal_webhook,
)
from files.helpers.support import (
    PAYPAL_CHECKOUT_CONFIGURED,
    PAYPAL_CLIENT_ID,
    PAYPAL_MODE,
    PAYPAL_READY,
    PAYPAL_WEBHOOK_ID,
    paypal_custom_id,
)
from files.routes.wrappers import auth_required, get_ID


@app.context_processor
def paypal_support_template_context():
    if request.path != "/donate":
        return {}

    viewer = getattr(g, "v", None)
    current_subscription = None
    if viewer:
        current_subscription = g.db.query(PaypalSubscription).filter(
            PaypalSubscription.user_id == viewer.id,
            PaypalSubscription.status.in_(("ACTIVE", "APPROVAL_PENDING", "PAYMENT_FAILED")),
        ).order_by(PaypalSubscription.updated_utc.desc()).first()
        if current_subscription:
            recalculate_paypal_patron(g.db, viewer.id)
            ensure_patron_extras(g.db, viewer.id)

    return {
        "paypal_checkout_configured": PAYPAL_CHECKOUT_CONFIGURED,
        "paypal_ready": PAYPAL_READY,
        "paypal_webhook_configured": bool(PAYPAL_WEBHOOK_ID),
        "paypal_client_id": PAYPAL_CLIENT_ID,
        "paypal_mode": PAYPAL_MODE,
        "paypal_custom_id": paypal_custom_id(viewer.id) if viewer else "",
        "paypal_current_subscription": current_subscription,
    }


_SUBSCRIPTION_EVENT_STATUS = {
    "BILLING.SUBSCRIPTION.CANCELLED": "CANCELLED",
    "BILLING.SUBSCRIPTION.EXPIRED": "EXPIRED",
    "BILLING.SUBSCRIPTION.SUSPENDED": "SUSPENDED",
    "BILLING.SUBSCRIPTION.PAYMENT.FAILED": "PAYMENT_FAILED",
    "BILLING.SUBSCRIPTION.ACTIVATED": "ACTIVE",
}


@app.post("/api/paypal/subscriptions/confirm")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@auth_required
def confirm_paypal_subscription(v):
    subscription_id = request.values.get("subscription_id", "").strip()
    try:
        details = get_paypal_subscription(subscription_id)
        subscription, tier = upsert_paypal_subscription(
            g.db,
            details,
            forced_user_id=v.id,
        )
        grants = sync_paypal_transactions(g.db, subscription)
        ensure_patron_extras(g.db, v.id)
    except PayPalError as exc:
        return jsonify(ok=False, error=str(exc)), 502

    return jsonify(
        ok=True,
        subscription_id=subscription.subscription_id,
        status=subscription.status,
        tier=tier["name"],
        grants_processed=grants,
        message=(
            "Payment confirmed and supporter benefits activated."
            if grants
            else "Subscription approved. Benefits activate when PayPal confirms the payment."
        ),
    )


@app.post("/api/paypal/subscriptions/cancel")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@auth_required
def cancel_current_paypal_subscription(v):
    subscription = g.db.query(PaypalSubscription).filter(
        PaypalSubscription.user_id == v.id,
        PaypalSubscription.status == "ACTIVE",
    ).order_by(PaypalSubscription.updated_utc.desc()).first()
    if not subscription:
        abort(404)

    try:
        cancel_paypal_subscription(subscription.subscription_id)
    except PayPalError:
        return redirect("/donate?payment=cancel_error")

    now = int(time.time())
    subscription.status = "CANCELLED"
    subscription.cancelled_utc = now
    subscription.updated_utc = now
    g.db.add(subscription)
    g.db.flush()
    recalculate_paypal_patron(g.db, v.id)
    return redirect("/donate?payment=cancelled")


@app.post("/api/paypal/webhook")
@limiter.limit("120/minute")
def paypal_webhook():
    event = request.get_json(silent=True)
    if not isinstance(event, dict) or not event.get("id") or not event.get("event_type"):
        abort(400)

    try:
        verified = verify_paypal_webhook(request.headers, event)
    except PayPalError:
        abort(503)
    if not verified:
        abort(400)

    event_id = str(event["id"])
    existing = g.db.get(PaypalWebhookEvent, event_id)
    if existing and existing.processed:
        return "", 204

    event_type = str(event["event_type"])
    resource = event.get("resource") or {}
    resource_id = str(resource.get("id") or resource.get("billing_agreement_id") or "")
    now = int(time.time())
    event_record = existing or PaypalWebhookEvent(event_id=event_id, received_utc=now)
    event_record.event_type = event_type
    event_record.resource_id = resource_id or None
    event_record.processed = False
    g.db.add(event_record)
    g.db.flush()

    try:
        if event_type.startswith("BILLING.SUBSCRIPTION."):
            subscription_id = str(resource.get("id") or "")
            try:
                details = get_paypal_subscription(subscription_id)
            except PayPalError:
                details = resource
            subscription, _tier = upsert_paypal_subscription(
                g.db,
                details,
                status_override=_SUBSCRIPTION_EVENT_STATUS.get(event_type),
            )
            if event_type in {"BILLING.SUBSCRIPTION.ACTIVATED", "BILLING.SUBSCRIPTION.UPDATED"}:
                sync_paypal_transactions(g.db, subscription)
                ensure_patron_extras(g.db, subscription.user_id)

        elif event_type == "PAYMENT.SALE.COMPLETED":
            subscription_id = str(resource.get("billing_agreement_id") or "")
            details = get_paypal_subscription(subscription_id)
            subscription, _tier = upsert_paypal_subscription(g.db, details)
            sync_paypal_transactions(g.db, subscription)
            ensure_patron_extras(g.db, subscription.user_id)

        elif event_type in {"PAYMENT.SALE.REFUNDED", "PAYMENT.SALE.REVERSED"}:
            reverse_paypal_payment(
                g.db,
                resource,
                status="REFUNDED" if event_type.endswith("REFUNDED") else "REVERSED",
            )

    except PayPalError:
        abort(503)

    event_record.processed = True
    g.db.add(event_record)
    return "", 204
