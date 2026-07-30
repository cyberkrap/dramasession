import time
from functools import wraps

import gevent
from flask import g, request
from sqlalchemy import text

from files.__main__ import app, db_session
from files.helpers.roulette import get_active_roulette_games, spin_roulette_wheel


ROULETTE_ROUND_SECONDS = 300
ROULETTE_LOCK_ID = 724682591
ROULETTE_ENDPOINTS = {
	"/casino/roulette/bets",
	"/casino/roulette/place-bet",
}


def _round_started_utc(active_games):
	started = []
	for game in active_games:
		try:
			started.append(int(game.game_state_json.get("parent_id")))
		except (AttributeError, TypeError, ValueError):
			started.append(int(game.created_utc))
	return min(started) if started else None


def get_roulette_round_state():
	active_games = get_active_roulette_games()
	started_utc = _round_started_utc(active_games)
	if started_utc is None:
		return {
			"active": False,
			"started_utc": None,
			"next_spin_utc": None,
			"seconds_remaining": None,
		}

	now = int(time.time())
	next_spin_utc = started_utc + ROULETTE_ROUND_SECONDS
	return {
		"active": True,
		"started_utc": started_utc,
		"next_spin_utc": next_spin_utc,
		"seconds_remaining": max(0, next_spin_utc - now),
	}


def _try_round_lock():
	bind = g.db.get_bind()
	if bind.dialect.name != "postgresql":
		return True
	return bool(g.db.execute(
		text("SELECT pg_try_advisory_xact_lock(:lock_id)"),
		{"lock_id": ROULETTE_LOCK_ID},
	).scalar())


def settle_roulette_if_due():
	state = get_roulette_round_state()
	if not state["active"] or state["seconds_remaining"] > 0:
		return False

	if not _try_round_lock():
		return False

	# Another worker may have settled the round before this request acquired
	# the advisory lock, so discard cached ORM state and verify again.
	g.db.expire_all()
	state = get_roulette_round_state()
	if not state["active"] or state["seconds_remaining"] > 0:
		return False

	spin_roulette_wheel()
	return True


@app.before_request
def settle_due_roulette_request():
	path = request.path.rstrip("/") or "/"
	if path in ROULETTE_ENDPOINTS:
		g.roulette_round_rolled = settle_roulette_if_due()


def _augment_roulette_response(handler):
	@wraps(handler)
	def wrapped(*args, **kwargs):
		response = handler(*args, **kwargs)
		if isinstance(response, dict):
			response["round"] = get_roulette_round_state()
			response["round"]["rolled"] = bool(getattr(g, "roulette_round_rolled", False))
		return response
	wrapped._roulette_round_state = True
	return wrapped


def install_roulette_response_state():
	for endpoint in ("roulette_get_bets", "roulette_player_placed_bet"):
		handler = app.view_functions.get(endpoint)
		if handler and not getattr(handler, "_roulette_round_state", False):
			app.view_functions[endpoint] = _augment_roulette_response(handler)


def _roulette_round_worker():
	while True:
		gevent.sleep(5)
		with app.app_context():
			g.db = db_session()
			try:
				settle_roulette_if_due()
				g.db.commit()
			except Exception:
				g.db.rollback()
				app.logger.exception("Roulette round settlement failed")
			finally:
				db_session.remove()


def start_roulette_round_worker():
	if getattr(app, "_roulette_round_worker_started", False):
		return
	app._roulette_round_worker_started = True
	gevent.spawn(_roulette_round_worker)


install_roulette_response_state()
start_roulette_round_worker()
