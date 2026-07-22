from flask import g

from files.__main__ import app, limiter
from files.helpers.config.const import DEFAULT_RATELIMIT, PERMS
from files.helpers.get import get_user
from files.helpers.lifetime_contributions import effective_contribution_cents


# Voting activity is public between users. Existing routes use this permission
# threshold, so setting it to zero removes the owner/admin-only gate without
# duplicating or replacing the route implementations.
PERMS['USER_VOTERS_VISIBLE'] = 0


@app.get('/api/profile/<username>/support-summary')
@limiter.limit(DEFAULT_RATELIMIT)
def profile_support_summary(username):
    user = get_user(username, v=getattr(g, 'v', None), include_shadowbanned=False)
    lifetime_cents = effective_contribution_cents(g.db, user.id)
    discount_percent = max(0, round((1 - float(user.discount)) * 100))
    return {
        'lifetime_donated': f'${int(lifetime_cents) / 100:,.2f}',
        'award_discount': f'{discount_percent}%',
    }
