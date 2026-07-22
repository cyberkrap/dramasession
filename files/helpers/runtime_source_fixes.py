import os
from pathlib import Path

import fcntl


_LOCK_PATH = "/tmp/obsession-runtime-source-fixes.lock"
_COMMENTS_PATH = Path("files/routes/comments.py")
_SETTINGS_PATH = Path("files/routes/settings.py")
_AWARDS_PATH = Path("files/routes/awards.py")
_ADMIN_PATH = Path("files/routes/admin.py")


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


def patch_award_currency_source():
	"""Make Wishbux the preferred award currency with Wishcoins fallback."""
	with open(_LOCK_PATH, "w", encoding="utf-8") as lock:
		fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
		source = _AWARDS_PATH.read_text(encoding="utf-8")
		original = source

		import_line = "from files.helpers.award_currency import charge_award\n"
		if import_line not in source:
			marker = "from files.helpers.support import patron_has\n"
			if marker not in source:
				raise RuntimeError("Could not locate the awards helper import block")
			source = source.replace(marker, marker + import_line, 1)

		old_buy_block = '''\tif request.values.get("mb"):\n\t\tif award == "grass":\n\t\t\tabort(403, "You can't buy the grass award with marseybux!")\n\n\t\tcharged = v.charge_account('marseybux', price)\n\t\tif not charged:\n\t\t\tabort(400, "Not enough marseybux!")\n\telse:\n\t\tcharged = v.charge_account('coins', price)\n\t\tif not charged:\n\t\t\tabort(400, "Not enough coins!")\n\n\t\tv.coins_spent += price\n\t\tif v.coins_spent >= 1000000:\n\t\t\tbadge_grant(badge_id=73, user=v)\n\t\telif v.coins_spent >= 500000:\n\t\t\tbadge_grant(badge_id=72, user=v)\n\t\telif v.coins_spent >= 250000:\n\t\t\tbadge_grant(badge_id=71, user=v)\n\t\telif v.coins_spent >= 100000:\n\t\t\tbadge_grant(badge_id=70, user=v)\n\t\telif v.coins_spent >= 10000:\n\t\t\tbadge_grant(badge_id=69, user=v)\n\t\tg.db.add(v)\n'''
		new_buy_block = '''\trequested_currency = request.values.get("currency") or ("marseybux" if request.values.get("mb") else None)\n\tif award == "benefactor":\n\t\tcharged_currency = "marseybux" if v.charge_account("marseybux", price) else None\n\telif award == "grass":\n\t\tcharged_currency = "coins" if v.charge_account("coins", price) else None\n\telse:\n\t\tcharged_currency = charge_award(v, price, requested_currency)\n\n\tif not charged_currency:\n\t\tabort(400, "Not enough Wishbux or Wishcoins!")\n\n\tif charged_currency == "coins":\n\t\tv.coins_spent += price\n\t\tif v.coins_spent >= 1000000:\n\t\t\tbadge_grant(badge_id=73, user=v)\n\t\telif v.coins_spent >= 500000:\n\t\t\tbadge_grant(badge_id=72, user=v)\n\t\telif v.coins_spent >= 250000:\n\t\t\tbadge_grant(badge_id=71, user=v)\n\t\telif v.coins_spent >= 100000:\n\t\t\tbadge_grant(badge_id=70, user=v)\n\t\telif v.coins_spent >= 10000:\n\t\t\tbadge_grant(badge_id=69, user=v)\n\t\tg.db.add(v)\n'''
		if new_buy_block not in source:
			if old_buy_block not in source:
				raise RuntimeError("Could not locate the award shop currency block")
			source = source.replace(old_buy_block, new_buy_block, 1)

		old_direct_block = '''\tif purchased_directly:\n\t\tprice = int(AWARDS[kind]['price'] * v.discount)\n\t\tcurrency = 'marseybux' if kind == 'benefactor' else 'coins'\n\t\tif not v.charge_account(currency, price):\n\t\t\tabort(400, f"Not enough {currency}!" )\n\t\tif currency == 'coins':\n\t\t\tv.coins_spent += price\n\t\taward = AwardRelationship(user_id=v.id, kind=kind, price_paid=price)\n\t\tg.db.add(v)\n'''
		new_direct_block = '''\tif purchased_directly:\n\t\tprice = int(AWARDS[kind]['price'] * v.discount)\n\t\trequested_currency = request.values.get("currency")\n\t\tif kind == "benefactor":\n\t\t\tcharged_currency = "marseybux" if v.charge_account("marseybux", price) else None\n\t\telif kind == "grass":\n\t\t\tcharged_currency = "coins" if v.charge_account("coins", price) else None\n\t\telse:\n\t\t\tcharged_currency = charge_award(v, price, requested_currency)\n\t\tif not charged_currency:\n\t\t\tabort(400, "Not enough Wishbux or Wishcoins!")\n\t\tif charged_currency == "coins":\n\t\t\tv.coins_spent += price\n\t\taward = AwardRelationship(user_id=v.id, kind=kind, price_paid=price)\n\t\tg.db.add(v)\n'''
		if new_direct_block not in source:
			if old_direct_block not in source:
				raise RuntimeError("Could not locate the direct award currency block")
			source = source.replace(old_direct_block, new_direct_block, 1)

		if import_line not in source or new_buy_block not in source or new_direct_block not in source:
			raise RuntimeError("Award currency source repair did not produce the expected structure")

		if source != original:
			_atomic_write(_AWARDS_PATH, source)


