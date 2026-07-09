from files.classes.casino_game import CASINO_GAME_KINDS
from files.helpers.alerts import *
from files.helpers.casino import *
from files.helpers.config.const import *
from files.helpers.get import *
from files.helpers.lottery import *
from files.helpers.roulette import *
from files.helpers.slots import *
from files.helpers.twentyone import *
from files.routes.wrappers import *

from files.__main__ import app, limiter

@app.get("/casino")
@limiter.limit("100/minute;2000/hour;12000/day")
@limiter.limit("100/minute;2000/hour;12000/day", key_func=get_ID)
@auth_required
def casino(v:User):
	if v.rehab:
		return render_template("casino/rehab.html", v=v), 403

	return render_template("casino.html", v=v)


@app.get("/casino/<game>")
@limiter.limit("100/minute;2000/hour;12000/day")
@limiter.limit("100/minute;2000/hour;12000/day", key_func=get_ID)
@auth_required
def casino_game_page(v:User, game):
	if v.rehab:
		return render_template("casino/rehab.html", v=v), 403
	elif game not in CASINO_GAME_KINDS:
		abort(404)

	feed = json.dumps(get_game_feed(game, g.db))
	leaderboard = json.dumps(get_game_leaderboard(game, g.db))
	v_stats = get_user_stats(v, game, g.db, game == 'blackjack')

	game_state = ''
	if game == 'blackjack':
		if get_active_twentyone_game(v):
			game_state = json.dumps(get_active_twentyone_game_state(v))

	return render_template(
		f"casino/{game}_screen.html",
		v=v,
		game=game,
		feed=feed,
		leaderboard=leaderboard,
		v_stats=v_stats,
		game_state=game_state
	)


@app.get("/casino/<game>/feed")
@limiter.limit("100/minute;2000/hour;12000/day")
@limiter.limit("100/minute;2000/hour;12000/day", key_func=get_ID)
@auth_required
def casino_game_feed(v:User, game):
	if v.rehab:
		abort(403, "You are under Rehab award effect!")
	elif game not in CASINO_GAME_KINDS:
		abort(404)

	feed = get_game_feed(game, g.db)
	return {"feed": feed}


# Lottershe
@app.get("/lottershe")
@limiter.limit("100/minute;2000/hour;12000/day")
@limiter.limit("100/minute;2000/hour;12000/day", key_func=get_ID)
@auth_required
def lottershe(v:User):
	if v.rehab:
		return render_template("casino/rehab.html", v=v)

	participants = get_users_participating_in_lottery()
	return render_template("lottery.html", v=v, participants=participants)

# Slots
@app.post("/casino/slots")
@limiter.limit("100/minute;2000/hour;12000/day")
@limiter.limit("100/minute;2000/hour;12000/day", key_func=get_ID)
@auth_required
def pull_slots(v:User):
	if v.rehab:
		abort(403, "You are under Rehab award effect!")

	try:
		wager = int(request.values.get("wager"))
	except:
		abort(400, "Invalid wager!")

	try:
		currency = request.values.get("currency", "").lower()
		if currency not in {'coins', 'marseybux'}: raise ValueError()
	except:
		abort(400, "Invalid currency (expected 'coins' or 'marseybux').")

	if (currency == "coins" and wager > v.coins) or (currency == "marseybux" and wager > v.marseybux):
		abort(400, f"Not enough {currency} to make that bet")

	game_id, game_state = casino_slot_pull(v, wager, currency)
	success = bool(game_id)

	if success:
		return {"game_state": game_state, "gambler": {"coins": v.coins, "marseybux": v.marseybux}}
	else:
		abort(400, f"Wager must be 5 {currency} or more")


# 21
@app.post("/casino/twentyone/deal")
@limiter.limit("1/second;100/minute;2000/hour;12000/day")
@limiter.limit("1/second;100/minute;2000/hour;12000/day", key_func=get_ID)
@auth_required
def blackjack_deal_to_player(v:User):
	if v.rehab:
		abort(403, "You are under Rehab award effect!")

	try:
		wager = int(request.values.get("wager"))
		currency = request.values.get("currency")
		create_new_game(v, wager, currency)
		state = dispatch_action(v, BlackjackAction.DEAL)
		feed = get_game_feed('blackjack', g.db)

		return {"success": True, "state": state, "feed": feed, "gambler": {"coins": v.coins, "marseybux": v.marseybux}}
	except Exception as e:
		abort(400, str(e))


