from __future__ import annotations

import importlib
import os
import time
from shutil import copyfile

from flask import abort, g, redirect, render_template, request
from sqlalchemy import or_

from files.__main__ import app, cache, limiter
from files.classes import Comment, ModAction, Submission, User
from files.helpers.bot_controls import (
    bot_profile_state,
    bot_publish_decision,
    is_bot_profile,
    save_bot_control,
)
from files.helpers.config.const import DEFAULT_RATELIMIT, DEFAULT_RATELIMIT_SLOWER, PAGE_SIZE, PERMS
from files.helpers.config import modaction_types as modaction_config
from files.helpers.get import get_profile_picture, get_user
from files.helpers.media import process_image
from files.helpers.regex import valid_username_regex
from files.helpers.sanitize import sanitize
from files.routes.wrappers import admin_level_required, auth_desired_with_logingate, auth_required, get_ID, get_logged_in_user


_ADMIN_PROFILE_ACTIONS = {
    "bot_controls_update": {
        "str": "updated bot controls for {self.target_link}",
        "icon": "fa-robot",
        "color": "bg-primary",
    },
    "force_username_change": {
        "str": "force-changed the username of {self.target_link}",
        "icon": "fa-user-edit",
        "color": "bg-primary",
    },
    "wipe_reserved_username": {
        "str": "wiped the reserved username of {self.target_link}",
        "icon": "fa-eraser",
        "color": "bg-danger",
    },
    "edit_user_bio": {
        "str": "edited the bio of {self.target_link}",
        "icon": "fa-address-card",
        "color": "bg-primary",
    },
    "edit_user_profile_css": {
        "str": "edited the profile CSS of {self.target_link}",
        "icon": "fa-code",
        "color": "bg-primary",
    },
    "set_profile_picture": {
        "str": "changed the profile picture of {self.target_link}",
        "icon": "fa-user-circle",
        "color": "bg-primary",
    },
    "set_profile_banner": {
        "str": "changed the profile banner of {self.target_link}",
        "icon": "fa-image",
        "color": "bg-primary",
    },
    "set_profile_background": {
        "str": "changed the profile background of {self.target_link}",
        "icon": "fa-images",
        "color": "bg-primary",
    },
}

for _catalog_name in ("MODACTION_TYPES", "MODACTION_TYPES_FILTERED", "MODACTION_TYPES__FILTERED"):
    _catalog = getattr(modaction_config, _catalog_name, None)
    if isinstance(_catalog, dict):
        _catalog.update({key: dict(value) for key, value in _ADMIN_PROFILE_ACTIONS.items()})


def _bot_state_for_template(user):
    return bot_profile_state(g.db, user, with_counts=True)


app.jinja_env.globals["bot_profile_state"] = _bot_state_for_template


def _target_user(user_id: int, actor: User) -> User:
    user = g.db.get(User, user_id)
    if not user:
        abort(404)
    if int(user.admin_level) > int(actor.admin_level):
        abort(403)
    return user


def _parse_limit(value, field: str) -> int | None:
    value = (value or "").strip()
    if value == "":
        return None
    try:
        result = int(value)
    except (TypeError, ValueError):
        abort(400, f"{field} must be a whole number or blank.")
    if result < 0 or result > 100000:
        abort(400, f"{field} must be between 0 and 100000.")
    return result


def _log(actor: User, target: User, kind: str, note: str | None = None) -> None:
    g.db.add(ModAction(
        kind=kind,
        user_id=actor.id,
        target_user_id=target.id,
        _note=(note or "")[:1000] or None,
    ))


def _remove_managed_image(filename: str | None) -> None:
    if filename and filename.startswith("/images/") and os.path.isfile(filename):
        try:
            os.remove(filename)
        except OSError:
            pass


@app.post("/admin/profile/<int:user_id>/bot-controls")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@admin_level_required(PERMS["USER_MODERATION_TOOLS_VISIBLE"])
def admin_profile_bot_controls(user_id, v: User):
    user = _target_user(user_id, v)
    if not is_bot_profile(g.db, user):
        abort(400, "This profile is not a bot account.")

    enabled = request.form.get("enabled") == "1"
    post_limit = _parse_limit(request.form.get("daily_post_limit"), "Daily post limit")
    comment_limit = _parse_limit(request.form.get("daily_comment_limit"), "Daily comment limit")
    save_bot_control(
        g.db,
        user.id,
        enabled=enabled,
        daily_post_limit=post_limit,
        daily_comment_limit=comment_limit,
        updated_by=v.id,
    )
    _log(
        v,
        user,
        "bot_controls_update",
        f"enabled: {enabled}, posts/day: {post_limit if post_limit is not None else 'unlimited'}, comments/day: {comment_limit if comment_limit is not None else 'unlimited'}",
    )
    return redirect(f"/@{user.username}")


