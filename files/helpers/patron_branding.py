"""Canonical support-tier branding and live contribution badge synchronization."""

import threading

from flask import g

from files.__main__ import app
from files.classes import BadgeDef, User
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
	global _SYNC_COMPLETE
	if _SYNC_COMPLETE or SITE_NAME != "Obsession":
		return

	with _SYNC_LOCK:
		if _SYNC_COMPLETE:
			return

		badge_ids = tuple(CONTRIBUTION_BADGE_NAMES)
		definitions = {
			badge.id: badge
			for badge in g.db.query(BadgeDef).filter(BadgeDef.id.in_(badge_ids)).all()
		}
		missing = [badge_id for badge_id in badge_ids if badge_id not in definitions]
		if missing:
			# Do not mark the synchronization complete until the expected definitions
			# exist. A later request can retry after startup migrations finish.
			return

		changed = False
		for badge_id, badge in definitions.items():
			name = CONTRIBUTION_BADGE_NAMES[badge_id]
			description = CONTRIBUTION_BADGE_DESCRIPTIONS[badge_id]
			if badge.name != name:
				badge.name = name
				changed = True
			if badge.description != description:
				badge.description = description
				changed = True
			if changed:
				g.db.add(badge)

		if changed:
			g.db.flush()
		_SYNC_COMPLETE = True


def install_patron_branding():
	global _INSTALLED
	if _INSTALLED:
		return
	User.patron_tooltip = property(_patron_tooltip)
	app.before_request(_sync_contribution_badge_definitions)
	_INSTALLED = True
