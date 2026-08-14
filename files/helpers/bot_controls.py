from __future__ import annotations

import time
from typing import Any

from flask import g
from sqlalchemy import func, text

from files.classes import Comment, Submission, User
from files.helpers.config.const import LONGPOSTBOT_ID, SNAPPY_ID, ZOZBOT_ID


KNOWN_BOT_USERNAMES = {
    "autojanny",
    "crappy",
    "longpostbot",
    "snappy",
    "snatchy",
    "zozbot",
}


def install_bot_controls(engine) -> None:
    with engine.begin() as connection:
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS bot_controls (
                user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
                enabled BOOLEAN NOT NULL DEFAULT TRUE,
                daily_post_limit INTEGER,
                daily_comment_limit INTEGER,
                updated_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
                updated_utc BIGINT NOT NULL DEFAULT 0,
                CONSTRAINT bot_controls_post_limit_nonnegative
                    CHECK (daily_post_limit IS NULL OR daily_post_limit >= 0),
                CONSTRAINT bot_controls_comment_limit_nonnegative
                    CHECK (daily_comment_limit IS NULL OR daily_comment_limit >= 0)
            )
        """))


def _control_row(db, user_id: int):
    return db.execute(text("""
        SELECT enabled, daily_post_limit, daily_comment_limit, updated_by, updated_utc
        FROM bot_controls
        WHERE user_id = :user_id
    """), {"user_id": user_id}).mappings().first()


def is_bot_profile(db, user: User | None) -> bool:
    if not user:
        return False
    if (user.username or "").strip().lower() in KNOWN_BOT_USERNAMES:
        return True
    if _control_row(db, user.id):
        return True
    if db.query(Submission.id).filter(
        Submission.author_id == user.id,
        Submission.is_bot == True,
    ).first():
        return True
    if db.query(Comment.id).filter(
        Comment.author_id == user.id,
        Comment.is_bot == True,
    ).first():
        return True
    return False


def _utc_day_start(now: int | None = None) -> int:
    now = int(now or time.time())
    return now - (now % 86400)


def bot_profile_state(db, user: User | None, *, with_counts: bool = True) -> dict[str, Any]:
    if not user:
        return {
            "is_bot": False,
            "enabled": True,
            "daily_post_limit": None,
            "daily_comment_limit": None,
            "posts_today": 0,
            "comments_today": 0,
        }

    row = _control_row(db, user.id)
    state = {
        "is_bot": is_bot_profile(db, user),
        "enabled": bool(row["enabled"]) if row else True,
        "daily_post_limit": row["daily_post_limit"] if row else None,
        "daily_comment_limit": row["daily_comment_limit"] if row else None,
        "posts_today": 0,
        "comments_today": 0,
    }
    if not with_counts:
        return state

    start = _utc_day_start()
    state["posts_today"] = db.query(func.count(Submission.id)).filter(
        Submission.author_id == user.id,
        Submission.created_utc >= start,
    ).scalar() or 0
    state["comments_today"] = db.query(func.count(Comment.id)).filter(
        Comment.author_id == user.id,
        Comment.created_utc >= start,
    ).scalar() or 0
    return state


def save_bot_control(
    db,
    user_id: int,
    *,
    enabled: bool,
    daily_post_limit: int | None,
    daily_comment_limit: int | None,
    updated_by: int,
) -> None:
    db.execute(text("""
        INSERT INTO bot_controls (
            user_id, enabled, daily_post_limit, daily_comment_limit, updated_by, updated_utc
        ) VALUES (
            :user_id, :enabled, :daily_post_limit, :daily_comment_limit, :updated_by, :updated_utc
        )
        ON CONFLICT (user_id) DO UPDATE SET
            enabled = EXCLUDED.enabled,
            daily_post_limit = EXCLUDED.daily_post_limit,
            daily_comment_limit = EXCLUDED.daily_comment_limit,
            updated_by = EXCLUDED.updated_by,
            updated_utc = EXCLUDED.updated_utc
    """), {
        "user_id": user_id,
        "enabled": enabled,
        "daily_post_limit": daily_post_limit,
        "daily_comment_limit": daily_comment_limit,
        "updated_by": updated_by,
        "updated_utc": int(time.time()),
    })


def bot_publish_decision(db, user_id: int, kind: str, *, cost: int = 1) -> tuple[bool, str, dict[str, Any]]:
    user = db.get(User, user_id)
    if not user:
        return False, "Bot account no longer exists.", {}

    state = bot_profile_state(db, user, with_counts=True)
    if not state["is_bot"]:
        return True, "", state
    if not state["enabled"]:
        return False, f"@{user.username} is disabled by an administrator.", state

    if kind == "post":
        limit = state["daily_post_limit"]
        used = int(state["posts_today"])
        label = "post"
    elif kind == "comment":
        limit = state["daily_comment_limit"]
        used = int(state["comments_today"])
        label = "comment"
    else:
        raise ValueError("Unknown bot publication kind")

    if limit is not None and used + max(1, int(cost)) > int(limit):
        return False, f"@{user.username} reached its daily {label} limit ({limit}).", state
    return True, "", state


def install_native_bot_action_guards() -> None:
    """Wrap legacy native bot emitters before routes import them by name."""
    import files.helpers.actions as actions

    if getattr(actions, "_toc_bot_controls_installed", False):
        return

    def guard(function, user_id: int, cost: int = 1):
        def wrapped(*args, **kwargs):
            if not user_id:
                return function(*args, **kwargs)
            allowed, _, _ = bot_publish_decision(g.db, user_id, "comment", cost=cost)
            if not allowed:
                return None
            return function(*args, **kwargs)
        wrapped.__name__ = function.__name__
        wrapped.__doc__ = function.__doc__
        return wrapped

    actions.execute_snappy = guard(actions.execute_snappy, SNAPPY_ID, 1)
    actions.execute_zozbot = guard(actions.execute_zozbot, ZOZBOT_ID, 3)
    actions.execute_longpostbot = guard(actions.execute_longpostbot, LONGPOSTBOT_ID, 1)

    # Routes import these legacy functions by name. If routes are already loaded,
    # replace their module globals too so installing this extension late is safe.
    import sys
    posts_module = sys.modules.get("files.routes.posts")
    comments_module = sys.modules.get("files.routes.comments")
    if posts_module is not None:
        posts_module.execute_snappy = actions.execute_snappy
    if comments_module is not None:
        comments_module.execute_zozbot = actions.execute_zozbot
        comments_module.execute_longpostbot = actions.execute_longpostbot

    actions._toc_bot_controls_installed = True


def install_crappy_service_guard(service_module) -> None:
    """Apply policy before provider work and again immediately before publication."""
    if getattr(service_module, "_toc_bot_controls_installed", False):
        return

    original = service_module._assert_crappy_can_publish

    def guarded(db, trigger, post, wall_owner):
        crappy = original(db, trigger, post, wall_owner)
        allowed, reason, _ = bot_publish_decision(db, crappy.id, "comment")
        if not allowed:
            raise service_module.CrappyIneligibleRequest(reason)
        return crappy

    service_module._assert_crappy_can_publish = guarded
    service_module._toc_bot_controls_installed = True
