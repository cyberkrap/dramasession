import hashlib
from datetime import datetime, timezone

from flask import g, request, session

from files.__main__ import app
from files.classes import User
from .login_activity import _record_login


_VISIT_SESSION_KEY = "toc_activity_visit_marker"


def _request_identity_marker(user_id: int) -> str:
    """Deduplicate normal browsing to one visit per account/device/IP each UTC day."""
    forwarded = request.headers.get("X-Forwarded-For") or ""
    ip_address = (
        request.headers.get("CF-Connecting-IP")
        or forwarded.split(",", 1)[0].strip()
        or request.remote_addr
        or "unknown"
    )
    user_agent = request.headers.get("User-Agent") or ""
    day = datetime.now(timezone.utc).date().isoformat()
    raw = f"{int(user_id)}|{day}|{ip_address}|{user_agent}".encode("utf-8", "ignore")
    return hashlib.sha256(raw).hexdigest()[:32]


def _is_html_page_response(response) -> bool:
    if request.method != "GET":
        return False
    if response.status_code < 200 or response.status_code >= 400:
        return False
    content_type = (response.headers.get("Content-Type") or "").lower()
    return content_type.startswith("text/html")


@app.after_request
def record_authenticated_site_visit(response):
    """Record already-authenticated members when they actually open a site page.

    Login/signup events remain explicit records. Normal browsing adds a `visit`
    event once per UTC day for each account + browser session + IP/UA identity,
    so persistent year-long sessions still show up in the daily activity view
    without writing a database row for every click, AJAX request, or asset.
    """
    if not _is_html_page_response(response):
        return response

    user_id = session.get("lo_user")
    if not user_id:
        return response

    marker = _request_identity_marker(user_id)
    if session.get(_VISIT_SESSION_KEY) == marker:
        return response

    # Do not create activity rows for stale/deleted account sessions.
    try:
        user = g.db.get(User, int(user_id))
    except Exception:
        user = None
    if not user:
        return response

    try:
        _record_login(user.id, "visit")
        session[_VISIT_SESSION_KEY] = marker
    except Exception:
        app.logger.exception("Failed to record authenticated site visit")

    return response
