import os
import threading
import time

from flask import g, render_template, request
from sqlalchemy import text

from files.__main__ import app, engine, limiter
from files.classes import ModAction
from files.helpers.config.const import DEFAULT_RATELIMIT, PERMS, SITE_NAME
from files.helpers.sanitize import sanitize
from files.routes.wrappers import admin_level_required, get_ID


_TABLE_LOCK = threading.Lock()
_TABLE_READY = False


def _ensure_table():
	global _TABLE_READY
	if _TABLE_READY:
		return
	with _TABLE_LOCK:
		if _TABLE_READY:
			return
		with engine.begin() as connection:
			connection.execute(text("""
				CREATE TABLE IF NOT EXISTS persistent_site_content (
					content_key VARCHAR(255) PRIMARY KEY,
					content TEXT NOT NULL,
					updated_utc BIGINT NOT NULL,
					updated_by VARCHAR(255)
				)
			"""))
		_TABLE_READY = True


def get_site_content(content_key, default=None):
	_ensure_table()
	value = g.db.execute(
		text("SELECT content FROM persistent_site_content WHERE content_key = :content_key"),
		{"content_key": content_key},
	).scalar()
	return default if value is None else value


def set_site_content(content_key, content, updated_by=None):
	_ensure_table()
	g.db.execute(text("""
		INSERT INTO persistent_site_content (content_key, content, updated_utc, updated_by)
		VALUES (:content_key, :content, :updated_utc, :updated_by)
		ON CONFLICT (content_key) DO UPDATE SET
			content = EXCLUDED.content,
			updated_utc = EXCLUDED.updated_utc,
			updated_by = EXCLUDED.updated_by
	"""), {
		"content_key": content_key,
		"content": content,
		"updated_utc": int(time.time()),
		"updated_by": updated_by,
	})


def delete_site_content(content_key):
	_ensure_table()
	g.db.execute(
		text("DELETE FROM persistent_site_content WHERE content_key = :content_key"),
		{"content_key": content_key},
	)


def get_site_content_keys(prefix):
	_ensure_table()
	rows = g.db.execute(
		text("SELECT content_key FROM persistent_site_content WHERE content_key LIKE :prefix"),
		{"prefix": f"{prefix}%"},
	).scalars().all()
	return set(rows)


def _rules_key():
	return f"rules:{SITE_NAME}"


def _default_rules():
	path = os.path.join(app.root_path, "templates", f"rules_{SITE_NAME}.html")
	try:
		with open(path, "r", encoding="utf-8") as stream:
			return stream.read()
	except OSError:
		return ""


def _rules_content_is_malformed(content):
	if SITE_NAME != "Obsession" or not content:
		return False

	# The sidebar editor sanitizes unsupported structural HTML into escaped text.
	# When that happens, tags such as </section>, <footer>, and social-link <a>
	# elements are printed visibly in the sidebar instead of being rendered.
	normalized = content.lower()
	return any(marker in normalized for marker in (
		"&lt;section",
		"&lt;/section",
		"&lt;footer",
		"&lt;/footer",
		"&lt;div",
		"&lt;/div",
		"&lt;a ",
		"&lt;/a",
	))


def _restore_default_rules(default):
	if not default:
		return
	_ensure_table()
	with engine.begin() as connection:
		connection.execute(text("""
			INSERT INTO persistent_site_content (content_key, content, updated_utc, updated_by)
			VALUES (:content_key, :content, :updated_utc, :updated_by)
			ON CONFLICT (content_key) DO UPDATE SET
				content = EXCLUDED.content,
				updated_utc = EXCLUDED.updated_utc,
				updated_by = EXCLUDED.updated_by
		"""), {
			"content_key": _rules_key(),
			"content": default,
			"updated_utc": int(time.time()),
			"updated_by": "automatic sidebar repair",
		})


def persistent_rules():
	default = _default_rules()
	content = get_site_content(_rules_key(), default)
	if _rules_content_is_malformed(content):
		_restore_default_rules(default)
		return default
	return content


@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@admin_level_required(PERMS["EDIT_RULES"])
def persistent_edit_rules_get(v):
	return render_template("admin/edit_rules.html", v=v, rules=persistent_rules())


@limiter.limit("1/second;30/minute;200/hour;1000/day")
@limiter.limit("1/second;30/minute;200/hour;1000/day", key_func=get_ID)
@admin_level_required(PERMS["EDIT_RULES"])
def persistent_edit_rules_post(v):
	rules = sanitize(request.values.get("rules", "").strip(), sidebar=True, showmore=False)
	set_site_content(_rules_key(), rules, v.username)
	g.db.add(ModAction(kind="edit_rules", user_id=v.id))
	return render_template("admin/edit_rules.html", v=v, rules=rules, msg="Rules edited successfully!")


def install_persistent_site_content():
	app.jinja_env.globals["persistent_rules"] = persistent_rules
	app.view_functions["edit_rules_get"] = persistent_edit_rules_get
	app.view_functions["edit_rules_post"] = persistent_edit_rules_post

	if SITE_NAME == "Obsession":
		# The legacy logged-out banner path prefers cached.webp before consulting
		# the persistent removal list. Delete that generated artifact on every
		# worker start so removed repository banners cannot return after a deploy.
		cached_banner = os.path.join(app.root_path, "assets", "images", "Obsession", "cached.webp")
		try:
			if os.path.isfile(cached_banner):
				os.remove(cached_banner)
		except OSError:
			pass

	original_listdir = app.jinja_env.globals.get("listdir", os.listdir)
	if getattr(original_listdir, "_persistent_asset_filter", False):
		return
	def persistent_asset_listdir(path):
		normalized = str(path).replace("\\", "/").rstrip("/")
		if normalized.endswith("files/assets/images/Obsession/banners"):
			from files.helpers.community_assets import active_community_asset_filenames
			return active_community_asset_filenames("banner")
		if normalized.endswith("files/assets/images/Obsession/sidebar"):
			from files.helpers.community_assets import active_community_asset_filenames
			return active_community_asset_filenames("sidebar")
		return original_listdir(path)

	persistent_asset_listdir._persistent_asset_filter = True
	app.jinja_env.globals["listdir"] = persistent_asset_listdir
