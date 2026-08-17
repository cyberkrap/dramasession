import os
import re
from pathlib import Path

import fcntl

from files.helpers.config.awards import AWARDS, AWARDS_ENABLED
from files.helpers.config import const as const_config


_LOCK_PATH = "/tmp/obsession-requested-awards.lock"
_AWARDS_ROUTE_PATH = Path("files/routes/awards.py")
_COMMENTS_TEMPLATE_PATH = Path("files/templates/comments.html")
_MACROS_TEMPLATE_PATH = Path("files/templates/util/macros.html")
_HTML_HEAD_PATH = Path("files/templates/util/html_head.html")
_ADMIN_HOME_PATH = Path("files/templates/admin/admin_home.html")
_ADMINTOOLS_PATH = Path("files/templates/userpage/admintools.html")
_CHUDS_PATH = Path("files/templates/chuds.html")
_BOARDS_PATH = Path("files/templates/sub/subs.html")
_AWARD_EFFECTS_PATH = Path("files/assets/js/award_effects.js")


REQUESTED_AWARDS = {
	"furry": {
		"kind": "furry",
		"title": "Furry",
		"description": "Summons a furry to dance on the post or comment.",
		"icon": "fas fa-rabbit",
		"color": "text-orange",
		"price": 200,
		"deflectable": False,
		"cosmetic": True,
		"ghost": True,
		"enabled": True,
	},
	"shit": {
		"kind": "shit",
		"title": "Shit",
		"description": "Makes flies swarm the post and destroys 150 of the recipient's coins. (Note: it won't drop the recipient's coins below 0)",
		"icon": "fas fa-poop",
		"color": "text-black-50",
		"price": 300,
		"deflectable": False,
		"cosmetic": True,
		"ghost": True,
		"enabled": True,
	},
	"truthnuke": {
		"kind": "truthnuke",
		"title": "Truth Nuke",
		"description": "For posts and comments containing facts so brutal they trigger a nuclear explosion.",
		"icon": "fas fa-explosion",
		"color": "text-orange",
		"price": 500,
		"deflectable": False,
		"cosmetic": True,
		"ghost": True,
		"enabled": True,
	},
	"lovebomb": {
		"kind": "lovebomb",
		"title": "Love Bomb",
		"description": "Tell the recipient you love them!",
		"icon": "fas fa-heart",
		"color": "text-red",
		"price": 500,
		"deflectable": False,
		"cosmetic": True,
		"ghost": True,
		"enabled": True,
	},
	"truthnova": {
		"kind": "truthnova",
		"title": "Truth Nova",
		"description": "For posts and comments containing facts so brutal they trigger a supernova explosion.",
		"icon": "fas fa-burst",
		"color": "text-purple",
		"price": 5000,
		"deflectable": False,
		"cosmetic": True,
		"ghost": True,
		"enabled": True,
	},
	"gigaunpin": {
		"kind": "gigaunpin",
		"title": "Giga Unpin",
		"description": "Removes 12 hours from the pin duration of a post or 12 days from the pin duration of a comment.",
		"icon": "fas fa-thumbtack fa-rotate--45",
		"color": "text-black-50",
		"price": 6750,
		"deflectable": False,
		"cosmetic": False,
		"ghost": True,
		"enabled": True,
	},
	"gigapin": {
		"kind": "gigapin",
		"title": "Giga Pin",
		"description": "Pins a post for 12 hours or a comment for 12 days.",
		"icon": "fas fa-thumbtack fa-rotate--45",
		"color": "text-danger",
		"price": 18000,
		"deflectable": False,
		"cosmetic": False,
		"ghost": True,
		"enabled": True,
	},
}


def _atomic_write(path, content):
	temp_path = path.with_name(f".{path.name}.{os.getpid()}.tmp")
	temp_path.write_text(content, encoding="utf-8")
	os.replace(temp_path, path)


