"""Cumulative contribution badge fulfillment for verified and admin-set totals."""

import importlib
import time

from files.classes import Badge, PaypalPayment, PaypalSubscription, User
from files.helpers.lifetime_contributions import effective_contribution_cents
from files.helpers.support import PAYPAL_ACTIVE_PLAN_IDS, SUPPORT_TIER_BY_LEVEL


CONTRIBUTION_BADGE_THRESHOLDS = (
    (500, 21),
    (1_000, 22),
    (2_000, 23),
    (5_000, 24),
    (10_000, 25),
    (25_000, 26),
    (50_000, 27),
)
CONTRIBUTION_BADGE_IDS = tuple(
    badge_id for _threshold_cents, badge_id in CONTRIBUTION_BADGE_THRESHOLDS
)


def grant_cumulative_contribution_badges(db, user):
    """Grant every lifetime contribution milestone reached by the user."""
    total_cents = effective_contribution_cents(db, user.id)
    for threshold_cents, badge_id in CONTRIBUTION_BADGE_THRESHOLDS:
        if total_cents < threshold_cents:
            continue
        if db.get(Badge, (user.id, badge_id)) is None:
            db.add(Badge(user_id=user.id, badge_id=badge_id))
    return total_cents


def sync_cumulative_contribution_badges(db, user, total_cents=None):
    """Make milestone badges exactly match the user's effective lifetime total."""
    if total_cents is None:
        total_cents = effective_contribution_cents(db, user.id)
    total_cents = max(0, int(total_cents))

    existing = {
        badge.badge_id: badge
        for badge in db.query(Badge).filter(
            Badge.user_id == user.id,
            Badge.badge_id.in_(CONTRIBUTION_BADGE_IDS),
        ).all()
    }
    for threshold_cents, badge_id in CONTRIBUTION_BADGE_THRESHOLDS:
        if total_cents >= threshold_cents:
            if badge_id not in existing:
                db.add(Badge(user_id=user.id, badge_id=badge_id))
        elif badge_id in existing:
            db.delete(existing[badge_id])
    return total_cents


def recalculate_paypal_patron(db, user_id):
    """Recalculate active benefits from the currently configured PayPal plans."""
    user = db.query(User).filter(User.id == int(user_id)).with_for_update().one_or_none()
    if user is None:
        return None

    paid_subscription_ids = set()
    candidates = []
    if PAYPAL_ACTIVE_PLAN_IDS:
        paid_subscription_ids = {
            row[0]
            for row in db.query(PaypalPayment.subscription_id).join(
                PaypalSubscription,
                PaypalSubscription.subscription_id == PaypalPayment.subscription_id,
            ).filter(
                PaypalPayment.user_id == user.id,
                PaypalPayment.status == "COMPLETED",
                PaypalSubscription.plan_id.in_(PAYPAL_ACTIVE_PLAN_IDS),
            ).all()
        }
        candidates = db.query(PaypalSubscription).filter(
            PaypalSubscription.user_id == user.id,
            PaypalSubscription.plan_id.in_(PAYPAL_ACTIVE_PLAN_IDS),
            PaypalSubscription.status.in_(("ACTIVE", "CANCELLED")),
        ).all()

    now = int(time.time())
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

    # Live totals replace old sandbox test totals. Manual contribution overrides
    # still take precedence through effective_contribution_cents().
    sync_cumulative_contribution_badges(db, user)
    user.__dict__.pop("_lazy", None)
    db.add(user)
    db.flush()
    return user


def install_cumulative_contribution_badges():
    """Replace the old highest-tier-only recalculation before requests begin."""
    paypal_helpers = importlib.import_module("files.helpers.paypal")
    paypal_routes = importlib.import_module("files.routes.paypal")
    paypal_helpers.recalculate_paypal_patron = recalculate_paypal_patron
    paypal_routes.recalculate_paypal_patron = recalculate_paypal_patron
