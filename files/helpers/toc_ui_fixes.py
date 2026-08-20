import os
from pathlib import Path

import fcntl

from files.helpers.config.awards import AWARDS, AWARDS_ENABLED
from files.helpers.config.const import FEATURES


_LOCK_PATH = "/tmp/obsession-toc-ui-fixes.lock"
_HEADER_TEMPLATE = Path("files/templates/header.html")
_MACROS_TEMPLATE = Path("files/templates/util/macros.html")
_COMMENTS_TEMPLATE = Path("files/templates/comments.html")
_PROFILE_BANNER_TEMPLATE = Path("files/templates/userpage/banner.html")


def _atomic_write(path: Path, content: str) -> None:
    temp_path = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temp_path.write_text(content, encoding="utf-8")
    os.replace(temp_path, path)


def _write_if_changed(path: Path, original: str, updated: str) -> None:
    if updated != original:
        _atomic_write(path, updated)


def install_toc_ui_fixes() -> None:
    """Restore TOC house identity UI and normalize user-facing award labels."""
    # Houses are a live TOC feature. Keep the feature flag enabled and also
    # remove stale template feature gates so an old flag value cannot hide a
    # user's stored house membership/icon again.
    FEATURES["HOUSES"] = True

    # Keep internal award keys/mechanics unchanged; these are display names only.
    for catalog in (AWARDS, AWARDS_ENABLED):
        if "ban" in catalog:
            catalog["ban"]["title"] = "Ban"
        if "unban" in catalog:
            catalog["unban"]["title"] = "Unban"

    with open(_LOCK_PATH, "w", encoding="utf-8") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)

        # Desktop navbar: show the current house immediately beside the username.
        source = _HEADER_TEMPLATE.read_text(encoding="utf-8")
        original = source
        if "header-house-icon" not in source:
            old = '''\t\t\t\t\t\t\t\t<div style="color: #{{v.name_color}}" class="text-small font-weight-bold"><span id="header--username" {% if v.patron %}class="patron" style="background-color:#{{v.name_color}}"{% endif %}>{{v.user_name}}</span></div>'''
            new = '''\t\t\t\t\t\t\t\t<div style="color: #{{v.name_color}}" class="text-small font-weight-bold d-flex align-items-center">{% if v.house %}<img loading="lazy" class="header-house-icon mr-1" src="{{v.house | house_icon}}" data-bs-toggle="tooltip" data-bs-placement="bottom" title="House {{v.house}}" alt="House {{v.house}}">{% endif %}<span id="header--username" {% if v.patron %}class="patron" style="background-color:#{{v.name_color}}"{% endif %}>{{v.user_name}}</span></div>'''
            if old not in source:
                raise RuntimeError("Could not locate the desktop header username block")
            source = source.replace(old, new, 1)
        _write_if_changed(_HEADER_TEMPLATE, original, source)

        # Post metadata: the screenshoted 30px author avatar had an inline 9px
        # top margin. Reduce it directly (rather than moving the unrelated 35px
        # navbar avatar) and always render a stored house icon.
        source = _MACROS_TEMPLATE.read_text(encoding="utf-8")
        original = source
        source = source.replace(
            "{% if FEATURES['HOUSES'] and p.author.house %}",
            "{% if p.author.house %}",
        )
        source = source.replace(
            '<div class="profile-pic-30-wrapper" style="margin-top:9px">',
            '<div class="profile-pic-30-wrapper" style="margin-top:4px">',
            1,
        )
        _write_if_changed(_MACROS_TEMPLATE, original, source)

        # Comments and profile pages use the same stored house value. Do not let
        # a feature-gate regression suppress the icon there either.
        source = _COMMENTS_TEMPLATE.read_text(encoding="utf-8")
        original = source
        source = source.replace(
            "{% if FEATURES['HOUSES'] and c.author.house %}",
            "{% if c.author.house %}",
        )
        _write_if_changed(_COMMENTS_TEMPLATE, original, source)

        source = _PROFILE_BANNER_TEMPLATE.read_text(encoding="utf-8")
        original = source
        source = source.replace(
            "{% if FEATURES['HOUSES'] and u.house %}",
            "{% if u.house %}",
        )
        _write_if_changed(_PROFILE_BANNER_TEMPLATE, original, source)
