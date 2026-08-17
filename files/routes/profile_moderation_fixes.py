import os

from flask import abort, g, request

from files.__main__ import app, engine, limiter
from files.classes import Badge, Comment, ModAction, Submission, User
from files.helpers.alerts import send_repeatable_notification
from files.helpers.bot_controls import install_bot_controls, install_native_bot_action_guards
from files.helpers.config.const import DEFAULT_RATELIMIT, PERMS
from files.helpers.config import modaction_types as modaction_config
from files.helpers.get import get_account
from files.routes.wrappers import admin_level_required, get_ID, get_logged_in_user


_PROFILE_ANTHEM_ACTION = {
    "str": "removed the profile anthem of {self.target_link}",
    "icon": "fa-music",
    "color": "bg-danger",
}
_ACCIDENTAL_CHUD_REPAIR_NOTE = "automatic repair: accidental award chud 2026-08-17"


# Keep the new action available everywhere the moderation log builds its type
# catalog. These dictionaries are imported by reference by the log routes.
for _catalog_name in (
    "MODACTION_TYPES",
    "MODACTION_TYPES_FILTERED",
    "MODACTION_TYPES__FILTERED",
):
    _catalog = getattr(modaction_config, _catalog_name, None)
    if isinstance(_catalog, dict):
        _catalog.setdefault("wipe_profile_anthem", _PROFILE_ANTHEM_ACTION)


@app.before_request
def repair_accidental_owner_chud_once():
    """One-time production repair for the owner's accidental award-origin Chud."""
    if getattr(app, "_toc_accidental_chud_repair_checked", False):
        return None

    marker = g.db.query(ModAction.id).filter(
        ModAction._note == _ACCIDENTAL_CHUD_REPAIR_NOTE,
    ).first()
    if marker:
        app._toc_accidental_chud_repair_checked = True
        return None

    user = g.db.query(User).filter(User.username == "cyberkrap").one_or_none()
    if not user:
        return None

    # Award Chuds intentionally leave chudded_by empty. Never auto-clear an
    # admin-issued Chud in this one-time repair.
    repaired = bool(user.agendaposter and not user.chudded_by)
    if repaired:
        user.agendaposter = 0
        user.chudded_by = None
        g.db.query(Badge).filter(
            Badge.user_id == user.id,
            Badge.badge_id == 28,
        ).delete(synchronize_session=False)
        g.db.add(user)

    # Persist a marker even if the state already changed before deployment so a
    # future legitimate award Chud can never be mistaken for this one-time fix.
    g.db.add(ModAction(
        kind="unchud" if repaired else "toc_repair",
        user_id=user.id,
        target_user_id=user.id,
        _note=_ACCIDENTAL_CHUD_REPAIR_NOTE,
    ))
    g.db.commit()
    app._toc_accidental_chud_repair_checked = True
    return None


@app.before_request
def protect_privileged_modlog_permalinks():
    """Make /log/<id> obey the same privileged-action rules as /log."""
    if request.endpoint != "log_item":
        return None

    action_id = (request.view_args or {}).get("id")
    if not action_id:
        return None

    action = g.db.get(ModAction, action_id)
    if not action or action.kind not in modaction_config.MODACTION_PRIVILEGED_TYPES:
        return None

    viewer = get_logged_in_user()
    if not viewer or viewer.admin_level < PERMS["USER_SHADOWBAN"]:
        abort(404)
    return None


@app.post("/admin/wipe_profile_anthem/<int:user_id>")
@admin_level_required(PERMS["USER_MODERATION_TOOLS_VISIBLE"])
def wipe_profile_anthem(user_id, v: User):
    user = g.db.query(User).filter_by(id=user_id).one_or_none()
    if not user:
        abort(404)
    if user.admin_level > v.admin_level:
        abort(403)

    song = user.song
    user.song = None
    g.db.add(user)

    # Uploaded anthems are unique, while YouTube-backed anthems may be shared.
    # Remove the physical MP3 only when no other account still references it.
    if song:
        remaining_users = g.db.query(User).filter(
            User.id != user.id,
            User.song == song,
        ).count()
        song_path = f"/songs/{song}.mp3"
        if remaining_users == 0 and os.path.isfile(song_path):
            try:
                os.remove(song_path)
            except OSError:
                # Clearing the account reference is the important moderation
                # action; a storage cleanup failure must not restore the anthem.
                pass

    g.db.add(ModAction(
        kind="wipe_profile_anthem",
        user_id=v.id,
        target_user_id=user.id,
    ))
    return {"message": f"@{user.username}'s profile anthem was removed."}


@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@admin_level_required(PERMS["USER_AGENDAPOSTER"])
def toc_unagendaposter(id, v):
    """Allow TOC admins to remove both admin-issued and award-issued Chuds."""
    if id.startswith("p_"):
        post = g.db.get(Submission, id.split("p_", 1)[1])
        if not post:
            abort(404)
        user = post.author
    elif id.startswith("c_"):
        comment = g.db.get(Comment, id.split("c_", 1)[1])
        if not comment:
            abort(404)
        user = comment.author
    else:
        user = get_account(id)

    source = "admin" if user.chudded_by else "award"
    user.agendaposter = 0
    user.chudded_by = None
    g.db.add(user)

    badge = g.db.query(Badge).filter(
        Badge.user_id == user.id,
        Badge.badge_id == 28,
    ).one_or_none()
    if badge:
        g.db.delete(badge)

    g.db.add(ModAction(
        kind="unchud",
        user_id=v.id,
        target_user_id=user.id,
        _note=f"source: {source} chud",
    ))
    send_repeatable_notification(user.id, f"@{v.username} (a site admin) has unchudded you.")
    return {"message": f"@{user.username} has been unchudded!"}


# The legacy rDrama endpoint deliberately forbids jannies from undoing an
# award-origin Chud. TOC admins are allowed to undo either source.
if "unagendaposter" in app.view_functions:
    app.view_functions["unagendaposter"] = toc_unagendaposter


# Install the shared bot policy after legacy route modules are loaded. The
# helper also replaces route-level references imported from actions.py.
install_bot_controls(engine)
install_native_bot_action_guards()

# Keep advanced profile moderation isolated from this compatibility module.
from .profile_admin_tools import *  # noqa: E402,F401,F403
