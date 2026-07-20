import json
import os
import time

from flask import g
from sqlalchemy import text

from files.helpers.config.const import HEAD_ADMIN_LEVEL, PERMS


def _enabled(value):
	return value.strip().lower() in {"1", "true", "yes", "on"}


def maybe_bootstrap_admin(user):
	"""Grant the configured first human signup admin access exactly once."""
	if not _enabled(os.environ.get("BOOTSTRAP_ADMIN_ENABLED", "0")):
		return False

	bootstrap_username = os.environ.get("BOOTSTRAP_ADMIN_USERNAME", "").strip()