import threading
import time

from flask import g
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from files.helpers.config.const import SITE_NAME


CAMPAIGN_KEY = "obsession-launch-signups-v2"
ALPHA_BADGE_ID = 1
MAX_REWARDED_SIGNUPS = 200

# Slot upper bound, Wishcoins, advertised value, audience label.
REWARD_TIERS = (
	(20, 24000, "$20", "the first 20 members"),
	(100, 12000, "$10", "the next 80 members"),
	(200, 6000, "$5", "the next 100 members"),
)

_TABLE_LOCK = threading.Lock()
_TABLE_READY = False


def install_signup_rewards(engine):
	global _TABLE_READY
	if _TABLE_READY:
		return True
	with _TABLE_LOCK:
		if _TABLE_READY:
			return True
		try:
			with engine.begin() as connection:
				connection.execute(text("""
					CREATE TABLE IF NOT EXISTS signup_reward_claims (
						campaign VARCHAR(80) NOT NULL,
						user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
						slot INTEGER NOT NULL,
						coins INTEGER NOT NULL,
						value_label VARCHAR(16) NOT NULL,
						created_utc BIGINT NOT NULL,
						claimed_utc BIGINT,
						PRIMARY KEY (campaign, user_id),
						UNIQUE (campaign, slot)
					)
				"""))
				connection.execute(text("""
					CREATE INDEX IF NOT EXISTS signup_reward_claims_campaign_claimed_idx
					ON signup_reward_claims (campaign, claimed_utc)
				"""))
		except SQLAlchemyError:
			return False
		_TABLE_READY = True
	return True


def reward_for_slot(slot):
	try:
		slot = int(slot)
	except (TypeError, ValueError):
		return None
	for upper_bound, coins, value_label, audience_label in REWARD_TIERS:
		if slot <= upper_bound:
			return {
				"slot": slot,
				"coins": coins,
				"value_label": value_label,
				"audience_label": audience_label,
				"tier_end": upper_bound,
			}
	return None


def reserve_signup_reward(user_id):
	"""Reserve a launch-promotion slot in signup order, not claim order."""
	if SITE_NAME != "Obsession" or not _TABLE_READY:
		return None

	try:
		# PostgreSQL advisory locking makes concurrent signups receive distinct,
		# strictly ordered slots without allowing the campaign past 200 users.
		bind = g.db.get_bind()
		if getattr(getattr(bind, "dialect", None), "name", "") == "postgresql":
			g.db.execute(
				text("SELECT pg_advisory_xact_lock(hashtext(:campaign))"),
				{"campaign": CAMPAIGN_KEY},
			)

		existing = g.db.execute(text("""
			SELECT slot, coins, value_label, claimed_utc
			FROM signup_reward_claims
			WHERE campaign = :campaign AND user_id = :user_id
		"""), {
			"campaign": CAMPAIGN_KEY,
			"user_id": int(user_id),
		}).mappings().one_or_none()
		if existing:
			return dict(existing)

		next_slot = g.db.execute(text("""
			SELECT COALESCE(MAX(slot), 0) + 1
			FROM signup_reward_claims
			WHERE campaign = :campaign
		"""), {"campaign": CAMPAIGN_KEY}).scalar_one()
		if next_slot > MAX_REWARDED_SIGNUPS:
			return None

		reward = reward_for_slot(next_slot)
		if not reward:
			return None

		g.db.execute(text("""
			INSERT INTO signup_reward_claims
				(campaign, user_id, slot, coins, value_label, created_utc, claimed_utc)
			VALUES
				(:campaign, :user_id, :slot, :coins, :value_label, :created_utc, NULL)
		"""), {
			"campaign": CAMPAIGN_KEY,
			"user_id": int(user_id),
			"slot": reward["slot"],
			"coins": reward["coins"],
			"value_label": reward["value_label"],
			"created_utc": int(time.time()),
		})
		return reward
	except SQLAlchemyError:
		return None


def get_signup_reward(user_id, lock=False):
	if SITE_NAME != "Obsession" or not _TABLE_READY:
		return None
	query = """
		SELECT slot, coins, value_label, created_utc, claimed_utc
		FROM signup_reward_claims
		WHERE campaign = :campaign AND user_id = :user_id
	"""
	if lock:
		query += " FOR UPDATE"
	row = g.db.execute(text(query), {
		"campaign": CAMPAIGN_KEY,
		"user_id": int(user_id),
	}).mappings().one_or_none()
	if not row:
		return None
	reward = dict(row)
	reward.update(reward_for_slot(reward["slot"]) or {})
	return reward


def mark_signup_reward_claimed(user_id):
	claimed_utc = int(time.time())
	g.db.execute(text("""
		UPDATE signup_reward_claims
		SET claimed_utc = :claimed_utc
		WHERE campaign = :campaign
			AND user_id = :user_id
			AND claimed_utc IS NULL
	"""), {
		"claimed_utc": claimed_utc,
		"campaign": CAMPAIGN_KEY,
		"user_id": int(user_id),
	})
	return claimed_utc