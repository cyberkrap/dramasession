from flask import abort, g, request

from files.__main__ import app, limiter
from files.classes import User
from files.helpers.config.const import DEFAULT_RATELIMIT
from files.helpers.username_effects import (
	normalize_username_effect_color,
	normalize_username_effects,
)
from files.routes.wrappers import get_ID


_MAX_USER_IDS = 100


@app.get('/api/username-effects')
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
def username_effect_hydration():
	"""Return current public username effects directly from the users table.

	Post and comment cards can outlive the author object that originally rendered
	them. Reading the effect columns here prevents cached author metadata from
	leaving those names stuck on an old or empty effect state.
	"""
	raw_ids = str(request.args.get('ids') or '')
	user_ids = []
	seen = set()
	for value in raw_ids.split(','):
		value = value.strip()
		if not value:
			continue
		try:
			user_id = int(value)
		except (TypeError, ValueError):
			abort(400, 'Invalid user ID list.')
		if user_id <= 0 or user_id in seen:
			continue
		seen.add(user_id)
		user_ids.append(user_id)
		if len(user_ids) > _MAX_USER_IDS:
			abort(400, 'Too many user IDs requested.')

	if not user_ids:
		return {'users': {}}

	rows = g.db.query(
		User.id,
		User.username_effects,
		User.username_effects_active,
		User.username_effect_color,
	).filter(User.id.in_(user_ids)).all()

	users = {}
	for user_id, owned_raw, active_raw, color_raw in rows:
		owned = set(normalize_username_effects(owned_raw))
		active = [
			effect
			for effect in normalize_username_effects(active_raw)
			if effect in owned
		]
		users[str(user_id)] = {
			'effects': active,
			'color': normalize_username_effect_color(color_raw),
		}

	return {'users': users}
