"""Make admin removals of mistaken supporter badges persist reliably.

The original supporter-badge guard depended on the badge-admin endpoint returning a
specific plain string.  The admin page can return a response object instead, so a
successful deletion was sometimes followed by the hourly patron sync re-adding the
badge.  This wrapper uses database state as the source of truth.
"""

from functools import wraps
import time

from flask import g, request
from sqlalchemy import text

from files.__main__ import app, engine
from files.classes import Badge
from files.helpers.contribution_badges import (
    ACTIVE_SUPPORT_BADGE_IDS,
    CONTRIBUTION_BADGE_IDS,
    has_active_paid_support,
    sync_active_support_badges,
)
from files.helpers.get import get_user
from files.helpers.support import PAYPAL_ACTIVE_PLAN_IDS


_INSTALLED = False


def _cleanup_known_mistaken_badges():
    """Remove the already-restored badges from Knife_ and Rip once at startup.

    Verified active PayPal supporters are explicitly excluded. A later verified
    recurring payment can also restore the normal paid-badge entitlement through
    the existing PayPal recalculation path.
    """
    params = {
        "now": int(time.time()),
        "knife": "knife_",
        "rip": "rip",
    }
    plan_slots = []
    for index, plan_id in enumerate(PAYPAL_ACTIVE_PLAN_IDS):
        key = f"support_fix_plan_{index}"
        params[key] = plan_id
        plan_slots.append(f":{key}")
    plans = ", ".join(plan_slots) or "NULL"

    eligibility = f"""
        (LOWER(u.username) IN (:knife, :rip)
         OR LOWER(COALESCE(u.original_username, '')) IN (:knife, :rip))
        AND NOT EXISTS (
            SELECT 1
            FROM paypal_subscriptions ps
            WHERE ps.user_id = u.id
              AND ps.plan_id IN ({plans})
              AND ps.status IN ('ACTIVE', 'CANCELLED')
              AND EXISTS (
                  SELECT 1
                  FROM paypal_payments pp
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
    """

    try:
        with engine.begin() as connection:
            connection.execute(text(f"""
                UPDATE users u
                SET patron_badges_disabled = TRUE
                WHERE {eligibility}
            """), params)
            connection.execute(text(f"""
                DELETE FROM badges b
                USING users u
                WHERE b.user_id = u.id
                  AND b.badge_id BETWEEN 21 AND 27
                  AND {eligibility}
            """), params)
    except Exception:
        # Never make a cleanup task capable of preventing the app from booting.
        pass


def install_support_badge_removal_fix():
    global _INSTALLED
    if _INSTALLED:
        return

    _cleanup_known_mistaken_badges()

    endpoint = "badge_remove_post"
    original = app.view_functions.get(endpoint)
    if original is None or getattr(original, "_db_verified_support_badge_removal", False):
        return

    @wraps(original)
    def remove_badge_with_db_verified_suppression(*args, **kwargs):
        try:
            badge_id = int(request.values.get("badge_id"))
        except (TypeError, ValueError):
            return original(*args, **kwargs)

        username = (request.values.get("username") or "").strip()
        user = get_user(username, graceful=True) if username else None
        was_present = False
        if user is not None and badge_id in ACTIVE_SUPPORT_BADGE_IDS:
            was_present = g.db.query(Badge.user_id).filter(
                Badge.user_id == user.id,
                Badge.badge_id == badge_id,
            ).first() is not None

        response = original(*args, **kwargs)

        if not was_present or user is None or badge_id not in ACTIVE_SUPPORT_BADGE_IDS:
            return response
        if has_active_paid_support(g.db, user.id):
            return response

        # The actual database state is the only reliable success signal. If the
        # route removed the requested badge, suppress all donation badges for this
        # non-paying patron before the global sync gets another chance to restore it.
        still_present = g.db.query(Badge.user_id).filter(
            Badge.user_id == user.id,
            Badge.badge_id == badge_id,
        ).first() is not None
        if still_present:
            return response

        user.patron_badges_disabled = True
        sync_active_support_badges(g.db, user, 0)
        user.__dict__.pop("_lazy", None)
        g.db.add(user)
        g.db.flush()
        return response

    remove_badge_with_db_verified_suppression._db_verified_support_badge_removal = True
    app.view_functions[endpoint] = remove_badge_with_db_verified_suppression
    _INSTALLED = True