@app.post("/casino/twentyone/hit")
@limiter.limit("1/second;100/minute;2000/hour;12000/day")
@limiter.limit("1/second;100/minute;2000/hour;12000/day", key_func=get_ID)
@auth_required
def blackjack_player_hit(v:User):
	if v.rehab:
		abort(403, "You are under Rehab award effect!")

	try:
		state = dispatch_action(v, BlackjackAction.HIT)
		feed = get_game_feed('blackjack', g.db)
		return {"success": True, "state": state, "feed": feed, "gambler": {"coins": v.coins, "marseybux": v.marseybux}}
	except:
		abort(400, "Unable to hit!")


@app.post("/casino/twentyone/stay")
@limiter.limit("1/second;100/minute;2000/hour;12000/day")
@limiter.limit("1/second;100/minute;2000/hour;12000/day", key_func=get_ID)
@auth_required
def blackjack_player_stay(v:User):
	if v.rehab:
		abort(403, "You are under Rehab award effect!")

	try:
		state = dispatch_action(v, BlackjackAction.STAY)
		feed = get_game_feed('blackjack', g.db)
		return {"success": True, "state": state, "feed": feed, "gambler": {"coins": v.coins, "marseybux": v.marseybux}}
	except:
		abort(400, "Unable to stay!")


@app.post("/casino/twentyone/double-down")
@limiter.limit("1/second;100/minute;2000/hour;12000/day")
@limiter.limit("1/second;100/minute;2000/hour;12000/day", key_func=get_ID)
@auth_required
def blackjack_player_doubled_down(v:User):
	if v.rehab:
		abort(403, "You are under Rehab award effect!")

	try:
		state = dispatch_action(v, BlackjackAction.DOUBLE_DOWN)
		feed = get_game_feed('blackjack', g.db)
		return {"success": True, "state": state, "feed": feed, "gambler": {"coins": v.coins, "marseybux": v.marseybux}}
	except:
		abort(400, "Unable to double down!")


@app.post("/casino/twentyone/buy-insurance")
@limiter.limit("1/second;100/minute;2000/hour;12000/day")
@limiter.limit("1/second;100/minute;2000/hour;12000/day", key_func=get_ID)
@auth_required
def blackjack_player_bought_insurance(v:User):
	if v.rehab:
		abort(403, "You are under Rehab award effect!")

	try:
		state = dispatch_action(v, BlackjackAction.BUY_INSURANCE)
		feed = get_game_feed('blackjack', g.db)
		return {"success": True, "state": state, "feed": feed, "gambler": {"coins": v.coins, "marseybux": v.marseybux}}
	except:
		abort(403, "Unable to buy insurance!")

# Roulette
@app.get("/casino/roulette/bets")
@limiter.limit("100/minute;2000/hour;12000/day")
@limiter.limit("100/minute;2000/hour;12000/day", key_func=get_ID)
@auth_required
def roulette_get_bets(v:User):
	if v.rehab:
		abort(403, "You are under Rehab award effect!")

	bets = get_roulette_bets()

	return {"success": True, "bets": bets, "gambler": {"coins": v.coins, "marseybux": v.marseybux}}


@app.post("/casino/roulette/place-bet")
@limiter.limit("100/minute;2000/hour;12000/day")
@limiter.limit("100/minute;2000/hour;12000/day", key_func=get_ID)
@auth_required
def roulette_player_placed_bet(v:User):
	if v.rehab:
		abort(403, "You are under Rehab award effect!")

	bet = request.values.get("bet")
	which = request.values.get("which", None)
	amount = request.values.get("wager", None, int)
	currency = request.values.get("currency")

	try: bet_type = RouletteAction(bet)
	except: abort(400, "Not a valid roulette bet type")

	if not amount or amount < 5: abort(400, f"Minimum bet is 5 {currency}.")
	if not which: abort(400, "Not a valid roulette bet")

	try: which_int = int(which)
	except: which_int = None

	if not bet_type.validation_function(which if which_int is None else which_int):
		abort(400, f"Not a valid roulette bet for bet type {bet_type.value[0]}")

	try:
		gambler_placed_roulette_bet(v, bet, which, amount, currency)
		bets = get_roulette_bets()
		return {"success": True, "bets": bets, "gambler": {"coins": v.coins, "marseybux": v.marseybux}}
	except:
		abort(400, "Unable to place a bet!")