def pin_credit(stickied):
	"""Return the public pin credit/source for the generic pin icon tooltip."""
	raw = str(stickied or "").strip()
	if not raw:
		return "(a site admin)"

	lower = raw.lower()
	if lower.endswith(" (giga pin award)"):
		name = raw[: -len(" (giga pin award)")].strip()
		return f"@{name.lstrip('@')} (Giga pin award)"
	if lower.endswith(" (gigapin award)"):
		name = raw[: -len(" (gigapin award)")].strip()
		return f"@{name.lstrip('@')} (Giga pin award)"
	if lower.endswith(" (pin award)"):
		name = raw[: -len(" (pin award)")].strip()
		return f"@{name.lstrip('@')} (Pin award)"

	# Legacy manual pins may have stored `(Mod)`/`(Admin)` in the same column.
	name = re.sub(r"\s+\((?:mod|admin|site admin)\)\s*$", "", raw, flags=re.I).strip()
	return f"@{name.lstrip('@')} (a site admin)"


def install_requested_awards(app):
	"""Restore Shit and add only the seven awards explicitly requested for TOC."""
	for kind, definition in REQUESTED_AWARDS.items():
		award = dict(definition)
		AWARDS[kind] = award
		AWARDS_ENABLED[kind] = award

	# New Pin awards use title-cased source text; old rows are normalized by
	# pin_credit() when rendered, so historical pins do not need a migration.
	const_config.PIN_AWARD_TEXT = " (Pin award)"
	app.jinja_env.globals["pin_credit"] = pin_credit


def patch_requested_awards_pre_batch_source():
	"""Add mechanics that must be present before the 1-30 award batch wrapper runs."""
	with open(_LOCK_PATH, "w", encoding="utf-8") as lock:
		fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
		source = _AWARDS_ROUTE_PATH.read_text(encoding="utf-8")
		if "# toc-requested-awards-mechanics-v1" in source:
			return
		if "# obsession-award-batch-v3" in source:
			raise RuntimeError("Requested award mechanics must be patched before award batching")

		giga_marker = '\telif kind == "agendaposter":\n'
		if giga_marker not in source:
			raise RuntimeError("Could not locate agendaposter award mechanics")
		giga_block = '''\t# toc-requested-awards-mechanics-v1
\telif kind == "gigapin":
\t\tif not FEATURES['PINS']: abort(403)
\t\tif thing.is_banned: abort(403)

\t\tif thing_type == 'comment': add = 3600 * 24 * 12
\t\telse: add = 3600 * 12

\t\tif thing.stickied_utc:
\t\t\tthing.stickied_utc += add
\t\telse:
\t\t\tthing.stickied_utc = int(time.time()) + add

\t\tthing.stickied = f'{v.username} (Giga pin award)'
\t\tg.db.add(thing)
\t\tcache.delete_memoized(frontlist)
\telif kind == "gigaunpin":
\t\tif not thing.stickied_utc: abort(400)
\t\tif thing.author_id == LAWLZ_ID and SITE_NAME == 'rDrama': abort(403, "You can't unpin lawlzposts!")

\t\tif thing_type == 'comment':
\t\t\tt = thing.stickied_utc - 3600 * 24 * 12
\t\telse:
\t\t\tt = thing.stickied_utc - 3600 * 12

\t\tif time.time() > t:
\t\t\tthing.stickied = None
\t\t\tthing.stickied_utc = None
\t\t\tcache.delete_memoized(frontlist)
\t\telse:
\t\t\tthing.stickied_utc = t
\t\tg.db.add(thing)
'''
		source = source.replace(giga_marker, giga_block + giga_marker, 1)

		post_mechanics_marker = '\tif kind == "grinch":\n'
		if post_mechanics_marker not in source:
			raise RuntimeError("Could not locate post-award mechanics marker")
		post_mechanics = '''\t# Shit destroys exactly 150 recipient coins per award and never underflows.
\tif kind == "shit":
\t\tauthor.coins = max(0, int(author.coins or 0) - 150)

\t# Truth Nova's XP reward is fixed, just like its fixed coin payout below.
\tif kind == "truthnova" and v.id != author.id:
\t\tauthor.xp = int(author.xp or 0) + 1375

'''
		source = source.replace(post_mechanics_marker, post_mechanics + post_mechanics_marker, 1)
		_atomic_write(_AWARDS_ROUTE_PATH, source)


