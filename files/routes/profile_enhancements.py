import re
from html import escape
from urllib.parse import unquote

from flask import g, request
from sqlalchemy import func
from sqlalchemy.orm.attributes import set_committed_value

from files.__main__ import app, limiter
from files.classes import User
from files.helpers.config.const import DEFAULT_RATELIMIT, PERMS
from files.helpers.contribution_badges import (
    CONTRIBUTION_BADGE_IDS,
    sync_cumulative_contribution_badges,
)
from files.helpers.get import get_user
from files.helpers.lifetime_contributions import effective_contribution_cents


# Voting activity is public between users. Existing routes use this permission
# threshold, so setting it to zero removes the owner/admin-only gate without
# duplicating or replacing the route implementations.
PERMS['USER_VOTERS_VISIBLE'] = 0

_PROFILE_PATH_RE = re.compile(r'^/@([^/]+)(?:/|$)')
_CONTRIBUTION_BADGE_ID_SET = set(CONTRIBUTION_BADGE_IDS)


def _profile_username_from_request():
    if request.view_args and request.view_args.get('username'):
        return str(request.view_args['username'])
    match = _PROFILE_PATH_RE.match(request.path)
    return unquote(match.group(1)) if match else None


def _support_summary(user, *, sync_badges=False):
    lifetime_cents = effective_contribution_cents(g.db, user.id)
    if sync_badges:
        sync_cumulative_contribution_badges(g.db, user, total_cents=lifetime_cents)
        g.db.flush()

        # Refresh the relationship after removing badges above the effective
        # total, then keep contribution milestones together in ascending order.
        g.db.expire(user, ['badges'])
        badges = list(user.badges)
        regular_badges = [
            badge for badge in badges
            if badge.badge_id not in _CONTRIBUTION_BADGE_ID_SET
        ]
        contribution_badges = sorted(
            (
                badge for badge in badges
                if badge.badge_id in _CONTRIBUTION_BADGE_ID_SET
            ),
            key=lambda badge: badge.badge_id,
        )
        set_committed_value(user, 'badges', regular_badges + contribution_badges)

    discount_percent = max(0, round((1 - float(user.discount)) * 100))
    return {
        'lifetime_donated': f'${int(lifetime_cents) / 100:,.2f}',
        'award_discount': f'{discount_percent}%',
    }


@app.before_request
def prepare_profile_support_details():
    """Resolve support details before the profile template renders."""
    if request.method != 'GET' or not request.path.startswith('/@'):
        return None

    username = _profile_username_from_request()
    if not username:
        return None

    user = g.db.query(User).filter(
        func.lower(User.username) == username.lower()
    ).one_or_none()
    if user is None:
        return None

    g.profile_support_summary = _support_summary(user, sync_badges=True)
    return None


@app.after_request
def inject_profile_support_details(response):
    """Place support values in Account details without a second HTTP request."""
    summary = getattr(g, 'profile_support_summary', None)
    if (
        not summary
        or response.status_code >= 400
        or response.direct_passthrough
        or response.mimetype != 'text/html'
    ):
        return response

    page = response.get_data(as_text=True)
    if 'data-profile-support-summary' in page:
        return response

    marker_position = page.find('id="profile--info"')
    if marker_position < 0:
        marker_position = page.find("id='profile--info'")
    if marker_position < 0:
        return response

    closing_position = page.find('</dl>', marker_position)
    if closing_position < 0:
        return response

    rows = (
        '\n\t\t\t\t\t<div data-profile-support-summary="1">'
        '<dt>Lifetime donated</dt>'
        f'<dd>{escape(summary["lifetime_donated"])}</dd>'
        '</div>'
        '\n\t\t\t\t\t<div data-profile-support-summary="1">'
        '<dt>Total award discount</dt>'
        f'<dd>{escape(summary["award_discount"])}</dd>'
        '</div>\n\t\t\t\t'
    )
    response.set_data(page[:closing_position] + rows + page[closing_position:])
    return response


@app.get('/api/profile/<username>/support-summary')
@limiter.limit(DEFAULT_RATELIMIT)
def profile_support_summary(username):
    user = get_user(username, v=getattr(g, 'v', None), include_shadowbanned=False)
    return _support_summary(user, sync_badges=True)
