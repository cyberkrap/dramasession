from pathlib import Path

from flask import abort, g, send_file

from files.__main__ import app
from files.classes import Marsey
from files.helpers.emote_management import approved_webp_path, category_for_emote, custom_emote_exists, custom_emote_url
from files.helpers.regex import marsey_regex
from files.routes.static import get_emojis


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
