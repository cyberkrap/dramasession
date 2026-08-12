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


@app.get("/admin/hats")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@admin_level_required(PERMS["UPDATE_ASSETS"])
def admin_hats(v):
    try:
        page = max(1, int(request.values.get("page", 1)))
    except (TypeError, ValueError):
        page = 1
    query_text = (request.values.get("q") or "").strip()[:64]

    query = g.db.query(HatDef).filter(HatDef.submitter_id.is_(None))
    if query_text:
        pattern = f"%{query_text}%"
        query = query.filter(or_(
            HatDef.name.ilike(pattern),
            HatDef.description.ilike(pattern),
        ))

    total = query.count()
    hats = (
        query.order_by(HatDef.name.asc())
        .offset((page - 1) * ADMIN_HATS_PAGE_SIZE)
        .limit(ADMIN_HATS_PAGE_SIZE)
        .all()
    )
    hat_ids = [hat.id for hat in hats]
    owner_counts = {}
    if hat_ids:
        owner_counts = dict(
            g.db.query(Hat.hat_id, func.count(Hat.user_id))
            .filter(Hat.hat_id.in_(hat_ids))
            .group_by(Hat.hat_id)
            .all()
        )

    return render_template(
        "admin/hats.html",
        v=v,
        hats=hats,
        owner_counts=owner_counts,
        total=total,
        pending_count=g.db.query(HatDef).filter(HatDef.submitter_id.isnot(None)).count(),
        page=page,
        next_exists=page * ADMIN_HATS_PAGE_SIZE < total,
        q=query_text,
        msg=request.values.get("msg"),
        error=request.values.get("error"),
    )


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

    try:
        purge_files_in_cache([
            f"https://{SITE}/i/hats/{name}.webp",
            f"https://{SITE}/assets/images/hats/{name}.webp",
        ])
    except Exception:
        pass

    params = {
        "msg": f"'{name}' deleted.",
        "page": request.form.get("page", "1"),
        "q": request.form.get("q", ""),
    }
    return redirect(f"/admin/hats?{urlencode(params)}")


_install_hat_modaction_types()
_patch_admin_home_hat_links()
_install_hat_submission_tracking()
