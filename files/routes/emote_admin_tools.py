from flask import abort, g, redirect, render_template, request

from files.__main__ import app, cache, limiter
from files.classes import Marsey, ModAction
from files.helpers.config.const import DEFAULT_RATELIMIT, DEFAULT_RATELIMIT_SLOWER, EMOJIS_CACHE_KEY, MARSEYS_CACHE_KEY, PERMS
from files.helpers.emote_management import (
	approve_emote_files, category_for_emote, get_emote_categories,
	remove_emote_files, rename_emote_files, save_emote_categories,
	set_emote_category,
)
from files.helpers.regex import marsey_regex, tags_regex
from files.routes.wrappers import admin_level_required, get_ID


def _clear():
	cache.delete(EMOJIS_CACHE_KEY)
	cache.delete(MARSEYS_CACHE_KEY)


@app.get('/admin/emotes')
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@admin_level_required(PERMS['MODERATE_PENDING_SUBMITTED_ASSETS'])
def admin_emotes(v):
	pending = g.db.query(Marsey).filter(Marsey.submitter_id != None).order_by(Marsey.created_utc.desc()).all()
	active = g.db.query(Marsey).filter(Marsey.submitter_id == None).order_by(Marsey.name).all()
	return render_template('admin/emotes.html', v=v, pending=pending, active=active,
		categories=get_emote_categories(), category_for_emote=category_for_emote,
		msg=request.values.get('msg'), error=request.values.get('error'))


@app.post('/admin/emotes/<name>/approve')
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@admin_level_required(PERMS['MODERATE_PENDING_SUBMITTED_ASSETS'])
def admin_emote_approve(name, v):
	marsey = g.db.get(Marsey, name.lower())
	if not marsey or marsey.submitter_id is None: abort(404)
	try: approve_emote_files(marsey.name)
	except FileNotFoundError: abort(409, 'Uploaded emote file is missing.')
	marsey.submitter_id = None
	g.db.add(marsey)
	set_emote_category(marsey.name, request.form.get('category', 'Community Emotes'), v.username)
	g.db.add(ModAction(kind='approve_marsey', user_id=v.id, _note=marsey.name))
	_clear()
	return redirect('/admin/emotes?msg=Emote approved.')


@app.post('/admin/emotes/<name>/update')
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@admin_level_required(PERMS['MODERATE_PENDING_SUBMITTED_ASSETS'])
def admin_emote_update(name, v):
	marsey = g.db.get(Marsey, name.lower())
	if not marsey: abort(404)
	new_name = (request.form.get('name') or '').lower().strip()
	tags = (request.form.get('tags') or '').lower().strip()
	category = request.form.get('category', 'Community Emotes')
	if not marsey_regex.fullmatch(new_name): abort(400, 'Invalid emote name.')
	if not tags_regex.fullmatch(tags): abort(400, 'Invalid tags.')
	if new_name != marsey.name and g.db.get(Marsey, new_name): abort(409, 'That emote name already exists.')
	old_name = marsey.name
	if new_name != old_name:
		rename_emote_files(old_name, new_name)
		g.db.delete(marsey); g.db.flush()
		marsey = Marsey(name=new_name, author_id=marsey.author_id, tags=tags, count=marsey.count, submitter_id=marsey.submitter_id, created_utc=marsey.created_utc)
	else:
		marsey.tags = tags
	g.db.add(marsey)
	set_emote_category(new_name, category, v.username)
	g.db.add(ModAction(kind='update_marsey', user_id=v.id, _note=f'{old_name} -> {new_name}'))
	_clear()
	return redirect('/admin/emotes?msg=Emote updated.')


@app.post('/admin/emotes/<name>/delete')
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@admin_level_required(PERMS['MODERATE_PENDING_SUBMITTED_ASSETS'])
def admin_emote_delete(name, v):
	marsey = g.db.get(Marsey, name.lower())
	if not marsey: abort(404)
	remove_emote_files(marsey.name)
	g.db.delete(marsey)
	g.db.add(ModAction(kind='delete_marsey', user_id=v.id, _note=marsey.name))
	_clear()
	return redirect('/admin/emotes?msg=Emote deleted.')


@app.post('/admin/emotes/categories')
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@admin_level_required(PERMS['MODERATE_PENDING_SUBMITTED_ASSETS'])
def admin_emote_category_create(v):
	category = (request.form.get('category') or '').strip()
	try: save_emote_categories(get_emote_categories() + [category], v.username)
	except ValueError: return redirect('/admin/emotes?error=Invalid category name.')
	return redirect('/admin/emotes?msg=Category created.')
