from functools import wraps
from pathlib import Path
import time

from sqlalchemy import text

from files.classes import User
from files.helpers.config.const import SITE_NAME


LEGACY_DEFAULT_OBSESSION_BACKGROUND = "/i/backgrounds/pixelart/5.webp"
DEFAULT_OBSESSION_BACKGROUND = "/i/backgrounds/movies/obsession.webp"
DEFAULT_OBSESSION_BACKGROUND_FILE = (
	Path(__file__).resolve().parents[1]
	/ "assets"
	/ "images"
	/ "backgrounds"
	/ "movies"
	/ "obsession.webp"
)
_BACKGROUND_MIGRATION_KEY = "default_background:obsession_movies_v1"
_INSTALLED = False


def _active_default_background():
	if DEFAULT_OBSESSION_BACKGROUND_FILE.is_file():
		return DEFAULT_OBSESSION_BACKGROUND
	return LEGACY_DEFAULT_OBSESSION_BACKGROUND


def _migrate_legacy_default_background():
	if not DEFAULT_OBSESSION_BACKGROUND_FILE.is_file():
		return

	# Use the existing persistent site-content table as an idempotent migration
	# marker so users who deliberately choose the old car later are not changed
	# again on every deployment.
	from files.__main__ import engine

	with engine.begin() as connection:
		connection.execute(text("""
			CREATE TABLE IF NOT EXISTS persistent_site_content (
				content_key VARCHAR(255) PRIMARY KEY,
				content TEXT NOT NULL,
				updated_utc BIGINT NOT NULL,
				updated_by VARCHAR(255)
			)
		"""))
		already_migrated = connection.execute(
			text("SELECT 1 FROM persistent_site_content WHERE content_key = :key"),
			{"key": _BACKGROUND_MIGRATION_KEY},
		).scalar()
		if already_migrated:
			return

		connection.execute(
			User.__table__.update()
			.where(User.background == LEGACY_DEFAULT_OBSESSION_BACKGROUND)
			.values(background=DEFAULT_OBSESSION_BACKGROUND)
		)
		connection.execute(text("""
			INSERT INTO persistent_site_content (content_key, content, updated_utc, updated_by)
			VALUES (:key, :content, :updated_utc, :updated_by)
			ON CONFLICT (content_key) DO NOTHING
		"""), {
			"key": _BACKGROUND_MIGRATION_KEY,
			"content": DEFAULT_OBSESSION_BACKGROUND,
			"updated_utc": int(time.time()),
			"updated_by": "automatic default background migration",
		})


def install_default_user_background():
	"""Use the Obsession movie background as the default once its asset exists."""
	global _INSTALLED
	if _INSTALLED or SITE_NAME != "Obsession":
		return

	default_background = _active_default_background()
	original_init = User.__init__

	@wraps(original_init)
	def init_with_background(self, **kwargs):
		if not kwargs.get("background"):
			kwargs["background"] = default_background
		original_init(self, **kwargs)

	User.__init__ = init_with_background
	_migrate_legacy_default_background()
	_INSTALLED = True
