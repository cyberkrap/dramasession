"""Idempotent patron badge and supporter notification fulfillment."""

from files.classes import Badge, BadgeDef, Comment, Notification, PaypalPayment, User
from files.helpers.config.const import AUTOJANNY_ID


INNER_CIRCLE_BADGE_ID = 25
SUPPORT_THANK_YOU = "Thank you for your support. Freaky Nikki must be obsessed with you!"
INNER_CIRCLE_BADGE_NOTICE = "You earned the Inner Circle supporter badge."


def ensure_inner_circle_badge_definition(db):
    """Return the existing tier-5 badge definition without mutating legacy data."""
    return db.get(BadgeDef, INNER_CIRCLE_BADGE_ID)


def _notification_exists(db, user_id, body):
    return db.query(Notification.comment_id).join(
        Comment,
        Notification.comment_id == Comment.id,
    ).filter(
        Notification.user_id == user_id,
        Comment.author_id == AUTOJANNY_ID,
        Comment.body == body,
        Comment.deleted_utc == 0,
    ).first() is not None


def _create_root_notification(db, user_id, body):
    """Create a root notification comment not tied to a submission."""
    if _notification_exists(db, user_id, body):
        return False

    comment = Comment(
        author_id=AUTOJANNY_ID,
        parent_submission=None,
        parent_comment_id=None,
        wall_user_id=None,
        sentto=None,
        level=1,
        distinguish_level=6,
        body=body,
        body_html=f"<p>{body}</p>",
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
            if (
                badge_def is not None
                and int(user.patron or 0) >= 5
                and db.get(Badge, (user_id, INNER_CIRCLE_BADGE_ID)) is None
            ):
                db.add(Badge(user_id=user_id, badge_id=INNER_CIRCLE_BADGE_ID))
                db.flush()
                badge_added = True

            has_completed_payment = db.query(PaypalPayment.payment_id).filter(
                PaypalPayment.user_id == user_id,
                PaypalPayment.status == "COMPLETED",
            ).first()
            if not has_completed_payment:
                return badge_added

            changed = _create_root_notification(db, user_id, SUPPORT_THANK_YOU)

            if int(user.patron or 0) >= 5 and (
                badge_added or db.get(Badge, (user_id, INNER_CIRCLE_BADGE_ID)) is not None
            ):
                changed = _create_root_notification(
                    db,
                    user_id,
                    INNER_CIRCLE_BADGE_NOTICE,
                ) or changed

            return changed or badge_added
    except Exception:
        return False
