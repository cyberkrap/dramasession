import os
from pathlib import Path

import fcntl


_LOCK_PATH = "/tmp/obsession-runtime-source-fixes.lock"
_COMMENTS_PATH = Path("files/routes/comments.py")
_SETTINGS_PATH = Path("files/routes/settings.py")


def _atomic_write(path, content):
	temp_path = path.with_name(f".{path.name}.{os.getpid()}.tmp")
	temp_path.write_text(content, encoding="utf-8")
	os.replace(temp_path, path)


def patch_comment_attachment_source():
	"""Repair the legacy attachment block before comments.py is imported."""
	with open(_LOCK_PATH, "w", encoding="utf-8") as lock:
		fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
		source = _COMMENTS_PATH.read_text(encoding="utf-8")
		original = source

		upload_marker = '\tif request.files.get("file") and not g.is_tor:\n'
		initialized_marker = '\tfiles = []\n' + upload_marker
		if initialized_marker not in source:
			if upload_marker not in source:
				raise RuntimeError("Could not locate the comment attachment initialization block")
			source = source.replace(upload_marker, initialized_marker, 1)

		broken_start = '\t\tif files:\n'
		body_marker = '\n\tbody = body.strip()'
		start = source.find(broken_start)
		end = source.find(body_marker, start)
		if start != -1:
			if end == -1:
				raise RuntimeError("Could not locate the end of the comment attachment block")
			block = source[start:end]
			fixed_lines = []
			for line in block.splitlines(keepends=True):
				fixed_lines.append(line[1:] if line.startswith('\t') else line)
			source = source[:start] + ''.join(fixed_lines) + source[end:]

		if '\tfiles = []\n' not in source or '\n\tif files:\n' not in source:
			raise RuntimeError("Comment attachment source repair did not produce the expected structure")

		if source != original:
			_atomic_write(_COMMENTS_PATH, source)


def patch_youtube_anthem_source():
	"""Route profile anthem downloads through the resilient downloader helper."""
	with open(_LOCK_PATH, "w", encoding="utf-8") as lock:
		fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
		source = _SETTINGS_PATH.read_text(encoding="utf-8")
		original = source

		import_line = "from files.helpers.youtube_anthem import download_youtube_audio\n"
		if import_line not in source:
			marker = "from files.helpers.useractions import *\n"
			if marker not in source:
				raise RuntimeError("Could not locate the settings helper import block")
			source = source.replace(marker, marker + import_line, 1)

		direct_download = (
			"        with yt_dlp.YoutubeDL(ydl_opts) as ydl:\n"
			"            ydl.download([f\"https://www.youtube.com/watch?v={video_id}\"])\n"
		)
		resilient_download = "        download_youtube_audio(video_id, ydl_opts)\n"
		if resilient_download not in source:
			if direct_download not in source:
				raise RuntimeError("Could not locate the direct YouTube anthem download block")
			source = source.replace(direct_download, resilient_download, 1)

		if import_line not in source or resilient_download not in source:
			raise RuntimeError("YouTube anthem source repair did not produce the expected structure")

		if source != original:
			_atomic_write(_SETTINGS_PATH, source)
