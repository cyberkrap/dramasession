from urllib.parse import quote

from flask import g, redirect, request

from files.__main__ import app, limiter
from files.classes import ModAction, User
from files.helpers.config.const import DEFAULT_RATELIMIT_SLOWER, PERMS
from files.helpers.contribution_badges import sync_cumulative_contribution_badges
from files.helpers.get import get_user
from files.helpers.lifetime_contributions import (
	clear_contribution_override,
	set_contribution_override,
)
from files.routes.wrappers import admin_level_required, get_ID


@app.post('/admin/lifetime-contributions/manage')
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@admin_level_required(PERMS['ADMIN_GRANT_CURRENCY'])
def manage_lifetime_contribution(v: User):
	if not v.has_permission('ADMIN_GRANT_CURRENCY'):
		return redirect('/admin/administrators?error=' + quote('Economy administrator access is required.'))

	username = (request.form.get('username') or '').strip()
	user = get_user(username, graceful=True)
	if not user:
		return redirect('/admin/administrators?error=' + quote('User not found.'))

	action = (request.form.get('action') or 'set').strip().lower()
	if action == 'clear':
		clear_contribution_override(g.db, user.id)
		total_cents = sync_cumulative_contribution_badges(g.db, user)
		message = f'Lifetime donation override cleared for @{user.username}. Effective total: ${total_cents / 100:,.2f}.'
	else:
		raw_amount = (request.form.get('amount') or '').strip().replace(',', '')
		try:
			amount_cents = int(round(float(raw_amount) * 100))
		except (TypeError, ValueError):
			return redirect('/admin/administrators?error=' + quote('Enter a valid lifetime donation amount.'))
		if amount_cents < 0:
			return redirect('/admin/administrators?error=' + quote('Lifetime donation amount cannot be negative.'))
		set_contribution_override(g.db, user.id, amount_cents, v.id)
		total_cents = sync_cumulative_contribution_badges(g.db, user)
		message = f'Lifetime donation set to ${total_cents / 100:,.2f} for @{user.username}.'

	g.db.add(ModAction(
		kind='lifetime_contribution_override',
		user_id=v.id,
		target_user_id=user.id,
		_note=message,
	))
	return redirect('/admin/administrators?msg=' + quote(message))
