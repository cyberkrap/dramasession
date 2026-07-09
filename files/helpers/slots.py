import json
import random
from json.encoder import INFINITY

from flask import abort, g

from files.classes.casino_game import CasinoGame
from files.classes.comment import Comment
from files.classes.user import User
from files.helpers.casino import distribute_wager_badges

from .config.const import *

minimum_bet = 5
maximum_bet = INFINITY
payout_to_symbols = {
	2: ["👣", "🍀", "🌈", "⭐️"],
	3: ["🍎", "🔞", "⚛️", "☢️"],
	5: ["✡️", "⚔️", "🍆", "🍒"],
	12: ["🐱"]
}


def casino_slot_pull(gambler, wager_value, currency):
	over_min = wager_value >= minimum_bet
	under_max = wager_value <= maximum_bet
	charged = gambler.charge_account(currency, wager_value)

	if (over_min and under_max and charged):
		payout = determine_payout()
		reward = wager_value * payout

		gambler.pay_account(currency, reward)

		if currency == 'coins':
			distribute_wager_badges(gambler, wager_value, won=(payout > 0))

		symbols = build_symbols(payout)
		text = build_text(wager_value, payout, currency)
		game_state = {
			"symbols": symbols,
			"text": text
		}
		casino_game = CasinoGame()
		casino_game.active = False
		casino_game.user_id = gambler.id
		casino_game.currency = currency
		casino_game.wager = wager_value
		casino_game.winnings = reward - wager_value
		casino_game.kind = 'slots'
		casino_game.game_state = json.dumps(game_state)
		g.db.add(casino_game)
		g.db.flush()

		return casino_game.id, casino_game.game_state
	else:
		return None, "{}",


def build_symbols(for_payout):
	all_symbols = []

	for payout in payout_to_symbols:
		for symbol in payout_to_symbols[payout]:
			all_symbols.append(symbol)

	shuffle(all_symbols)

	if for_payout == 0:
		return "".join([all_symbols[0], ",", all_symbols[1], ",", all_symbols[2]])
	elif for_payout == 1:
		indices = shuffle([0, 1, 2])
		symbol_set = ["", "", ""]
		match_a = indices[0]
		match_b = indices[1]
		nonmatch = indices[2]
		matching_symbol = all_symbols[0]
		other_symbol = all_symbols[1]
		symbol_set[match_a] = matching_symbol
		symbol_set[match_b] = matching_symbol
		symbol_set[nonmatch] = other_symbol

		return "".join([symbol_set[0], ",", symbol_set[1], ",", symbol_set[2]])
	else:
		relevantSymbols = shuffle(payout_to_symbols[for_payout])
		symbol = relevantSymbols[0]

		return "".join([symbol, ",", symbol, ",", symbol])


def build_text(wager_value, result, currency):
	if result == 0:
		return f'Lost {wager_value} {currency}'
	elif result == 1:
		return 'Broke Even'
	elif result == 12:
		return f'Jackpot! Won {wager_value * (result-1)} {currency}'
	else:
		return f'Won {wager_value * (result-1)} {currency}'


def determine_payout():
	value = random.randint(1, 100)
	if value == 100:
		return 12
	elif value >= 96:
		return 5
	elif value >= 88:
		return 3
	elif value >= 72:
		return 2
	elif value >= 61:
		return 1
	else:
		return 0


def shuffle(stuff):
	random.shuffle(stuff)
	return stuff


def check_slots_command(c:Comment, v:User, u:User):
	if not FEATURES['GAMBLING']: return
	body = c.body.lower()

	if '!slotsmb' in body:
		command_word = '!slotsmb'
		currency = 'marseybux'
	elif '!slots' in body:
		command_word = '!slots'
		currency = 'coins'
	else:
		return

	if u.rehab:
		if v.id == u.id:
			abort(403, "You are under Rehab award effect!")
		return

	try:
		wager = body.split(command_word)[1].split()[0]
		wager = int(wager)
	except:
		if v.id == u.id:
			abort(400, "Invalid wager!")
		return

	if wager < 100:
		if v.id == u.id:
			abort(400, f"Wager must be 100 {currency} or more")
		return

	if (currency == "coins" and wager > u.coins) or (currency == "marseybux" and wager > u.marseybux):
		if v.id == u.id:
			abort(400, f"Not enough {currency} to make that bet")
		return

	game_id, game_state = casino_slot_pull(u, wager, currency)
	c.casino_game_id = game_id
