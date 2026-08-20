import os
from pathlib import Path

import fcntl

from files.helpers.config.awards import AWARDS, AWARDS_ENABLED
from files.helpers.config.const import FEATURES


_LOCK_PATH = "/tmp/obsession-toc-ui-fixes.lock"
_HEADER_TEMPLATE = Path("files/templates/header.html")


def _atomic_write(path: Path, content: str) -> None:
    temp_path = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temp_path.write_text(content, encoding="utf-8")
    os.replace(temp_path, path)


def install_toc_ui_fixes() -> None:
    """Restore TOC house identity UI and normalize user-facing award labels."""
    # House membership never went away in the database/settings. The feature
    # flag was simply left disabled, which hid every existing house icon.
    FEATURES["HOUSES"] = True

    # Keep internal award keys/mechanics unchanged; these are display names only.
    for catalog in (AWARDS, AWARDS_ENABLED):
        if "ban" in catalog:
            catalog["ban"]["title"] = "Ban"
        if "unban" in catalog:
            catalog["unban"]["title"] = "Unban"

    with open(_LOCK_PATH, "w", encoding="utf-8") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        source = _HEADER_TEMPLATE.read_text(encoding="utf-8")
        if "header-house-icon" in source:
            return

        old = '''\t\t\t\t\t\t\t\t<div style="color: #{{v.name_color}}" class="text-small font-weight-bold"><span id="header--username" {% if v.patron %}class="patron" style="background-color:#{{v.name_color}}"{% endif %}>{{v.user_name}}</span></div>'''
        new = '''\t\t\t\t\t\t\t\t<div style="color: #{{v.name_color}}" class="text-small font-weight-bold d-flex align-items-center">{% if FEATURES['HOUSES'] and v.house %}<img loading="lazy" class="header-house-icon mr-1" src="{{v.house | house_icon}}" data-bs-toggle="tooltip" data-bs-placement="bottom" title="House {{v.house}}" alt="House {{v.house}}">{% endif %}<span id="header--username" {% if v.patron %}class="patron" style="background-color:#{{v.name_color}}"{% endif %}>{{v.user_name}}</span></div>'''
        if old not in source:
            raise RuntimeError("Could not locate the desktop header username block")
        _atomic_write(_HEADER_TEMPLATE, source.replace(old, new, 1))
