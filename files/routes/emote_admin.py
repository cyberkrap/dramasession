from pathlib import Path

from flask import abort, g, send_file

from files.__main__ import app, limiter
from files.classes import Marsey, User
from files.helpers.config.const import PERMS
from files.helpers.emote_management import (
	approved_webp_path,
	category_for_emote,
	custom_emote_exists,
	custom_emote_url,
	find_pending_webp,
)
from files.helpers.regex import marsey_regex
from files.routes.static import get_emojis
from files.routes.wrappers import auth_required


FILES_ROOT = Path(__file__).resolve().parents[1]
STATIC_EMOTE_DIR = FILES_ROOT / 'assets' / 'images' / 'emojis'
RDRAMA_EMOTE_CATEGORY = 'rDrama Emotes'
RDRAMA_EMOTE_PREFIXES = ('marsey', 'capy', 'carp', 'platy', 'wolf')


def _is_rdrama_emote(name):
	return str(name or '').lower().startswith(RDRAMA_EMOTE_PREFIXES)


def _search_tags(name, existing_tags=None, marsey=None, author=None):
	tags = []
	seen = set()

	def add(value):
		value = str(value or '').strip().lower()
		if value and value not in seen:
			seen.add(value)
			tags.append(value)

	add(name)
	if isinstance(existing_tags, str):
		existing_tags = existing_tags.split()
	for tag in existing_tags or ():
		add(tag)
	if marsey and marsey.tags:
		for tag in marsey.tags.split():
			add(tag)
	if author:
		add(author)
		add(f'author:{author}')
		add(f'@{author}')
	return tags


def enhanced_emoji_list():
	metadata = {}
	rows = (g.db.query(Marsey, User.username)
		.outerjoin(User, Marsey.author_id == User.id)
		.filter(Marsey.submitter_id == None)
		.order_by(Marsey.name).all())
	for marsey, author in rows:
		metadata[marsey.name] = (marsey, author)

	items = []
	known = set()
	for raw_item in get_emojis(g.db):
		item = dict(raw_item)
		name = str(item.get('name') or '').strip().lower()
		if not name:
			continue
		item['name'] = name
		known.add(name)

		marsey, author = metadata.get(name, (None, item.get('author')))
		if marsey:
			item['count'] = int(marsey.count or 0)
		if author:
			item['author'] = author
		item['tags'] = _search_tags(name, item.get('tags'), marsey, item.get('author'))

		if _is_rdrama_emote(name):
			item['class'] = RDRAMA_EMOTE_CATEGORY
		items.append(item)

	for name, (marsey, author) in metadata.items():
		if name in known:
			continue
		if not custom_emote_exists(name) and not (STATIC_EMOTE_DIR / f'{name}.webp').is_file():
			continue
		items.append({
			'name': name,
			'author': author,
			'tags': _search_tags(name, (), marsey, author),
			'count': int(marsey.count or 0),
			'class': RDRAMA_EMOTE_CATEGORY if _is_rdrama_emote(name) else category_for_emote(name),
			'url': custom_emote_url(name) if custom_emote_exists(name) else f'/e/{name}.webp',
		})
	return items


def _serve_pending_emote(v, name):
	name = str(name or '').lower().strip()
	if not marsey_regex.fullmatch(name):
		abort(404)

	marsey = g.db.get(Marsey, name)
	if not marsey or marsey.submitter_id is None:
		abort(404)
	if v.id != marsey.submitter_id and v.admin_level < PERMS['VIEW_PENDING_SUBMITTED_MARSEYS']:
		abort(404)

	preview = find_pending_webp(name)
	if not preview:
		abort(404)
	return send_file(preview, mimetype='image/webp', conditional=True, max_age=0)


@app.get('/pending-emote/<name>.webp')
@limiter.exempt
@auth_required
def pending_emote_preview(v, name):
	"""Serve pending previews through an application route that nginx does not intercept."""
	return _serve_pending_emote(v, name)


@app.get('/asset_submissions/marseys/<name>.webp')
@limiter.exempt
@auth_required
def pending_emote_file(v, name):
	"""Backward-compatible pending preview URL."""
	return _serve_pending_emote(v, name)


@app.get('/emote-preview/<name>.webp')
@limiter.exempt
def active_emote_preview(name):
	"""Serve either persistent or bundled active emotes through one stable URL."""
	name = str(name or '').lower().strip()
	if not marsey_regex.fullmatch(name):
		abort(404)

	custom_path = approved_webp_path(name)
	if custom_path.is_file():
		return send_file(custom_path, mimetype='image/webp', conditional=True, max_age=3600)

	bundled_path = STATIC_EMOTE_DIR / f'{name}.webp'
	if bundled_path.is_file():
		return send_file(bundled_path, mimetype='image/webp', conditional=True, max_age=3600)

	abort(404)


@app.get('/community-emote/<name>.webp')
@limiter.exempt
def community_emote_file(name):
	name = str(name or '').lower().strip()
	if not marsey_regex.fullmatch(name):
		abort(404)
	path = approved_webp_path(name)
	if not path.is_file():
		abort(404)
	return send_file(path, mimetype='image/webp', conditional=True, max_age=3600)


def install_emote_management():
	app.view_functions['emoji_list'] = enhanced_emoji_list
