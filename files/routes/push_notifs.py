from files.routes.wrappers import *
from files.__main__ import app
from flask import request, g
from files.classes.push_subscriptions import PushSubscription

@app.post("/push_subscribe")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def push_subscribe(v):
	subscription_json = request.values.get("subscription_json")

	subscription = g.db.query(PushSubscription).filter_by(
		user_id=v.id,
		subscription_json=subscription_json,
	).one_or_none()

	if not subscription:
		subscription = PushSubscription(
			user_id=v.id,
			subscription_json=subscription_json,
		)
		g.db.add(subscription)

	return ''
