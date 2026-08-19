import re
import time
from datetime import datetime, timedelta, timezone

from flask import g, render_template, request, session
from sqlalchemy import text

from files.__main__ import app, engine, limiter
from files.classes import User
from files.helpers.config.const import DEFAULT_RATELIMIT, PERMS
from files.helpers.get import get_user
from files.routes.wrappers import admin_level_required, get_ID


_LOGIN_ACTIVITY_SCHEMA = """
CREATE TABLE IF NOT EXISTS public.login_activity (
    id BIGSERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    login_utc INTEGER NOT NULL,
    ip_address VARCHAR(64),
    forwarded_for VARCHAR(512),
    country_code VARCHAR(8),
    user_agent TEXT,
    device_type VARCHAR(32),
    device_name VARCHAR(160),
    os_name VARCHAR(120),
    browser_name VARCHAR(120),
    accept_language VARCHAR(255),
    source VARCHAR(24) NOT NULL DEFAULT 'login'
);
CREATE INDEX IF NOT EXISTS login_activity_login_utc_idx
    ON public.login_activity (login_utc DESC);
CREATE INDEX IF NOT EXISTS login_activity_user_utc_idx
    ON public.login_activity (user_id, login_utc DESC);
CREATE INDEX IF NOT EXISTS login_activity_ip_utc_idx
    ON public.login_activity (ip_address, login_utc DESC);
"""


def _ensure_schema():
    with engine.begin() as connection:
        connection.execute(text(_LOGIN_ACTIVITY_SCHEMA))


def _first_ip(value):
    return (value or '').split(',', 1)[0].strip() or None


def _version(ua, pattern, label):
    match = re.search(pattern, ua, re.I)
    if not match:
        return label
    return f"{label} {match.group(1).replace('_', '.')}"


def _ua_details(ua):
    ua = ua or ''
    lower = ua.lower()

    if any(token in lower for token in ('bot', 'crawler', 'spider', 'slurp', 'preview')):
        device_type = 'Bot'
    elif 'ipad' in lower or 'tablet' in lower:
        device_type = 'Tablet'
    elif any(token in lower for token in ('iphone', 'android', 'mobile')):
        device_type = 'Mobile'
    else:
        device_type = 'Desktop'

    if 'iphone' in lower:
        device_name = 'iPhone'
    elif 'ipad' in lower:
        device_name = 'iPad'
    elif 'android' in lower:
        model = re.search(r'Android[^;)]*;\s*([^;)]+?)(?:\s+Build/|;|\))', ua, re.I)
        device_name = model.group(1).strip() if model else 'Android device'
    elif 'windows' in lower:
        device_name = 'Windows PC'
    elif 'macintosh' in lower or 'mac os x' in lower:
        device_name = 'Mac'
    elif 'cros' in lower:
        device_name = 'Chromebook'
    elif 'linux' in lower:
        device_name = 'Linux PC'
    else:
        device_name = 'Unknown device'

    if 'iphone' in lower or 'ipad' in lower:
        os_name = _version(ua, r'OS\s+([0-9_]+)', 'iOS')
    elif 'android' in lower:
        os_name = _version(ua, r'Android\s+([0-9.]+)', 'Android')
    elif 'windows nt 10.0' in lower:
        os_name = 'Windows 10/11'
    elif 'windows nt 6.3' in lower:
        os_name = 'Windows 8.1'
    elif 'windows nt 6.1' in lower:
        os_name = 'Windows 7'
    elif 'cros' in lower:
        os_name = 'ChromeOS'
    elif 'mac os x' in lower:
        os_name = _version(ua, r'Mac OS X\s+([0-9_]+)', 'macOS')
    elif 'linux' in lower:
        os_name = 'Linux'
    else:
        os_name = 'Unknown OS'

    if 'edg/' in lower:
        browser_name = _version(ua, r'Edg/([0-9.]+)', 'Edge')
    elif 'opr/' in lower:
        browser_name = _version(ua, r'OPR/([0-9.]+)', 'Opera')
    elif 'samsungbrowser/' in lower:
        browser_name = _version(ua, r'SamsungBrowser/([0-9.]+)', 'Samsung Internet')
    elif 'crios/' in lower:
        browser_name = _version(ua, r'CriOS/([0-9.]+)', 'Chrome')
    elif 'chrome/' in lower:
        browser_name = _version(ua, r'Chrome/([0-9.]+)', 'Chrome')
    elif 'fxios/' in lower:
        browser_name = _version(ua, r'FxiOS/([0-9.]+)', 'Firefox')
    elif 'firefox/' in lower:
        browser_name = _version(ua, r'Firefox/([0-9.]+)', 'Firefox')
    elif 'safari/' in lower and 'version/' in lower:
        browser_name = _version(ua, r'Version/([0-9.]+)', 'Safari')
    else:
        browser_name = 'Unknown browser'

    return device_type, device_name[:160], os_name[:120], browser_name[:120]


