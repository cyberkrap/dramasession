"""Persistent manual lifetime-contribution overrides for economy administrators."""

import threading
import time

from sqlalchemy import func, text

from files.__main__ import engine
from files.classes import PaypalPayment, PaypalSubscription
from files.helpers.support import PAYPAL_ACTIVE_PLAN_IDS


_TABLE_LOCK = threading.Lock()
_TABLE_READY = False
_CREATE_TABLE_SQL = text("""
	CREATE TABLE IF NOT EXISTS lifetime_contribution_overrides (
		user_id BIGINT PRIMARY KEY,
		amount_cents BIGINT NOT NULL CHECK (amount_cents >= 0),
		updated_utc BIGINT NOT NULL,
		updated_by BIGINT
	)
""")


def _ensure_table(db=None):
	global _TABLE_READY
	if _TABLE_READY:
		return
	with _TABLE_LOCK:
		if _TABLE_READY:
			return

		# Contribution totals are normally read during an active profile request.
		# Reuse that request's SQLAlchemy session instead of opening a second
		# engine transaction, which can wait behind the request and make the two
		# support fields appear several seconds after the rest of the profile.
		if db is not None:
			db.execute(_CREATE_TABLE_SQL)
		else:
			with engine.begin() as connection:
				connection.execute(_CREATE_TABLE_SQL)
		_TABLE_READY = True


def verified_contribution_cents(db, user_id):
	if not PAYPAL_ACTIVE_PLAN_IDS:
		return 0
	return int(db.query(
		func.coalesce(func.sum(PaypalPayment.gross_cents), 0)
	).join(
		PaypalSubscription,
		PaypalSubscription.subscription_id == PaypalPayment.subscription_id,
	).filter(
		PaypalPayment.user_id == int(user_id),
		PaypalPayment.status == "COMPLETED",
		PaypalSubscription.plan_id.in_(PAYPAL_ACTIVE_PLAN_IDS),
	).scalar() or 0)


def contribution_override_cents(db, user_id):
	_ensure_table(db)
	return db.execute(
		text("SELECT amount_cents FROM lifetime_contribution_overrides WHERE user_id = :user_id"),
		{"user_id": int(user_id)},
	).scalar()


def effective_contribution_cents(db, user_id):
	override = contribution_override_cents(db, user_id)
	if override is not None:
		return int(override)
	return verified_contribution_cents(db, user_id)


def set_contribution_override(db, user_id, amount_cents, updated_by):
	_ensure_table(db)
	amount_cents = max(0, int(amount_cents))
	db.execute(text("""
		INSERT INTO lifetime_contribution_overrides (user_id, amount_cents, updated_utc, updated_by)
		VALUES (:user_id, :amount_cents, :updated_utc, :updated_by)
		ON CONFLICT (user_id) DO UPDATE SET
			amount_cents = EXCLUDED.amount_cents,
			updated_utc = EXCLUDED.updated_utc,
			updated_by = EXCLUDED.updated_by
	"""), {
		"user_id": int(user_id),
		"amount_cents": amount_cents,
		"updated_utc": int(time.time()),
		"updated_by": int(updated_by),
	})
	return amount_cents


def clear_contribution_override(db, user_id):
	_ensure_table(db)
	db.execute(
		text("DELETE FROM lifetime_contribution_overrides WHERE user_id = :user_id"),
		{"user_id": int(user_id)},
	)
