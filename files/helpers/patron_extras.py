"""Idempotent patron contribution badge and notification fulfillment."""

from sqlalchemy import or_

from files.classes import (
    Badge,
    BadgeDef,
    Comment,
    Notification,
    PaypalPayment,
    PaypalSubscription,
    User,
)
from files.helpers.config.const import AUTOJANNY_ID
from files.helpers.contribution_badges import CONTRIBUTION_BADGE_THRESHOLDS
from files.helpers.sanitize import sanitize
from files.helpers.support import (
    CONTRIBUTION_BADGE_DESCRIPTIONS,
    CONTRIBUTION_BADGE_NAMES,
    PAYPAL_ACTIVE_PLAN_IDS,
)


INNER_CIRCLE_BADGE_ID = 25
SUPPORT_THANK_YOU = "Thank you for your support. Freaky Nikki must be obsessed with you!"
LEGACY_INNER_CIRCLE_BADGE_NOTICE = "You earned the Inner Circle supporter badge."

OBSESSION_BADGE_BRANDING = {
    16: (
        "Emoji Master",
        "Made major contributions to the site's emoji collection.",
    ),
    17: (
        "Emoji Artisan",
        "Created an approved emoji for the site.",
    ),
    99: (
        "Sidebar Artist",
        "Created approved artwork for the site sidebar.",
    ),
}


def ensure_obsession_badge_definitions(db):
    """Remove legacy Marsey branding and keep contribution badges current."""
    definitions = dict(OBSESSION_BADGE_BRANDING)
    definitions.update({
        badge_id: (
            CONTRIBUTION_BADGE_NAMES[badge_id],
            CONTRIBUTION_BADGE_DESCRIPTIONS[badge_id],
        )
        for badge_id in CONTRIBUTION_BADGE_NAMES
    })

    changed = False
    for badge_id, (name, description) in definitions.items():
        badge = db.get(BadgeDef, badge_id)
        if badge is None:
            continue
        if badge.name != name:
            badge.name = name
            changed = True
        if badge.description != description:
            badge.description = description
            changed = True
        if changed:
            db.add(badge)

    if changed:
        db.flush()
    return changed


def ensure_inner_circle_badge_definition(db):
    """Keep the existing PayPal route interface while refreshing badge data."""
    ensure_obsession_badge_definitions(db)
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


def _badge_notice(badge):
    description = badge.badge.description or ""
    return (
        "@AutoJanny has given you the following profile badge:\n\n"
        f"![]({badge.path})\n\n"
        f"**{badge.name}**\n\n"
        f"{description}"
    )


def _legacy_badge_bodies(badge):
    if badge.badge_id != INNER_CIRCLE_BADGE_ID:
        return ()
    old_card = (
        "@AutoJanny has given you the following profile badge:\n\n"
        f"![]({badge.path})\n\n"
        "**Marsey's Sugar Daddy**\n\n"
        "Contributed at least $100"
    )
    return (LEGACY_INNER_CIRCLE_BADGE_NOTICE, old_card)


def ensure_patron_extras(db, user_id):
    """Backfill live contribution badges and their one-time notices."""
    user_id = int(user_id)

    try:
        with db.begin_nested():
            ensure_obsession_badge_definitions(db)
            user = db.get(User, user_id)
            if user is None or not PAYPAL_ACTIVE_PLAN_IDS:
                return False

            has_completed_payment = db.query(PaypalPayment.payment_id).join(
                PaypalSubscription,
                PaypalSubscription.subscription_id == PaypalPayment.subscription_id,
            ).filter(
                PaypalPayment.user_id == user_id,
                PaypalPayment.status == "COMPLETED",
                PaypalSubscription.plan_id.in_(PAYPAL_ACTIVE_PLAN_IDS),
            ).first()
            if not has_completed_payment:
                return False

            changed = _ensure_root_notification(db, user_id, SUPPORT_THANK_YOU)
            badge_ids = tuple(badge_id for _threshold, badge_id in CONTRIBUTION_BADGE_THRESHOLDS)
            badges = db.query(Badge).filter(
                Badge.user_id == user_id,
                Badge.badge_id.in_(badge_ids),
            ).order_by(Badge.badge_id).all()

            for badge in badges:
                notice = _badge_notice(badge)
                changed = _ensure_root_notification(
                    db,
                    user_id,
                    notice,
                    body_html=sanitize(notice),
                    legacy_bodies=_legacy_badge_bodies(badge),
                ) or changed

            return changed
    except Exception:
        return False
