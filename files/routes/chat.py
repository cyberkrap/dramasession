import atexit
import time
import uuid

from flask_socketio import SocketIO, emit

from files.helpers.actions import *
from files.helpers.alerts import *
from files.helpers.config.const import *
from files.helpers.regex import *
from files.helpers.media import process_image
from files.helpers.sanitize import sanitize
from files.helpers.alerts import push_notif
from files.routes.wrappers import *

from files.__main__ import app, cache, limiter

socketio = SocketIO(
	app,
	async_mode='gevent',
)

typing = []
online =  []
cache.set(CHAT_ONLINE_CACHE_KEY, len(online), timeout=0)
muted = cache.get(f'muted') or {}
messages = cache.get(f'messages') or {}

@app.get("/chat")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@admin_level_required(PERMS['CHAT'])
def chat(v):
	if not v.admin_level and TRUESCORE_CHAT_MINIMUM and v.truescore < TRUESCORE_CHAT_MINIMUM:
		abort(403, f"Need at least {TRUESCORE_CHAT_MINIMUM} truescore for access to chat!")
	return render_template("chat.html", v=v, messages=messages)

@socketio.on('speak')
@admin_level_required(PERMS['CHAT'])
def speak(data, v):
	image = None
	if data['file']:
		name = f'/chat_images/{time.time()}'.replace('.','') + '.webp'
		with open(name, 'wb') as f:
			f.write(data['file'])
		image = process_image(name, v)

	if v.is_banned: return '', 403
	if TRUESCORE_CHAT_MINIMUM and v.truescore < TRUESCORE_CHAT_MINIMUM:
		return '', 403

	global messages

	text = sanitize_raw_body(data['message'], False)[:CHAT_LENGTH_LIMIT]
	if image: text += f'\n\n![]({image})'
	if not text: return '', 400

	text_html = sanitize(text, count_marseys=True, chat=True)
	if isinstance(text_html , tuple):
		return text_html

	quotes = data['quotes']
	id = str(uuid.uuid4())

	self_only = False

	vname = v.username.lower()
	if vname in muted:
		if time.time() < muted[vname]:
			self_only = True
		else:
			del muted[vname]
			emit("online", [online, muted], broadcast=True)

	if SITE == 'rdrama.net':
		def shut_up():
			self_only = True
			muted_until = int(time.time() + 3600)
			muted[vname] = muted_until
			emit("online", [online, muted], broadcast=True)

		if not self_only:
			identical = [x for x in list(messages.values())[-5:] if v.id == x['user_id'] and text == x['text']]
			if len(identical) >= 3: shut_up()

		if not self_only:
			count = len([x for x in list(messages.values())[-12:] if v.id == x['user_id']])
			if count >= 10: shut_up()

		if not self_only:
			count = len([x for x in list(messages.values())[-25:] if v.id == x['user_id']])
			if count >= 20: shut_up()

	data = {
		"id": id,
		"quotes": quotes if messages.get(quotes) else '',
		"hat": v.hat_active(v)[0],
		"user_id": v.id,
		"username": v.username,
		"namecolor": v.name_color,
		"text": text,
		"text_html": text_html,
		"text_censored": censor_slurs(text_html, 'chat'),
		"time": int(time.time()),
	}


	if v.admin_level >= PERMS['USER_BAN']:
		text = text.lower()
		for i in mute_regex.finditer(text):
			username = i.group(1).lower()
			muted_until = int(int(i.group(2)) * 60 + time.time())
			muted[username] = muted_until
			emit("online", [online, muted], broadcast=True)
			self_only = True

	if self_only or v.shadowbanned or not execute_blackjack(v, None, text, "chat"):
		emit('speak', data)
	else:
		emit('speak', data, broadcast=True)
		messages[id] = data
		messages = dict(list(messages.items())[-500:])

	typing = []

	return '', 204

def refresh_online():
	emit("online", [online, muted], broadcast=True)
	cache.set(CHAT_ONLINE_CACHE_KEY, len(online), timeout=0)

@socketio.on('connect')
@admin_level_required(PERMS['CHAT'])
def connect(v):

	if [v.username, v.id, v.name_color] not in online:
		online.append([v.username, v.id, v.name_color])

	refresh_online()

	emit('typing', typing)
	return '', 204

@socketio.on('disconnect')
@admin_level_required(PERMS['CHAT'])
def disconnect(v):
	if [v.username, v.id, v.name_color] in online:
		online.remove([v.username, v.id, v.name_color])
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


@socketio.on('delete')
@admin_level_required(PERMS['POST_COMMENT_MODERATION'])
def delete(id, v):
	del messages[id]

	emit('delete', id, broadcast=True)

	return '', 204


def close_running_threads():
	cache.set(f'messages', messages)
	cache.set(f'muted', muted)
atexit.register(close_running_threads)
