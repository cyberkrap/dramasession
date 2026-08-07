import os

from flask import abort, request

from files.__main__ import app
from files.classes import ModAction, User
from files.helpers.config.const import PERMS
from files.helpers.config import modaction_types as modaction_config
from files.helpers.get import get_logged_in_user
from files.routes.wrappers import admin_level_required


_PROFILE_ANTHEM_ACTION = {
    "str": "removed the profile anthem of {self.target_link}",
    "icon": "fa-music",
    "color": "bg-danger",
}

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
def protect_privileged_modlog_permalinks():
    """Make /log/<id> obey the same privileged-action rules as /log."""
    if request.endpoint != "log_item":
        return None

    action_id = (request.view_args or {}).get("id")
    if not action_id:
        return None

    action = app.extensions["sqlalchemy"].session.get(ModAction, action_id) if False else None
    # g.db is installed by the core request lifecycle before route hooks run.
    from flask import g
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
