import os
from pathlib import Path


_ADMIN_HOME_PATH = Path('files/templates/admin/admin_home.html')


def _atomic_write(path, content):
    temp_path = path.with_name(f'.{path.name}.{os.getpid()}.tmp')
    temp_path.write_text(content, encoding='utf-8')
    os.replace(temp_path, path)


def install_login_activity_home_link():
    """Expose the persistent login tracker beside the existing active-user pages."""
    source = _ADMIN_HOME_PATH.read_text(encoding='utf-8')
    link = '\t\t<li><a href="/admin/login-activity">Login Activity ({{login_activity_today_unique()}} users today)</a></li>\n'
    if link in source:
        return

    marker = '\t\t<li><a href="/admin/loggedout">Currently Logged-out Users</a></li>\n'
    if marker not in source:
        raise RuntimeError('Could not locate active-user links on admin home')

    source = source.replace(marker, marker + link, 1)
    _atomic_write(_ADMIN_HOME_PATH, source)
