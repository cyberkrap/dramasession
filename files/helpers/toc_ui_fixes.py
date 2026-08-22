import os
from pathlib import Path

import fcntl
from flask import abort, g, has_request_context, render_template_string, request, session

from files.__main__ import app
from files.classes.submission import Submission
from files.classes.user import User
from files.helpers.config.awards import AWARDS, AWARDS_ENABLED
from files.helpers.config.const import FEATURES


_LOCK_PATH = "/tmp/obsession-toc-ui-fixes.lock"
_MACROS_TEMPLATE = Path("files/templates/util/macros.html")
_SUBMISSION_LISTING_TEMPLATE = Path("files/templates/submission_listing.html")
_COMMENTS_TEMPLATE = Path("files/templates/comments.html")
_PROFILE_BANNER_TEMPLATE = Path("files/templates/userpage/banner.html")

# House identity is a compact metadata badge, like Verified. Keep it out of the
# avatar/username spacing and keep the house/checkmark pair visually tight.
_HOUSE_ICON_STYLE = "width:20px;height:20px;display:inline-block!important;object-fit:contain;vertical-align:middle;margin-right:-2px"


@app.template_filter("house_identity")
def house_identity(user):
    """Return the authoritative house for an identity row."""
    if not user:
        return ""

    house = str(getattr(user, "house", "") or "").strip()
    if house:
        return house

    if not has_request_context() or not hasattr(g, "db"):
        return ""

    user_id = getattr(user, "id", None)
    if not user_id:
        return ""

    cache = getattr(g, "_toc_house_identity_cache", None)
    if cache is None:
        cache = {}
        g._toc_house_identity_cache = cache

    if user_id not in cache:
        cache[user_id] = str(
            g.db.query(User.house).filter(User.id == user_id).scalar() or ""
        ).strip()

    return cache[user_id]


def _atomic_write(path: Path, content: str) -> None:
    temp_path = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temp_path.write_text(content, encoding="utf-8")
    os.replace(temp_path, path)


def _write_if_changed(path: Path, original: str, updated: str) -> None:
    if updated != original:
        _atomic_write(path, updated)


def _patch_post_identity() -> None:
    """Render house identity on both full threads and compact post listings.

    Compact listings render metadata inside a zero-width horizontal-scroll
    wrapper. A standalone image before the author link can disappear there even
    while the same image is visible on a full thread. The repository previously
    solved this exact production bug by rendering the house marker *inside* the
    author link for listings. A later cleanup mistakenly removed that proven
    listing-specific path. Restore it while keeping one authoritative house value.
    """
    source = _MACROS_TEMPLATE.read_text(encoding="utf-8")
    original = source

    # Macro accepts an explicit listing mode again. This is intentional: the
    # listing container behaves differently from the full-thread metadata row.
    source = source.replace(
        "{% macro post_meta(p) %}",
        "{% macro post_meta(p, house_inline=false) %}",
        1,
    )

    # Resolve one authoritative house value for both rendering paths.
    if "p.author | house_identity" not in source:
        source = source.replace(
            "{% if FEATURES['HOUSES'] and p.author.house %}",
            "{% set author_house = p.author | house_identity %}\n\t\t{% if author_house and not house_inline %}",
            1,
        )
        source = source.replace(
            "{% if p.author.house %}",
            "{% set author_house = p.author | house_identity %}\n\t\t{% if author_house and not house_inline %}",
            1,
        )
    else:
        source = source.replace(
            "{% if author_house %}",
            "{% if author_house and not house_inline %}",
            1,
        )

    source = source.replace("{{p.author.house | house_icon}}", "{{author_house | house_icon}}", 1)
    source = source.replace("House {{p.author.house}}", "House {{author_house}}", 2)

    original_house = '\t\t\t<img loading="lazy" src="{{author_house | house_icon}}" height="20" data-bs-toggle="tooltip" data-bs-placement="bottom" title="House {{author_house}}" alt="House {{author_house}}">'
    old_compact_house = '\t\t\t<img loading="lazy" class="house-user-icon" src="{{author_house | house_icon}}" width="20" height="20" style="width:20px;height:20px;display:inline-block!important;object-fit:contain;vertical-align:middle;margin-right:-2px" data-bs-toggle="tooltip" data-bs-placement="bottom" title="House {{author_house}}" alt="House {{author_house}}">'
    compact_house = '\t\t\t<img loading="lazy" class="house-user-icon" src="{{author_house | house_icon}}" width="20" height="20" style="' + _HOUSE_ICON_STYLE + '" data-bs-toggle="tooltip" data-bs-placement="bottom" title="House {{author_house}}" alt="House {{author_house}}">'
    source = source.replace(original_house, compact_house, 1)
    source = source.replace(old_compact_house, compact_house, 1)

    # House and Verified are one compact badge group on full threads.
    source = source.replace(
        'class="fas fa-badge-check align-middle ml-1 {% if p.author.verified==\'Glowiefied\' %}glow{% endif %}"',
        'class="fas fa-badge-check align-middle {% if not author_house %}ml-1 {% endif %}{% if p.author.verified==\'Glowiefied\' %}glow{% endif %}"',
        1,
    )
    source = source.replace(
        "{% if not p.author.house %}ml-1 {% endif %}",
        "{% if not author_house %}ml-1 {% endif %}",
        1,
    )

    # Listing-safe marker: put the image inside the author link so the zero-width
    # metadata wrapper cannot clip it away. Insert it before the compact avatar.
    if 'class="house-user-icon house-inline-user-icon"' not in source:
        avatar_marker = '\t\t\t<div class="profile-pic-30-wrapper"'
        marker_index = source.find(avatar_marker)
        if marker_index < 0:
            raise RuntimeError("Could not locate compact post author avatar")
        inline_icon = (
            '\t\t\t{% if author_house and house_inline %}\n'
            '\t\t\t\t<img loading="lazy" class="house-user-icon house-inline-user-icon" '
            'src="{{author_house | house_icon}}" width="20" height="20" style="' + _HOUSE_ICON_STYLE + '" '
            'data-bs-toggle="tooltip" data-bs-placement="bottom" title="House {{author_house}}" alt="House {{author_house}}">\n'
            '\t\t\t{% endif %}\n'
        )
        source = source[:marker_index] + inline_icon + source[marker_index:]

    source = source.replace(
        '<div class="profile-pic-30-wrapper" style="margin-top:9px">',
        '<div class="profile-pic-30-wrapper" style="margin-top:2px">',
        1,
    )
    source = source.replace(
        '<div class="profile-pic-30-wrapper" style="margin-top:4px">',
        '<div class="profile-pic-30-wrapper" style="margin-top:2px">',
        1,
    )

    if "{% macro post_meta(p, house_inline=false) %}" not in source:
        raise RuntimeError("Post metadata did not become listing-aware")
    if "author_house and not house_inline" not in source:
        raise RuntimeError("Standalone post house marker was not scoped to full threads")
    if "author_house and house_inline" not in source:
        raise RuntimeError("Inline post listing house marker was not installed")

    _write_if_changed(_MACROS_TEMPLATE, original, source)


