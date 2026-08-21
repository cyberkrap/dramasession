import os
from pathlib import Path

import fcntl

from files.helpers.config.awards import AWARDS, AWARDS_ENABLED
from files.helpers.config.const import FEATURES


_LOCK_PATH = "/tmp/obsession-toc-ui-fixes.lock"
_MACROS_TEMPLATE = Path("files/templates/util/macros.html")
_COMMENTS_TEMPLATE = Path("files/templates/comments.html")
_PROFILE_BANNER_TEMPLATE = Path("files/templates/userpage/banner.html")

_HOUSE_ICON_STYLE = "width:22px;height:22px;display:inline-block!important;object-fit:contain;vertical-align:middle;margin:0 3px 0 1px"


def _atomic_write(path: Path, content: str) -> None:
    temp_path = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temp_path.write_text(content, encoding="utf-8")
    os.replace(temp_path, path)


def _write_if_changed(path: Path, original: str, updated: str) -> None:
    if updated != original:
        _atomic_write(path, updated)


def _patch_post_house_identity():
    source = _MACROS_TEMPLATE.read_text(encoding="utf-8")
    original = source

    source = source.replace(
        "{% if FEATURES['HOUSES'] and p.author.house %}",
        "{% if p.author.house %}",
    )

    old_icon = '\t\t\t<img loading="lazy" src="{{p.author.house | house_icon}}" height="20" data-bs-toggle="tooltip" data-bs-placement="bottom" title="House {{p.author.house}}" alt="House {{p.author.house}}">'
    new_icon = '\t\t\t<img loading="lazy" class="house-user-icon" src="{{p.author.house | house_icon}}" width="22" height="22" style="' + _HOUSE_ICON_STYLE + '" data-bs-toggle="tooltip" data-bs-placement="bottom" title="House {{p.author.house}}" alt="House {{p.author.house}}">'
    if 'class="house-user-icon"' not in source:
        if old_icon not in source:
            raise RuntimeError("Could not locate the post house identity icon")
        source = source.replace(old_icon, new_icon, 1)

    source = source.replace(
        '<div class="profile-pic-30-wrapper" style="margin-top:9px">',
        '<div class="profile-pic-30-wrapper" style="margin-top:4px">',
        1,
    )

    _write_if_changed(_MACROS_TEMPLATE, original, source)


def _patch_comment_house_identity():
    source = _COMMENTS_TEMPLATE.read_text(encoding="utf-8")
    original = source

    source = source.replace(
        "{% if FEATURES['HOUSES'] and c.author.house %}",
        "{% if c.author.house %}",
    )

    old_icon = '\t\t\t\t\t\t<img loading="lazy" src="{{c.author.house | house_icon}}" height="20" data-bs-toggle="tooltip" data-bs-placement="bottom" title="House {{c.author.house}}" alt="House {{c.author.house}}">'
    new_icon = '\t\t\t\t\t\t<img loading="lazy" class="house-user-icon" src="{{c.author.house | house_icon}}" width="22" height="22" style="' + _HOUSE_ICON_STYLE + '" data-bs-toggle="tooltip" data-bs-placement="bottom" title="House {{c.author.house}}" alt="House {{c.author.house}}">'
    if 'class="house-user-icon"' not in source:
        if old_icon not in source:
            raise RuntimeError("Could not locate the comment house identity icon")
        source = source.replace(old_icon, new_icon, 1)

    _write_if_changed(_COMMENTS_TEMPLATE, original, source)


def _remove_profile_house_identity():
    source = _PROFILE_BANNER_TEMPLATE.read_text(encoding="utf-8")
    original = source

    profile_house = """\t\t\t\t\t\t{% if FEATURES['HOUSES'] and u.house %}
\t\t\t\t\t\t\t<img loading="lazy" id="profile--house" src="{{u.house | house_icon}}" height="20" data-bs-toggle="tooltip" data-bs-placement="bottom" title="House {{u.house}}" alt="House {{u.house}}">
\t\t\t\t\t\t{% endif %}
"""
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
        _patch_post_house_identity()
        _patch_comment_house_identity()
        _remove_profile_house_identity()