def patch_badge_gift_message_source():
	"""Treat the badge grant text field as a notification gift message."""
	with open(_LOCK_PATH, "w", encoding="utf-8") as lock:
		fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
		source = _ADMIN_PATH.read_text(encoding="utf-8")
		original = source

		old_inputs = '''\tdescription = request.values.get("description")\n\turl = request.values.get("url")\n'''
		new_inputs = '''\tgift_message = request.values.get("message", "").strip()\n\tif len(gift_message) > 500:\n\t\tabort(400, "Gift message is too long!")\n\turl = request.values.get("url")\n'''
		if new_inputs not in source:
			if old_inputs not in source:
				raise RuntimeError("Could not locate the badge grant input block")
			source = source.replace(old_inputs, new_inputs, 1)

		old_existing = '''\tif existing:\n\t\tif url or description:\n\t\t\texisting.url = url\n\t\t\texisting.description = description\n\t\t\tg.db.add(existing)\n\t\t\treturn render_template("admin/badge_admin.html", v=v, badge_types=badges, grant=True, msg="Badge attributes edited successfully!")\n\t\treturn render_template("admin/badge_admin.html", v=v, badge_types=badges, grant=True, error="User already has that badge!")\n'''
		new_existing = '''\tif existing:\n\t\tif url:\n\t\t\texisting.url = url\n\t\t\tg.db.add(existing)\n\t\t\treturn render_template("admin/badge_admin.html", v=v, badge_types=badges, grant=True, msg="Badge link edited successfully!")\n\t\treturn render_template("admin/badge_admin.html", v=v, badge_types=badges, grant=True, error="User already has that badge!")\n'''
		if new_existing not in source:
			if old_existing not in source:
				raise RuntimeError("Could not locate the existing badge update block")
			source = source.replace(old_existing, new_existing, 1)

		old_badge = '''\tnew_badge = Badge(\n\t\tbadge_id=badge_id,\n\t\tuser_id=user.id,\n\t\turl=url,\n\t\tdescription=description\n\t\t)\n'''
		new_badge = '''\tnew_badge = Badge(\n\t\tbadge_id=badge_id,\n\t\tuser_id=user.id,\n\t\turl=url\n\t\t)\n'''
		if new_badge not in source:
			if old_badge not in source:
				raise RuntimeError("Could not locate the new badge creation block")
			source = source.replace(old_badge, new_badge, 1)

		old_notification = '''\tif v.id != user.id:\n\t\ttext = f"@{v.username} (a site admin) has given you the following profile badge:\\n\\n![]({new_badge.path})\\n\\n**{new_badge.name}**\\n\\n{new_badge.badge.description}"\n\t\tsend_repeatable_notification(user.id, text)\n'''
		new_notification = '''\tif v.id != user.id:\n\t\ttext = f"@{v.username} (a site admin) has given you the following profile badge:\\n\\n![]({new_badge.path})\\n\\n**{new_badge.name}**\\n\\n{new_badge.badge.description}"\n\t\tif gift_message:\n\t\t\ttext += f"\\n\\n**Gift message from @{v.username}:**\\n\\n> {gift_message}"\n\t\tsend_repeatable_notification(user.id, text)\n'''
		if new_notification not in source:
			if old_notification not in source:
				raise RuntimeError("Could not locate the badge notification block")
			source = source.replace(old_notification, new_notification, 1)

		if new_inputs not in source or new_existing not in source or new_badge not in source or new_notification not in source:
			raise RuntimeError("Badge gift-message source repair did not produce the expected structure")

		if source != original:
			_atomic_write(_ADMIN_PATH, source)
