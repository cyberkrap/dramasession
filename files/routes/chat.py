import atexit
import re
import time

from flask_socketio import SocketIO, emit
from sqlalchemy import func

from files.classes.chat import ChatMessage
from files.classes.mod_logs import ModAction
from files.classes.user import User
from files.helpers.actions import *
from files.helpers.alerts import *
from files.helpers.config.const import *
from files.helpers.regex import *
from files.helpers.media import process_image
from files.helpers.sanitize import sanitize
from files.routes.wrappers import *
from files.__main__ import app, cache, limiter

CHAT_CHANNEL = "public"
CHAT_PAGE_SIZE = 50

socketio = SocketIO(
	app,
	async_mode='gevent',
)

typing = []
online = []
cache.set(CHAT_ONLINE_CACHE_KEY, len(online), timeout=0)
muted = cache.get('muted') or {}


def _message_dict(message):
	removed = bool(message.removed_by_username)
	author = g.db.query(User).filter(User.id == message.user_id).one_or_none()
	return {
		"id": message.id,
		"quotes": str(message.quotes) if message.quotes else "",
		"hat": message.hat or "",
		"user_id": message.user_id,
		"is_admin": bool(message.distinguish_by_id),
		"username": author.username if author else message.username,
		"namecolor": author.name_color if author else message.namecolor,
		"patron": bool(author and author.patron),
		"text": "" if removed else message.body,
		"text_html": "" if removed else message.body_html,
		"text_censored": "" if removed else message.body_censored,
		"time": message.created_utc,
		"removed_by": message.removed_by_username,
		"removed_by_id": message.removed_by_id,
		"distinguish_by": message.distinguish_by_username,
		"distinguish_by_id": message.distinguish_by_id,
		"has_attachment": bool(message.has_attachment),
	}


def _message_map(rows):
	return {str(item["id"]): item for item in (_message_dict(row) for row in rows)}


def _parse_timeout(text):
	match = re.fullmatch(r'/timeout\s+@?([a-z0-9_-]{3,30})\s+((?:\d+\s*[dhm]\s*)+)', text.strip(), re.IGNORECASE)
	if not match:
		return None
	seconds = 0
	for amount, unit in re.findall(r'(\d+)\s*([dhm])', match.group(2), re.IGNORECASE):
		seconds += int(amount) * {'d': 86400, 'h': 3600, 'm': 60}[unit.lower()]
	return match.group(1), seconds if seconds > 0 else None


def _parse_untimeout(text):
	match = re.fullmatch(r'/untimeout\s+@?([a-z0-9_-]{3,30})', text.strip(), re.IGNORECASE)
	return match.group(1) if match else None

def _format_timeout_duration(seconds):
	parts = []
	remaining = int(seconds)
	for unit, size in (('day', 86400), ('hour', 3600), ('minute', 60)):
		amount, remaining = divmod(remaining, size)
		if amount:
			parts.append(f"{amount} {unit}{'' if amount == 1 else 's'}")
	return ' '.join(parts) or '0 minutes'


def _active_filters(filters):
	return bool(filters and any(str(value).strip() for value in filters.values() if value not in (False, None)))


def _apply_filters(query, filters):
	if not filters:
		return query

	author = str(filters.get("author") or "").strip()[:80]
	keyword = str(filters.get("keyword") or "").strip()[:120]
	mentions = str(filters.get("mentions") or "").strip()[:80]
	if author:
		query = query.filter(func.lower(ChatMessage.username) == author.lower())
	if keyword:
		query = query.filter(ChatMessage.body.ilike(f"%{keyword}%"))
	if mentions:
		query = query.filter(ChatMessage.body.ilike(f"%@{mentions}%"))
	if filters.get("has_attachment") in (True, "true", "1", 1):
		query = query.filter(ChatMessage.has_attachment.is_(True))
	try:
		from_ts = int(float(filters.get("from_ts"))) if filters.get("from_ts") else None
		to_ts = int(float(filters.get("to_ts"))) if filters.get("to_ts") else None
	except (TypeError, ValueError):
		from_ts = None
		to_ts = None
	if from_ts is not None:
		query = query.filter(ChatMessage.created_utc >= from_ts)
	if to_ts is not None:
		query = query.filter(ChatMessage.created_utc <= to_ts)
	return query


