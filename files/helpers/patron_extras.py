"""Idempotent patron badge and supporter notification fulfillment."""

from sqlalchemy import or_

from files.classes import Badge, BadgeDef, Comment, Notification, PaypalPayment, User
from files.helpers.config.const import AUTOJANNY_ID
from files.helpers.sanitize import sanitize


INNER_CIRCLE_BADGE_ID = 25
SUPPORT_THANK_YOU = "Thank you for your support. Freaky Nikki must be obsessed with you!"
LEGACY_INNER_CIRCLE_BADGE_NOTICE = "You earned the Inner Circle supporter badge."


def ensure_inner_circle_badge_definition(db):
    """Return the existing tier-5 badge definition without mutating legacy data."""
    return db.get(BadgeDef, INNER_CIRCLE_BADGE_ID)


def _find_notification_comment(db, user_id, bodies, body_html):
    return db.query(Comment).join(
        Notification,
        Notification.comment_id == Comment.id,
    ).filter(
        Notification.user_id == user_id,
        Comment.author_id == AUTOJANNY_ID,
        Comment.deleted_utc == 0,
        or_(Comment.body.in_(tuple(bodies)), Comment.body_html == body_html),
    ).order_by(Comment.id.desc()).first()


def _ensure_root_notification(db, user_id, body, *, body_html=None, legacy_bodies=()):
    """Create a root notification, or upgrade an older version in place."""
    body_html = body_html or sanitize(body)
    bodies = (body, *legacy_bodies)
    comment = _find_notification_comment(db, user_id, bodies, body_html)

    if comment is not None:
        changed = False
        if comment.body != body:
            comment.body = body
            changed = True
        if comment.body_html != body_html:
            comment.body_html = body_html
            changed = True
        if comment.parent_submission is not None:
            comment.parent_submission = None
            changed = True
        if comment.parent_comment_id is not None:
            comment.parent_comment_id = None
            changed = True
        if comment.wall_user_id is not None:
            comment.wall_user_id = None
            changed = True
        if comment.sentto is not None:
            comment.sentto = None
            changed = True
        if changed:
            db.add(comment)
            db.flush()
        return changed

    comment = Comment(
        author_id=AUTOJANNY_ID,
        parent_submission=None,
        parent_comment_id=None,
        wall_user_id=None,
        sentto=None,
        level=1,
        distinguish_level=6,
        body=body,
        body_html=body_html,
        is_bot=True,
        over_18=False,
        ghost=False,
    )
    comment.upvotes = 1
    comment.downvotes = 0
    comment.realupvotes = 1
    db.add(comment)
    db.flush()
    comment.top_comment_id = comment.id
    db.add(comment)
    db.add(Notification(user_id=user_id, comment_id=comment.id))
    db.flush()
    return True


def _inner_circle_badge_notice(badge):
    description = badge.badge.description or ""
    return (
        "@AutoJanny has given you the following profile badge:\n\n"
        f"![]({badge.path})\n\n"
        f"**{badge.name}**\n\n"
        f"{description}"
    )


def ensure_patron_extras(db, user_id):
    """Best-effort badge and one-time supporter notifications.

    This runs inside a nested transaction so an optional badge or notification
    failure cannot invalidate a verified PayPal payment.
    """
    user_id = int(user_id)

    try:
        with db.begin_nested():
            user = db.get(User, user_id)
            badge_def = ensure_inner_circle_badge_definition(db)
            if user is None:
                return False

            badge_added = False
            badge = db.get(Badge, (user_id, INNER_CIRCLE_BADGE_ID))
            if badge_def is not None and int(user.patron or 0) >= 5 and badge is None:
                badge = Badge(user_id=user_id, badge_id=INNER_CIRCLE_BADGE_ID)
                db.add(badge)
                db.flush()
                badge_added = True

            has_completed_payment = db.query(PaypalPayment.payment_id).filter(
                PaypalPayment.user_id == user_id,
                PaypalPayment.status == "COMPLETED",
            ).first()
            if not has_completed_payment:
                return badge_added

            changed = _ensure_root_notification(db, user_id, SUPPORT_THANK_YOU)

            if int(user.patron or 0) >= 5 and badge is not None:
                badge_notice = _inner_circle_badge_notice(badge)
                changed = _ensure_root_notification(
                    db,
                    user_id,
                    badge_notice,
                    body_html=sanitize(badge_notice),
                    legacy_bodies=(LEGACY_INNER_CIRCLE_BADGE_NOTICE,),
                ) or changed

            return changed or badge_added
    except Exception:
        return False
