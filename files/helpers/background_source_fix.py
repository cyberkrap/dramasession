import os
from pathlib import Path

import fcntl


_LOCK_PATH = "/tmp/obsession-runtime-source-fixes.lock"
_SETTINGS_PATH = Path("files/routes/settings.py")


def _atomic_write(path, content):
	temp_path = path.with_name(f".{path.name}.{os.getpid()}.tmp")
	temp_path.write_text(content, encoding="utf-8")
	os.replace(temp_path, path)


def patch_background_validation_source():
	"""Allow safe built-in background paths without the legacy 20-char limit."""
	with open(_LOCK_PATH, "w", encoding="utf-8") as lock:
		fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
		source = _SETTINGS_PATH.read_text(encoding="utf-8")
		original = source

		old_block = '''\tbackground = request.values.get("background", v.background)\n\tif background != v.background and background.endswith(".webp") and len(background) <= 20:\n\t\tv.background = '/i/backgrounds/' + request.values.get("background")\n\t\tupdated = True\n'''
		new_block = '''\tbackground = request.values.get("background", v.background)\n\tvalid_background = (\n\t\tisinstance(background, str)\n\t\tand re.fullmatch(\n\t\t\tr"(?:glitter|anime|fantasy|solarpunk|pixelart|movies)/[A-Za-z0-9_-]{1,64}\\.webp",\n\t\t\tbackground,\n\t\t)\n\t)\n\tif background != v.background and valid_background:\n\t\tv.background = '/i/backgrounds/' + background\n\t\tupdated = True\n'''

		if new_block not in source:
			if old_block not in source:
				raise RuntimeError("Could not locate the legacy background validation block")
			source = source.replace(old_block, new_block, 1)

		if new_block not in source:
			raise RuntimeError("Background validation source repair did not produce the expected structure")

		if source != original:
			_atomic_write(_SETTINGS_PATH, source)
