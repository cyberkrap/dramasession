import json
import os
import time

from flask import g
from sqlalchemy import text

from files.classes.mod_logs import ModAction
from files.helpers.config.const import HEAD_ADMIN_LEVEL, PERMS


def _enabled(value):
	return value.strip().lower() in {"1", "true", "yes", "on"}


def maybe_bootstrap_admin(user):
	"""Grant the configured first human signup admin access exactly once."""
	if not _enabled(os.environ.get("BOOTSTRAP_ADMIN_ENABLED", "0")):
		return False

	bootstrap_username = os.environ.get("BOOTSTRAP_ADMIN_USERNAME", "").strip()
	if not bootstrap_username or user.username.casefold() != bootstrap_username.casefold():
		return False

	g.db.flush()
	g.db.execute(text("""
		CREATE TABLE IF NOT EXISTS public.production_bootstrap (
			bootstrap_key VARCHAR(80) PRIMARY KEY,
			completed_utc INTEGER NOT NULL,
			user_id INTEGER NOT NULL REFERENCES public.users(id)
		)
	"""))
	inserted = g.db.execute(text("""
		INSERT INTO public.production_bootstrap (bootstrap_key, completed_utc, user_id)
		VALUES ('head_admin', :completed_utc, :user_id)
		ON CONFLICT (bootstrap_key) DO NOTHING
		RETURNING bootstrap_key
	"""), {
		"completed_utc": int(time.time()),
		"user_id": user.id,
	}).scalar()
	if not inserted:
		return False

	user.admin_level = HEAD_ADMIN_LEVEL
	user.admin_permissions = json.dumps(sorted(PERMS.keys()))
	user.unlimited_spending = True
	g.db.add(ModAction(
		kind="bootstrap_admin",
		user_id=user.id,
		target_user_id=user.id,
		_note="Disable BOOTSTRAP_ADMIN_ENABLED after this account is confirmed.",
	))
	print("Production bootstrap succeeded; disable BOOTSTRAP_ADMIN_ENABLED now.", flush=True)
	return True
