import os
import time
from functools import wraps
from pathlib import Path
from urllib.parse import urlencode

import fcntl
from flask import abort, g, redirect, render_template, request
from sqlalchemy import func, or_

from files.__main__ import app, limiter
from files.classes.hats import Hat, HatDef
from files.classes.mod_logs import ModAction
from files.helpers.cloudflare import purge_files_in_cache
from files.helpers.config.const import *
from files.helpers.config.modaction_types import MODACTION_TYPES, MODACTION_TYPES_FILTERED
from files.helpers.regex import description_regex, hat_regex
from files.routes.wrappers import admin_level_required, get_ID


ADMIN_HATS_PAGE_SIZE = 60
_LOCK_PATH = "/tmp/obsession-final-ui-fixes.lock"
_ADMIN_HOME_PATH = Path("files/templates/admin/admin_home.html")

HAT_MODACTION_TYPES = {
    "approve_hat": {
        "str": "approved a hat made by {self.target_link}",
        "icon": "fa-hat-cowboy",
        "color": "bg-success",
    },
    "reject_hat": {
        "str": "rejected a hat made by {self.target_link}",
        "icon": "fa-hat-cowboy",
        "color": "bg-danger",
    },
    "edit_hat": {
        "str": "edited a hat made by {self.target_link}",
        "icon": "fa-hat-cowboy",
        "color": "bg-primary",
    },
    "delete_hat": {
        "str": "deleted a hat made by {self.target_link}",
        "icon": "fa-hat-cowboy",
        "color": "bg-danger",
    },
}


def _install_hat_modaction_types():
    MODACTION_TYPES.update(HAT_MODACTION_TYPES)
    MODACTION_TYPES_FILTERED.update(HAT_MODACTION_TYPES)


def _patch_admin_home_hat_links():
    if not _ADMIN_HOME_PATH.exists():
        return
    with open(_LOCK_PATH, "w", encoding="utf-8") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        source = _ADMIN_HOME_PATH.read_text(encoding="utf-8")
        marker = "<h4>Community Assets</h4>\n<ul>\n"
        block = """<h4>Community Assets</h4>
<ul>
    {% if FEATURES['HATS'] and v.admin_level >= PERMS['MODERATE_PENDING_SUBMITTED_ASSETS'] %}
        <li><a href="/submit/hats">Review Hat Submissions</a></li>
    {% endif %}
    {% if FEATURES['HATS'] and v.admin_level >= PERMS['UPDATE_ASSETS'] %}
        <li><a href="/admin/hats">Manage Approved Hats</a></li>
    {% endif %}
"""
        if block in source or marker not in source:
            return
        source = source.replace(marker, block, 1)
        temp_path = _ADMIN_HOME_PATH.with_name(f".{_ADMIN_HOME_PATH.name}.{os.getpid()}.tmp")
        temp_path.write_text(source, encoding="utf-8")
        os.replace(temp_path, _ADMIN_HOME_PATH)


def _recent_hat_action(kind, name):
    now = int(time.time())
    return (
        g.db.query(ModAction.id)
        .filter(
            ModAction.kind == kind,
            ModAction._note == name,
            ModAction.created_utc >= now - 10,
        )
        .first()
    )


def _install_hat_submission_tracking():
    approve = app.view_functions.get("approve_hat")
    if approve and not getattr(approve, "_tracks_hat_approval", False):
        @wraps(approve)
        def tracked_approve(*args, **kwargs):
            pending_name = str((request.view_args or {}).get("name") or "").strip()
            hat = g.db.query(HatDef).filter_by(name=pending_name).one_or_none()
            was_pending = bool(hat and hat.submitter_id is not None)
            author_id = hat.author_id if hat else None

            response = approve(*args, **kwargs)

            actor = getattr(g, "v", None)
            approved_name = (request.values.get("name") or pending_name).strip()
            if was_pending and hat:
                hat.created_utc = int(time.time())
                g.db.add(hat)
            if was_pending and actor and author_id and not _recent_hat_action("approve_hat", approved_name):
                g.db.add(ModAction(
                    kind="approve_hat",
                    user_id=actor.id,
                    target_user_id=author_id,
                    _note=approved_name,
                ))
            return response

        tracked_approve._tracks_hat_approval = True
        app.view_functions["approve_hat"] = tracked_approve

    remove = app.view_functions.get("remove_hat")
    if remove and not getattr(remove, "_tracks_hat_rejection", False):
        @wraps(remove)
        def tracked_remove(*args, **kwargs):
            name = str((request.view_args or {}).get("name") or "").strip()
            hat = g.db.query(HatDef).filter_by(name=name).one_or_none()
            if hat and hat.submitter_id is None:
                abort(409, "Approved hats must be removed from the Manage Hats admin page.")

            was_pending = bool(hat and hat.submitter_id is not None)
            submitter_id = hat.submitter_id if hat else None
            author_id = hat.author_id if hat else None
            response = remove(*args, **kwargs)

            actor = getattr(g, "v", None)
            if (
                was_pending
                and actor
                and actor.id != submitter_id
                and actor.admin_level >= PERMS["MODERATE_PENDING_SUBMITTED_ASSETS"]
                and not _recent_hat_action("reject_hat", name)
            ):
                g.db.add(ModAction(
                    kind="reject_hat",
                    user_id=actor.id,
                    target_user_id=author_id,
                    _note=name,
                ))
            return response

        tracked_remove._tracks_hat_rejection = True
        app.view_functions["remove_hat"] = tracked_remove


