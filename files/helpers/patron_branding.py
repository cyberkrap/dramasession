"""Canonical support-tier branding and live contribution badge synchronization."""

import threading

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from files.__main__ import app, engine
from files.classes import User
from files.helpers.config.const import SITE_NAME
from files.helpers.support import (
	CONTRIBUTION_BADGE_DESCRIPTIONS,
	CONTRIBUTION_BADGE_NAMES,
	SUPPORT_TIER_BY_LEVEL,
)


_SYNC_LOCK = threading.Lock()
_SYNC_COMPLETE = False
_INSTALLED = False


def _patron_tooltip(user):
	tier = SUPPORT_TIER_BY_LEVEL.get(user.active_patron)
	if not tier:
		return ""
	description = CONTRIBUTION_BADGE_DESCRIPTIONS.get(tier["badge"], "")
	return f'{tier["name"]} — {description}' if description else tier["name"]


def _sync_contribution_badge_definitions():
	"""Synchronize badge branding without depending on request-session setup.

	This hook can run before the application's request-scoped ``g.db`` session is
	created, so it uses the engine directly. Database availability or migration
	timing must never turn an otherwise valid page request into a 500 response.
	"""
	global _SYNC_COMPLETE
	if _SYNC_COMPLETE or SITE_NAME != "Obsession":
		return

	with _SYNC_LOCK:
		if _SYNC_COMPLETE:
			return

		badge_ids = tuple(CONTRIBUTION_BADGE_NAMES)
		try:
			with engine.begin() as connection:
				existing_ids = set(connection.execute(
					text("SELECT id FROM badge_defs WHERE id IN :badge_ids")
					.bindparams(badge_ids=badge_ids),
				).scalars().all())

				if existing_ids != set(badge_ids):
					# Startup migrations may still be finishing. Leave the flag unset so a
					# later request retries, but never fail the current request.
					return

				for badge_id in badge_ids:
					connection.execute(text("""
						UPDATE badge_defs
						SET name = :name, description = :description
						WHERE id = :badge_id
					"""), {
						"badge_id": badge_id,
						"name": CONTRIBUTION_BADGE_NAMES[badge_id],
						"description": CONTRIBUTION_BADGE_DESCRIPTIONS[badge_id],
					})
		except SQLAlchemyError:
			# Branding synchronization is best-effort and must never break page loads.
			return

		_SYNC_COMPLETE = True


def install_patron_branding():
	global _INSTALLED
	if _INSTALLED:
		return
	User.patron_tooltip = property(_patron_tooltip)
	app.before_request(_sync_contribution_badge_definitions)
	_INSTALLED = True
