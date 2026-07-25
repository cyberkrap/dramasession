from flask import g, request

from files.__main__ import app, limiter
from files.classes import User
from files.helpers.config.const import DEFAULT_RATELIMIT
from files.routes.wrappers import auth_required, get_ID


@app.get('/api/chat/username-effects')
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def chat_username_effects(v):
	requested = str(request.args.get('ids') or '')
	ids = []
	seen = set()
	for raw in requested.split(','):
		try:
			user_id = int(raw)
		except (TypeError, ValueError):
			continue
		if user_id < 1 or user_id in seen:
			continue
		seen.add(user_id)
		ids.append(user_id)
		if len(ids) >= 100:
			break

	if not ids:
		return {'users': {}}

	users = g.db.query(User).filter(User.id.in_(ids)).all()
	return {
		'users': {
			str(user.id): {
				'username': user.username,
				'effects': user.active_username_effects,
				'effect_color': user.username_effect_text_color,
				'name_color': user.name_color,
				'patron': bool(user.patron),
			}
			for user in users
		}
	}
