import json
import time

from flask import abort, g, request
from werkzeug.exceptions import HTTPException

from files.__main__ import app, limiter
from files.classes.casino_game import CasinoGame
from files.classes.user import User
from files.helpers.roulette import RouletteAction, get_active_roulette_games, get_roulette_bets
from files.routes.wrappers import auth_required, get_ID


def _currency_name(currency, amount):
	if currency == "coins":
		return "Wishcoin" if amount == 1 else "Wishcoins"
	return "Wishbux"


def _available_balance(user, currency):
	return user.coins if currency == "coins" else user.marseybux


@limiter.limit("100/minute;2000/hour;12000/day")
@limiter.limit("100/minute;2000/hour;12000/day", key_func=get_ID)
@auth_required
def fixed_roulette_player_placed_bet(v: User):
	if v.rehab:
		abort(403, "You are under Rehab award effect!")

	bet_raw = (request.values.get("bet") or "").strip()
	which = (request.values.get("which") or "").strip()
	currency = (request.values.get("currency") or "").strip().lower()

	if currency not in {"coins", "marseybux"}:
		abort(400, "Choose Wishcoins or Wishbux before placing the bet.")

	try:
		amount = int(request.values.get("wager"))
	except (TypeError, ValueError):
		abort(400, "Enter a whole-number wager.")

	if amount < 5:
		abort(400, f"Minimum roulette wager is 5 {_currency_name(currency, 5)}.")

	try:
		bet_type = RouletteAction(bet_raw)
	except (TypeError, ValueError):
		abort(400, "That roulette bet type is invalid. Reload the page and try again.")

	if not which:
		abort(400, "Choose a roulette number or betting area first.")

	try:
		which_value = int(which)
	except ValueError:
		which_value = which

	if not bet_type.validation_function(which_value):
		abort(400, "That selection is not valid for this roulette bet.")

	if not v.can_spend(currency, amount):
		available = _available_balance(v, currency)
		abort(
			400,
			f"Not enough {_currency_name(currency, available)}. "
			f"You have {available:,}, but the wager is {amount:,}.",
		)

	try:
		active_games = get_active_roulette_games()
		if active_games:
			parent_id = min(
				int(game.game_state_json.get("parent_id", game.created_utc))
				for game in active_games
			)
		else:
			parent_id = int(time.time())

		if not v.charge_account(currency, amount):
			fresh_user = g.db.query(User).filter(User.id == v.id).one()
			available = _available_balance(fresh_user, currency)
			abort(
				400,
				f"Not enough {_currency_name(currency, available)}. "
				f"You have {available:,}, but the wager is {amount:,}.",
			)

		game = CasinoGame(
			user_id=v.id,
			currency=currency,
			wager=amount,
			winnings=0,
			kind="roulette",
			game_state=json.dumps({
				"parent_id": parent_id,
				"bet": bet_type.value,
				"which": which,
			}),
			active=True,
		)
		g.db.add(game)
		g.db.flush()

		bets = get_roulette_bets()
		g.db.expire(v, ["coins", "marseybux"])
		return {
			"success": True,
			"bets": bets,
			"gambler": {"coins": v.coins, "marseybux": v.marseybux},
		}
	except HTTPException:
		raise
	except Exception:
		g.db.rollback()
		app.logger.exception(
			"Roulette bet failed for user_id=%s bet=%s which=%s wager=%s currency=%s",
			v.id,
			bet_raw,
			which,
			amount,
			currency,
		)
		abort(500, "Roulette could not save the bet. Your balance was not charged. Reload and try again.")


# The legacy route is already registered in files.routes.casino. Replace only its
# view function so the original URL remains unchanged, then let roulette_rounds
# wrap this corrected handler with round-state metadata.
fixed_roulette_player_placed_bet.__name__ = "roulette_player_placed_bet"
app.view_functions["roulette_player_placed_bet"] = fixed_roulette_player_placed_bet
