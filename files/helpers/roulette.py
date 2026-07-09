import json
from enum import Enum
from random import randint
import time

from flask import g

from files.classes.casino_game import CasinoGame
from files.helpers.alerts import *
from files.helpers.get import get_account

class RouletteAction(str, Enum):
	STRAIGHT_UP_BET = "STRAIGHT_UP_BET",
	LINE_BET = "LINE_BET"
	COLUMN_BET = "COLUMN_BET"
	DOZEN_BET = "DOZEN_BET"
	EVEN_ODD_BET = "EVEN_ODD_BET"
	RED_BLACK_BET = "RED_BLACK_BET"
	HIGH_LOW_BET = "HIGH_LOW_BET"

	@property
	def validation_function(self):
		if self == self.__class__.STRAIGHT_UP_BET: return lambda x: x is not None and x >= 0 and x <= 37
		if self == self.__class__.LINE_BET: return lambda x: x in LINES
		if self == self.__class__.COLUMN_BET: return lambda x: x in COLUMNS
		if self == self.__class__.DOZEN_BET: return lambda x: x in DOZENS
		if self == self.__class__.EVEN_ODD_BET: return lambda x: x in [y.value for y in RouletteEvenOdd]
		if self == self.__class__.RED_BLACK_BET: return lambda x: x in [y.value for y in RouletteRedBlack]
		if self == self.__class__.HIGH_LOW_BET: return lambda x: x in [y.value for y in RouletteHighLow]
		raise ValueError("Unhandled validation function for RouletteAction")


class RouletteEvenOdd(str, Enum):
	EVEN = "EVEN"
	ODD = "ODD"


class RouletteRedBlack(str, Enum):
	RED = "RED"
	BLACK = "BLACK"


class RouletteHighLow(str, Enum):
	HIGH = "HIGH"
	LOW = "LOW"


REDS = (1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36)
BLACKS = (2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35)
LINES = {
	1: (1, 2, 3, 4, 5, 6),
	2: (7, 8, 9, 10, 11, 12),
	3: (13, 14, 15, 16, 17, 18),
	4: (19, 20, 21, 22, 23, 24),
	5: (25, 26, 27, 28, 29, 30),
	6: (31, 32, 33, 34, 35, 36)
}
COLUMNS = {
	1: (1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31, 34),
	2: (2, 5, 8, 11, 14, 17, 20, 23, 26, 29, 32, 35),
	3: (3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36)
}
DOZENS = {
	1: (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12),
	2: (13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24),
	3: (25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36)
}
PAYOUT_MULITPLIERS = {
	RouletteAction.STRAIGHT_UP_BET: 35,
	RouletteAction.LINE_BET: 5,
	RouletteAction.COLUMN_BET: 2,
	RouletteAction.DOZEN_BET: 2,
	RouletteAction.EVEN_ODD_BET: 1,
	RouletteAction.RED_BLACK_BET: 1,
	RouletteAction.HIGH_LOW_BET: 1,
}


def get_active_roulette_games():
	return g.db.query(CasinoGame).filter(
		CasinoGame.active == True,
		CasinoGame.kind == 'roulette'
	).all()


def charge_gambler(gambler, amount, currency):
	charged = gambler.charge_account(currency, amount)

	if not charged:
		raise Exception("Gambler cannot afford charge.")


def gambler_placed_roulette_bet(gambler, bet, which, amount, currency):
	if not bet in (
		RouletteAction.STRAIGHT_UP_BET,
		RouletteAction.LINE_BET,
		RouletteAction.COLUMN_BET,
		RouletteAction.DOZEN_BET,
		RouletteAction.EVEN_ODD_BET,
		RouletteAction.RED_BLACK_BET,
		RouletteAction.HIGH_LOW_BET
	):
		raise Exception(
			f'Illegal bet {bet} passed to Roulette#gambler_placed_roulette_bet')

	active_games = get_active_roulette_games()

	if len(active_games) == 0:
		parent_id = int(time.time())
	else:
		parent_id = active_games[0].game_state_json['parent_id']

	charge_gambler(gambler, amount, currency)

	game = CasinoGame()
	game.user_id = gambler.id
	game.currency = currency
	game.wager = amount
	game.winnings = 0
	game.kind = 'roulette'
	game.game_state = json.dumps(
		{"parent_id": parent_id, "bet": bet, "which": which})
	game.active = True
	g.db.add(game)
	g.db.commit()


