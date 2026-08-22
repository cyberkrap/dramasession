import time
from files.classes.casino_game import CasinoGame
from files.helpers.alerts import *
from files.helpers.bank_statement_noise_fixes import ECONOMY_RESET_UTC
from files.helpers.config.const import *
from files.helpers.useractions import badge_grant

# All three casino "All Time" winner/loser cards were reset on 2026-08-22 after
# development/testing balances polluted the historical extremes. Game rows stay
# intact for feeds, user stats and audit/history; only leaderboard eligibility
# starts fresh from the shared economy reset cutoff.
CASINO_LEADERBOARD_RESET_UTC = {
	'slots': ECONOMY_RESET_UTC,
	'blackjack': ECONOMY_RESET_UTC,
	'roulette': ECONOMY_RESET_UTC,
}

def get_game_feed(game, db):
	games = db.query(CasinoGame) \
		.filter(CasinoGame.active == False, CasinoGame.kind == game) \
		.order_by(CasinoGame.created_utc.desc()).limit(30).all()

	def format_game(game):
		user = db.query(User).filter(User.id == game.user_id).one()
		wonlost = 'lost' if game.winnings < 0 else 'won'
		relevant_currency = "coin" if game.currency == "coins" else "marseybux"

		return {
			"user": user.username,
			"won_or_lost": wonlost,
			"amount": abs(game.winnings),
			"currency": relevant_currency
		}

	return list(map(format_game, games))

def get_user_stats(u:User, game:str, db:scoped_session, include_ties=False):
	games = db.query(CasinoGame.user_id, CasinoGame.winnings).filter(CasinoGame.kind == game, CasinoGame.user_id == u.id)
	wins = games.filter(CasinoGame.winnings > 0).count()
	ties = games.filter(CasinoGame.winnings == 0).count() if include_ties else 0
	losses = games.filter(CasinoGame.winnings < 0).count()
	return (wins, ties, losses)

def get_game_leaderboard(game, db:scoped_session):
	timestamp_24h_ago = time.time() - 86400
	leaderboard_reset = CASINO_LEADERBOARD_RESET_UTC.get(game, 0)
	# "All Time" normally starts on casino release day. For explicitly reset
	# games it starts at the reset cutoff instead. The 24h card also respects the
	# same cutoff, so pre-reset games cannot leak into either card.
	timestamp_all_time = max(CASINO_RELEASE_DAY, leaderboard_reset)
	timestamp_last_24h = max(timestamp_24h_ago, leaderboard_reset)

	biggest_win_all_time = db.query(CasinoGame.user_id, User.username, CasinoGame.currency, CasinoGame.winnings).select_from(
		CasinoGame).join(User).order_by(CasinoGame.winnings.desc()).filter(
			CasinoGame.kind == game,
			CasinoGame.winnings > 0,
			CasinoGame.created_utc > timestamp_all_time
		).limit(1).one_or_none()

	biggest_win_last_24h = db.query(CasinoGame.user_id, User.username, CasinoGame.currency, CasinoGame.winnings).select_from(
		CasinoGame).join(User).order_by(CasinoGame.winnings.desc()).filter(
			CasinoGame.kind == game,
			CasinoGame.winnings > 0,
			CasinoGame.created_utc > timestamp_last_24h
		).limit(1).one_or_none()

	biggest_loss_all_time = db.query(CasinoGame.user_id, User.username, CasinoGame.currency, CasinoGame.winnings).select_from(
		CasinoGame).join(User).order_by(CasinoGame.winnings.asc()).filter(
			CasinoGame.kind == game,
			CasinoGame.winnings < 0,
			CasinoGame.created_utc > timestamp_all_time
		).limit(1).one_or_none()

	biggest_loss_last_24h = db.query(CasinoGame.user_id, User.username, CasinoGame.currency, CasinoGame.winnings).select_from(
		CasinoGame).join(User).order_by(CasinoGame.winnings.asc()).filter(
			CasinoGame.kind == game,
			CasinoGame.winnings < 0,
			CasinoGame.created_utc > timestamp_last_24h
		).limit(1).one_or_none()

	if not biggest_win_all_time:
		biggest_win_all_time = [None, None, None, 0]

	if not biggest_win_last_24h:
		biggest_win_last_24h = [None, None, None, 0]

	if not biggest_loss_all_time:
		biggest_loss_all_time = [None, None, None, 0]

	if not biggest_loss_last_24h:
		biggest_loss_last_24h = [None, None, None, 0]

	return {
		"all_time": {
			"biggest_win": {
				"user": biggest_win_all_time[1],
				"currency": biggest_win_all_time[2],
				"amount": biggest_win_all_time[3]
			},
			"biggest_loss": {
				"user": biggest_loss_all_time[1],
				"currency": biggest_loss_all_time[2],
				"amount": abs(biggest_loss_all_time[3])
			}
		},
		"last_24h": {
			"biggest_win": {
				"user": biggest_win_last_24h[1],
				"currency": biggest_win_last_24h[2],
				"amount": biggest_win_last_24h[3]
			},
			"biggest_loss": {
				"user": biggest_loss_last_24h[1],
				"currency": biggest_loss_last_24h[2],
				"amount": abs(biggest_loss_last_24h[3])
			}
		}
	}


def distribute_wager_badges(user, wager, won):
	badges_earned = []

	if won:
		if wager >= 1000:
			badges_earned.append(160)
		if wager >= 10000:
			badges_earned.append(161)
		if wager >= 100000:
			badges_earned.append(162)
		if wager >= 1000000:
			badges_earned.append(366)
	else:
		if wager >= 1000:
			badges_earned.append(157)
		if wager >= 10000:
			badges_earned.append(158)
		if wager >= 100000:
			badges_earned.append(159)
		if wager >= 1000000:
			badges_earned.append(367)

	for badge in badges_earned:
		badge_grant(user, badge)
