"""Bind Didit enforcement to the persistent admin-site setting."""

import os

from files.helpers.settings import get_setting


_installed = False


def age_verification_required() -> bool:
	"""Return the live site toggle, with the Railway variable as a fallback."""
	try:
		return bool(get_setting('age_verification_required'))
	except (KeyError, TypeError):
		return os.environ.get('DIDIT_ENABLED', 'false').strip().lower() in {
			'1', 'true', 'yes', 'on'
		}


def install_age_verification_toggle() -> None:
	global _installed
	if _installed:
		return

	# Patch before web or chat routes import didit_enabled. Imported route
	# references and the chat gate then use the same live setting function.
	from files.helpers import age_verification
	age_verification.didit_enabled = age_verification_required
	_installed = True