def get_roulette_bets_and_betters():
	participants = []
	bets = {
		RouletteAction.STRAIGHT_UP_BET: [],
		RouletteAction.LINE_BET: [],
		RouletteAction.COLUMN_BET: [],
		RouletteAction.DOZEN_BET: [],
		RouletteAction.EVEN_ODD_BET: [],
		RouletteAction.RED_BLACK_BET: [],
		RouletteAction.HIGH_LOW_BET: [],
	}
	active_games = get_active_roulette_games()

	for game in active_games:
		if not game.user_id in participants:
			participants.append(game.user_id)

		user = get_account(game.user_id)
		game_state = game.game_state_json
		bet = game_state['bet']
		bets[bet].append({
			'game_id': game.id,
			'gambler': game.user_id,
			'gambler_username': user.username,
			'gambler_profile_url': user.profile_url,
			'bet': bet,
			'which': game_state['which'],
			'wager': {
				'amount': game.wager,
				'currency': game.currency
			}
		})

	return participants, bets, active_games


def spin_roulette_wheel():
	participants, bets, active_games = get_roulette_bets_and_betters()

	if len(participants) > 0:
		number = randint(0, 37)  # 37 is 00

		winners, payouts, rewards_by_game_id = determine_roulette_winners(number, bets)

		if number == 37: number = '00'

		# Pay out to the winners and send a notification.
		for user_id in winners:
			gambler = get_account(user_id)
			gambler_payout = payouts[user_id]
			coin_winnings = gambler_payout['coins']
			procoin_winnings = gambler_payout['marseybux']

			gambler.pay_account('coins', coin_winnings)
			gambler.pay_account('marseybux', procoin_winnings)

			# Notify the winners.
			notification_text = f"Winning number: {number}\nCongratulations! One or more of your roulette bets paid off!\n"

			if coin_winnings > 0:
				notification_text = notification_text + \
					f"* You received {coin_winnings} coins.\n"

			if procoin_winnings > 0:
				notification_text = notification_text + \
					f"* You received {procoin_winnings} marseybux.\n"

			send_repeatable_notification(user_id, notification_text)

		# Give condolences.
		for participant in participants:
			if not participant in winners:
				send_repeatable_notification(
					participant, f"Winning number: {number}\nSorry, none of your recent roulette bets paid off.")

				g.db.flush()

		# Adjust game winnings.
		for game in active_games:
			if rewards_by_game_id.get(game.id):
				game.winnings = rewards_by_game_id[game.id]
			else:
				game.winnings = -game.wager

			game.active = False
			g.db.add(game)

		# Commit early when dirty because of long-running tasks after roulette
		g.db.commit()


def determine_roulette_winners(number, bets):
	winners = []
	payouts = {}
	rewards_by_game_id = {}

	def add_to_winnings(bet):
		game_id = int(bet['game_id'])
		gambler_id = bet['gambler']
		wager_amount = bet['wager']['amount']
		bet_kind = bet['bet']
		reward = wager_amount * PAYOUT_MULITPLIERS[bet_kind]
		payout = wager_amount + reward
		currency = bet['wager']['currency']

		if not gambler_id in winners:
			winners.append(gambler_id)

		if not payouts.get(gambler_id):
			payouts[gambler_id] = {
				'coins': 0,
				'marseybux': 0
			}

		if not rewards_by_game_id.get(game_id):
			rewards_by_game_id[game_id] = reward

		payouts[gambler_id][currency] += payout

	# Straight-Up Bet
	for bet in bets[RouletteAction.STRAIGHT_UP_BET]:
		if int(bet['which']) == number:
			add_to_winnings(bet)

	if number == 0 or number == 37:
		return winners, payouts, rewards_by_game_id


	# Line Bet
	line = -1
	for i in range(1, 7):
		if number in LINES[i]:
			line = i

	for bet in bets[RouletteAction.LINE_BET]:
		if int(bet['which']) == line:
			add_to_winnings(bet)

	# Column Bet
	column = -1
	for i in range(1, 4):
		if number in COLUMNS[i]:
			column = i

	for bet in bets[RouletteAction.COLUMN_BET]:
		if int(bet['which']) == column:
			add_to_winnings(bet)

	# Dozen Bet
	dozen = -1
	for i in range(1, 4):
		if number in DOZENS[i]:
			dozen = i

	for bet in bets[RouletteAction.DOZEN_BET]:
		if int(bet['which']) == dozen:
			add_to_winnings(bet)

	# Even/Odd Bet
	even_odd = RouletteEvenOdd.EVEN if number % 2 == 0 else RouletteEvenOdd.ODD

	for bet in bets[RouletteAction.EVEN_ODD_BET]:
		if bet['which'] == even_odd:
			add_to_winnings(bet)

	# Red/Black Bet
	red_black = RouletteRedBlack.RED if number in REDS else RouletteRedBlack.BLACK

	for bet in bets[RouletteAction.RED_BLACK_BET]:
		if bet['which'] == red_black:
			add_to_winnings(bet)

	# High/Low Bet
	high_low = RouletteHighLow.HIGH if number > 18 else RouletteHighLow.LOW

	for bet in bets[RouletteAction.HIGH_LOW_BET]:
		if bet['which'] == high_low:
			add_to_winnings(bet)

	return winners, payouts, rewards_by_game_id


def get_roulette_bets():
	return get_roulette_bets_and_betters()[1]