@app.post("/admin/profile/<int:user_id>/username")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@admin_level_required(PERMS["USER_MODERATION_TOOLS_VISIBLE"])
def admin_force_username(user_id, v: User):
    user = _target_user(user_id, v)
    new_name = (request.form.get("username") or "").strip()
    if not valid_username_regex.fullmatch(new_name):
        abort(400, "This isn't a valid username.")
    if new_name.lower() == (user.username or "").lower():
        abort(400, "That is already the user's username.")

    search_name = new_name.replace("\\", "").replace("_", "\\_").replace("%", "")
    collision = g.db.query(User).filter(
        User.id != user.id,
        or_(
            User.username.ilike(search_name),
            User.original_username.ilike(search_name),
        ),
    ).first()
    if collision:
        abort(409, f"Username '{new_name}' is already in use or reserved.")

    old_name = user.username
    user.username = new_name
    g.db.add(user)
    for identifier in (user.id, old_name, user.original_username, new_name):
        if identifier is not None:
            cache.delete_memoized(get_profile_picture, identifier)
    _log(v, user, "force_username_change", f"@{old_name} -> @{new_name}")
    return redirect(f"/@{new_name}")


@app.post("/admin/profile/<int:user_id>/wipe-reserved-username")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@admin_level_required(PERMS["USER_MODERATION_TOOLS_VISIBLE"])
def admin_wipe_reserved_username(user_id, v: User):
    user = _target_user(user_id, v)
    old_reserved = user.original_username
    if not old_reserved:
        return redirect(f"/@{user.username}")
    user.original_username = None
    g.db.add(user)
    cache.delete_memoized(get_profile_picture, old_reserved)
    _log(v, user, "wipe_reserved_username", f"released @{old_reserved}")
    return redirect(f"/@{user.username}")


@app.post("/admin/profile/<int:user_id>/bio")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@admin_level_required(PERMS["USER_MODERATION_TOOLS_VISIBLE"])
def admin_edit_user_bio(user_id, v: User):
    user = _target_user(user_id, v)
    bio = (request.form.get("bio") or "")[:1500].strip()
    if bio:
        bio_html = sanitize(bio)
        if isinstance(bio_html, tuple) or len(bio_html) > 10000:
            abort(400, "Rendered bio is too long.")
        user.bio = bio
        user.bio_html = bio_html
    else:
        user.bio = None
        user.bio_html = None
    g.db.add(user)
    _log(v, user, "edit_user_bio")
    return redirect(f"/@{user.username}")


@app.post("/admin/profile/<int:user_id>/profile-css")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@admin_level_required(PERMS["USER_MODERATION_TOOLS_VISIBLE"])
def admin_edit_user_profile_css(user_id, v: User):
    user = _target_user(user_id, v)
    css = (request.form.get("profilecss") or "").replace("\\", "").strip()[:6000]
    # Reuse the same validator as self-service profile CSS.
    from files.helpers.sanitize import validate_css
    valid, error = validate_css(css)
    if not valid:
        abort(400, error)
    user.profilecss = css or None
    g.db.add(user)
    _log(v, user, "edit_user_profile_css")
    return redirect(f"/@{user.username}")


@app.post("/admin/profile/<int:user_id>/image/<kind>")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@admin_level_required(PERMS["USER_MODERATION_TOOLS_VISIBLE"])
def admin_set_profile_image(user_id, kind, v: User):
    user = _target_user(user_id, v)
    if kind not in {"picture", "banner", "background"}:
        abort(404)
    file = request.files.get("file")
    if not file or not file.filename or not (file.content_type or "").startswith("image/"):
        abort(400, "Choose a valid image.")

    name = f"/images/{str(time.time()).replace('.', '')}.webp"
    file.save(name)

    if kind == "picture":
        highres = process_image(name, v, uploader_id=user.id)
        if not highres:
            abort(422)
        resized = name.replace(".webp", "r.webp")
        copyfile(name, resized)
        imageurl = process_image(resized, v, resize=100, uploader_id=user.id)
        if not imageurl:
            abort(422)
        _remove_managed_image(user.profileurl)
        if user.highres != user.profileurl:
            _remove_managed_image(user.highres)
        user.highres = highres
        user.profileurl = imageurl
        action = "set_profile_picture"
        for identifier in (user.id, user.username, user.original_username):
            if identifier is not None:
                cache.delete_memoized(get_profile_picture, identifier)
    elif kind == "banner":
        imageurl = process_image(name, v, uploader_id=user.id)
        if not imageurl:
            abort(422)
        _remove_managed_image(user.bannerurl)
        user.bannerurl = imageurl
        action = "set_profile_banner"
    else:
        imageurl = process_image(name, v, uploader_id=user.id)
        if not imageurl:
            abort(422)
        _remove_managed_image(user.profile_background)
        user.profile_background = imageurl
        action = "set_profile_background"

    g.db.add(user)
    _log(v, user, action)
    return redirect(f"/@{user.username}")


