import os
import re
import threading
import time
from urllib.parse import urlparse

import bleach
from flask import abort, g, render_template, request
from sqlalchemy import text

from files.__main__ import app, engine, limiter
from files.classes import ModAction
from files.helpers.config.const import DEFAULT_RATELIMIT, PERMS, SITE_NAME
from files.helpers.sanitize import sanitize
from files.routes.wrappers import admin_level_required, get_ID


_TABLE_LOCK = threading.Lock()
_TABLE_READY = False

_OBSESSION_RULE_TAGS = (
	"section", "footer", "nav", "div", "span",
	"h1", "h2", "h3", "h4", "h5", "h6",
	"p", "strong", "em", "b", "i", "br", "hr",
	"ol", "ul", "li", "a", "img",
)
_SAFE_CLASS_TOKEN = re.compile(r"^[A-Za-z0-9_-]{1,64}$")
_SAFE_ID = re.compile(r"^[A-Za-z][A-Za-z0-9_-]{0,63}$")


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

	# Old editor submissions converted structural HTML into escaped text. Those
	# values must be repaired before they can print literal tags in the sidebar.
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


def _safe_sidebar_url(value):
	value = str(value or "").strip()
	if not value or "\\" in value or any(ord(char) < 32 for char in value):
		return False
	if value.startswith("/"):
		return not value.startswith("//")
	parsed = urlparse(value)
	return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _obsession_rule_attribute_allowed(tag, name, value):
	if name == "class":
		tokens = str(value or "").split()
		return bool(tokens) and len(tokens) <= 12 and all(_SAFE_CLASS_TOKEN.fullmatch(token) for token in tokens)
	if name == "id":
		return bool(_SAFE_ID.fullmatch(str(value or "")))
	if tag == "a" and name == "href":
		return _safe_sidebar_url(value)
	if tag == "img" and name == "src":
		return _safe_sidebar_url(value)
	if tag == "a" and name == "target":
		return value == "_blank"
	if tag == "a" and name == "rel":
		tokens = set(str(value or "").split())
		return bool(tokens) and tokens.issubset({"nofollow", "noopener", "noreferrer"})
	if name in {"title", "alt", "aria-label"}:
		return len(str(value or "")) <= 300
	if name == "aria-hidden":
		return value in {"true", "false"}
	if tag == "img" and name in {"width", "height"}:
		return str(value or "").isdigit() and 0 < int(value) <= 512
	return False


def _sanitize_obsession_rules_html(raw_rules):
	cleaner = bleach.Cleaner(
		tags=_OBSESSION_RULE_TAGS,
		attributes=_obsession_rule_attribute_allowed,
		protocols=("http", "https"),
		strip=True,
		strip_comments=True,
	)
	return cleaner.clean(str(raw_rules or "").strip()).strip()


def _sanitize_rules_submission(raw_rules):
	if SITE_NAME != "Obsession":
		return sanitize(str(raw_rules or "").strip(), sidebar=True, showmore=False)

	rules = _sanitize_obsession_rules_html(raw_rules)
	lowered = rules.lower()
	required_structure = ("<section", "<ol", "<footer")
	if not rules or not all(marker in lowered for marker in required_structure):
		abort(400, "The sidebar must keep its section, rules list, and footer structure.")
	return rules


def _normalize_obsession_sidebar_links(content):
	if SITE_NAME != "Obsession" or not content:
		return content

	content = content.replace(
		"https://discord.gg/SnzRCwkJ3s",
		"https://discord.gg/ymKWdNHSXq",
	)
	content = content.replace(
		"Discord and Reddit chuds will be banned on sight.",
		"WPD and rDrama chuds will be banned on sight.",
	)
	content = content.replace(
		"<h3>Welcome to the Obsession Fan Club</h3>",
		"<h3>Welcome to The Obsession Club</h3>",
	)
	content = content.replace(
		"<p>A fan-run community for discussing <em>Obsession</em>, its cast, characters, production, theories, edits, artwork, and everything surrounding the film.</p>",
		"<p><strong>The Obsession Club (TOC)</strong> is a fan-run community built around <em>Obsession</em> and boards for other movies, with discussions, theories, edits, artwork, memes, and more.</p>",
	)
	content = content.replace(
		"<p><strong>This platform is intended only for adults aged 18 or older.</strong></p>",
		"<p><strong>TOC is intended only for adults aged 18 or older.</strong></p>",
	)
	return "".join(
		line for line in content.splitlines(keepends=True)
		if "watchpeopledie.tv" not in line.lower()
	)


def _restore_default_rules(default):
	if not default:
		return

	# Reuse the request session. Opening another transaction here can wait on a
	# row lock already held by this request and eventually kill the web worker.
	set_site_content(_rules_key(), default, "automatic sidebar repair")


def persistent_rules():
	default = _default_rules()
	content = get_site_content(_rules_key(), default)
	if _rules_content_is_malformed(content):
		_restore_default_rules(default)
		return default

	cleaned = _normalize_obsession_sidebar_links(content)
	if cleaned != content:
		set_site_content(_rules_key(), cleaned, "automatic sidebar link cleanup")
		content = cleaned
	return content


@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@admin_level_required(PERMS["EDIT_RULES"])
def persistent_edit_rules_get(v):
	return render_template("admin/edit_rules.html", v=v, rules=persistent_rules())


@limiter.limit("1/second;30/minute;200/hour;1000/day")
@limiter.limit("1/second;30/minute;200/hour;1000/day", key_func=get_ID)
@admin_level_required(PERMS["EDIT_RULES"])
def persistent_edit_rules_post(v):
	rules = _sanitize_rules_submission(request.values.get("rules", ""))
	rules = _normalize_obsession_sidebar_links(rules)
	set_site_content(_rules_key(), rules, v.username)
	g.db.add(ModAction(kind="edit_rules", user_id=v.id))
	g.db.flush()
	return render_template("admin/edit_rules.html", v=v, rules=rules, msg="Rules edited successfully!")


def install_persistent_site_content():
	app.jinja_env.globals["persistent_rules"] = persistent_rules
	app.view_functions["edit_rules_get"] = persistent_edit_rules_get
	app.view_functions["edit_rules_post"] = persistent_edit_rules_post

	if SITE_NAME == "Obsession":
		# The legacy logged-out banner path prefers cached.webp before consulting
		# the persistent removal list. Delete that artifact on every worker start.
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
