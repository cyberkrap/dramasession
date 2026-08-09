from urllib.parse import quote

from flask import abort, g, redirect, render_template, request

from files.__main__ import app, limiter
from files.classes import ModAction, User
from files.helpers.admin_economy_ui import install_admin_economy_ui
from files.helpers.config.const import DEFAULT_RATELIMIT, DEFAULT_RATELIMIT_SLOWER, PERMS
from files.helpers.contribution_badges import sync_cumulative_contribution_badges
from files.helpers.economy_ledger import set_economy_context
from files.helpers.get import get_user
from files.helpers.lifetime_contributions import (
	clear_contribution_override,
	effective_contribution_cents,
	set_contribution_override,
)
from files.helpers.support import SUPPORT_TIERS
from files.routes.wrappers import admin_level_required, get_ID


install_admin_economy_ui()

_ECONOMY_PERMISSIONS = (
	'ADMIN_GRANT_CURRENCY',
	'ADMIN_REMOVE_CURRENCY',
	'ADMIN_UNLIMITED_SPENDING',
)
_ECONOMY_RETURN_ENDPOINTS = {
	'grant_currency',
	'remove_currency',
	'manage_patron_from_admin_page',
	'manage_lifetime_contribution',
}


def _has_economy_access(user):
	return any(user.has_permission(permission) for permission in _ECONOMY_PERMISSIONS)


def _can_manage_patrons(user):
	return bool(
		user.has_all_admin_permissions
		and user.has_permission('ADMIN_UNLIMITED_SPENDING')
		and user.has_permission('ADMIN_GRANT_CURRENCY')
		and user.has_permission('ADMIN_REMOVE_CURRENCY')
	)


@app.get('/admin/economy')
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@admin_level_required(PERMS['ADMIN_HOME_VISIBLE'])
def admin_economy(v: User):
	if not _has_economy_access(v):
		abort(403, 'Economy administrator access is required.')
	return render_template(
		'admin/economy.html',
		v=v,
		support_tiers=SUPPORT_TIERS,
		patron_levels=range(1, 7),
		can_manage_patrons=_can_manage_patrons(v),
		error=request.values.get('error'),
		msg=request.values.get('msg'),
	)


@app.post('/admin/economy/patron-reward')
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@admin_level_required(PERMS['ADMIN_GRANT_CURRENCY'])
def grant_patron_reward(v: User):
	if not v.has_permission('ADMIN_GRANT_CURRENCY'):
		abort(403, 'Economy administrator access is required.')

	username = (request.form.get('username') or '').strip()
	user = get_user(username, graceful=True)
	if not user:
		return redirect('/admin/economy?error=' + quote('User not found.'))

	try:
		tier_level = int(request.form.get('tier') or 0)
	except (TypeError, ValueError):
		tier_level = 0
	tier = next((item for item in SUPPORT_TIERS if int(item['level']) == tier_level), None)
	if not tier:
		return redirect('/admin/economy?error=' + quote('Choose a valid patron tier.'))

	reward = int(tier['wishbux'])
	tier_name = str(tier['name'])
	meta = {
		'tier_name': tier_name,
		'tier_level': int(tier['level']),
		'reward_wishbux': reward,
		'actor_username': v.username,
		'target_username': user.username,
		'admin_granted': True,
	}

	# Mutate and flush while the PostgreSQL ledger trigger is explicitly tagged
	# as a patron reward. Do not use the generic balance wrapper here: this entry
	# must be distinguishable from an ordinary admin currency adjustment.
	set_economy_context(g.db, 'patron', 'Patron reward', meta)
	try:
		user.marseybux = int(user.marseybux or 0) + reward
		g.db.add(user)
		g.db.flush()
	finally:
		set_economy_context(g.db)

	message = f'{tier_name} patron reward ({reward:,} Wishbux) granted to @{user.username}.'
	return redirect('/admin/economy?msg=' + quote(message))


@app.post('/admin/lifetime-contributions/manage')
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@admin_level_required(PERMS['ADMIN_GRANT_CURRENCY'])
def manage_lifetime_contribution(v: User):
	if not v.has_permission('ADMIN_GRANT_CURRENCY'):
		return redirect('/admin/economy?error=' + quote('Economy administrator access is required.'))

	username = (request.form.get('username') or '').strip()
	user = get_user(username, graceful=True)
	if not user:
		return redirect('/admin/economy?error=' + quote('User not found.'))

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
			return redirect('/admin/economy?error=' + quote('Enter a valid lifetime donation amount.'))
		if amount_cents < 0:
			return redirect('/admin/economy?error=' + quote('Lifetime donation amount cannot be negative.'))
		set_contribution_override(g.db, user.id, amount_cents, v.id)
		total_cents = sync_cumulative_contribution_badges(g.db, user)
		message = f'Lifetime donation set to ${total_cents / 100:,.2f} for @{user.username}.'

	g.db.add(ModAction(
		kind='grant_currency',
		user_id=v.id,
		target_user_id=user.id,
		_note=message,
	))
	return redirect('/admin/economy?msg=' + quote(message))


@app.after_request
def keep_economy_actions_in_economy_workspace(response):
	"""Existing currency/patron endpoints should return to the new workspace."""
	if request.method != 'POST' or request.endpoint not in _ECONOMY_RETURN_ENDPOINTS:
		return response
	if response.status_code < 300 or response.status_code >= 400:
		return response
	location = str(response.headers.get('Location') or '')
	if not (location.startswith('/admin?') or location.startswith('/admin/administrators?') or location in {'/admin', '/admin/administrators'}):
		return response
	query = location.split('?', 1)[1] if '?' in location else ''
	response.headers['Location'] = '/admin/economy' + (f'?{query}' if query else '')
	return response
