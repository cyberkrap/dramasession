import time
from random import choice

from flask import g
from sqlalchemy import *
from files.classes.lottery import Lottery

from files.helpers.alerts import *
from files.helpers.useractions import *

from .config.const import *

LOTTERY_WINNER_BADGE_ID = 137

def get_active_lottery():
	return g.db.query(Lottery).order_by(Lottery.id.desc()).filter(Lottery.is_active).one_or_none()


def get_users_participating_in_lottery():
	return g.db.query(User) \
		.filter(User.currently_held_lottery_tickets > 0) \
		.order_by(User.currently_held_lottery_tickets.desc()).all()


def get_active_lottery_stats():
	active_lottery = get_active_lottery()
	participating_users = get_users_participating_in_lottery()

	return None if active_lottery is None else active_lottery.stats, len(participating_users)


def end_lottery_session():
	active_lottery = get_active_lottery()

	if (active_lottery is None):
		return False, "There is no active lottery!"

	participating_users = get_users_participating_in_lottery()
	raffle = []
	for user in participating_users:
		for _ in range(user.currently_held_lottery_tickets):
			raffle.append(user.id)

	if len(raffle) == 0:
		active_lottery.is_active = False
		return True, "Lottery ended with no participants!"

	winner = choice(raffle)
	active_lottery.winner_id = winner
	winning_user = next(filter(lambda x: x.id == winner, participating_users))
	winning_user.pay_account('coins', active_lottery.prize)
	winning_user.total_lottery_winnings += active_lottery.prize
	badge_grant(user=winning_user, badge_id=LOTTERY_WINNER_BADGE_ID)

	for user in participating_users:
		chance_to_win = user.currently_held_lottery_tickets / len(raffle) * 100
		chance_to_win = str(chance_to_win)[:3]
		if user.id == winner:
			notification_text = f'You won {active_lottery.prize} coins in the lottershe! ' \
				+ f'Congratulations!\nYour odds of winning were: {chance_to_win}%'
		else:
			notification_text = f'You did not win the lottershe. Better luck next time!\n' \
				+ f'Your odds of winning were: {chance_to_win}%\nWinner: @{winning_user.username} (won {active_lottery.prize} coins)'
		send_repeatable_notification(user.id, notification_text)
		user.currently_held_lottery_tickets = 0

	active_lottery.is_active = False

	g.db.add(winning_user)
	g.db.add(active_lottery)
	g.db.commit() # Intentionally commit early because cron runs with other tasks

	return True, f'{winning_user.username} won {active_lottery.prize} coins!'


def start_new_lottery_session():
	end_lottery_session()

	lottery = Lottery()
	epoch_time = int(time.time())
	# Subtract 4 minutes from one cycle so cronjob interval doesn't cause the
	# time to drift toward over multiple cycles.
	one_week_from_now = epoch_time + LOTTERY_DURATION - (4 * 60)
	lottery.ends_at = one_week_from_now
	lottery.is_active = True

	g.db.add(lottery)
	g.db.commit() # Intentionally commit early, not autocommitted from cron


def check_if_end_lottery_task():
	active_lottery = get_active_lottery()

	if active_lottery is None:
		return False
	elif active_lottery.timeleft > 0:
		return False

	start_new_lottery_session()
	return True

def lottery_ticket_net_value():
	return LOTTERY_TICKET_COST - LOTTERY_SINK_RATE

def purchase_lottery_tickets(v, quantity=1):
	if quantity < 1:
		return False, f"Must purchase one or more lottershe tickets!"
	elif (v.coins < LOTTERY_TICKET_COST * quantity):
		return False, f"Lottery tickets cost {LOTTERY_TICKET_COST} coins each!"

	most_recent_lottery = get_active_lottery()
	if (most_recent_lottery is None):
		return False, "There is no active lottery!"

	if not v.charge_account('coins', LOTTERY_TICKET_COST * quantity):
		return False, "You don't have enough coins"
	v.currently_held_lottery_tickets += quantity
	v.total_held_lottery_tickets += quantity

	net_ticket_value = lottery_ticket_net_value() * quantity
	most_recent_lottery.prize += net_ticket_value
	most_recent_lottery.tickets_sold += quantity


	if quantity == 1: return True, f'Successfully purchased {quantity} lottershe ticket!'
	return True, f'Successfully purchased {quantity} lottershe tickets!'

def grant_lottery_tickets_to_user(v, quantity):
	active_lottery = get_active_lottery()
	prize_value = lottery_ticket_net_value() * quantity

	if active_lottery:
		v.currently_held_lottery_tickets += quantity
		v.total_held_lottery_tickets += quantity

		active_lottery.prize += prize_value
		active_lottery.tickets_sold += quantity
