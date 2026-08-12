import os
from pathlib import Path
from shutil import copyfile

import fcntl
from flask import abort
from PIL import Image

from files.helpers.support import patron_limit


_LOCK_PATH = "/tmp/obsession-final-ui-fixes.lock"
_ASSET_SUBMISSIONS_PATH = Path("files/routes/asset_submissions.py")
_HAT_SUBMISSIONS_ROOT = Path("/asset_submissions/hats")
_HAT_ORIGINALS_ROOT = _HAT_SUBMISSIONS_ROOT / "original"


def _atomic_write(path: Path, content: str) -> None:
	temp_path = path.with_name(f".{path.name}.{os.getpid()}.tmp")
	temp_path.write_text(content, encoding="utf-8")
	os.replace(temp_path, path)


def preserve_hat_preview(original_path: str, output_path: str, v) -> str:
	"""Preserve valid WebP hats byte-for-byte; convert other formats normally."""
	with Image.open(original_path) as image:
		is_webp = (image.format or "").upper() == "WEBP"

	if is_webp:
		max_bytes = patron_limit(v, "image_audio_mb") * 1024 * 1024
		if os.stat(original_path).st_size > max_bytes:
			abort(413, "Hat image is too large.")
		Path(output_path).parent.mkdir(parents=True, exist_ok=True)
		copyfile(original_path, output_path)
		return output_path

	from files.helpers.media import process_image

	Path(output_path).parent.mkdir(parents=True, exist_ok=True)
	copyfile(original_path, output_path)
	return process_image(output_path, v, resize=100)


def repair_pending_hat_webp_previews() -> None:
	"""Restore pending WebP previews from the pristine archived uploads."""
	if not _HAT_ORIGINALS_ROOT.is_dir():
		return

	for original_path in _HAT_ORIGINALS_ROOT.glob("*.webp"):
		pending_path = _HAT_SUBMISSIONS_ROOT / original_path.name
		if not pending_path.is_file():
			continue
		try:
			copyfile(original_path, pending_path)
		except OSError:
			pass


