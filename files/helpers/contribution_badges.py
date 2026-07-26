"""Active recurring-support badge fulfilment for verified PayPal subscriptions."""

import importlib
import time

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from files.__main__ import engine
from files.classes import Badge, PaypalPayment, PaypalSubscription, User
from files.helpers.support import PAYPAL_ACTIVE_PLAN_IDS, SUPPORT_TIER_BY_LEVEL


# Badge IDs 21-25 correspond to the five live monthly support tiers. IDs 26-27
# were legacy lifetime milestones and are removed from users by the active sync.
CONTRIBUTION_BADGE_THRESHOLDS = (
    (1, 21),
    (2, 22),
    (3, 23),
    (4, 24),
    (5, 25),
)
ACTIVE_SUPPORT_BADGE_IDS = tuple(
    badge_id for _level, badge_id in CONTRIBUTION_BADGE_THRESHOLDS
)
LEGACY_LIFETIME_BADGE_IDS = (26, 27)
CONTRIBUTION_BADGE_IDS = ACTIVE_SUPPORT_BADGE_IDS + LEGACY_LIFETIME_BADGE_IDS


def sync_active_support_badges(db, user, level=None):
    """Match cumulative badges to the user's currently entitled monthly tier."""
    if level is None:
        level = int(getattr(user, "patron", 0) or 0)
        expires = int(getattr(user, "patron_utc", 0) or 0)
        if expires and expires <= int(time.time()):
            level = 0
    level = max(0, min(5, int(level or 0)))
    desired = set(range(21, 21 + level))

    existing = {
        badge.badge_id: badge
        for badge in db.query(Badge).filter(
            Badge.user_id == user.id,
            Badge.badge_id.in_(CONTRIBUTION_BADGE_IDS),
        ).all()
    }
    for badge_id in CONTRIBUTION_BADGE_IDS:
        if badge_id in desired:
            if badge_id not in existing:
                db.add(Badge(user_id=user.id, badge_id=badge_id))
        elif badge_id in existing:
            db.delete(existing[badge_id])
    return level


def grant_cumulative_contribution_badges(db, user):
    """Compatibility wrapper for the old badge fulfilment interface."""
    return sync_active_support_badges(db, user)


def sync_cumulative_contribution_badges(db, user, total_cents=None):
    """Compatibility wrapper; lifetime totals no longer control supporter badges."""
    return sync_active_support_badges(db, user)


def recalculate_paypal_patron(db, user_id):
    """Recalculate active benefits and badges from configured PayPal plans."""
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

    sync_active_support_badges(db, user, user.patron)
    user.__dict__.pop("_lazy", None)
    db.add(user)
    db.flush()
    return user


def _sync_existing_active_support_badges():
    """Migrate existing badge ownership without resetting valid badge timestamps."""
    if not PAYPAL_ACTIVE_PLAN_IDS:
        return False

    params = {"now": int(time.time())}
    placeholders = []
    for index, plan_id in enumerate(PAYPAL_ACTIVE_PLAN_IDS):
        key = f"plan_{index}"
        params[key] = plan_id
        placeholders.append(f":{key}")
    plans = ", ".join(placeholders)
    entitlement_sql = f"""
        WITH eligible AS (
            SELECT ps.user_id, LEAST(MAX(ps.tier), 5) AS tier
            FROM paypal_subscriptions ps
            WHERE ps.plan_id IN ({plans})
              AND EXISTS (
                  SELECT 1 FROM paypal_payments pp
                  WHERE pp.subscription_id = ps.subscription_id
                    AND pp.user_id = ps.user_id
                    AND pp.status = 'COMPLETED'
              )
              AND (
                  ps.status = 'ACTIVE'
                  OR (
                      ps.status = 'CANCELLED'
                      AND GREATEST(
                          COALESCE(ps.next_billing_utc, 0),
                          COALESCE(ps.last_payment_utc, 0) + 3024000
                      ) > :now
                  )
              )
            GROUP BY ps.user_id
        ), desired AS (
            SELECT eligible.user_id, generate_series(21, 20 + eligible.tier) AS badge_id
            FROM eligible
        )
    """

    try:
        with engine.begin() as connection:
            connection.execute(text(entitlement_sql + """
                DELETE FROM badges badge
                WHERE badge.badge_id BETWEEN 21 AND 27
                  AND NOT EXISTS (
                      SELECT 1 FROM desired
                      WHERE desired.user_id = badge.user_id
                        AND desired.badge_id = badge.badge_id
                  )
            """), params)
            connection.execute(text(entitlement_sql + """
                INSERT INTO badges (user_id, badge_id, created_utc)
                SELECT desired.user_id, desired.badge_id, :now
                FROM desired
                ON CONFLICT (user_id, badge_id) DO NOTHING
            """), params)
        return True
    except SQLAlchemyError:
        return False


def install_cumulative_contribution_badges():
    """Install active-subscription recalculation and migrate old badge ownership."""
    paypal_helpers = importlib.import_module("files.helpers.paypal")
    paypal_routes = importlib.import_module("files.routes.paypal")
    paypal_helpers.recalculate_paypal_patron = recalculate_paypal_patron
    paypal_routes.recalculate_paypal_patron = recalculate_paypal_patron
    _sync_existing_active_support_badges()