def patch_requested_awards_post_batch_source():
	"""Apply fixed payouts and aggregate notifications after batch-v3 rewrites awards.py."""
	with open(_LOCK_PATH, "w", encoding="utf-8") as lock:
		fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
		source = _AWARDS_ROUTE_PATH.read_text(encoding="utf-8")
		if "# toc-requested-awards-post-v1" in source:
			return
		if "# obsession-award-batch-v3" not in source:
			raise RuntimeError("Award batch patch did not run before requested award payout patch")

		payout_pattern = re.compile(
			r"(?m)^(?P<i>\t+)awarded_coins = 250 if kind == 'gold' else \(int\(AWARDS\[kind\]\['price'\] \* COSMETIC_AWARD_COIN_AWARD_PCT\) if AWARDS\[kind\]\['cosmetic'\] and kind != 'shit' else 0\)$"
		)
		match = payout_pattern.search(source)
		if not match:
			raise RuntimeError("Could not locate fixed Gold payout after award batching")
		indent = match.group("i")
		payout_replacement = (
			f"{indent}fixed_award_coin_payouts = {{'gold': 250, 'truthnuke': 250, 'truthnova': 2500}}\n"
			f"{indent}awarded_coins = fixed_award_coin_payouts.get(kind, int(AWARDS[kind]['price'] * COSMETIC_AWARD_COIN_AWARD_PCT) if AWARDS[kind]['cosmetic'] and kind != 'shit' else 0)"
		)
		source = payout_pattern.sub(payout_replacement, source, count=1)

		single_pattern = re.compile(
			r'(?m)^(?P<i>\t+)if awarded_coins > 0:\n(?P=i)\tmsg \+= f" and you have received \{awarded_coins\} coins as a result"\n(?P=i)msg \+= "!"$'
		)
		match = single_pattern.search(source)
		if not match:
			raise RuntimeError("Could not locate single-award payout notification")
		indent = match.group("i")
		single_replacement = (
			f'{indent}if awarded_coins > 0:\n'
			f'{indent}\tmsg += f" and you have received {{awarded_coins}} coins as a result"\n'
			f'{indent}msg += "!"\n'
			f'{indent}if kind == "truthnova":\n'
			f'{indent}\tmsg += "\\n\\nYou have received 1,375 XP!"'
		)
		source = single_pattern.sub(single_replacement, source, count=1)

		batch_old = '''\t\tif kind == "gold":
\t\t\tmsg += f" and you have received {250 * amount} coins as a result"
\t\tmsg += "!"
'''
		batch_new = '''\t\tfixed_batch_coin_payouts = {"gold": 250, "truthnuke": 250, "truthnova": 2500}
\t\tif kind in fixed_batch_coin_payouts:
\t\t\tmsg += f" and you have received {fixed_batch_coin_payouts[kind] * amount} coins as a result"
\t\tmsg += "!"
\t\tif kind == "truthnova":
\t\t\tmsg += f"\\n\\nYou have received {1375 * amount:,} XP!"
'''
		if batch_old not in source:
			raise RuntimeError("Could not locate batch Gold notification")
		source = source.replace(batch_old, batch_new, 1)

		source = source.replace(
			"\t# obsession-award-batch-v3\n",
			"\t# obsession-award-batch-v3\n\t# toc-requested-awards-post-v1\n",
			1,
		)
		_atomic_write(_AWARDS_ROUTE_PATH, source)


