"""Idempotent patron badge and thank-you notification fulfillment."""

from files.classes import Badge, BadgeDef, Comment, Notification, PaypalPayment, User
from files.helpers.config.const import AUTOJANNY_ID, NOTIFICATION_THREAD


INNER_CIRCLE_BADGE_ID = 25
SUPPORT_THANK_YOU = "Thank you for your support. Freaky Nikki must be obsessed with you!"


def ensure_patron_extras(db, user_id):
    """Backfill the Inner Circle badge definition and one thank-you notification."""
    user_id = int(user_id)
    user = db.get(User, user_id)
    if user is None:
        return False

    badge_def = db.get(BadgeDef, INNER_CIRCLE_BADGE_ID)
    if badge_def is None:
        badge_def = BadgeDef(
            id=INNER_CIRCLE_BADGE_ID,
            name="JIDF Bankroller",
            description="Contributed at least $100",
        )
        db.add(badge_def)
        db.flush()

    if int(user.patron or 0) >= 5 and db.get(Badge, (user_id, INNER_CIRCLE_BADGE_ID)) is None:
        db.add(Badge(user_id=user_id, badge_id=INNER_CIRCLE_BADGE_ID))

    has_completed_payment = db.query(PaypalPayment.payment_id).filter(
        PaypalPayment.user_id == user_id,
        PaypalPayment.status == "COMPLETED",
    ).first()
    if not has_completed_payment:
        db.flush()
        return False

    existing_notification = db.query(Notification.comment_id).join(
        Comment,
        Notification.comment_id == Comment.id,
    ).filter(
        Notification.user_id == user_id,
        Comment.author_id == AUTOJANNY_ID,
        Comment.body == SUPPORT_THANK_YOU,
        Comment.deleted_utc == 0,
    ).first()
    if existing_notification:
        db.flush()
        return False

    comment = Comment(
        author_id=AUTOJANNY_ID,
        parent_submission=NOTIFICATION_THREAD,
        level=1,
        distinguish_level=6,
        body=SUPPORT_THANK_YOU,
        body_html=f"<p>{SUPPORT_THANK_YOU}</p>",
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
