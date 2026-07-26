"""Default-follow the Obsession owner account without preventing later unfollows."""

import time
from functools import wraps

from flask import g, session
from sqlalchemy import case, func, or_, text

from files.classes.follows import Follow
from files.helpers.config.const import SIGNUP_FOLLOW_ID, SITE_NAME


_PRIMARY_USERNAME = "cybercrap"
_SECONDARY_USERNAME = "a1"
_CANONICAL_USER_ID = 5
_MIGRATION_KEY = "obsession-default-follow-cybercrap-v1"


def _is_obsession():
	return SITE_NAME == "Obsession"


def _resolve_target(db):
	"""Resolve the same account through its current or previous username."""
	if not _is_obsession():
		return None

	from files.classes import User

	primary = _PRIMARY_USERNAME.lower()
	secondary = _SECONDARY_USERNAME.lower()
	target = db.query(User).filter(
		or_(
			func.lower(User.username) == primary,
			func.lower(func.coalesce(User.original_username, "")) == primary,
			func.lower(User.username) == secondary,
			func.lower(func.coalesce(User.original_username, "")) == secondary,
		)
	).order_by(
		case(
			(func.lower(User.username) == primary, 0),
			(func.lower(func.coalesce(User.original_username, "")) == primary, 1),
			(func.lower(User.username) == secondary, 2),
			(func.lower(func.coalesce(User.original_username, "")) == secondary, 3),
			else_=4,
		)
	).first()
	if target:
		return target

	for user_id in (_CANONICAL_USER_ID, SIGNUP_FOLLOW_ID):
		if not user_id:
			continue
		target = db.get(User, int(user_id))
		if target:
			return target
	return None


def ensure_default_follow(db, user):
	"""Add the default follow once and keep the stored follower count accurate."""
	if not _is_obsession() or user is None or not getattr(user, "id", None):
		return False

	target = _resolve_target(db)
	if not target or target.id == user.id:
		return False

	existing = db.query(Follow.target_id).filter_by(
		target_id=target.id,
		user_id=user.id,
	).one_or_none()
	if existing:
		return False

	db.add(Follow(target_id=target.id, user_id=user.id))
	db.flush()
	target.stored_subscriber_count = int(db.query(func.count(Follow.user_id)).filter(
		Follow.target_id == target.id,
	).scalar() or 0)
	db.add(target)
	return True


def _resolve_target_id(connection):
	params = {
		"primary": _PRIMARY_USERNAME.lower(),
		"secondary": _SECONDARY_USERNAME.lower(),
	}
	target_id = connection.execute(text("""
		SELECT id
		FROM users
		WHERE lower(username) IN (:primary, :secondary)
			OR lower(COALESCE(original_username, '')) IN (:primary, :secondary)
		ORDER BY CASE
			WHEN lower(username) = :primary THEN 0
			WHEN lower(COALESCE(original_username, '')) = :primary THEN 1
			WHEN lower(username) = :secondary THEN 2
			WHEN lower(COALESCE(original_username, '')) = :secondary THEN 3
			ELSE 4
		END
		LIMIT 1
	"""), params).scalar()
	if target_id:
		return int(target_id)

	for user_id in (_CANONICAL_USER_ID, SIGNUP_FOLLOW_ID):
		if not user_id:
			continue
		found = connection.execute(
			text("SELECT id FROM users WHERE id = :user_id"),
			{"user_id": int(user_id)},
		).scalar()
		if found:
			return int(found)
	return None


def backfill_existing_default_follows(engine):
	"""One-time backfill for accounts that existed before default following."""
	if not _is_obsession():
		return 0

	with engine.begin() as connection:
		connection.execute(text("""
			CREATE TABLE IF NOT EXISTS obsession_site_migrations (
				migration_key VARCHAR(255) PRIMARY KEY,
				completed_utc BIGINT NOT NULL
			)
		"""))

		target_id = _resolve_target_id(connection)
		if not target_id:
			return 0

		claim = connection.execute(text("""
			INSERT INTO obsession_site_migrations (migration_key, completed_utc)
			VALUES (:migration_key, :completed_utc)
			ON CONFLICT (migration_key) DO NOTHING
		"""), {
			"migration_key": _MIGRATION_KEY,
			"completed_utc": int(time.time()),
		})
		if claim.rowcount != 1:
			return 0

		inserted = connection.execute(text("""
			INSERT INTO follows (target_id, user_id, created_utc)
			SELECT :target_id, users.id, :created_utc
			FROM users
			WHERE users.id != :target_id
			ON CONFLICT (target_id, user_id) DO NOTHING
		"""), {
			"target_id": target_id,
			"created_utc": int(time.time()),
		})

		connection.execute(text("""
			UPDATE users
			SET stored_subscriber_count = (
				SELECT COUNT(*) FROM follows WHERE target_id = :target_id
			)
			WHERE id = :target_id
		"""), {"target_id": target_id})
		return max(0, int(inserted.rowcount or 0))


def _install_signup_default_follow(app):
	endpoint = "sign_up_post"
	original = app.view_functions.get(endpoint)
	if not original or getattr(original, "_obsession_default_follow", False):
		return

	@wraps(original)
	def wrapped(*args, **kwargs):
		previous_user_id = session.get("lo_user")
		response = original(*args, **kwargs)
		new_user_id = session.get("lo_user")
		if new_user_id and new_user_id != previous_user_id and getattr(g, "db", None):
			from files.classes import User
			new_user = g.db.get(User, int(new_user_id))
			if new_user:
				ensure_default_follow(g.db, new_user)
				g.db.flush()
		return response

	wrapped._obsession_default_follow = True
	app.view_functions[endpoint] = wrapped


def install_default_following(app, engine):
	"""Backfill current accounts once, then default-follow future signups."""
	if not _is_obsession():
		return

	try:
		backfill_existing_default_follows(engine)
	except Exception as exc:
		# Do not take the site down if an optional migration cannot run at boot.
		print(f"Default-follow backfill skipped: {exc}", flush=True)

	_install_signup_default_follow(app)
