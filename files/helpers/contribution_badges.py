"""Active recurring-support badge fulfilment for verified and manual patrons."""

from functools import wraps
import importlib
import threading
import time

from flask import g, request
from sqlalchemy import Boolean, Column, inspect, text
from sqlalchemy.exc import SQLAlchemyError

from files.__main__ import app, engine
from files.classes import Badge, PaypalPayment, PaypalSubscription, User
from files.helpers.get import get_comment, get_post, get_user
from files.helpers.support import (
    CONTRIBUTION_BADGE_NAMES,
    PAYPAL_ACTIVE_PLAN_IDS,
    SUPPORT_TIER_BY_LEVEL,
)


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

_SYNC_LOCK = threading.Lock()
_NEXT_GLOBAL_SYNC_UTC = 0
_FLAG_INSTALLED = False
_ADMIN_ROUTE_INSTALLED = False
_BENEFACTOR_ROUTE_INSTALLED = False
_BADGE_REMOVE_ROUTE_INSTALLED = False


def _install_patron_badge_flag():
    """Persist whether a manually granted patron must receive no donation badges."""
    global _FLAG_INSTALLED
    if _FLAG_INSTALLED:
        return

    if not hasattr(User, "patron_badges_disabled"):
        User.patron_badges_disabled = Column(
            Boolean,
            nullable=False,
            default=False,
            server_default=text("FALSE"),
        )

    inspector = inspect(engine)
    if inspector.has_table("users"):
        existing = {column["name"] for column in inspector.get_columns("users")}
        if "patron_badges_disabled" not in existing:
            with engine.begin() as connection:
                if engine.dialect.name == "postgresql":
                    connection.exec_driver_sql(
                        "ALTER TABLE users ADD COLUMN IF NOT EXISTS "
                        "patron_badges_disabled BOOLEAN NOT NULL DEFAULT FALSE"
                    )
                else:
                    connection.exec_driver_sql(
                        "ALTER TABLE users ADD COLUMN "
                        "patron_badges_disabled BOOLEAN NOT NULL DEFAULT FALSE"
                    )
    _FLAG_INSTALLED = True


def _active_paypal_support_level(db, user_id):
    """Return the user's active paid PayPal tier, or 0 for non-paid patron time."""
    if not PAYPAL_ACTIVE_PLAN_IDS:
        return 0

    now = int(time.time())
    subscriptions = db.query(PaypalSubscription).filter(
        PaypalSubscription.user_id == int(user_id),
        PaypalSubscription.plan_id.in_(PAYPAL_ACTIVE_PLAN_IDS),
        PaypalSubscription.status.in_(("ACTIVE", "CANCELLED")),
    ).all()

    level = 0
    for subscription in subscriptions:
        paid = db.query(PaypalPayment.payment_id).filter(
            PaypalPayment.subscription_id == subscription.subscription_id,
            PaypalPayment.user_id == int(user_id),
            PaypalPayment.status == "COMPLETED",
        ).first()
        if not paid:
            continue

        entitlement_until = max(
            int(subscription.next_billing_utc or 0),
            int(subscription.last_payment_utc or 0) + 35 * 86400,
        )
        if subscription.status == "ACTIVE" or entitlement_until > now:
            level = max(level, min(5, int(subscription.tier or 0)))

    return level


def has_active_paid_support(db, user_id):
    return _active_paypal_support_level(db, user_id) > 0


def sync_active_support_badges(db, user, level=None):
    """Match cumulative badges to the user's entitled monthly tier."""
    if bool(getattr(user, "patron_badges_disabled", False)):
        level = 0
    elif level is None:
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
        # A verified recurring payment always restores the proper paid badges.
        user.patron_badges_disabled = False

    sync_active_support_badges(db, user, user.patron)
    user.__dict__.pop("_lazy", None)
    db.add(user)
    db.flush()
    return user


def _entitlement_sql():
    placeholders = []
    params = {"now": int(time.time())}
    for index, plan_id in enumerate(PAYPAL_ACTIVE_PLAN_IDS):
        key = f"plan_{index}"
        params[key] = plan_id
        placeholders.append(f":{key}")
    plans = ", ".join(placeholders) or "NULL"

    sql = f"""
        WITH paypal_eligible AS (
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
        ), manual_eligible AS (
            SELECT u.id AS user_id, LEAST(COALESCE(u.patron, 0), 5) AS tier
            FROM users u
            WHERE COALESCE(u.patron_badges_disabled, FALSE) = FALSE
              AND COALESCE(u.patron, 0) > 0
              AND (COALESCE(u.patron_utc, 0) = 0 OR u.patron_utc > :now)
        ), eligible AS (
            SELECT user_id, LEAST(MAX(tier), 5) AS tier
            FROM (
                SELECT user_id, tier FROM paypal_eligible
                UNION ALL
                SELECT user_id, tier FROM manual_eligible
            ) entitlements
            GROUP BY user_id
        ), desired AS (
            SELECT eligible.user_id, generate_series(21, 20 + eligible.tier) AS badge_id
            FROM eligible
        )
    """
    return sql, params