def patch_hat_submission_source() -> None:
	"""Make pending hat files durable, lossless for WebP, and approval safe to retry."""
	with open(_LOCK_PATH, "w", encoding="utf-8") as lock:
		fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
		source = _ASSET_SUBMISSIONS_PATH.read_text(encoding="utf-8")
		original_source = source

		media_import = "from files.helpers.media import *\n"
		quality_import = media_import + "from files.helpers.hat_submission_fixes import preserve_hat_preview\n"
		if quality_import not in source:
			if media_import not in source:
				raise RuntimeError("Could not locate the media import for hat preservation")
			source = source.replace(media_import, quality_import, 1)

		submit_old = '''\tos.makedirs('/asset_submissions/hats', exist_ok=True)\n\thighquality = f'/asset_submissions/hats/{name}'\n\tfile.save(highquality)\n\n\twith Image.open(highquality) as i:\n\t\tif i.width > 100 or i.height > 130:\n\t\t\tos.remove(highquality)\n\t\t\treturn error("Images must be 100x130")\n\n\t\tif len(list(Iterator(i))) > 1: price = 1000\n\t\telse: price = 500\n\n\tfilename = f'/asset_submissions/hats/{name}.webp'\n\tcopyfile(highquality, filename)\n\tprocess_image(filename, v, resize=100)\n'''
		submit_new = '''\tos.makedirs('/asset_submissions/hats/original', exist_ok=True)\n\thighquality = f'/asset_submissions/hats/{name}'\n\tfile.save(highquality)\n\n\twith Image.open(highquality) as i:\n\t\tif i.width > 100 or i.height > 130:\n\t\t\tos.remove(highquality)\n\t\t\treturn error("Images must be 100x130")\n\n\t\tformat = i.format.lower()\n\t\tif len(list(Iterator(i))) > 1: price = 1000\n\t\telse: price = 500\n\n\tfor ext in IMAGE_FORMATS:\n\t\told_original = f'/asset_submissions/hats/original/{name}.{ext}'\n\t\tif path.isfile(old_original): os.remove(old_original)\n\toriginal_path = f'/asset_submissions/hats/original/{name}.{format}'\n\tos.replace(highquality, original_path)\n\n\tfilename = f'/asset_submissions/hats/{name}.webp'\n\tpreserve_hat_preview(original_path, filename, v)\n'''
		if submit_new not in source:
			if submit_old not in source:
				raise RuntimeError("Could not locate the patched hat submission image block")
			source = source.replace(submit_old, submit_new, 1)

		approve_old = '''\that.name = new_name\n\that.description = description\n\tg.db.add(hat)\n\n\n\tg.db.flush()\n\tauthor = hat.author\n\n\tall_by_author = g.db.query(HatDef).filter_by(author_id=author.id).count()\n\n\tif all_by_author >= 250:\n\t\tbadge_grant(badge_id=166, user=author)\n\telif all_by_author >= 100:\n\t\tbadge_grant(badge_id=165, user=author)\n\telif all_by_author >= 50:\n\t\tbadge_grant(badge_id=164, user=author)\n\telif all_by_author >= 10:\n\t\tbadge_grant(badge_id=163, user=author)\n\n\that_copy = Hat(\n\t\tuser_id=author.id,\n\t\that_id=hat.id\n\t)\n\tg.db.add(hat_copy)\n\n\n\tif v.id != author.id:\n\t\tmsg = f"@{v.username} (a site admin) has approved a hat you made: '{hat.name}'"\n\t\tsend_repeatable_notification(author.id, msg)\n\n\tif v.id != hat.submitter_id and author.id != hat.submitter_id:\n\t\tmsg = f"@{v.username} (a site admin) has approved a hat you submitted: '{hat.name}'"\n\t\tsend_repeatable_notification(hat.submitter_id, msg)\n\n\that.submitter_id = None\n\n\tmove(f"/asset_submissions/hats/{name}.webp", f"files/assets/images/hats/{hat.name}.webp")\n\n\thighquality = f"/asset_submissions/hats/{name}"\n\twith Image.open(highquality) as i:\n\t\tnew_path = f'/asset_submissions/hats/original/{name}.{i.format.lower()}'\n\trename(highquality, new_path)\n\n\treturn {"message": f"'{hat.name}' approved!"}\n'''
		approve_new = '''\texisting_name = g.db.query(HatDef.id).filter(HatDef.name == new_name, HatDef.id != hat.id).first()\n\tif existing_name:\n\t\tabort(409, "A hat with this name already exists!")\n\n\tos.makedirs('/asset_submissions/hats/original', exist_ok=True)\n\tpending_preview = f"/asset_submissions/hats/{name}.webp"\n\tapproved_preview = f"files/assets/images/hats/{new_name}.webp"\n\tlegacy_original = f"/asset_submissions/hats/{name}"\n\n\tarchived_original = None\n\tfor candidate_name in (new_name, name):\n\t\tfor ext in IMAGE_FORMATS:\n\t\t\tcandidate = f'/asset_submissions/hats/original/{candidate_name}.{ext}'\n\t\t\tif path.isfile(candidate):\n\t\t\t\tarchived_original = candidate\n\t\t\t\tbreak\n\t\tif archived_original: break\n\n\tif not archived_original and path.isfile(legacy_original):\n\t\twith Image.open(legacy_original) as i:\n\t\t\tformat = i.format.lower()\n\t\tarchived_original = f'/asset_submissions/hats/original/{new_name}.{format}'\n\t\tos.replace(legacy_original, archived_original)\n\telif archived_original and name != new_name and f'/original/{name}.' in archived_original:\n\t\tformat = archived_original.rsplit('.', 1)[-1]\n\t\trenamed_original = f'/asset_submissions/hats/original/{new_name}.{format}'\n\t\tif archived_original != renamed_original:\n\t\t\tos.replace(archived_original, renamed_original)\n\t\t\tarchived_original = renamed_original\n\n\tif archived_original and archived_original.lower().endswith('.webp'):\n\t\tcopyfile(archived_original, approved_preview)\n\t\ttry: os.remove(pending_preview)\n\t\texcept FileNotFoundError: pass\n\telif path.isfile(pending_preview):\n\t\tos.replace(pending_preview, approved_preview)\n\telif not path.isfile(approved_preview):\n\t\tabort(409, "The pending hat image is missing. Please resubmit the hat.")\n\n\tif not archived_original:\n\t\t# Recover legacy pending hats whose extensionless original was already lost.\n\t\tarchived_original = f'/asset_submissions/hats/original/{new_name}.webp'\n\t\tcopyfile(approved_preview, archived_original)\n\n\that.name = new_name\n\that.description = description\n\tg.db.add(hat)\n\tg.db.flush()\n\tauthor = hat.author\n\n\tall_by_author = g.db.query(HatDef).filter_by(author_id=author.id).count()\n\n\tif all_by_author >= 250:\n\t\tbadge_grant(badge_id=166, user=author)\n\telif all_by_author >= 100:\n\t\tbadge_grant(badge_id=165, user=author)\n\telif all_by_author >= 50:\n\t\tbadge_grant(badge_id=164, user=author)\n\telif all_by_author >= 10:\n\t\tbadge_grant(badge_id=163, user=author)\n\n\tif not g.db.query(Hat.user_id).filter_by(user_id=author.id, hat_id=hat.id).first():\n\t\tg.db.add(Hat(user_id=author.id, hat_id=hat.id))\n\n\tif v.id != author.id:\n\t\tmsg = f"@{v.username} (a site admin) has approved a hat you made: '{hat.name}'"\n\t\tsend_repeatable_notification(author.id, msg)\n\n\tif v.id != hat.submitter_id and author.id != hat.submitter_id:\n\t\tmsg = f"@{v.username} (a site admin) has approved a hat you submitted: '{hat.name}'"\n\t\tsend_repeatable_notification(hat.submitter_id, msg)\n\n\that.submitter_id = None\n\n\treturn {"message": f"'{hat.name}' approved!"}\n'''
		if approve_new not in source:
			if approve_old not in source:
				raise RuntimeError("Could not locate the hat approval block")
			source = source.replace(approve_old, approve_new, 1)

		update_old = '''\tfilename = f"files/assets/images/hats/{name}.webp"\n\tcopyfile(new_path, filename)\n\tprocess_image(filename, v, resize=100)\n\tpurge_files_in_cache([f"https://{SITE}/i/hats/{name}.webp", f"https://{SITE}/assets/images/hats/{name}.webp", f"https://{SITE}/asset_submissions/hats/original/{name}.{format}"])\n'''
		update_new = '''\tfilename = f"files/assets/images/hats/{name}.webp"\n\tpreserve_hat_preview(new_path, filename, v)\n\tpurge_files_in_cache([f"https://{SITE}/i/hats/{name}.webp", f"https://{SITE}/assets/images/hats/{name}.webp", f"https://{SITE}/asset_submissions/hats/original/{name}.{format}"])\n'''
		if update_new not in source:
			if update_old not in source:
				raise RuntimeError("Could not locate the hat image update block")
			source = source.replace(update_old, update_new, 1)

		remove_old = '''\t\tfor candidate in (f"/asset_submissions/{type_name}s/{name}.webp", f"/asset_submissions/{type_name}s/{name}"):\n\t\t\ttry: os.remove(candidate)\n\t\t\texcept FileNotFoundError: pass\n\treturn {"message": f"'{name}' removed!"}\n'''
		remove_new = '''\t\tfor candidate in (f"/asset_submissions/{type_name}s/{name}.webp", f"/asset_submissions/{type_name}s/{name}"):\n\t\t\ttry: os.remove(candidate)\n\t\t\texcept FileNotFoundError: pass\n\t\tif type_name == 'hat':\n\t\t\tfor ext in IMAGE_FORMATS:\n\t\t\t\tcandidate = f'/asset_submissions/hats/original/{name}.{ext}'\n\t\t\t\ttry: os.remove(candidate)\n\t\t\t\texcept FileNotFoundError: pass\n\treturn {"message": f"'{name}' removed!"}\n'''
		if remove_new not in source:
			if remove_old not in source:
				raise RuntimeError("Could not locate the patched hat removal block")
			source = source.replace(remove_old, remove_new, 1)

		if source != original_source:
			_atomic_write(_ASSET_SUBMISSIONS_PATH, source)

	repair_pending_hat_webp_previews()
