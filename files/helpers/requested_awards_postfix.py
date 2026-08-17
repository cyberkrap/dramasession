import os
import re
from pathlib import Path

import fcntl

from files.helpers.config.awards import AWARDS, AWARDS_ENABLED


_LOCK_PATH = "/tmp/obsession-requested-awards.lock"
_AWARDS_ROUTE_PATH = Path("files/routes/awards.py")
_HTML_HEAD_PATH = Path("files/templates/util/html_head.html")
_LEGACY_EFFECTS_JS_PATH = Path("files/assets/js/award_effects.js")

_REQUESTED_ICON_CLASSES = {
	"furry": "toc-award-glyph toc-award-glyph-furry",
	"truthnuke": "toc-award-glyph toc-award-glyph-truthnuke",
	"lovebomb": "toc-award-glyph toc-award-glyph-lovebomb",
	"truthnova": "toc-award-glyph toc-award-glyph-truthnova",
}


def _atomic_write(path, content):
	temp_path = path.with_name(f".{path.name}.{os.getpid()}.tmp")
	temp_path.write_text(content, encoding="utf-8")
	os.replace(temp_path, path)


def _install_requested_award_icons():
	"""Use TOC-owned SVG glyphs instead of Font Awesome names missing from this build."""
	for kind, icon_class in _REQUESTED_ICON_CLASSES.items():
		for catalog in (AWARDS, AWARDS_ENABLED):
			award = catalog.get(kind)
			if not award:
				continue
			award["icon"] = icon_class
			award["color"] = ""


def _ensure_requested_award_effect_assets():
	"""Make requested award effects load even if later legacy template patching aborts."""
	_install_requested_award_icons()

	head = _HTML_HEAD_PATH.read_text(encoding="utf-8")
	original_head = head

	js_marker = "\t\t<script defer src=\"{{'js/message_inline_images.js' | asset}}\"></script>\n"
	js_lines = (
		"\t\t<script defer src=\"{{'js/award_effects.js' | asset}}\"></script>\n",
		"\t\t<script defer src=\"{{'js/award_effects_requested.js' | asset}}\"></script>\n",
	)
	missing_js = "".join(line for line in js_lines if line not in head)
	if missing_js:
		if js_marker not in head:
			raise RuntimeError("Could not locate Obsession JS asset block for requested awards")
		head = head.replace(js_marker, js_marker + missing_js, 1)

	css_marker = "\t<link rel=\"stylesheet\" href=\"{{'css/awards.css' | asset}}\">\n"
	css_lines = (
		"\t<link rel=\"stylesheet\" href=\"{{'css/award_effects_scoped.css' | asset}}\">\n",
		"\t<link rel=\"stylesheet\" href=\"{{'css/award_effects_requested.css' | asset}}\">\n",
	)
	missing_css = "".join(line for line in css_lines if line not in head)
	if missing_css:
		if css_marker not in head:
			raise RuntimeError("Could not locate award stylesheet block for requested awards")
		head = head.replace(css_marker, css_marker + missing_css, 1)

	if head != original_head:
		_atomic_write(_HTML_HEAD_PATH, head)

	# `shit` used to mean Spark Trail in TOC's legacy effect renderer. Shit is
	# now the real fly-swarm award and is owned exclusively by the requested
	# award renderer, so never let the old renderer add sparks as a second effect.
	legacy = _LEGACY_EFFECTS_JS_PATH.read_text(encoding="utf-8")
	legacy_old = "const visualKinds = ['confetti', 'fireflies', 'ricardo', 'firework', 'wholesome', 'shit'];"
	legacy_new = "const visualKinds = ['confetti', 'fireflies', 'ricardo', 'firework', 'wholesome'];"
	if legacy_old in legacy:
		_atomic_write(_LEGACY_EFFECTS_JS_PATH, legacy.replace(legacy_old, legacy_new, 1))


