"""Small, idempotent template-source cleanup for the economy admin workspace."""

import fcntl
import os
import re
from pathlib import Path


_LOCK_PATH = "/tmp/obsession-admin-economy-ui.lock"
_ADMIN_HOME = Path("files/templates/admin/admin_home.html")
_ADMINISTRATORS = Path("files/templates/admin/administrators.html")


def _atomic_write(path: Path, content: str) -> None:
    temp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temp.write_text(content, encoding="utf-8")
    os.replace(temp, path)


def _patch_admin_home(source: str) -> str:
    economy_nav = '''{% if v.has_permission('ADMIN_GRANT_CURRENCY') or v.has_permission('ADMIN_REMOVE_CURRENCY') or v.has_permission('ADMIN_UNLIMITED_SPENDING') %}
<h4>Economy</h4>
<ul>
	<li><a href="/admin/economy">Manage Economy</a></li>
</ul>
{% endif %}

'''
    administration_marker = "{% if v.has_all_admin_permissions %}\n<h4>Administration</h4>"
    if economy_nav not in source:
        if administration_marker not in source:
            raise RuntimeError("Could not locate the Administration section on admin home")
        source = source.replace(administration_marker, economy_nav + administration_marker, 1)

    grant_start = "{% if v.has_permission('ADMIN_GRANT_CURRENCY') %}\n<section class=\"admin-currency-grant mt-4 mb-4\">"
    remove_start = "{% if v.has_permission('ADMIN_REMOVE_CURRENCY') %}\n<section class=\"admin-currency-removal mb-4\">"
    settings_start = "{% if v.admin_level >= PERMS['SITE_SETTINGS'] %}"

    grant_at = source.find(grant_start)
    if grant_at != -1:
        remove_at = source.find(remove_start, grant_at)
        if remove_at == -1:
            raise RuntimeError("Could not locate Remove Currency after Grant Currency")
        source = source[:grant_at] + source[remove_at:]

    remove_at = source.find(remove_start)
    if remove_at != -1:
        settings_at = source.find(settings_start, remove_at)
        if settings_at == -1:
            raise RuntimeError("Could not locate settings after Remove Currency")
        source = source[:remove_at] + source[settings_at:]

    return source


def _patch_administrators(source: str) -> str:
    patron_pattern = re.compile(
        r"\n\t\{% if v\.has_all_admin_permissions and v\.has_permission\('ADMIN_UNLIMITED_SPENDING'\).*?"
        r"<h2>Patron management</h2>.*?\n\t\{% endif %\}\n",
        re.S,
    )
    lifetime_pattern = re.compile(
        r"\n\t\{% if v\.has_permission\('ADMIN_GRANT_CURRENCY'\) %\}.*?"
        r"<h2>Lifetime donation amount</h2>.*?\n\t\{% endif %\}\n",
        re.S,
    )
    source = patron_pattern.sub("\n", source, count=1)
    source = lifetime_pattern.sub("\n", source, count=1)
    return source


def install_admin_economy_ui() -> None:
    """Move economy forms out of unrelated admin pages before first render."""
    with open(_LOCK_PATH, "w", encoding="utf-8") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        for path, patcher in (
            (_ADMIN_HOME, _patch_admin_home),
            (_ADMINISTRATORS, _patch_administrators),
        ):
            source = path.read_text(encoding="utf-8")
            patched = patcher(source)
            if patched != source:
                _atomic_write(path, patched)
