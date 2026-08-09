import os
from pathlib import Path

import fcntl

from files.helpers.config.awards import AWARDS, AWARDS_ENABLED


_LOCK_PATH = "/tmp/obsession-runtime-source-fixes.lock"
_AWARDS_ROUTE_PATH = Path("files/routes/awards.py")
_COMMENTS_TEMPLATE_PATH = Path("files/templates/comments.html")
_MACROS_TEMPLATE_PATH = Path("files/templates/util/macros.html")
_HTML_HEAD_PATH = Path("files/templates/util/html_head.html")

RETIRED_AWARDS = {"train", "scooter", "marsey", "pause", "unpausable"}


def _atomic_write(path, content):
	temp_path = path.with_name(f".{path.name}.{os.getpid()}.tmp")
	temp_path.write_text(content, encoding="utf-8")
	os.replace(temp_path, path)


def disable_retired_awards():
	"""Remove obsolete awards from every live catalog without deleting history."""
	for kind in RETIRED_AWARDS:
		if kind in AWARDS:
			AWARDS[kind]["enabled"] = False
		AWARDS_ENABLED.pop(kind, None)


def patch_award_batch_source():
	"""Add atomic-ish 1-30 award batching and permanent-upgrade duplicate guards."""
	with open(_LOCK_PATH, "w", encoding="utf-8") as lock:
		fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
		source = _AWARDS_ROUTE_PATH.read_text(encoding="utf-8")
		if "# obsession-award-batch-v2" in source:
			return

		fn_marker = "def award_thing(v, thing_type, id):\n"
		fn_start = source.find(fn_marker)
		if fn_start == -1:
			raise RuntimeError("Could not locate award_thing")

		kind_line = '\tkind = request.values.get("kind", "").strip()\n'
		kind_at = source.find(kind_line, fn_start)
		if kind_at == -1:
			raise RuntimeError("Could not locate award kind input")
		quantity_block = kind_line + '''\t# obsession-award-batch-v2\n\ttry:\n\t\tamount = int(request.values.get("amount", 1))\n\texcept (TypeError, ValueError):\n\t\tabort(400, "Invalid award quantity!")\n\tif amount < 1 or amount > 30:\n\t\tabort(400, "Award quantity must be between 1 and 30!")\n'''
		source = source[:kind_at] + source[kind_at:].replace(kind_line, quantity_block, 1)

		validation_marker = '\tif kind not in AWARDS: abort(404, "This award doesn\'t exist")\n'
		validation_at = source.find(validation_marker, fn_start)
		if validation_at == -1:
			raise RuntimeError("Could not locate award validation")
		upgrade_guard = validation_marker + '''\n\t# Permanent profile upgrades should never be sold twice.\n\tprofile_upgrade_badges = {\n\t\t"checkmark": 150,\n\t\t"eye": 83,\n\t\t"alt": 84,\n\t\t"unblockable": 87,\n\t\t"fish": 90,\n\t\t"beano": 128,\n\t\t"offsitementions": 140,\n\t}\n\tupgrade_username = "👻" if thing.ghost and v.id != author.id else f"@{author.username}"\n\tupgrade_badge_id = profile_upgrade_badges.get(kind)\n\tif kind == "checkmark" and author.verified:\n\t\tabort(409, f"{upgrade_username} already has this profile upgrade!")\n\tif upgrade_badge_id and any(b.badge_id == upgrade_badge_id for b in author.badges):\n\t\tabort(409, f"{upgrade_username} already has this profile upgrade!")\n\tif amount > 1 and kind in profile_upgrade_badges:\n\t\tabort(409, "This profile upgrade can only be given once!")\n'''
		source = source[:validation_at] + source[validation_at:].replace(validation_marker, upgrade_guard, 1)

		loop_start = source.find('\taward = g.db.query(AwardRelationship).filter(\n', fn_start)
		if loop_start == -1:
			raise RuntimeError("Could not locate award inventory block")

		final_return = '\treturn {"message": f"{AWARDS[kind][\'title\']} award given to {thing_type} successfully!"}\n'
		fn_end = source.find('\n@app.', loop_start)
		if fn_end == -1:
			fn_end = len(source)
		final_return_at = source.rfind(final_return, loop_start, fn_end)
		if final_return_at == -1:
			raise RuntimeError("Could not locate final award response")

		loop_body = source[loop_start:final_return_at]
		early_return = '\t\t\treturn {"message": f"{AWARDS[kind][\'title\']} award given to {thing_type} successfully!"}\n'
		if early_return in loop_body:
			loop_body = loop_body.replace(early_return, '\t\t\tcontinue\n', 1)

		indented_body = ''.join('\t' + line if line.strip() else line for line in loop_body.splitlines(keepends=True))
		batch_loop = '\tfor _award_batch_index in range(amount):\n\t\tauthor = thing.author\n' + indented_body
		batch_return = '''\tif amount == 1:\n\t\tmessage = f"{AWARDS[kind]['title']} award given to {thing_type} successfully!"\n\telse:\n\t\tmessage = f"{amount}× {AWARDS[kind]['title']} awards given to {thing_type} successfully!"\n\treturn {"message": message}\n'''
		source = source[:loop_start] + batch_loop + batch_return + source[final_return_at + len(final_return):]

		_atomic_write(_AWARDS_ROUTE_PATH, source)


def patch_award_templates_source():
	"""Install scoped effect assets and rDrama-style award timestamp tooltips."""
	with open(_LOCK_PATH, "w", encoding="utf-8") as lock:
		fcntl.flock(lock.fileno(), fcntl.LOCK_EX)

		for path in (_COMMENTS_TEMPLATE_PATH, _MACROS_TEMPLATE_PATH):
			source = path.read_text(encoding="utf-8")
			original = source
			old = 'title="{{a.title}} Award given by @{{a.user.username}}"'
			new = 'title="{{a.title}} Award given by @{{a.user.username}}{% if a.kind != \'deflector\' and a.awarded_date %} on {{a.awarded_date}}{% endif %}"'
			if new not in source:
				if old not in source:
					raise RuntimeError(f"Could not locate award tooltip in {path}")
				source = source.replace(old, new)
			if source != original:
				_atomic_write(path, source)

		source = _HTML_HEAD_PATH.read_text(encoding="utf-8")
		original = source
		js_line = "\t\t<script defer src=\"{{'js/award_effects.js' | asset}}\"></script>\n"
		js_marker = "\t\t<script defer src=\"{{'js/message_inline_images.js' | asset}}\"></script>\n"
		if js_line not in source:
			if js_marker not in source:
				raise RuntimeError("Could not locate Obsession JS asset block")
			source = source.replace(js_marker, js_marker + js_line, 1)

		css_line = "\t<link rel=\"stylesheet\" href=\"{{'css/award_effects_scoped.css' | asset}}\">\n"
		css_marker = "\t<link rel=\"stylesheet\" href=\"{{'css/awards.css' | asset}}\">\n"
		if css_line not in source:
			if css_marker not in source:
				raise RuntimeError("Could not locate award stylesheet block")
			source = source.replace(css_marker, css_marker + css_line, 1)

		if source != original:
			_atomic_write(_HTML_HEAD_PATH, source)