def _visible_modaction_types(v: User | None):
    if v and v.admin_level >= PERMS["USER_SHADOWBAN"]:
        if v.admin_level >= PERMS["PROGSTACK"]:
            return modaction_config.MODACTION_TYPES
        return modaction_config.MODACTION_TYPES__FILTERED
    return modaction_config.MODACTION_TYPES_FILTERED


def _target_action_query(target_id: int, v: User | None):
    post_ids = g.db.query(Submission.id).filter(Submission.author_id == target_id)
    comment_ids = g.db.query(Comment.id).filter(Comment.author_id == target_id)
    actions = g.db.query(ModAction).filter(or_(
        ModAction.target_user_id == target_id,
        ModAction.target_submission_id.in_(post_ids),
        ModAction.target_comment_id.in_(comment_ids),
    ))
    if not (v and v.admin_level >= PERMS["USER_SHADOWBAN"]):
        actions = actions.filter(ModAction.kind.notin_(modaction_config.MODACTION_PRIVILEGED_TYPES))
    if not (v and v.admin_level >= PERMS["PROGSTACK"]):
        actions = actions.filter(ModAction.kind.notin_(modaction_config.MODACTION_PRIVILEGED__TYPES))
    return actions


def _history_context(target: User, v: User | None, *, full_log: bool):
    try:
        page = max(1, int(request.args.get("page", 1)))
    except (TypeError, ValueError):
        page = 1

    types = _visible_modaction_types(v)
    kind = request.args.get("kind")
    if kind and kind not in types:
        kind = None

    admin = (request.args.get("admin") or "").strip() if full_log else ""
    actions = _target_action_query(target.id, v)
    if admin:
        actor = get_user(admin, graceful=True, include_shadowbanned=True)
        if actor:
            actions = actions.filter(ModAction.user_id == actor.id)
        else:
            admin = ""
    if kind:
        actions = actions.filter(ModAction.kind == kind)

    actions = actions.order_by(ModAction.id.desc()).offset(PAGE_SIZE * (page - 1)).limit(PAGE_SIZE + 1).all()
    next_exists = len(actions) > PAGE_SIZE
    actions = actions[:PAGE_SIZE]

    relevant_kinds = {action.kind for action in _target_action_query(target.id, v).all()}
    types = {key: value for key, value in types.items() if key in relevant_kinds}
    admins = []
    if full_log:
        actor_ids = {action.user_id for action in _target_action_query(target.id, v).all() if action.user_id}
        if actor_ids:
            admins = [row[0] for row in g.db.query(User.username).filter(User.id.in_(actor_ids)).order_by(User.username).all()]

    return {
        "actions": actions,
        "next_exists": next_exists,
        "page": page,
        "types": types,
        "type": kind,
        "admin": admin,
        "admins": admins,
    }


@app.get("/@<username>/modlog")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_desired_with_logingate
def profile_moderation_history(username, v=None):
    user = get_user(username, v=v, graceful=True, include_shadowbanned=bool(v and v.can_see_shadowbanned))
    if not user or not user.is_visible_to(v):
        abort(404)
    context = _history_context(user, v, full_log=False)
    return render_template("userpage/moderation_history.html", v=v, u=user, **context)


def _install_target_log_filter() -> None:
    original = app.view_functions.get("log")
    if not original or getattr(original, "_toc_target_filter", False):
        return

    @limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
    @auth_required
    def target_aware_log(v: User):
        target_raw = (request.args.get("target_id") or "").strip()
        if not target_raw:
            return original()
        try:
            target_id = int(target_raw)
        except ValueError:
            abort(400, "Invalid target_id")
        target = g.db.get(User, target_id)
        if not target:
            abort(404)
        context = _history_context(target, v, full_log=True)
        return render_template("user_modlog.html", v=v, target=target, **context)

    target_aware_log._toc_target_filter = True
    app.view_functions["log"] = target_aware_log


_install_target_log_filter()


def _install_snatchy_guard() -> None:
    snatchy = importlib.import_module("files.routes.snatchy")
    original = getattr(snatchy, "_import_reddit_post", None)
    if not original or getattr(original, "_toc_bot_controls_guard", False):
        return

    def guarded(payload):
        account = snatchy.ensure_snatchy_account(g.db)
        allowed, reason, _ = bot_publish_decision(g.db, account.id, "post")
        if not allowed:
            return {"status": "disabled", "reason": reason}
        return original(payload)

    guarded._toc_bot_controls_guard = True
    snatchy._import_reddit_post = guarded


_install_snatchy_guard()


@app.before_request
def enforce_api_bot_controls():
    if request.endpoint not in {"submit_post", "comment"}:
        return None
    v = get_logged_in_user()
    if not v or not v.client or not is_bot_profile(g.db, v):
        return None
    kind = "post" if request.endpoint == "submit_post" else "comment"
    allowed, reason, _ = bot_publish_decision(g.db, v.id, kind)
    if not allowed:
        abort(429, reason)
    return None
