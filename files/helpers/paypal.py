"""PayPal subscription API, verification, and patron fulfillment helpers."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import threading
import time

import requests

from files.classes import Badge, PaypalPayment, PaypalSubscription, User
from files.helpers.support import (
    PAYPAL_API_BASE,
    PAYPAL_CLIENT_ID,
    PAYPAL_CLIENT_SECRET,
    PAYPAL_CURRENCY,
    PAYPAL_WEBHOOK_ID,
    SUPPORT_TIER_BY_LEVEL,
    SUPPORT_TIER_BY_PLAN_ID,
    paypal_user_id_from_custom_id,
)


PATRON_BADGE_IDS = tuple(range(21, 26))
_TERMINAL_SUBSCRIPTION_STATUSES = {"CANCELLED", "EXPIRED", "SUSPENDED", "PAYMENT_FAILED"}
_token_lock = threading.Lock()
_token_cache = {"value": "", "expires_utc": 0}


class PayPalError(RuntimeError):
    pass


def _utc_timestamp(value):
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return int(parsed.timestamp())


def _paypal_time(value):
    return value.astimezone(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _access_token():
    now = int(time.time())
    if _token_cache["value"] and _token_cache["expires_utc"] > now + 60:
        return _token_cache["value"]

    if not PAYPAL_CLIENT_ID or not PAYPAL_CLIENT_SECRET:
        raise PayPalError("PayPal credentials are not configured")

    with _token_lock:
        now = int(time.time())
        if _token_cache["value"] and _token_cache["expires_utc"] > now + 60:
            return _token_cache["value"]

        try:
            response = requests.post(
                f"{PAYPAL_API_BASE}/v1/oauth2/token",
                auth=(PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET),
                data={"grant_type": "client_credentials"},
                headers={"Accept": "application/json", "Accept-Language": "en_US"},
                timeout=20,
            )
        except requests.RequestException as exc:
            raise PayPalError("Could not contact PayPal for an access token") from exc

        if response.status_code != 200:
            raise PayPalError(f"PayPal authentication failed with HTTP {response.status_code}")

        payload = response.json()
        token = str(payload.get("access_token") or "")
        if not token:
            raise PayPalError("PayPal returned no access token")
        expires_in = int(payload.get("expires_in") or 300)
        _token_cache.update(value=token, expires_utc=now + max(expires_in, 120))
        return token


def paypal_api_request(method, path, *, params=None, json=None):
    try:
        response = requests.request(
            method,
            f"{PAYPAL_API_BASE}{path}",
            params=params,
            json=json,
            headers={
                "Authorization": f"Bearer {_access_token()}",
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            timeout=25,
        )
    except requests.RequestException as exc:
        raise PayPalError("Could not contact PayPal") from exc

    if not 200 <= response.status_code < 300:
        try:
            details = response.json().get("message") or response.text
        except ValueError:
            details = response.text
        raise PayPalError(f"PayPal API HTTP {response.status_code}: {str(details)[:240]}")

    if response.status_code == 204 or not response.content:
        return {}
    try:
        return response.json()
    except ValueError as exc:
        raise PayPalError("PayPal returned an invalid JSON response") from exc


def get_paypal_subscription(subscription_id):
    subscription_id = str(subscription_id or "").strip()
    if not subscription_id.startswith("I-") or len(subscription_id) > 64:
        raise PayPalError("Invalid PayPal subscription ID")
    return paypal_api_request("GET", f"/v1/billing/subscriptions/{subscription_id}")


def cancel_paypal_subscription(subscription_id, reason="Cancelled by the subscriber"):
    subscription_id = str(subscription_id or "").strip()
    if not subscription_id.startswith("I-") or len(subscription_id) > 64:
        raise PayPalError("Invalid PayPal subscription ID")
    return paypal_api_request(
        "POST",
        f"/v1/billing/subscriptions/{subscription_id}/cancel",
        json={"reason": str(reason)[:128]},
    )


def list_paypal_transactions(subscription_id, *, days=31):
    now = datetime.now(timezone.utc)
    return paypal_api_request(
        "GET",
        f"/v1/billing/subscriptions/{subscription_id}/transactions",
        params={
            "start_time": _paypal_time(now - timedelta(days=days)),
            "end_time": _paypal_time(now + timedelta(minutes=10)),
        },
    ).get("transactions", [])


def verify_paypal_webhook(headers, event):
    if not PAYPAL_WEBHOOK_ID:
        raise PayPalError("PAYPAL_WEBHOOK_ID is not configured")

    required = {
        "auth_algo": headers.get("PAYPAL-AUTH-ALGO"),
        "cert_url": headers.get("PAYPAL-CERT-URL"),
        "transmission_id": headers.get("PAYPAL-TRANSMISSION-ID"),
        "transmission_sig": headers.get("PAYPAL-TRANSMISSION-SIG"),
        "transmission_time": headers.get("PAYPAL-TRANSMISSION-TIME"),
        "webhook_id": PAYPAL_WEBHOOK_ID,
        "webhook_event": event,
    }
    if any(value in (None, "") for key, value in required.items() if key != "webhook_event"):
        return False

    result = paypal_api_request(
        "POST",
        "/v1/notifications/verify-webhook-signature",
        json=required,
    )
    return result.get("verification_status") == "SUCCESS"


def _subscription_user_id(details, existing=None):
    custom_user_id = paypal_user_id_from_custom_id(details.get("custom_id"))
    if custom_user_id is not None:
        return custom_user_id
    if existing is not None:
        return existing.user_id
    raise PayPalError("PayPal subscription is missing a valid signed account reference")


def upsert_paypal_subscription(db, details, *, forced_user_id=None, status_override=None):
    subscription_id = str(details.get("id") or "").strip()
    plan_id = str(details.get("plan_id") or "").strip()
    tier = SUPPORT_TIER_BY_PLAN_ID.get(plan_id)
    if not subscription_id.startswith("I-") or not tier:
        raise PayPalError("PayPal subscription uses an unknown ID or plan")

    existing = db.get(PaypalSubscription, subscription_id)
    user_id = _subscription_user_id(details, existing)
    if forced_user_id is not None and user_id != int(forced_user_id):
        raise PayPalError("This PayPal subscription belongs to another account")
    if existing is not None and existing.user_id != user_id:
        raise PayPalError("PayPal subscription account association changed unexpectedly")
    if db.get(User, user_id) is None:
        raise PayPalError("The linked Obsession account no longer exists")

    now = int(time.time())
    status = str(status_override or details.get("status") or "APPROVAL_PENDING").upper()
    billing_info = details.get("billing_info") or {}
    subscriber = details.get("subscriber") or {}
    created_utc = _utc_timestamp(details.get("create_time")) or now
    next_billing_utc = _utc_timestamp(billing_info.get("next_billing_time"))

    record = existing or PaypalSubscription(
        subscription_id=subscription_id,
        user_id=user_id,
        created_utc=created_utc,
    )
    record.plan_id = plan_id
    record.tier = tier["level"]
    record.status = status
    record.payer_email = subscriber.get("email_address") or record.payer_email
    record.updated_utc = now
    record.next_billing_utc = next_billing_utc or record.next_billing_utc
    if status in _TERMINAL_SUBSCRIPTION_STATUSES:
        record.cancelled_utc = record.cancelled_utc or now
    elif status == "ACTIVE":
        record.cancelled_utc = None

    db.add(record)
    db.flush()
    recalculate_paypal_patron(db, user_id)
    return record, tier


def _gross_money(transaction):
    breakdown = transaction.get("amount_with_breakdown") or {}
    gross = breakdown.get("gross_amount") or {}
    currency = str(gross.get("currency_code") or "").upper()
    value = str(gross.get("value") or "")
    try:
        cents = int((Decimal(value) * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    except (InvalidOperation, ValueError):
        raise PayPalError("PayPal transaction has an invalid amount")
    return cents, currency


def record_completed_paypal_transaction(db, subscription, transaction):
    payment_id = str(transaction.get("id") or "").strip()
    if not payment_id or str(transaction.get("status") or "").upper() != "COMPLETED":
        return False

    existing = db.get(PaypalPayment, payment_id)
    if existing is not None:
        return False

    tier = SUPPORT_TIER_BY_LEVEL.get(subscription.tier)
    if not tier:
        raise PayPalError("PayPal transaction maps to an unknown support tier")

    gross_cents, currency = _gross_money(transaction)
    expected_cents = int(tier["price"]) * 100
    if currency != PAYPAL_CURRENCY or gross_cents != expected_cents:
        raise PayPalError("PayPal transaction amount does not match the configured support tier")

    user = db.query(User).filter(User.id == subscription.user_id).with_for_update().one()
    now = int(time.time())
    payment_utc = _utc_timestamp(transaction.get("time")) or now
    granted = int(tier["wishbux"])

    payment = PaypalPayment(
        payment_id=payment_id,
        subscription_id=subscription.subscription_id,
        user_id=user.id,
        tier=tier["level"],
        gross_cents=gross_cents,
        currency=currency,
        status="COMPLETED",
        wishbux_granted=granted,
        created_utc=payment_utc,
        updated_utc=now,
    )
    user.marseybux = int(user.marseybux or 0) + granted
    subscription.status = "ACTIVE"
    subscription.last_payment_utc = max(int(subscription.last_payment_utc or 0), payment_utc)
    subscription.updated_utc = now
    subscription.cancelled_utc = None

    db.add(payment)
    db.add(subscription)
    db.add(user)
    db.flush()
    recalculate_paypal_patron(db, user.id)
    return True


def sync_paypal_transactions(db, subscription):
    granted = 0
    for transaction in list_paypal_transactions(subscription.subscription_id):
        if record_completed_paypal_transaction(db, subscription, transaction):
            granted += 1
    return granted


def recalculate_paypal_patron(db, user_id):
    user = db.query(User).filter(User.id == int(user_id)).with_for_update().one_or_none()
    if user is None:
        return None

    paid_subscription_ids = {
        row[0]
        for row in db.query(PaypalPayment.subscription_id).filter(
            PaypalPayment.user_id == user.id,
            PaypalPayment.status == "COMPLETED",
        ).all()
    }
    now = int(time.time())
    candidates = db.query(PaypalSubscription).filter(
        PaypalSubscription.user_id == user.id,
        PaypalSubscription.status.in_(("ACTIVE", "CANCELLED")),
    ).all()
    active = []
    for subscription in candidates:
        if subscription.subscription_id not in paid_subscription_ids:
            continue
        entitlement_until = max(
            int(subscription.next_billing_utc or 0),
            int(subscription.last_payment_utc or 0) + 35 * 86400,
        )
        if subscription.status == "ACTIVE" or entitlement_until > now:
            active.append(subscription)

    db.query(Badge).filter(
        Badge.user_id == user.id,
        Badge.badge_id.in_(PATRON_BADGE_IDS),
    ).delete(synchronize_session=False)

    if not active:
        user.patron = 0
        user.patron_utc = 0
    else:
        highest = max(active, key=lambda item: item.tier)
        tier = SUPPORT_TIER_BY_LEVEL[highest.tier]
        paid_until = max(
            [int(item.next_billing_utc or 0) for item in active]
            + [int(item.last_payment_utc or 0) + 35 * 86400 for item in active]
        )
        user.patron = tier["level"]
        user.patron_utc = max(paid_until, now + 86400)
        db.add(Badge(user_id=user.id, badge_id=tier["badge"]))

    user.__dict__.pop("_lazy", None)
    db.add(user)
    db.flush()
    return user


def reverse_paypal_payment(db, resource, *, status):
    candidate_ids = [
        resource.get("sale_id"),
        resource.get("parent_payment"),
        resource.get("id"),
    ]
    payment = None
    for candidate in candidate_ids:
        if candidate:
            payment = db.get(PaypalPayment, str(candidate))
            if payment:
                break

    subscription_id = resource.get("billing_agreement_id")
    if payment:
        user = db.query(User).filter(User.id == payment.user_id).with_for_update().one()
        if payment.status == "COMPLETED" and payment.wishbux_granted:
            user.marseybux = max(0, int(user.marseybux or 0) - int(payment.wishbux_granted))
        payment.status = status
        payment.updated_utc = int(time.time())
        db.add(payment)
        db.add(user)
        subscription_id = subscription_id or payment.subscription_id

    if subscription_id:
        subscription = db.get(PaypalSubscription, str(subscription_id))
        if subscription:
            subscription.status = "SUSPENDED"
            subscription.updated_utc = int(time.time())
            db.add(subscription)
            db.flush()
            recalculate_paypal_patron(db, subscription.user_id)

    return payment is not None or bool(subscription_id)