def _admin_hat_params(**extra):
    params = {
        "page": request.form.get("page", request.values.get("page", "1")),
        "q": request.form.get("q", request.values.get("q", "")),
        "sort": request.form.get("sort", request.values.get("sort", "name")),
    }
    params.update(extra)
    return urlencode(params)


def _system_hat_names():
    names = {"Santa Hat III", "Winter Cap", "Present Bow", "Cakeday"}
    for value in forced_hats.values():
        if isinstance(value, (tuple, list)) and value:
            names.add(str(value[0]))
    return names


def _hat_rename_moves(old_name, new_name):
    if old_name == new_name:
        return []

    approved_old = Path("files/assets/images/hats") / f"{old_name}.webp"
    approved_new = Path("files/assets/images/hats") / f"{new_name}.webp"
    if not approved_old.is_file():
        abort(409, "The approved hat image is missing, so this hat cannot be safely renamed.")
    if approved_new.exists():
        abort(409, "A hat image with the new name already exists.")

    moves = [(approved_old, approved_new)]
    optional_pairs = [
        (Path("/asset_submissions/hats") / f"{old_name}.webp", Path("/asset_submissions/hats") / f"{new_name}.webp"),
        (Path("/asset_submissions/hats") / old_name, Path("/asset_submissions/hats") / new_name),
    ]
    for ext in IMAGE_FORMATS:
        optional_pairs.append((
            Path("/asset_submissions/hats/original") / f"{old_name}.{ext}",
            Path("/asset_submissions/hats/original") / f"{new_name}.{ext}",
        ))

    for source, destination in optional_pairs:
        if not source.is_file():
            continue
        if destination.exists():
            abort(409, "A stored hat file with the new name already exists.")
        moves.append((source, destination))
    return moves


def _apply_hat_file_moves(moves):
    moved = []
    try:
        for source, destination in moves:
            destination.parent.mkdir(parents=True, exist_ok=True)
            os.replace(source, destination)
            moved.append((source, destination))
    except OSError:
        _restore_hat_file_moves(moved)
        raise
    return moved


def _restore_hat_file_moves(moves):
    for source, destination in reversed(moves):
        try:
            if destination.exists() and not source.exists():
                os.replace(destination, source)
        except OSError:
            pass


def _purge_hat_names(*names):
    urls = []
    for name in dict.fromkeys(name for name in names if name):
        urls.extend([
            f"https://{SITE}/i/hats/{name}.webp",
            f"https://{SITE}/assets/images/hats/{name}.webp",
        ])
    try:
        purge_files_in_cache(urls)
    except Exception:
        pass


@app.get("/admin/hats")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@admin_level_required(PERMS["UPDATE_ASSETS"])
def admin_hats(v):
    try:
        page = max(1, int(request.values.get("page", 1)))
    except (TypeError, ValueError):
        page = 1
    query_text = (request.values.get("q") or "").strip()[:64]
    sort_name = (request.values.get("sort") or "name").strip().lower()
    if sort_name not in {"name", "newest", "price-desc", "price-asc", "owners"}:
        sort_name = "name"

    query = g.db.query(HatDef).filter(HatDef.submitter_id.is_(None))
    if query_text:
        pattern = f"%{query_text}%"
        query = query.filter(or_(
            HatDef.name.ilike(pattern),
            HatDef.description.ilike(pattern),
        ))

    all_hats = query.all()
    hat_ids = [hat.id for hat in all_hats]
    owner_counts = {}
    if hat_ids:
        owner_counts = dict(
            g.db.query(Hat.hat_id, func.count(Hat.user_id))
            .filter(Hat.hat_id.in_(hat_ids))
            .group_by(Hat.hat_id)
            .all()
        )

    all_hats.sort(key=lambda hat: hat.name.lower())
    if sort_name == "newest":
        all_hats.sort(key=lambda hat: hat.created_utc or 0, reverse=True)
    elif sort_name == "price-desc":
        all_hats.sort(key=lambda hat: hat.price or 0, reverse=True)
    elif sort_name == "price-asc":
        all_hats.sort(key=lambda hat: hat.price or 0)
    elif sort_name == "owners":
        all_hats.sort(key=lambda hat: owner_counts.get(hat.id, 0), reverse=True)

    total = len(all_hats)
    start = (page - 1) * ADMIN_HATS_PAGE_SIZE
    end = start + ADMIN_HATS_PAGE_SIZE
    hats = all_hats[start:end]

    return render_template(
        "admin/hats.html",
        v=v,
        hats=hats,
        owner_counts=owner_counts,
        total=total,
        pending_count=g.db.query(HatDef).filter(HatDef.submitter_id.isnot(None)).count(),
        page=page,
        next_exists=end < total,
        q=query_text,
        sort=sort_name,
        msg=request.values.get("msg"),
        error=request.values.get("error"),
    )