def _honor_admin_support_badge_removals():
    """Persist prior admin removals that old patron sync code used to undo."""
    if not PAYPAL_ACTIVE_PLAN_IDS:
        return False

    params = {"now": int(time.time())}
    plan_slots = []
    for index, plan_id in enumerate(PAYPAL_ACTIVE_PLAN_IDS):
        key = f"cleanup_plan_{index}"
        params[key] = plan_id
        plan_slots.append(f":{key}")

    badge_slots = []
    for index, badge_id in enumerate(ACTIVE_SUPPORT_BADGE_IDS):
        key = f"cleanup_badge_{index}"
        params[key] = CONTRIBUTION_BADGE_NAMES[badge_id].lower()
        badge_slots.append(f":{key}")

    plans = ", ".join(plan_slots)
    badge_names = ", ".join(badge_slots)
    statement = text(f"""
        UPDATE users u
        SET patron_badges_disabled = TRUE
        WHERE COALESCE(u.patron_badges_disabled, FALSE) = FALSE
          AND EXISTS (
              SELECT 1
              FROM modactions ma
              WHERE ma.target_user_id = u.id
                AND ma.kind = 'badge_remove'
                AND LOWER(COALESCE(ma._note, '')) IN ({badge_names})
          )
          AND NOT EXISTS (
              SELECT 1
              FROM paypal_subscriptions ps
              WHERE ps.user_id = u.id
                AND ps.plan_id IN ({plans})
                AND ps.status IN ('ACTIVE', 'CANCELLED')
                AND EXISTS (
                    SELECT 1 FROM paypal_payments pp
                    WHERE pp.subscription_id = ps.subscription_id
                      AND pp.user_id = ps.user_id
                      AND pp.status = 'COMPLETED'
                )
                AND (
                    ps.status = 'ACTIVE'
                    OR GREATEST(
                        COALESCE(ps.next_billing_utc, 0),
                        COALESCE(ps.last_payment_utc, 0) + 3024000
                    ) > :now
                )
          )
    """)

    try:
        with engine.begin() as connection:
            result = connection.execute(statement, params)
        return bool(getattr(result, "rowcount", 0))
    except SQLAlchemyError:
        return False


def _sync_existing_active_support_badges():
    """Synchronize all active paid and explicitly non-free manual patrons."""
    sql, params = _entitlement_sql()
    try:
        with engine.begin() as connection:
            connection.execute(text(sql + """
                DELETE FROM badges badge
                WHERE badge.badge_id BETWEEN 21 AND 27
                  AND NOT EXISTS (
                      SELECT 1 FROM desired
                      WHERE desired.user_id = badge.user_id
                        AND desired.badge_id = badge.badge_id
                  )
            """), params)
            connection.execute(text(sql + """
                INSERT INTO badges (user_id, badge_id, created_utc)
                SELECT desired.user_id, desired.badge_id, :now
                FROM desired
                ON CONFLICT (user_id, badge_id) DO NOTHING
            """), params)
        return True
    except SQLAlchemyError:
        return False


def _periodic_active_support_badge_sync():
    """Remove expired badges even when PayPal sends no event at access expiry."""
    global _NEXT_GLOBAL_SYNC_UTC
    now = int(time.time())
    if now < _NEXT_GLOBAL_SYNC_UTC:
        return
    if not _SYNC_LOCK.acquire(blocking=False):
        return
    try:
        if now < _NEXT_GLOBAL_SYNC_UTC:
            return
        _sync_existing_active_support_badges()
        _NEXT_GLOBAL_SYNC_UTC = now + 3600
    finally:
        _SYNC_LOCK.release()


def _install_admin_patron_badge_option():
    """Apply the admin form's free-patron choice after the existing route runs."""
    global _ADMIN_ROUTE_INSTALLED
    if _ADMIN_ROUTE_INSTALLED:
        return

    endpoint = "manage_patron_from_admin_page"
    original = app.view_functions.get(endpoint)
    if original is None or getattr(original, "_free_patron_badge_option", False):
        return

    @wraps(original)
    def manage_patron_with_badge_option(*args, **kwargs):
        response = original(*args, **kwargs)
        location = str(getattr(response, "location", "") or "")
        if request.method != "POST" or "error=" in location:
            return response

        username = (request.form.get("username") or "").strip()
        user = get_user(username, graceful=True)
        if user is None:
            return response

        action = (request.form.get("action") or "set").strip().lower()
        if action == "end":
            user.patron_badges_disabled = False
            sync_active_support_badges(g.db, user, 0)
        else:
            free_patron = request.form.get("free_patron") == "on"
            user.patron_badges_disabled = free_patron
            sync_active_support_badges(g.db, user, 0 if free_patron else None)

        user.__dict__.pop("_lazy", None)
        g.db.add(user)
        g.db.flush()
        return response

    manage_patron_with_badge_option._free_patron_badge_option = True
    app.view_functions[endpoint] = manage_patron_with_badge_option
    _ADMIN_ROUTE_INSTALLED = True


