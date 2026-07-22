"""Persistent manual lifetime-contribution overrides for economy administrators."""

import threading
import time

from sqlalchemy import func, text

from files.__main__ import engine
from files.classes import PaypalPayment


_TABLE_LOCK = threading.Lock()
_TABLE_READY = False


def _ensure_table():
	global _TABLE_READY
	if _TABLE_READY:
		return
	with _TABLE_LOCK:
		if _TABLE_READY:
			return
		with engine.begin() as connection:
			connection.execute(text("""
				CREATE TABLE IF NOT EXISTS lifetime_contribution_overrides (
					user_id BIGINT PRIMARY KEY,
					amount_cents BIGINT NOT NULL CHECK (amount_cents >= 0),
					updated_utc BIGINT NOT NULL,
					updated_by BIGINT
				)
			"""))
		_TABLE_READY = True


def verified_contribution_cents(db, user_id):
	return int(db.query(
		func.coalesce(func.sum(PaypalPayment.gross_cents), 0)
	).filter(
		PaypalPayment.user_id == int(user_id),
		PaypalPayment.status == "COMPLETED",
	).scalar() or 0)


def contribution_override_cents(db, user_id):
	_ensure_table()
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
	_ensure_table()
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
	_ensure_table()
	db.execute(
		text("DELETE FROM lifetime_contribution_overrides WHERE user_id = :user_id"),
		{"user_id": int(user_id)},
	)
