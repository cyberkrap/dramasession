import os
import re
from pathlib import Path

import fcntl


_LOCK_PATH = "/tmp/obsession-requested-awards.lock"
_AWARDS_ROUTE_PATH = Path("files/routes/awards.py")


def _atomic_write(path, content):
	temp_path = path.with_name(f".{path.name}.{os.getpid()}.tmp")
	temp_path.write_text(content, encoding="utf-8")
	os.replace(temp_path, path)


def patch_requested_awards_post_batch_source_v2():
	"""Patch fixed Truth payouts/XP after the existing batch-v3 source rewrite."""
	with open(_LOCK_PATH, "w", encoding="utf-8") as lock:
		fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
		source = _AWARDS_ROUTE_PATH.read_text(encoding="utf-8")
		if "# toc-requested-awards-post-v2" in source:
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
		replacement = (
			f"{indent}fixed_award_coin_payouts = {{'gold': 250, 'truthnuke': 250, 'truthnova': 2500}}\n"
			f"{indent}awarded_coins = fixed_award_coin_payouts.get(kind, int(AWARDS[kind]['price'] * COSMETIC_AWARD_COIN_AWARD_PCT) if AWARDS[kind]['cosmetic'] and kind != 'shit' else 0)"
		)
		source = payout_pattern.sub(replacement, source, count=1)

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
			f'{indent}msg += "!"\n'
			f'{indent}if kind == "truthnova":\n'
			f'{indent}\tmsg += "\\n\\nYou have received 1,375 XP!"'
		)
		source = single_pattern.sub(replacement, source, count=1)

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
			f'{indent}msg += "!"\n'
			f'{indent}if kind == "truthnova":\n'
			f'{indent}\tmsg += f"\\n\\nYou have received {{1375 * amount:,}} XP!"'
		)
		source = batch_pattern.sub(replacement, source, count=1)

		source = source.replace(
			"\t# obsession-award-batch-v3\n",
			"\t# obsession-award-batch-v3\n\t# toc-requested-awards-post-v2\n",
			1,
		)
		_atomic_write(_AWARDS_ROUTE_PATH, source)
