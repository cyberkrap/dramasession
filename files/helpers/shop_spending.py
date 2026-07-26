"""Unified award-shop spending totals and cumulative spender badges."""

from sqlalchemy import func

from files.classes.award import AwardRelationship
from files.helpers.useractions import badge_grant


SPENDING_BADGE_THRESHOLDS = (
	(10_000, 69),
	(100_000, 70),
	(250_000, 71),
	(500_000, 72),
	(1_000_000, 73),
)
SPENDING_BADGE_IDS = tuple(
	badge_id for _threshold, badge_id in SPENDING_BADGE_THRESHOLDS
)


def recorded_award_spend(db, user_id):
	"""Return the value of every award purchase still represented in the ledger."""
	return int(db.query(
		func.coalesce(func.sum(AwardRelationship.price_paid), 0)
	).filter(
		AwardRelationship.user_id == int(user_id),
	).scalar() or 0)


def sync_spending_badges(user):
	"""Grant every spending milestone reached, including skipped middle tiers."""
	total = max(0, int(user.coins_spent or 0))
	for threshold, badge_id in SPENDING_BADGE_THRESHOLDS:
		if total >= threshold:
			badge_grant(user=user, badge_id=badge_id)
	return total


def reconcile_award_spend(db, user):
	"""Recover historical Wishbux purchases from award price records."""
	ledger_total = recorded_award_spend(db, user.id)
	user.coins_spent = max(int(user.coins_spent or 0), ledger_total)
	return sync_spending_badges(user)


def record_award_spend(db, user, amount):
	"""Add one purchase to the shared total and grant all reached milestones."""
	amount = max(0, int(amount or 0))
	current_total = max(int(user.coins_spent or 0), recorded_award_spend(db, user.id))
	user.coins_spent = current_total + amount
	return sync_spending_badges(user)
