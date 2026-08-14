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

	The hook can run before the request-scoped ``g.db`` session exists, so it
	uses an independent engine transaction. Any database problem is treated as a
	best-effort retry condition and can never fail the page request.
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
				existing_ids = {
					badge_id
					for badge_id in badge_ids
					if connection.execute(
						text("SELECT 1 FROM badge_defs WHERE id = :badge_id"),
						{"badge_id": badge_id},
					).scalar()
				}

				if existing_ids != set(badge_ids):
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
			return

		_SYNC_COMPLETE = True


def install_patron_branding():
	global _INSTALLED
	if _INSTALLED:
		return

	# Raw ``User.patron`` can outlive the paid entitlement. Publish the canonical
	# active state with popover data so generic username renderers can remove a
	# stale patron plate before applying a username effect.
	original_json_popover = User.json_popover
	def json_popover_with_patron_state(user, viewer):
		data = dict(original_json_popover(user, viewer))
		data["active_patron"] = bool(user.active_patron)
		return data

	User.json_popover = json_popover_with_patron_state
	User.patron_tooltip = property(_patron_tooltip)
	app.before_request(_sync_contribution_badge_definitions)
	_INSTALLED = True