def patch_requested_award_templates_source():
	"""Restore Chud language, board creation, generic pin credits, and requested effects."""
	with open(_LOCK_PATH, "w", encoding="utf-8") as lock:
		fcntl.flock(lock.fileno(), fcntl.LOCK_EX)

		# Chud is the public feature name everywhere, not Restrict/Restricted.
		for path, replacements in (
			(_ADMIN_HOME_PATH, (("Restricted Users", "Chudded Users"),)),
			(_CHUDS_PATH, (
				("Restricted Users", "Chudded Users"),
				("Restriction ends", "Chud ends"),
			)),
			(_ADMINTOOLS_PATH, (
				("Remove restriction", "Remove Chud"),
				('value="Restrict user"', 'value="Chud user"'),
			)),
			(_COMMENTS_TEMPLATE_PATH, (("User was restricted for this comment", "User was chudded for this comment"),)),
			(_MACROS_TEMPLATE_PATH, (("User was restricted for this post", "User was chudded for this post"),)),
		):
			source = path.read_text(encoding="utf-8")
			original = source
			for old, new in replacements:
				source = source.replace(old, new)
			if source != original:
				_atomic_write(path, source)

		# The generic pin icon owns the source tooltip for every pin, regardless of
		# whether the source was Pin, Giga Pin, or a manual site-admin action.
		for path, old, new in (
			(_COMMENTS_TEMPLATE_PATH, 'title="Pinned by @{{c.stickied}}"', 'title="Pinned by {{pin_credit(c.stickied)}}"'),
			(_MACROS_TEMPLATE_PATH, 'title="Pinned by @{{p.stickied}}"', 'title="Pinned by {{pin_credit(p.stickied)}}"'),
		):
			source = path.read_text(encoding="utf-8")
			if new not in source:
				if old not in source:
					raise RuntimeError(f"Could not locate generic pin tooltip in {path}")
				source = source.replace(old, new, 1)
				_atomic_write(path, source)

		# Bring the normal board creation control back on the board directory.
		source = _BOARDS_PATH.read_text(encoding="utf-8")
		old_header = '<h5 class="mt-3 mb-1">{{HOLE_NAME|capitalize}} List</h5>\n'
		new_header = '''<div class="d-flex align-items-center justify-content-between mt-3 mb-1">
\t<h5 class="m-0">{{HOLE_NAME|capitalize}} List</h5>
\t{% if v and v.can_create_hole %}<a class="btn btn-primary" href="/create_board"><i class="fas fa-plus mr-1"></i>Create Board</a>{% endif %}
</div>
'''
		if new_header not in source:
			if old_header not in source:
				raise RuntimeError("Could not locate board-list heading")
			source = source.replace(old_header, new_header, 1)
			_atomic_write(_BOARDS_PATH, source)

		# Spark Trail was the wrong interpretation of the legacy Shit key. Disable
		# that renderer; the dedicated requested-effects script renders real flies.
		source = _AWARD_EFFECTS_PATH.read_text(encoding="utf-8")
		original = source
		source = source.replace(
			"const visualKinds = ['confetti', 'fireflies', 'ricardo', 'firework', 'wholesome', 'shit'];",
			"const visualKinds = ['confetti', 'fireflies', 'ricardo', 'firework', 'wholesome'];",
		)
		if source != original:
			_atomic_write(_AWARD_EFFECTS_PATH, source)

		# Load the requested award effects after the existing scoped award effects.
		source = _HTML_HEAD_PATH.read_text(encoding="utf-8")
		original = source
		js_marker = '<script defer src="{{\'js/award_effects.js\' | asset}}"></script>'
		js_line = '<script defer src="{{\'js/award_effects_requested.js\' | asset}}"></script>'
		if js_line not in source:
			if js_marker not in source:
				raise RuntimeError("Could not locate award effects script in html_head")
			source = source.replace(js_marker, js_marker + "\n\t\t" + js_line, 1)

		css_marker = '<link rel="stylesheet" href="{{\'css/award_effects_scoped.css\' | asset}}">'
		css_line = '<link rel="stylesheet" href="{{\'css/award_effects_requested.css\' | asset}}">'
		if css_line not in source:
			if css_marker not in source:
				raise RuntimeError("Could not locate scoped award effects stylesheet in html_head")
			source = source.replace(css_marker, css_marker + "\n\t" + css_line, 1)

		if source != original:
			_atomic_write(_HTML_HEAD_PATH, source)
