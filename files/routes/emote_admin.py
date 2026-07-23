from pathlib import Path

from flask import abort, g, send_file

from files.__main__ import app
from files.classes import Marsey
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


def enhanced_emoji_list():
	items = list(get_emojis(g.db))
	known = {item.get('name') for item in items}
	for marsey in g.db.query(Marsey).filter(Marsey.submitter_id == None).order_by(Marsey.name).all():
		if marsey.name in known:
			continue
		if not custom_emote_exists(marsey.name) and not Path(f'files/assets/images/emojis/{marsey.name}.webp').is_file():
			continue
		items.append({
			'name': marsey.name,
			'tags': marsey.tags_list(),
			'count': marsey.count,
			'class': category_for_emote(marsey.name),
			'url': custom_emote_url(marsey.name) if custom_emote_exists(marsey.name) else f'/e/{marsey.name}.webp',
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
@auth_required
def pending_emote_preview(v, name):
	"""Serve pending previews through an application route that nginx does not intercept."""
	return _serve_pending_emote(v, name)


@app.get('/asset_submissions/marseys/<name>.webp')
@auth_required
def pending_emote_file(v, name):
	"""Backward-compatible pending preview URL."""
	return _serve_pending_emote(v, name)


@app.get('/community-emote/<name>.webp')
def community_emote_file(name):
	if not marsey_regex.fullmatch(name):
		abort(404)
	path = approved_webp_path(name)
	if not path.is_file():
		abort(404)
	return send_file(path, conditional=True, max_age=3600)


def install_emote_management():
	app.view_functions['emoji_list'] = enhanced_emoji_list
