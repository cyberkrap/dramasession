import json
import os

import gevent
import gevent_inotifyx as inotify

from files.helpers.config.const import SETTINGS_FILENAME


def _env_bool(name: str, default: bool = False) -> bool:
	value = os.environ.get(name)
	if value is None:
		return default
	return value.strip().lower() in {'1', 'true', 'yes', 'on'}


_DEFAULT_SETTINGS = {
	"bots": True,
	"fart_mode": False,
	"read_only_mode": False,
	"signups": True,
	"login_required": False,
	"under_siege": False,
	"dm_images": True,
	"age_verification_required": _env_bool("DIDIT_ENABLED", False),
}

_SETTINGS = dict(_DEFAULT_SETTINGS)


def get_setting(setting: str):
	if not setting or not isinstance(setting, str):
		raise TypeError()
	return _SETTINGS[setting]


def get_settings() -> dict[str, bool]:
	return _SETTINGS


def toggle_setting(setting: str):
	val = not _SETTINGS[setting]
	_SETTINGS[setting] = val
	_save_settings()
	return val


def reload_settings():
	global _SETTINGS
	loaded = {}
	if os.path.isfile(SETTINGS_FILENAME):
		with open(SETTINGS_FILENAME, 'r', encoding='utf_8') as f:
			value = json.load(f)
			if isinstance(value, dict):
				loaded = value

	# Merge new settings into existing installations instead of replacing the
	# defaults wholesale. This keeps newly introduced toggles available after a
	# deployment even when the persisted settings file predates them.
	_SETTINGS = dict(_DEFAULT_SETTINGS)
	for key, value in loaded.items():
		if key in _DEFAULT_SETTINGS and isinstance(value, bool):
			_SETTINGS[key] = value

	if loaded != _SETTINGS:
		_save_settings()


def _save_settings():
	with open(SETTINGS_FILENAME, "w", encoding='utf_8') as f:
		json.dump(_SETTINGS, f)


def start_watching_settings():
	gevent.spawn(_settings_watcher, SETTINGS_FILENAME)


def _settings_watcher(filename):
	fd = inotify.init()
	try:
		inotify.add_watch(fd, filename, inotify.IN_CLOSE_WRITE)
		while True:
			for event in inotify.get_events(fd, 0):
				reload_settings()
				break
			gevent.sleep(0.5)
	finally:
		os.close(fd)