def _install_benefactor_patron_badge_guard():
    """Benefactor award time grants patron perks, never donation badges."""
    global _BENEFACTOR_ROUTE_INSTALLED
    if _BENEFACTOR_ROUTE_INSTALLED:
        return

    endpoint = "award_thing"
    original = app.view_functions.get(endpoint)
    if original is None or getattr(original, "_benefactor_patron_badge_guard", False):
        return

    @wraps(original)
    def award_with_benefactor_patron_guard(*args, **kwargs):
        kind = (request.values.get("kind") or "").strip().lower()
        if kind != "benefactor":
            return original(*args, **kwargs)

        target = None
        prior_level = 0
        try:
            view_args = request.view_args or {}
            thing_type = view_args.get("thing_type")
            thing_id = int(view_args.get("id"))
            thing = get_post(thing_id) if thing_type == "post" else get_comment(thing_id)
            target = thing.author
            prior_level = int(getattr(target, "patron", 0) or 0)
            prior_expiry = int(getattr(target, "patron_utc", 0) or 0)
            if prior_expiry and prior_expiry <= int(time.time()):
                prior_level = 0
        except Exception:
            target = None
            prior_level = 0

        response = original(*args, **kwargs)

        if target is not None:
            # Never let a Benefactor award downgrade an existing higher patron tier.
            if prior_level > int(getattr(target, "patron", 0) or 0):
                target.patron = prior_level

            # A brand-new patron entitlement created by Benefactor is a perk grant,
            # not evidence of a donation. Verified paid support remains untouched.
            if prior_level == 0 and not has_active_paid_support(g.db, target.id):
                target.patron_badges_disabled = True
                sync_active_support_badges(g.db, target, 0)

            target.__dict__.pop("_lazy", None)
            g.db.add(target)
            g.db.flush()

        return response

    award_with_benefactor_patron_guard._benefactor_patron_badge_guard = True
    app.view_functions[endpoint] = award_with_benefactor_patron_guard
    _BENEFACTOR_ROUTE_INSTALLED = True


def _install_support_badge_removal_guard():
    """Let admins permanently remove mistaken supporter badges from non-payers."""
    global _BADGE_REMOVE_ROUTE_INSTALLED
    if _BADGE_REMOVE_ROUTE_INSTALLED:
        return

    endpoint = "badge_remove_post"
    original = app.view_functions.get(endpoint)
    if original is None or getattr(original, "_support_badge_removal_guard", False):
        return

    @wraps(original)
    def remove_badge_with_support_guard(*args, **kwargs):
        response = original(*args, **kwargs)

        try:
            badge_id = int(request.values.get("badge_id"))
        except (TypeError, ValueError):
            return response
        if badge_id not in ACTIVE_SUPPORT_BADGE_IDS:
            return response

        # Only apply the suppression when the normal admin route actually reports
        # a successful removal; failed/nonexistent removals must not change patron state.
        if not isinstance(response, str) or "Badge removed from @" not in response:
            return response

        username = (request.values.get("username") or "").strip()
        user = get_user(username, graceful=True)
        if user is None or has_active_paid_support(g.db, user.id):
            return response

        user.patron_badges_disabled = True
        sync_active_support_badges(g.db, user, 0)
        user.__dict__.pop("_lazy", None)
        g.db.add(user)
        g.db.flush()
        return response

    remove_badge_with_support_guard._support_badge_removal_guard = True
    app.view_functions[endpoint] = remove_badge_with_support_guard
    _BADGE_REMOVE_ROUTE_INSTALLED = True


def install_cumulative_contribution_badges():
    """Install active-support recalculation, free patrons, and badge migration."""
    _install_patron_badge_flag()
    _install_admin_patron_badge_option()
    _install_benefactor_patron_badge_guard()
    _install_support_badge_removal_guard()

    paypal_helpers = importlib.import_module("files.helpers.paypal")
    paypal_routes = importlib.import_module("files.routes.paypal")
    paypal_helpers.recalculate_paypal_patron = recalculate_paypal_patron
    paypal_routes.recalculate_paypal_patron = recalculate_paypal_patron
    _honor_admin_support_badge_removals()
    _sync_existing_active_support_badges()
    app.before_request(_periodic_active_support_badge_sync)