@app.post("/admin/hats/<int:hat_id>/update")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@admin_level_required(PERMS["UPDATE_ASSETS"])
def admin_hat_update(hat_id, v):
    hat = (
        g.db.query(HatDef)
        .filter(HatDef.id == hat_id, HatDef.submitter_id.is_(None))
        .one_or_none()
    )
    if not hat:
        abort(404, "Hat not found.")

    new_name = (request.form.get("name") or "").strip()
    description = (request.form.get("description") or "").strip()
    if not hat_regex.fullmatch(new_name):
        return redirect(f"/admin/hats?{_admin_hat_params(error='Invalid hat name.')}")
    if not description_regex.fullmatch(description):
        return redirect(f"/admin/hats?{_admin_hat_params(error='Invalid hat description.')}")
    try:
        price = int(request.form.get("price", ""))
    except (TypeError, ValueError):
        return redirect(f"/admin/hats?{_admin_hat_params(error='Invalid hat price.')}")
    if price < 0 or price > 2_000_000_000:
        return redirect(f"/admin/hats?{_admin_hat_params(error='Hat price must be between 0 and 2,000,000,000.')}")

    old_name = hat.name
    old_description = hat.description
    old_price = hat.price
    if old_name == new_name and old_description == description and old_price == price:
        return redirect(f"/admin/hats?{_admin_hat_params(msg='No hat changes to save.')}")

    if new_name != old_name and old_name in _system_hat_names():
        return redirect(f"/admin/hats?{_admin_hat_params(error='This system hat name is used by automatic site behavior and cannot be renamed safely.')}")

    if new_name != old_name:
        duplicate = (
            g.db.query(HatDef.id)
            .filter(HatDef.name == new_name, HatDef.id != hat.id)
            .first()
        )
        if duplicate:
            return redirect(f"/admin/hats?{_admin_hat_params(error='A hat with that name already exists.')}")

    moves = _hat_rename_moves(old_name, new_name)
    try:
        moved = _apply_hat_file_moves(moves)
    except OSError:
        return redirect(f"/admin/hats?{_admin_hat_params(error='Could not rename the stored hat files. Nothing was changed.')}")

    changes = []
    if old_name != new_name:
        changes.append(f"name: {old_name} -> {new_name}")
    if old_price != price:
        changes.append(f"price: {old_price} -> {price}")
    if old_description != description:
        changes.append("description changed")

    try:
        hat.name = new_name
        hat.description = description
        hat.price = price
        g.db.add(hat)
        g.db.add(ModAction(
            kind="edit_hat",
            user_id=v.id,
            target_user_id=hat.author_id,
            _note="; ".join(changes),
        ))
        g.db.commit()
    except Exception:
        g.db.rollback()
        _restore_hat_file_moves(moved)
        raise

    _purge_hat_names(old_name, new_name)
    message = f"'{new_name}' updated."
    return redirect(f"/admin/hats?{_admin_hat_params(msg=message)}")


@app.post("/admin/hats/<int:hat_id>/delete")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@admin_level_required(PERMS["UPDATE_ASSETS"])
def admin_hat_delete(hat_id, v):
    hat = (
        g.db.query(HatDef)
        .filter(HatDef.id == hat_id, HatDef.submitter_id.is_(None))
        .one_or_none()
    )
    if not hat:
        abort(404, "Hat not found.")

    name = hat.name
    author_id = hat.author_id

    g.db.query(Hat).filter(Hat.hat_id == hat.id).delete(synchronize_session=False)
    g.db.delete(hat)
    g.db.add(ModAction(
        kind="delete_hat",
        user_id=v.id,
        target_user_id=author_id,
        _note=name,
    ))
    g.db.flush()

    candidates = [
        f"files/assets/images/hats/{name}.webp",
        f"/asset_submissions/hats/{name}.webp",
        f"/asset_submissions/hats/{name}",
    ]
    candidates.extend(
        f"/asset_submissions/hats/original/{name}.{ext}"
        for ext in IMAGE_FORMATS
    )
    for candidate in candidates:
        try:
            os.remove(candidate)
        except OSError:
            pass

    _purge_hat_names(name)

    params = {
        "msg": f"'{name}' deleted.",
        "page": request.form.get("page", "1"),
        "q": request.form.get("q", ""),
        "sort": request.form.get("sort", "name"),
    }
    return redirect(f"/admin/hats?{urlencode(params)}")


_install_hat_modaction_types()
_patch_admin_home_hat_links()
_install_hat_submission_tracking()
