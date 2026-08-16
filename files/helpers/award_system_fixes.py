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
	"""Normalize the live award catalog and remove obsolete awards without deleting history."""
	# Preserve the legacy internal keys so owned awards and historical rows remain
	# valid while exposing the current catalog names, descriptions, and prices.
	if "wholesome" in AWARDS:
		AWARDS["wholesome"].update({
			"title": "Emoji",
			"description": "Summons a moving emoji on the post or comment.",
			"price": 100,
		})
	if "ricardo" in AWARDS:
		AWARDS["ricardo"].update({
			"title": "Ricardo",
			"description": "Summons Ricardo to dance on the post or comment.",
			"price": 200,
		})

	for kind in RETIRED_AWARDS:
		if kind in AWARDS:
			AWARDS[kind]["enabled"] = False
		AWARDS_ENABLED.pop(kind, None)


def patch_award_batch_source():
	"""Add 1-30 award batching plus Emoji award metadata without ledger spam."""
	with open(_LOCK_PATH, "w", encoding="utf-8") as lock:
		fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
		source = _AWARDS_ROUTE_PATH.read_text(encoding="utf-8")
		if "# obsession-award-batch-v3" in source:
			return

		batch_import = (
			"from files.helpers.award_batch_runtime import "
			"award_batch_ledger_start, collapse_award_batch_ledger\n"
		)
		import_marker = "from files.helpers.support import patron_has\n"
		if batch_import not in source:
			if import_marker not in source:
				raise RuntimeError("Could not locate the awards support import")
			source = source.replace(import_marker, import_marker + batch_import, 1)

		fn_marker = "def award_thing(v, thing_type, id):\n"
		fn_start = source.find(fn_marker)
		if fn_start == -1:
			raise RuntimeError("Could not locate award_thing")
		fn_end = source.find("\n@app.", fn_start)
		if fn_end == -1:
			fn_end = len(source)

		# Route all existing per-award notifications through a local helper. For a
		# quantity batch they are suppressed and replaced by one summary notification.
		fn_source = source[fn_start:fn_end]
		fn_source = fn_source.replace("send_repeatable_notification(", "_award_notify(")
		source = source[:fn_start] + fn_source + source[fn_end:]

		fn_start = source.find(fn_marker)
		kind_line = '\tkind = request.values.get("kind", "").strip()\n'
		kind_at = source.find(kind_line, fn_start)
		if kind_at == -1:
			raise RuntimeError("Could not locate award kind input")
		quantity_block = kind_line + '''\t# obsession-award-batch-v3
\ttry:
\t\tamount = int(request.values.get("amount", 1))
\texcept (TypeError, ValueError):
\t\tabort(400, "Invalid award quantity!")
\tif amount < 1 or amount > 30:
\t\tabort(400, "Award quantity must be between 1 and 30!")

\temoji_name = request.values.get("emoji", "").strip()
\tif kind == "wholesome":
\t\tif not emoji_name:
\t\t\tabort(400, "You need to provide an emoji name!")
\t\tif len(emoji_name) > 80 or not all(char.isalnum() or char in "_-" for char in emoji_name):
\t\t\tabort(400, "Invalid emoji name!")
'''
		source = source[:kind_at] + source[kind_at:].replace(kind_line, quantity_block, 1)

		author_line = "\tauthor = thing.author\n"
		author_at = source.find(author_line, fn_start)
		if author_at == -1:
			raise RuntimeError("Could not locate award target author")
		batch_setup = author_line + '''\t_award_batch_target_author = author
\t_award_batch_ledger_start = award_batch_ledger_start(g.db) if amount > 1 else 0

\tdef _award_notify(user_id, message):
\t\tif amount == 1:
\t\t\tsend_repeatable_notification(user_id, message)
'''
		source = source[:author_at] + source[author_at:].replace(author_line, batch_setup, 1)

		validation_marker = '\tif kind not in AWARDS: abort(404, "This award doesn\'t exist")\n'
		validation_at = source.find(validation_marker, fn_start)
		if validation_at == -1:
			raise RuntimeError("Could not locate award validation")
		upgrade_guard = validation_marker + '''
\t# Permanent profile upgrades should never be sold twice.
\tprofile_upgrade_badges = {
\t\t"checkmark": 150,
\t\t"eye": 83,
\t\t"alt": 84,
\t\t"unblockable": 87,
\t\t"fish": 90,
\t\t"beano": 128,
\t\t"offsitementions": 140,
\t}
\tupgrade_username = "👻" if thing.ghost and v.id != author.id else f"@{author.username}"
\tupgrade_badge_id = profile_upgrade_badges.get(kind)
\tif kind == "checkmark" and author.verified:
\t\tabort(409, f"{upgrade_username} already has this profile upgrade!")
\tif upgrade_badge_id and any(b.badge_id == upgrade_badge_id for b in author.badges):
\t\tabort(409, f"{upgrade_username} already has this profile upgrade!")
\tif amount > 1 and kind in profile_upgrade_badges:
\t\tabort(409, "This profile upgrade can only be given once!")
'''
		source = source[:validation_at] + source[validation_at:].replace(validation_marker, upgrade_guard, 1)

		loop_start = source.find('\taward = g.db.query(AwardRelationship).filter(\n', fn_start)
		if loop_start == -1:
			raise RuntimeError("Could not locate award inventory block")

		assignment_marker = "\tif thing_type == 'post': award.submission_id = thing.id\n\telse: award.comment_id = thing.id\n"
		assignment_at = source.find(assignment_marker, loop_start)
		if assignment_at == -1:
			raise RuntimeError("Could not locate award target assignment")
		emoji_assignment = assignment_marker + '''\tif kind == "wholesome":
\t\t# `kind` is a legacy VARCHAR(20) catalog key. Keep it exactly `wholesome`
\t\t# and persist the selected emoji in its dedicated metadata column.
\t\taward.emoji_name = emoji_name
'''
		source = source[:assignment_at] + source[assignment_at:].replace(assignment_marker, emoji_assignment, 1)

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
		batch_return = '''\tif amount > 1:
\t\tcollapse_award_batch_ledger(
\t\t\tg.db,
\t\t\t_award_batch_ledger_start,
\t\t\trequest.path,
\t\t\tkind=kind,
\t\t\tquantity=amount,
\t\t\tthing_type=thing_type,
\t\t\tthing_id=thing.id,
\t\t\tactor=v,
\t\t\trecipient=_award_batch_target_author,
\t\t)
\t\tif v.id != _award_batch_target_author.id and kind != "spider":
\t\t\tmsg = f"@{v.username} has given your [{thing_type}]({thing.shortlink}) the {amount} {AWARDS[kind]['title']} Awards!"
\t\t\tif note:
\t\t\t\tmsg += f"\\n\\n> {note}"
\t\t\tsend_repeatable_notification(_award_batch_target_author.id, msg)

\tif amount == 1:
\t\tmessage = f"{AWARDS[kind]['title']} award given to {thing_type} successfully!"
\telse:
\t\tmessage = f"{amount}× {AWARDS[kind]['title']} awards given to {thing_type} successfully!"
\treturn {"message": message}
'''
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
