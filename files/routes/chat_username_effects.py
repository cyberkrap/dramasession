import fcntl
import os
from pathlib import Path

from flask import g, request

from files.__main__ import app, limiter
from files.classes import User
from files.helpers.chat_admin_modlog_source import patch_chat_admin_modlog_source
from files.helpers.config.const import DEFAULT_RATELIMIT
from files.routes.wrappers import auth_required, get_ID


_CHAT_CSS = Path('files/assets/css/chat.css')
_CHAT_STYLE_LOCK = '/tmp/obsession-chat-removed-style.lock'
_CHAT_REMOVED_STYLE = r'''

/* obsession-admin-removed-message-v1
   Removed chat content is intentionally unmistakable to moderators. */
body#chat #chat-window .chat-line.chat-removed {
	position: relative !important;
	background: rgba(220, 35, 58, .18) !important;
	border-left: 3px solid #ef2343 !important;
	box-shadow: inset 0 0 0 1px rgba(239, 35, 67, .08) !important;
}

body#chat #chat-window .chat-line.chat-removed .chat-message,
body#chat #chat-window .chat-line.chat-removed .chat-removed-original,
body#chat #chat-window .chat-line.chat-removed .chat-removed-original *,
body#chat #chat-window .chat-line.chat-removed .chat-removal-notice,
body#chat #chat-window .chat-line.chat-removed .chat-removal-notice * {
	color: #ff6b7d !important;
}

body#chat #chat-window .chat-line.chat-removed .chat-removal-notice {
	background: rgba(220, 35, 58, .14) !important;
	border-left-color: #ef2343 !important;
}

@media (min-width: 768px) {
	body#chat #chat-window .chat-line.chat-removed {
		padding: 7px 10px !important;
		margin-top: 4px !important;
		margin-bottom: 4px !important;
	}
}

@media (max-width: 767.98px) {
	body#chat #chat-window .chat-line.chat-removed {
		padding: 7px 8px !important;
		border-radius: 2px !important;
	}
}
'''


def _install_removed_chat_style():
	with open(_CHAT_STYLE_LOCK, 'w', encoding='utf-8') as lock:
		fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
		source = _CHAT_CSS.read_text(encoding='utf-8')
		if 'obsession-admin-removed-message-v1' in source:
			return
		temp = _CHAT_CSS.with_name(f'.{_CHAT_CSS.name}.{os.getpid()}.tmp')
		temp.write_text(source.rstrip() + _CHAT_REMOVED_STYLE + '\n', encoding='utf-8')
		os.replace(temp, _CHAT_CSS)


_install_removed_chat_style()
# __main__ imports this module immediately before files.routes.chat in the chat
# service, so the source patch is guaranteed to run before chat handlers load.
patch_chat_admin_modlog_source()


@app.get('/api/chat/username-effects')
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def chat_username_effects(v):
	requested = str(request.args.get('ids') or '')
	ids = []
	seen = set()
	for raw in requested.split(','):
		try:
			user_id = int(raw)
		except (TypeError, ValueError):
			continue
		if user_id < 1 or user_id in seen:
			continue
		seen.add(user_id)
		ids.append(user_id)
		if len(ids) >= 100:
			break

	if not ids:
		return {'users': {}}

	users = g.db.query(User).filter(User.id.in_(ids)).all()
	return {
		'users': {
			str(user.id): {
				'username': user.username,
				'effects': user.active_username_effects,
				'effect_color': user.username_effect_text_color,
				'name_color': user.name_color,
				'patron': bool(user.patron),
			}
			for user in users
		}
	}