def patch_requested_awards_post_batch_source_v2():
	"""Patch fixed Truth payouts/XP and rDrama-style Shit loss notifications."""
	with open(_LOCK_PATH, "w", encoding="utf-8") as lock:
		fcntl.flock(lock.fileno(), fcntl.LOCK_EX)

		# Do this first. If some legacy source rewrite later stops matching, the
		# visual award JS/CSS and custom award glyphs still get installed.
		_ensure_requested_award_effect_assets()

		source = _AWARDS_ROUTE_PATH.read_text(encoding="utf-8")
		if "# toc-requested-awards-post-v2" in source:
			return
		if "# obsession-award-batch-v3" not in source:
			raise RuntimeError("Award batch patch did not run before requested award payout patch")

		# Preserve the target's starting balance for both single and batch Shit
		# notifications so the reported destruction matches the floor-at-zero math.
		batch_setup_old = (
			"\t_award_batch_target_author = author\n"
			"\t_award_batch_ledger_start = award_batch_ledger_start(g.db) if amount > 1 else 0\n"
		)
		batch_setup_new = (
			"\t_award_batch_target_author = author\n"
			"\t_award_batch_target_coins_before = int(author.coins or 0)\n"
			"\t_award_batch_ledger_start = award_batch_ledger_start(g.db) if amount > 1 else 0\n"
		)
		if batch_setup_new not in source:
			if batch_setup_old not in source:
				raise RuntimeError("Could not locate award batch target setup")
			source = source.replace(batch_setup_old, batch_setup_new, 1)

		payout_pattern = re.compile(
			r"(?m)^(?P<i>\t+)awarded_coins = 250 if kind == 'gold' else \(int\(AWARDS\[kind\]\['price'\] \* COSMETIC_AWARD_COIN_AWARD_PCT\) if AWARDS\[kind\]\['cosmetic'\] and kind != 'shit' else 0\)$"
		)
		match = payout_pattern.search(source)
		if not match:
			raise RuntimeError("Could not locate fixed Gold payout after award batching")
		indent = match.group("i")
		replacement = (
			f"{indent}fixed_award_coin_payouts = {{'gold': 250, 'truthnuke': 250, 'truthnova': 2500}}\n"
			f"{indent}awarded_coins = fixed_award_coin_payouts.get(kind, int(AWARDS[kind]['price'] * COSMETIC_AWARD_COIN_AWARD_PCT) if AWARDS[kind]['cosmetic'] and kind != 'shit' else 0)"
		)
		source = payout_pattern.sub(lambda _match: replacement, source, count=1)

		single_pattern = re.compile(
			r'(?m)^(?P<i>\t+)if awarded_coins > 0:\n(?P=i)\tmsg \+= f" and you have received \{awarded_coins\} coins as a result"\n(?P=i)msg \+= "!"$'
		)
		match = single_pattern.search(source)
		if not match:
			raise RuntimeError("Could not locate single-award payout notification")
		indent = match.group("i")
		replacement = (
			f'{indent}if awarded_coins > 0:\n'
			f'{indent}\tmsg += f" and you have received {{awarded_coins:,}} coins as a result"\n'
			f'{indent}if kind == "shit":\n'
			f'{indent}\tdestroyed_coins = max(0, _award_batch_target_coins_before - int(author.coins or 0))\n'
			f'{indent}\tmsg += f" and has destroyed {{destroyed_coins:,}} of your coins as a result"\n'
			f'{indent}msg += "!"\n'
			f'{indent}if kind == "truthnova":\n'
			f'{indent}\tmsg += "\\n\\nYou have received 1,375 XP!"'
		)
		source = single_pattern.sub(lambda _match: replacement, source, count=1)

		batch_pattern = re.compile(
			r'(?m)^(?P<i>\t+)if kind == "gold":\n(?P=i)\tmsg \+= f" and you have received \{250 \* amount\} coins as a result"\n(?P=i)msg \+= "!"$'
		)
		match = batch_pattern.search(source)
		if not match:
			raise RuntimeError("Could not locate aggregate Gold payout notification")
		indent = match.group("i")
		replacement = (
			f'{indent}fixed_batch_coin_payouts = {{"gold": 250, "truthnuke": 250, "truthnova": 2500}}\n'
			f'{indent}if kind in fixed_batch_coin_payouts:\n'
			f'{indent}\tmsg += f" and you have received {{fixed_batch_coin_payouts[kind] * amount:,}} coins as a result"\n'
			f'{indent}if kind == "shit":\n'
			f'{indent}\tdestroyed_coins = max(0, _award_batch_target_coins_before - int(_award_batch_target_author.coins or 0))\n'
			f'{indent}\tmsg += f" and has destroyed {{destroyed_coins:,}} of your coins as a result"\n'
			f'{indent}msg += "!"\n'
			f'{indent}if kind == "truthnova":\n'
			f'{indent}\tmsg += f"\\n\\nYou have received {{1375 * amount:,}} XP!"'
		)
		source = batch_pattern.sub(lambda _match: replacement, source, count=1)

		source = source.replace(
			"\t# obsession-award-batch-v3\n",
			"\t# obsession-award-batch-v3\n\t# toc-requested-awards-post-v2\n",
			1,
		)
		_atomic_write(_AWARDS_ROUTE_PATH, source)
