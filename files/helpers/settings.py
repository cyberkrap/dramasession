import fcntl
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
_SETTINGS_MTIME_NS = -1


def _open_settings_file():
	directory = os.path.dirname(os.path.abspath(SETTINGS_FILENAME))
	if directory:
		os.makedirs(directory, exist_ok=True)
	fd = os.open(SETTINGS_FILENAME, os.O_RDWR | os.O_CREAT, 0o600)
	return os.fdopen(fd, 'r+', encoding='utf_8')


def _normalize_settings(value) -> dict[str, bool]:
	settings = dict(_DEFAULT_SETTINGS)
	if isinstance(value, dict):
		for key, enabled in value.items():
			if key in settings and isinstance(enabled, bool):
				settings[key] = enabled
	return settings


def _read_locked(handle) -> dict[str, bool]:
	handle.seek(0)
	raw = handle.read().strip()
	if not raw:
		return dict(_DEFAULT_SETTINGS)
	try:
		return _normalize_settings(json.loads(raw))
	except (TypeError, ValueError, json.JSONDecodeError):
		# Keep the last known state if an old process was interrupted while
		# writing during a rolling deployment. The next successful toggle repairs
		# the file instead of silently resetting every switch.
		return _normalize_settings(_SETTINGS)


def _write_locked(handle, settings: dict[str, bool]) -> None:
	handle.seek(0)
	handle.truncate()
	json.dump(settings, handle, separators=(',', ':'))
	handle.flush()
	os.fsync(handle.fileno())


def _set_local_state(settings: dict[str, bool], handle=None) -> None:
	global _SETTINGS, _SETTINGS_MTIME_NS
	_SETTINGS = dict(settings)
	try:
		_SETTINGS_MTIME_NS = (
			os.fstat(handle.fileno()).st_mtime_ns
			if handle is not None
			else os.stat(SETTINGS_FILENAME).st_mtime_ns
		)
	except (FileNotFoundError, OSError):
		_SETTINGS_MTIME_NS = -1


def _refresh_if_changed() -> None:
	try:
		mtime_ns = os.stat(SETTINGS_FILENAME).st_mtime_ns
	except (FileNotFoundError, OSError):
		reload_settings()
		return
	if mtime_ns != _SETTINGS_MTIME_NS:
		reload_settings()


def get_setting(setting: str):
	if not setting or not isinstance(setting, str):
		raise TypeError()
	_refresh_if_changed()
	return _SETTINGS[setting]


def get_settings() -> dict[str, bool]:
	_refresh_if_changed()
	return dict(_SETTINGS)


def toggle_setting(setting: str):
	if setting not in _DEFAULT_SETTINGS:
		raise KeyError(setting)

	with _open_settings_file() as handle:
		fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
		settings = _read_locked(handle)
		settings[setting] = not settings[setting]
		_write_locked(handle, settings)
		_set_local_state(settings, handle)
		fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
		return settings[setting]


def reload_settings():
	with _open_settings_file() as handle:
		fcntl.flock(handle.fileno(), fcntl.LOCK_SH)
		settings = _read_locked(handle)
		_set_local_state(settings, handle)
		fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def _save_settings():
	with _open_settings_file() as handle:
		fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
		settings = _normalize_settings(_SETTINGS)
		_write_locked(handle, settings)
		_set_local_state(settings, handle)
		fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def start_watching_settings():
	gevent.spawn(_settings_watcher, SETTINGS_FILENAME)


def _settings_watcher(filename):
	fd = inotify.init()
	try:
		inotify.add_watch(fd, filename, inotify.IN_CLOSE_WRITE)
		while True:
			for _event in inotify.get_events(fd, 0):
				try:
					reload_settings()
				except Exception:
					# A request-side stat check will retry. Never let the watcher die and
					# leave one worker permanently stuck on an old setting.
					pass
				break
			gevent.sleep(0.5)
	finally:
		os.close(fd)
