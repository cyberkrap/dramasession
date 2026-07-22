import os
from pathlib import Path

import fcntl


_LOCK_PATH = "/tmp/obsession-final-ui-fixes.lock"
_MACROS_PATH = Path("files/templates/util/macros.html")
_ADMIN_PATH = Path("files/routes/admin.py")
_STATIC_PATH = Path("files/routes/static.py")


def _atomic_write(path, content):
	temp_path = path.with_name(f".{path.name}.{os.getpid()}.tmp")
	temp_path.write_text(content, encoding="utf-8")
	os.replace(temp_path, path)


def patch_live_banner_source():
	"""Route the site banner through the active-banner endpoint only."""
	with open(_LOCK_PATH, "w", encoding="utf-8") as lock:
		fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
		source = _MACROS_PATH.read_text(encoding="utf-8")
		old = '''{%- macro live_banner() -%}\n\t{% set path = "files/assets/images/" ~ SITE_NAME %}\n\t{%- if not v and os_path.exists(path ~ "/cached.webp") -%}\n\t\t{{ 'cached.webp' | asset_siteimg -}}\n\t{% elif os_path.exists(path ~ "/banners") and listdir(path ~ "/banners") -%}\n\t\t{{ random_image("assets/images/" ~ SITE_NAME ~ "/banners") -}}\n\t{% else -%}\n\t\t{{ 'banner.webp' | asset_siteimg -}}\n\t{% endif %}\n{%- endmacro -%}\n'''
		new = '''{%- macro live_banner() -%}\n\t{% if SITE_NAME == 'Obsession' %}\n\t\t/site-banner\n\t{% else %}\n\t\t{% set path = "files/assets/images/" ~ SITE_NAME %}\n\t\t{% if os_path.exists(path ~ "/banners") and listdir(path ~ "/banners") %}\n\t\t\t{{ random_image("assets/images/" ~ SITE_NAME ~ "/banners") -}}\n\t\t{% else %}\n\t\t\t{{ 'banner.webp' | asset_siteimg -}}\n\t\t{% endif %}\n\t{% endif %}\n{%- endmacro -%}\n'''
		if old in source:
			source = source.replace(old, new, 1)
		elif new not in source:
			raise RuntimeError("Could not locate the live banner macro")
		_atomic_write(_MACROS_PATH, source)


def patch_badge_gift_note_source():
	"""Keep only the quoted badge gift note, without a redundant heading."""
	with open(_LOCK_PATH, "w", encoding="utf-8") as lock:
		fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
		source = _ADMIN_PATH.read_text(encoding="utf-8")
		old = 'text += f"\\n\\n**Gift message from @{v.username}:**\\n\\n> {gift_message}"'
		new = 'text += f"\\n\\n> {gift_message}"'
		if old in source:
			source = source.replace(old, new, 1)
		elif new not in source:
			raise RuntimeError("Could not locate the badge gift-message notification")
		_atomic_write(_ADMIN_PATH, source)


def patch_marseys_source():
	"""Let the emote directory page render when original uploads are unavailable."""
	with open(_LOCK_PATH, "w", encoding="utf-8") as lock:
		fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
		source = _STATIC_PATH.read_text(encoding="utf-8")
		old = '\toriginal = os.listdir("/asset_submissions/marseys/original")\n'
		new = '''\toriginal_dir = "/asset_submissions/marseys/original"\n\ttry:\n\t\toriginal = set(os.listdir(original_dir))\n\texcept OSError:\n\t\t# Original submission files are optional and may not exist on a fresh\n\t\t# deployment or when the asset-submissions volume is not mounted.\n\t\toriginal = set()\n'''
		if old in source:
			source = source.replace(old, new, 1)
		elif new not in source:
			raise RuntimeError("Could not locate the marseys original-file listing")
		_atomic_write(_STATIC_PATH, source)