def _patch_submission_listing_macro_import() -> None:
    """Use the listing-safe house rendering mode everywhere posts are listed."""
    source = _SUBMISSION_LISTING_TEMPLATE.read_text(encoding="utf-8")
    original = source

    unconditional = "{%- import 'util/macros.html' as macros with context -%}"
    conditional = (
        "{% if macros is not defined -%}\n"
        "{%- import 'util/macros.html' as macros with context -%}\n"
        "{%- endif %}"
    )
    if source.startswith(unconditional):
        source = conditional + source[len(unconditional):]

    source = source.replace(
        "{{ macros.post_meta(p) }}",
        "{{ macros.post_meta(p, true) }}",
        1,
    )

    if not source.startswith(conditional):
        raise RuntimeError("Submission listing still owns an unconditional macro import")
    if "{{ macros.post_meta(p, true) }}" not in source:
        raise RuntimeError("Submission listing did not enable inline house identity")

    _write_if_changed(_SUBMISSION_LISTING_TEMPLATE, original, source)


def _patch_comment_identity() -> None:
    """Keep comment house/checkmark spacing consistent with post identity."""
    source = _COMMENTS_TEMPLATE.read_text(encoding="utf-8")
    original = source

    source = source.replace(
        "{% if FEATURES['HOUSES'] and c.author.house %}",
        "{% if c.author.house %}",
    )

    original_house = '\t\t\t\t\t\t<img loading="lazy" src="{{c.author.house | house_icon}}" height="20" data-bs-toggle="tooltip" data-bs-placement="bottom" title="House {{c.author.house}}" alt="House {{c.author.house}}">'
    compact_house = '\t\t\t\t\t\t<img loading="lazy" class="house-user-icon" src="{{c.author.house | house_icon}}" width="20" height="20" style="' + _HOUSE_ICON_STYLE + '" data-bs-toggle="tooltip" data-bs-placement="bottom" title="House {{c.author.house}}" alt="House {{c.author.house}}">'
    source = source.replace(original_house, compact_house, 1)

    source = source.replace(
        'class="fas fa-badge-check align-middle ml-1 {% if c.author.verified==\'Glowiefied\' %}glow{% endif %}"',
        'class="fas fa-badge-check align-middle {% if not c.author.house %}ml-1 {% endif %}{% if c.author.verified==\'Glowiefied\' %}glow{% endif %}"',
        1,
    )

    _write_if_changed(_COMMENTS_TEMPLATE, original, source)


