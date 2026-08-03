"""Bind Didit enforcement to the persistent admin-site setting."""

import os
import sys

from files.helpers.settings import get_setting


_installed = False

_AGE_VERIFICATION_MODACTIONS = {
	'enable_age_verification_required': {
		"str": 'enabled age verification requirement',
		"icon": 'fa-user-shield',
		"color": 'bg-success',
	},
	'disable_age_verification_required': {
		"str": 'disabled age verification requirement',
		"icon": 'fa-user-shield',
		"color": 'bg-danger',
	},
}


def age_verification_required() -> bool:
	"""Return the live site toggle, with the Railway variable as a fallback."""
	try:
		return bool(get_setting('age_verification_required'))
	except (KeyError, TypeError, OSError, ValueError):
		return os.environ.get('DIDIT_ENABLED', 'false').strip().lower() in {
			'1', 'true', 'yes', 'on'
		}


def _install_modaction_types() -> None:
	from files.helpers.config.modaction_types import (
		MODACTION_TYPES,
		MODACTION_TYPES_FILTERED,
	)
	MODACTION_TYPES.update(_AGE_VERIFICATION_MODACTIONS)
	MODACTION_TYPES_FILTERED.update(_AGE_VERIFICATION_MODACTIONS)


def install_age_verification_toggle() -> None:
	global _installed
	if _installed:
		return

	from files.helpers import age_verification
	age_verification.didit_enabled = age_verification_required

	# files.routes is initialized before this installer because __main__ first
	# imports files.routes.allroutes. The web route imported didit_enabled by
	# value, so patch its module-level reference as well. Without this, chat used
	# the admin toggle while posting and comments kept reading DIDIT_ENABLED.
	web_routes = sys.modules.get('files.routes.age_verification')
	if web_routes is not None:
		web_routes.didit_enabled = age_verification_required

	_install_modaction_types()
	_installed = True