def _select_messages(filters=None, before_id=None, around_id=None, initial=False, limit=CHAT_PAGE_SIZE):
	query = g.db.query(ChatMessage).filter(ChatMessage.channel == CHAT_CHANNEL)
	query = _apply_filters(query, filters)
	limit = max(1, min(int(limit or CHAT_PAGE_SIZE), 100))

	if around_id is not None:
		try:
			around_id = int(around_id)
		except (TypeError, ValueError):
			around_id = 0
		query = query.filter(ChatMessage.id >= max(1, around_id - limit // 2))
		query = query.filter(ChatMessage.id <= around_id + limit // 2)
		rows = query.order_by(ChatMessage.id.asc()).limit(limit).all()
		return rows, False

	if before_id is not None:
		try:
			before_id = int(before_id)
		except (TypeError, ValueError):
			before_id = 0
		query = query.filter(ChatMessage.id < before_id)

	rows = query.order_by(ChatMessage.id.desc()).limit(limit + 1).all()
	has_more = len(rows) > limit
	return list(reversed(rows[:limit])), has_more


@app.get("/chat")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@admin_level_required(PERMS['CHAT'])
def chat(v):
	if not v.admin_level and TRUESCORE_CHAT_MINIMUM and v.truescore < TRUESCORE_CHAT_MINIMUM:
		abort(403, f"Need at least {TRUESCORE_CHAT_MINIMUM} truescore for access to chat!")
	rows, has_more = _select_messages(initial=True, limit=100)
	chat_mention_notifications = g.db.query(Notification).join(Comment).filter(
		Notification.user_id == v.id,
		Notification.read == False,
		Comment.author_id == AUTOJANNY_ID,
		Comment.parent_submission == None,
		Comment.body_html.like('%/chat#%'),
	).all()
	for notification in chat_mention_notifications:
		notification.read = True
	if chat_mention_notifications:
		g.db.commit()
	payload = [_message_dict(row) for row in rows]
	return render_template(
		"chat.html",
		v=v,
		messages=_message_map(rows),
		initial_messages=payload,
		initial_has_more=has_more,
	)


@socketio.on('speak')
@admin_level_required(PERMS['CHAT'])
def speak(data, v):
	global typing
	data = data or {}
	vname = v.username.lower()
	now = int(time.time())
	muted_until = muted.get(vname)
	if muted_until and now < muted_until:
		emit('chat_error', 'You are timed out from chat until the timeout expires.')
		return '', 403
	if muted_until:
		del muted[vname]
		cache.set('muted', muted)
	image = None
	file_data = data.get('file')
	if file_data:
		name = f'/chat_images/{time.time()}'.replace('.', '') + '.webp'
		with open(name, 'wb') as f:
			f.write(file_data)
		image = process_image(name, v)

	if v.is_banned:
		return '', 403
	if TRUESCORE_CHAT_MINIMUM and v.truescore < TRUESCORE_CHAT_MINIMUM:
		return '', 403

	text = sanitize_raw_body(data.get('message', ''), False)[:CHAT_LENGTH_LIMIT]
	if image:
		text += f'\n\n![]({image})'
	if not text:
		return '', 400

	text_html = sanitize(text, count_marseys=True, chat=True)
	if isinstance(text_html, tuple):
		return text_html

	quote_id = None
	quote_value = str(data.get('quotes') or '').strip()
	if quote_value.isdigit():
		quoted = g.db.query(ChatMessage.id).filter(
			ChatMessage.id == int(quote_value),
			ChatMessage.channel == CHAT_CHANNEL,
		).one_or_none()
		if quoted:
			quote_id = quoted[0]

	self_only = False

	if SITE == 'rdrama.net':
		recent = g.db.query(ChatMessage).filter(
			ChatMessage.user_id == v.id,
			ChatMessage.channel == CHAT_CHANNEL,
		).order_by(ChatMessage.id.desc()).limit(25).all()

		def shut_up():
			global muted
			muted_until = int(time.time() + 3600)
			muted[vname] = muted_until
			emit("online", [online, muted], broadcast=True)
			return True

		if sum(1 for row in recent[:5] if row.body == text) >= 3:
			self_only = shut_up()
		if not self_only and len(recent[:12]) >= 10:
			self_only = shut_up()
		if not self_only and len(recent) >= 20:
			self_only = shut_up()

	distinguished = bool(data.get('distinguished')) and v.has_permission('POST_COMMENT_DISTINGUISH')
	timeout_target = None
	timeout_duration = None
	untimeout_target = None
	timeout = _parse_timeout(text)
	untimeout_name = _parse_untimeout(text)
	if timeout or untimeout_name:
		if not distinguished:
			emit('chat_error', 'Timeout commands require Send as admin.')
			return '', 403
		target_name = timeout[0] if timeout else untimeout_name
		target = g.db.query(User).filter(func.lower(User.username) == target_name.lower()).one_or_none()
		if not target or (timeout and not timeout[1]):
			emit('chat_error', 'Use /timeout @username 1d 1h 1m or /untimeout @username.')
			return '', 400
		if timeout:
			timeout_duration = timeout[1]
			muted[target.username.lower()] = int(time.time()) + timeout_duration
			timeout_target = target
		else:
			muted.pop(target.username.lower(), None)
			untimeout_target = target
	cache.set('muted', muted)
	emit("online", [online, muted], broadcast=True)
	execute_blackjack(v, None, text, "chat")
	if v.admin_level >= PERMS['USER_BAN']:
		for match in mute_regex.finditer(text.lower()):
			username = match.group(1).lower()
			muted[username] = int(int(match.group(2)) * 60 + time.time())
			emit("online", [online, muted], broadcast=True)
			self_only = True

	message = ChatMessage(
		channel=CHAT_CHANNEL,
		user_id=v.id,
		username=v.username,
		namecolor=v.name_color,
		hat=v.hat_active(v)[0],
		body=text,
		body_html=text_html,
		body_censored=censor_slurs(text_html, 'chat'),
		quotes=quote_id,
		created_utc=int(time.time()),
		has_attachment=bool(image),
		distinguish_by_id=v.id if distinguished else None,
		distinguish_by_username=v.username if distinguished else None,
	)
	g.db.add(message)
	g.db.commit()
	if timeout_target:
		g.db.add(ModAction(
			kind='chat_timeout',
			user_id=v.id,
			target_user_id=timeout_target.id,
			_note=f'<a href="/chat#{message.id}">Chat</a> for {_format_timeout_duration(timeout_duration)}',
		))
		g.db.commit()
	elif untimeout_target:
		g.db.add(ModAction(
			kind='chat_untimeout',
			user_id=v.id,
			target_user_id=untimeout_target.id,
			_note=f'<a href="/chat#{message.id}">Chat</a>',
		))
		g.db.commit()
	mention_uids = NOTIFY_USERS(text, v)
	for uid in mention_uids:
		send_notification(uid, f"@{v.username} mentioned you in [public chat message #{message.id}](/chat#{message.id})")
	if mention_uids:
		g.db.commit()
	payload = _message_dict(message)

	if self_only or v.shadowbanned:
		emit('speak', payload)
	else:
		emit('speak', payload, broadcast=True)

	typing = []
	return '', 204


def refresh_online():
	emit("online", [online, muted], broadcast=True)
	cache.set(CHAT_ONLINE_CACHE_KEY, len(online), timeout=0)


@socketio.on('connect')
@admin_level_required(PERMS['CHAT'])
def connect(v):
	entry = [v.username, v.id, v.name_color, bool(v.patron)]
	if not any(item[:2] == entry[:2] for item in online):
		online.append(entry)
	refresh_online()
	emit('typing', typing)
	return '', 204


@socketio.on('disconnect')
@admin_level_required(PERMS['CHAT'])
def disconnect(v):
	for item in online[:]:
		if item[:2] == [v.username, v.id]:
			online.remove(item)
			break
		refresh_online()
	if v.username in typing:
		typing.remove(v.username)
	return '', 204


@socketio.on('typing')
@admin_level_required(PERMS['CHAT'])
def typing_indicator(data, v):
	if data and v.username not in typing:
		typing.append(v.username)
	elif not data and v.username in typing:
		typing.remove(v.username)
	emit('typing', typing, broadcast=True)
	return '', 204


@socketio.on('history')
@admin_level_required(PERMS['CHAT'])
def history(data, v):
	data = data or {}
	filters = data.get('filters') or {}
	if _active_filters(filters) and v.admin_level < PERMS['POST_COMMENT_MODERATION']:
		return '', 403
	around_id = data.get('around')
	before_id = data.get('before') if around_id is None and not _active_filters(filters) else None
	initial = around_id is None and before_id is None and not _active_filters(filters)
	rows, has_more = _select_messages(
		filters=filters,
		before_id=before_id,
		around_id=around_id,
		initial=initial,
		limit=data.get('limit', CHAT_PAGE_SIZE),
	)
	emit('history', {
		'messages': [_message_dict(row) for row in rows],
		'has_more': has_more,
		'mode': 'around' if around_id is not None else ('filter' if _active_filters(filters) else ('prepend' if before_id is not None else 'replace')),
	})
	return '', 204


@socketio.on('delete')
@admin_level_required(PERMS['POST_COMMENT_MODERATION'])
def delete(message_id, v):
	try:
		message_id = int(message_id)
	except (TypeError, ValueError):
		return '', 400
	message = g.db.query(ChatMessage).filter(ChatMessage.id == message_id).one_or_none()
	if message is None:
		return '', 204
	message.removed_by_id = v.id
	message.removed_by_username = v.username
	message.body = ''
	message.body_html = ''
	message.body_censored = ''
	g.db.commit()
	emit('delete', {
		'id': message_id,
		'removed_by': v.username,
		'removed_by_id': v.id,
		'removed_by_admin': True,
	}, broadcast=True)
	return '', 204


def close_running_threads():
	cache.set('muted', muted)


atexit.register(close_running_threads)