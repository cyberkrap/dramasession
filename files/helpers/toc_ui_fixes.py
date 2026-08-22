import os
from pathlib import Path

import fcntl

from files.helpers.config.awards import AWARDS, AWARDS_ENABLED
from files.helpers.config.const import FEATURES


_LOCK_PATH = "/tmp/obsession-toc-ui-fixes.lock"
_MACROS_TEMPLATE = Path("files/templates/util/macros.html")
_COMMENTS_TEMPLATE = Path("files/templates/comments.html")
_PROFILE_BANNER_TEMPLATE = Path("files/templates/userpage/banner.html")

_HOUSE_ICON_STYLE = "width:20px;height:20px;display:inline-block!important;object-fit:contain;vertical-align:middle;margin-right:-2px"


def _atomic_write(path: Path, content: str) -> None:
    temp_path = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temp_path.write_text(content, encoding="utf-8")
    os.replace(temp_path, path)


def _write_if_changed(path: Path, original: str, updated: str) -> None:
    if updated != original:
        _atomic_write(path, updated)


def _patch_post_identity() -> None:
    """Keep one global post-author identity layout across listings and threads.

    The homepage, board feeds, profile feeds and full threads all call the same
    post_meta macro. House identity therefore belongs in that macro exactly where
    the native full-thread layout already puts it: with the metadata badges before
    the avatar/username. Do not inject a second listing-only house icon.
    """
    source = _MACROS_TEMPLATE.read_text(encoding="utf-8")
    original = source

    # Undo the abandoned listing-only experiment if this helper ever runs over a
    # previously mutated worktree. Fresh Railway checkouts already use post_meta(p).
    source = source.replace("{% macro post_meta(p, house_inline=false) %}", "{% macro post_meta(p) %}", 1)
    source = source.replace("{% if p.author.house and not house_inline %}", "{% if p.author.house %}")
    source = source.replace("{% if FEATURES['HOUSES'] and p.author.house %}", "{% if p.author.house %}", 1)

    original_house = '\t\t\t<img loading="lazy" src="{{p.author.house | house_icon}}" height="20" data-bs-toggle="tooltip" data-bs-placement="bottom" title="House {{p.author.house}}" alt="House {{p.author.house}}">'
    compact_house = '\t\t\t<img loading="lazy" class="house-user-icon" src="{{p.author.house | house_icon}}" width="20" height="20" style="' + _HOUSE_ICON_STYLE + '" data-bs-toggle="tooltip" data-bs-placement="bottom" title="House {{p.author.house}}" alt="House {{p.author.house}}">'
    source = source.replace(original_house, compact_house, 1)

    # House and verified are adjacent identity badges. When a house is present,
    # remove Bootstrap's extra left margin from the checkmark so the pair reads as
    # one compact badge group rather than two unrelated blocks.
    source = source.replace(
        'class="fas fa-badge-check align-middle ml-1 {% if p.author.verified==\'Glowiefied\' %}glow{% endif %}"',
        'class="fas fa-badge-check align-middle {% if not p.author.house %}ml-1 {% endif %}{% if p.author.verified==\'Glowiefied\' %}glow{% endif %}"',
        1,
    )

    # The post author avatar sat slightly below the username baseline. Keep the
    # existing wrapper geometry but reduce the old top offset by another 2px.
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

    _write_if_changed(_MACROS_TEMPLATE, original, source)


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


def _remove_profile_house_identity() -> None:
    """House badges are post/comment identity, not profile-header decoration."""
    source = _PROFILE_BANNER_TEMPLATE.read_text(encoding="utf-8")
    original = source

    profile_house = """\t\t\t\t\t\t{% if FEATURES['HOUSES'] and u.house %}\n\t\t\t\t\t\t\t<img loading=\"lazy\" id=\"profile--house\" src=\"{{u.house | house_icon}}\" height=\"20\" data-bs-toggle=\"tooltip\" data-bs-placement=\"bottom\" title=\"House {{u.house}}\" alt=\"House {{u.house}}\">\n\t\t\t\t\t\t{% endif %}\n"""
    ungated_profile_house = profile_house.replace(
        "{% if FEATURES['HOUSES'] and u.house %}",
        "{% if u.house %}",
    )
    source = source.replace(profile_house, "", 1)
    source = source.replace(ungated_profile_house, "", 1)

    _write_if_changed(_PROFILE_BANNER_TEMPLATE, original, source)


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
        _patch_comment_identity()
        _remove_profile_house_identity()
