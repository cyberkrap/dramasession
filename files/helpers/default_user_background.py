from functools import wraps

from files.classes import User
from files.helpers.config.const import SITE_NAME


DEFAULT_OBSESSION_BACKGROUND = "/i/backgrounds/pixelart/5.webp"
_INSTALLED = False


def install_default_user_background():
	"""Assign the car background only when a new Obsession user is constructed."""
	global _INSTALLED
	if _INSTALLED or SITE_NAME != "Obsession":
		return

	original_init = User.__init__

	@wraps(original_init)
	def init_with_background(self, **kwargs):
		if not kwargs.get("background"):
			kwargs["background"] = DEFAULT_OBSESSION_BACKGROUND
		original_init(self, **kwargs)

	User.__init__ = init_with_background
	_INSTALLED = True
