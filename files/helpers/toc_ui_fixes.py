import os
from pathlib import Path

import fcntl

from files.__main__ import app
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


def _atomic_write(path: Path, content: str) -> None:
    temp_path = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temp_path.write_text(content, encoding="utf-8")
    os.replace(temp_path, path)


def _write_if_changed(path: Path, original: str, updated: str) -> None:
    if updated != original:
        _atomic_write(path, updated)


def _patch_post_identity() -> None:
    """Keep one global post-author identity layout across every post surface.

    Homepage, board feeds, profile post listings and full threads all render the
    same post_meta macro. House identity therefore lives in that macro beside the
    native Verified badge; there is no listing-only house implementation.
    """
    source = _MACROS_TEMPLATE.read_text(encoding="utf-8")
    original = source

    # Undo the abandoned listing-only experiment if this helper ever runs over a
    # previously mutated worktree.
    source = source.replace("{% macro post_meta(p, house_inline=false) %}", "{% macro post_meta(p) %}", 1)
    source = source.replace("{% if p.author.house and not house_inline %}", "{% if p.author.house %}")
    source = source.replace("{% if FEATURES['HOUSES'] and p.author.house %}", "{% if p.author.house %}", 1)

    original_house = '\t\t\t<img loading="lazy" src="{{p.author.house | house_icon}}" height="20" data-bs-toggle="tooltip" data-bs-placement="bottom" title="House {{p.author.house}}" alt="House {{p.author.house}}">'
    old_compact_house = '\t\t\t<img loading="lazy" class="house-user-icon" src="{{p.author.house | house_icon}}" width="20" height="20" style="width:20px;height:20px;display:inline-block!important;object-fit:contain;vertical-align:middle;margin-right:-2px" data-bs-toggle="tooltip" data-bs-placement="bottom" title="House {{p.author.house}}" alt="House {{p.author.house}}">'
    compact_house = '\t\t\t<img loading="lazy" class="house-user-icon" src="{{p.author.house | house_icon}}" width="20" height="20" style="' + _HOUSE_ICON_STYLE + '" data-bs-toggle="tooltip" data-bs-placement="bottom" title="House {{p.author.house}}" alt="House {{p.author.house}}">'
    source = source.replace(original_house, compact_house, 1)
    source = source.replace(old_compact_house, compact_house, 1)

    # House and Verified are one compact badge group. Do not add Bootstrap's
    # extra left margin between them when a house exists.
    source = source.replace(
        'class="fas fa-badge-check align-middle ml-1 {% if p.author.verified==\'Glowiefied\' %}glow{% endif %}"',
        'class="fas fa-badge-check align-middle {% if not p.author.house %}ml-1 {% endif %}{% if p.author.verified==\'Glowiefied\' %}glow{% endif %}"',
        1,
    )

    # The compact author avatar used to sit visibly below the username baseline.
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

    # Remove any stale inline/listing-only house block from an older runtime tree.
    stale_inline_start = '\t\t\t{% if p.author.house and house_inline %}\n'
    if stale_inline_start in source:
        start = source.index(stale_inline_start)
        end_marker = '\t\t\t{% endif %}\n'
        end = source.index(end_marker, start) + len(end_marker)
        source = source[:start] + source[end:]

    _write_if_changed(_MACROS_TEMPLATE, original, source)


def _patch_submission_listing_macro_import() -> None:
    """Stop post listings from shadowing the root template's repaired macros.

    root.html already imports util/macros.html and passes that namespace through
    includes. submission_listing.html historically imported the same file again,
    which allowed the listing to hold a different compiled post_meta macro than a
    full thread. Only import locally when this template is rendered standalone
    (for example by the post_embed filter).
    """
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
    """Discard templates compiled before runtime source normalization.

    This is important for submission_listing.html: a cached import of post_meta
    could otherwise keep the old macro while a full thread compiled the repaired
    version later, making house badges appear only after opening a post.
    """
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
