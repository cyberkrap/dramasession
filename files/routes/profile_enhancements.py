from flask import g
from sqlalchemy.orm.attributes import set_committed_value

from files.__main__ import app, limiter
from files.helpers.config.const import DEFAULT_RATELIMIT, PERMS
from files.helpers.contribution_badges import (
    CONTRIBUTION_BADGE_IDS,
    sync_cumulative_contribution_badges,
)
from files.helpers.get import get_user
from files.helpers.lifetime_contributions import effective_contribution_cents
from files.helpers.shop_spending import reconcile_award_spend


# Voting activity is public between users. Existing routes use this permission
# threshold, so setting it to zero removes the owner/admin-only gate without
# duplicating or replacing the route implementations.
PERMS['USER_VOTERS_VISIBLE'] = 0

_CONTRIBUTION_BADGE_ID_SET = set(CONTRIBUTION_BADGE_IDS)


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


def profile_support_summary_for_template(user):
    """Resolve profile economy stats while the template has an active DB session."""
    if user is None or not getattr(g, 'db', None):
        return {
            'lifetime_donated': '$0.00',
            'award_discount': '0%',
        }
    reconcile_award_spend(g.db, user)
    return _support_summary(user, sync_badges=True)


app.jinja_env.globals['profile_support_summary_for_template'] = profile_support_summary_for_template


@app.get('/api/profile/<username>/support-summary')
@limiter.limit(DEFAULT_RATELIMIT)
def profile_support_summary(username):
    user = get_user(username, v=getattr(g, 'v', None), include_shadowbanned=False)
    reconcile_award_spend(g.db, user)
    return _support_summary(user, sync_badges=True)