def _restore_profile_house_identity() -> None:
    """Keep the house badge on the profile identity row beside other badges."""
    source = _PROFILE_BANNER_TEMPLATE.read_text(encoding="utf-8")
    original = source

    if 'id="profile--house"' not in source:
        verified_marker = '\t\t\t\t\t\t{% if u.verified %}\n'
        if verified_marker not in source:
            raise RuntimeError("Could not locate profile verified badge block")
        house_block = (
            '\t\t\t\t\t\t{% if FEATURES[\'HOUSES\'] and u.house %}\n'
            '\t\t\t\t\t\t\t<img loading="lazy" id="profile--house" src="{{u.house | house_icon}}" height="20" data-bs-toggle="tooltip" data-bs-placement="bottom" title="House {{u.house}}" alt="House {{u.house}}">\n'
            '\t\t\t\t\t\t{% endif %}\n'
        )
        source = source.replace(verified_marker, house_block + verified_marker, 1)

    _write_if_changed(_PROFILE_BANNER_TEMPLATE, original, source)


def _clear_template_cache() -> None:
    app.jinja_env.cache.clear()
    bytecode_cache = app.jinja_env.bytecode_cache
    if bytecode_cache and hasattr(bytecode_cache, "clear"):
        bytecode_cache.clear()


def install_toc_ui_fixes() -> None:
    """Keep TOC identity markers and public award labels consistent."""
    FEATURES["HOUSES"] = True

    for catalog in (AWARDS, AWARDS_ENABLED):
        if "ban" in catalog:
            catalog["ban"]["title"] = "Ban"
        if "unban" in catalog:
            catalog["unban"]["title"] = "Unban"

    with open(_LOCK_PATH, "w", encoding="utf-8") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        _patch_post_identity()
        _patch_submission_listing_macro_import()
        _patch_comment_identity()
        _restore_profile_house_identity()
        _clear_template_cache()


@app.get("/admin/toc-house-debug")
def toc_house_debug():
    """Admin-only production probe for the listing/full-thread mismatch."""
    try:
        viewer_id = int(session.get("lo_user") or 0)
    except (TypeError, ValueError):
        viewer_id = 0
    viewer = g.db.get(User, viewer_id) if viewer_id else None
    if not viewer or not int(viewer.admin_level):
        abort(403)
    viewer.client = None

    try:
        requested_post = int(request.args.get("post", 0) or 0)
    except (TypeError, ValueError):
        requested_post = 0

    query = g.db.query(Submission)
    if requested_post:
        posts = query.filter(Submission.id == requested_post).all()
    else:
        posts = query.order_by(Submission.id.desc()).limit(12).all()

    macro_source, _, _ = app.jinja_env.loader.get_source(app.jinja_env, "util/macros.html")
    listing_source, _, _ = app.jinja_env.loader.get_source(app.jinja_env, "submission_listing.html")

    rows = []
    for post in posts:
        loaded_house = str(getattr(post.author, "house", "") or "").strip() if post.author else ""
        direct_house = str(
            g.db.query(User.house).filter(User.id == post.author_id).scalar() or ""
        ).strip()
        resolved_house = house_identity(post.author)

        try:
            rendered_full_meta = render_template_string(
                "{% import 'util/macros.html' as macros with context %}{{ macros.post_meta(p, false) }}",
                p=post,
                v=viewer,
            )
            rendered_listing_meta = render_template_string(
                "{% import 'util/macros.html' as macros with context %}{{ macros.post_meta(p, true) }}",
                p=post,
                v=viewer,
            )
        except Exception as exc:
            rendered_full_meta = f"render-error:{type(exc).__name__}:{exc}"
            rendered_listing_meta = rendered_full_meta

        rows.append({
            "post_id": post.id,
            "title": post.title,
            "author_id": post.author_id,
            "author": post.author.username if post.author else None,
            "loaded_house": loaded_house,
            "direct_db_house": direct_house,
            "resolved_house": resolved_house,
            "full_meta_has_house_icon": "house-user-icon" in rendered_full_meta,
            "listing_meta_has_inline_house_icon": "house-inline-user-icon" in rendered_listing_meta,
            "full_meta_has_house_alt": bool(resolved_house and f"House {resolved_house}" in rendered_full_meta),
            "listing_meta_has_house_alt": bool(resolved_house and f"House {resolved_house}" in rendered_listing_meta),
            "listing_meta_excerpt": rendered_listing_meta[:800],
        })

    return {
        "features_houses": bool(FEATURES.get("HOUSES")),
        "macro_source_is_listing_aware": "post_meta(p, house_inline=false)" in macro_source,
        "macro_source_has_inline_house_icon": "house-inline-user-icon" in macro_source,
        "listing_calls_inline_house_mode": "macros.post_meta(p, true)" in listing_source,
        "jinja_cache_entries": len(app.jinja_env.cache),
        "posts": rows,
    }
