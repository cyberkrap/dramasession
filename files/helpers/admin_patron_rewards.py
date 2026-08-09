"""Attach the configured Wishbux payout to successful manual patron grants."""

from functools import wraps
from urllib.parse import quote

from flask import g, request

from files.__main__ import app
from files.helpers.economy_ledger import set_economy_context
from files.helpers.get import get_user
from files.helpers.support import SUPPORT_TIER_BY_LEVEL


_installed = False


def _reward_tier(level):
    if not SUPPORT_TIER_BY_LEVEL:
        return None
    highest = max(int(item) for item in SUPPORT_TIER_BY_LEVEL)
    level = max(1, min(int(level), highest))
    return SUPPORT_TIER_BY_LEVEL.get(level)


def install_admin_patron_rewards() -> None:
    """Grant the tier Wishbux reward unless the admin explicitly chooses Free patron."""
    global _installed
    if _installed:
        return

    endpoint = 'manage_patron_from_admin_page'
    original = app.view_functions.get(endpoint)
    if original is None or getattr(original, '_admin_patron_reward_payout', False):
        return

    @wraps(original)
    def manage_patron_with_reward(*args, **kwargs):
        response = original(*args, **kwargs)
        location = str(getattr(response, 'location', '') or '')

        if request.method != 'POST' or 'error=' in location:
            return response
        if (request.form.get('action') or 'set').strip().lower() == 'end':
            return response
        if request.form.get('free_patron') == 'on':
            return response

        username = (request.form.get('username') or '').strip()
        user = get_user(username, graceful=True)
        if user is None:
            return response

        try:
            level = int(request.form.get('level') or 0)
        except (TypeError, ValueError):
            return response
        tier = _reward_tier(level)
        if not tier:
            return response

        reward = int(tier['wishbux'])
        tier_name = str(tier['name'])
        meta = {
            'tier_name': tier_name,
            'tier_level': int(tier['level']),
            'reward_wishbux': reward,
            'target_username': user.username,
            'admin_patron_grant': True,
        }

        # Direct mutation keeps the explicit Patron reward ledger context intact;
        # the generic pay_account wrapper would classify this as an admin adjustment.
        set_economy_context(g.db, 'patron', 'Patron reward', meta)
        try:
            user.marseybux = int(user.marseybux or 0) + reward
            g.db.add(user)
            g.db.flush()
        finally:
            set_economy_context(g.db)

        message = (
            f'Patron level {level} applied to @{user.username}. '
            f'{tier_name} patron reward ({reward:,} Wishbux) granted.'
        )
        response.headers['Location'] = '/admin/economy?msg=' + quote(message)
        return response

    manage_patron_with_reward._admin_patron_reward_payout = True
    app.view_functions[endpoint] = manage_patron_with_reward
    _installed = True
