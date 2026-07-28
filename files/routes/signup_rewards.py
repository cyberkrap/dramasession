from flask import g, session

from files.__main__ import app, limiter
from files.helpers.alerts import send_notification
from files.helpers.config.const import DEFAULT_RATELIMIT, DEFAULT_RATELIMIT_SLOWER
from files.helpers.signup_rewards import (
	ALPHA_BADGE_ID,
	get_signup_reward,
	mark_signup_reward_claimed,
	reserve_signup_reward,
)
from files.helpers.useractions import badge_grant
from files.routes.wrappers import auth_required, get_ID


def _public_reward(reward):
	return {
		"eligible": True,
		"slot": reward["slot"],
		"coins": reward["coins"],
		"coins_formatted": f'{reward["coins"]:,}',
		"value_label": reward["value_label"],
		"audience_label": reward["audience_label"],
		"tier_end": reward["tier_end"],
		"badge_name": "Alpha User",
	}


@app.get('/api/signup-reward')
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def signup_reward_status(v):
	reward = get_signup_reward(v.id)
	if not reward or reward.get("claimed_utc"):
		return {"eligible": False}
	return _public_reward(reward)


@app.post('/api/signup-reward/claim')
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@auth_required
def signup_reward_claim(v):
	reward = get_signup_reward(v.id, lock=True)
	if not reward:
		return {"error": "No signup reward is reserved for this account."}, 404
	if reward.get("claimed_utc"):
		return {"eligible": False, "claimed": True, "message": "This reward has already been claimed."}

	v.pay_account('coins', reward["coins"])
	send_notification(
		v.id,
		f'{reward["coins"]:,} Wishcoins have been added to your account. '
		'You can spend them here in [Shop Awards, Hats, or Effects](https://theobsessionclub.com/shop), '
		'or risk it at the [Casino](https://theobsessionclub.com/casino). '
		'Or save and collect them for your future!',
	)
	badge_grant(user=v, badge_id=ALPHA_BADGE_ID, notify=True)
	mark_signup_reward_claimed(v.id)
	g.db.flush()

	response = _public_reward(reward)
	response.update({
		"eligible": False,
		"claimed": True,
		"message": f'{reward["coins"]:,} Wishcoins and the Alpha User badge are now yours.',
		"balance": v.coins,
	})
	return response


def install_signup_reward_signup_hook():
	"""Reserve a reward after a signup succeeds, without rewriting legacy signup code."""
	original = app.view_functions.get('sign_up_post')
	if not original or getattr(original, '_signup_reward_hook', False):
		return

	def wrapped(*args, **kwargs):
		previous_user_id = session.get('lo_user')
		response = original(*args, **kwargs)
		new_user_id = session.get('lo_user')
		if not previous_user_id and new_user_id:
			reserve_signup_reward(new_user_id)
		return response

	wrapped.__name__ = getattr(original, '__name__', 'sign_up_post')
	wrapped._signup_reward_hook = True
	app.view_functions['sign_up_post'] = wrapped