def _record_login(user_id, source):
    ua = request.headers.get('User-Agent', '')[:4096]
    device_type, device_name, os_name, browser_name = _ua_details(ua)
    forwarded_for = (request.headers.get('X-Forwarded-For') or '')[:512] or None
    ip_address = (
        request.headers.get('CF-Connecting-IP')
        or _first_ip(forwarded_for)
        or request.remote_addr
        or None
    )

    params = {
        'user_id': int(user_id),
        'login_utc': int(time.time()),
        'ip_address': (ip_address or '')[:64] or None,
        'forwarded_for': forwarded_for,
        'country_code': (request.headers.get('CF-IPCountry') or '')[:8] or None,
        'user_agent': ua or None,
        'device_type': device_type,
        'device_name': device_name,
        'os_name': os_name,
        'browser_name': browser_name,
        'accept_language': (request.headers.get('Accept-Language') or '')[:255] or None,
        'source': source,
    }
    with engine.begin() as connection:
        connection.execute(text("""
            INSERT INTO public.login_activity
                (user_id, login_utc, ip_address, forwarded_for, country_code,
                 user_agent, device_type, device_name, os_name, browser_name,
                 accept_language, source)
            VALUES
                (:user_id, :login_utc, :ip_address, :forwarded_for, :country_code,
                 :user_agent, :device_type, :device_name, :os_name, :browser_name,
                 :accept_language, :source)
        """), params)


def _date_bounds(date_string=None):
    if date_string:
        try:
            selected = datetime.strptime(date_string, '%Y-%m-%d').replace(tzinfo=timezone.utc)
        except ValueError:
            selected = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        selected = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    end = selected + timedelta(days=1)
    return selected, int(selected.timestamp()), int(end.timestamp())


def _rows_with_users(rows):
    rows = [dict(row) for row in rows]
    user_ids = {row['user_id'] for row in rows}
    users = {}
    if user_ids:
        users = {user.id: user for user in g.db.query(User).filter(User.id.in_(user_ids)).all()}
    for row in rows:
        row['user'] = users.get(row['user_id'])
    return rows


def login_activity_today_unique():
    _, start, end = _date_bounds()
    result = g.db.execute(text("""
        SELECT COUNT(DISTINCT user_id)
        FROM public.login_activity
        WHERE login_utc >= :start AND login_utc < :end
    """), {'start': start, 'end': end}).scalar()
    return int(result or 0)


_ensure_schema()
app.jinja_env.globals['login_activity_today_unique'] = login_activity_today_unique


@app.after_request
def record_successful_login_activity(response):
    """Persist successful logins/signups without ever storing credentials or cookies."""
    if request.method != 'POST' or request.endpoint not in {'login_post', 'sign_up_post'}:
        return response
    if not (200 <= response.status_code < 400):
        return response

    user_id = session.get('lo_user')
    if not user_id:
        return response

    # A password-valid MFA challenge is HTTP 200 but does not establish lo_user,
    # so it never reaches this branch. One completed POST login = one event.
    try:
        _record_login(user_id, 'signup' if request.endpoint == 'sign_up_post' else 'login')
    except Exception:
        app.logger.exception('Failed to record login activity')
    return response


@app.get('/admin/login-activity')
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@admin_level_required(PERMS['VIEW_ACTIVE_USERS'])
def admin_login_activity(v: User):
    selected, start, end = _date_bounds(request.args.get('date'))
    query = (request.args.get('q') or '').strip()
    params = {'start': start, 'end': end, 'limit': 1000}
    where = ['la.login_utc >= :start', 'la.login_utc < :end']
    if query:
        params['query'] = f"%{query.lstrip('@')}%"
        where.append('(u.username ILIKE :query OR COALESCE(la.ip_address, \'\') ILIKE :query)')

    rows = g.db.execute(text(f"""
        SELECT la.*
        FROM public.login_activity la
        JOIN public.users u ON u.id = la.user_id
        WHERE {' AND '.join(where)}
        ORDER BY la.login_utc DESC, la.id DESC
        LIMIT :limit
    """), params).mappings().all()
    entries = _rows_with_users(rows)

    unique_users = len({entry['user_id'] for entry in entries})
    unique_ips = len({entry['ip_address'] for entry in entries if entry['ip_address']})
    signup_count = sum(1 for entry in entries if entry['source'] == 'signup')
    previous_date = (selected - timedelta(days=1)).date().isoformat()
    next_date = (selected + timedelta(days=1)).date().isoformat()

    return render_template(
        'admin/login_activity.html',
        v=v,
        entries=entries,
        selected_date=selected.date().isoformat(),
        previous_date=previous_date,
        next_date=next_date,
        query=query,
        unique_users=unique_users,
        unique_ips=unique_ips,
        signup_count=signup_count,
    )


@app.get('/admin/login-activity/user/<username>')
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@admin_level_required(PERMS['VIEW_ACTIVE_USERS'])
def admin_user_login_activity(username, v: User):
    user = get_user(username, graceful=True)
    if not user:
        return render_template('errors/404.html', v=v), 404

    rows = g.db.execute(text("""
        SELECT *
        FROM public.login_activity
        WHERE user_id = :user_id
        ORDER BY login_utc DESC, id DESC
        LIMIT 500
    """), {'user_id': user.id}).mappings().all()
    entries = [dict(row) for row in rows]
    unique_ips = len({entry['ip_address'] for entry in entries if entry['ip_address']})
    active_days = len({datetime.fromtimestamp(entry['login_utc'], timezone.utc).date() for entry in entries})

    return render_template(
        'admin/login_activity_user.html',
        v=v,
        user=user,
        entries=entries,
        unique_ips=unique_ips,
        active_days=active_days,
    )
