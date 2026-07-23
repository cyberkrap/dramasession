from flask import abort, g, redirect, render_template, request
from sqlalchemy import or_

from files.__main__ import app, cache, limiter
from files.classes.marsey import Marsey
from files.classes.mod_logs import ModAction
from files.helpers.config.const import DEFAULT_RATELIMIT, DEFAULT_RATELIMIT_SLOWER, EMOJIS_CACHE_KEY, MARSEYS_CACHE_KEY, PERMS
from files.helpers.emote_management import (
	approve_emote_files, custom_emote_exists, delete_emote_category,
	get_emote_categories, get_emote_category_map, remove_emote_files,
	rename_emote_category, rename_emote_files, save_emote_categories,
	set_emote_category,
)
from files.helpers.regex import marsey_regex, tags_regex
from files.routes.wrappers import admin_level_required, get_ID


ADMIN_EMOTES_PAGE_SIZE = 48


def _clear():
	cache.delete(EMOJIS_CACHE_KEY)
	cache.delete(MARSEYS_CACHE_KEY)


@app.get('/admin/emotes')
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@admin_level_required(PERMS['MODERATE_PENDING_SUBMITTED_ASSETS'])
def admin_emotes(v):
	try:
		page = max(1, int(request.values.get('page', 1)))
	except (TypeError, ValueError):
		page = 1
	query = (request.values.get('q') or '').strip().lower()[:64]

	pending_query = g.db.query(Marsey).filter(Marsey.submitter_id != None)
	active_query = g.db.query(Marsey).filter(Marsey.submitter_id == None)
	if query:
		pattern = f'%{query}%'
		search_filter = or_(Marsey.name.ilike(pattern), Marsey.tags.ilike(pattern))
		pending_query = pending_query.filter(search_filter)
		active_query = active_query.filter(search_filter)

	pending = pending_query.order_by(Marsey.created_utc.desc()).limit(ADMIN_EMOTES_PAGE_SIZE).all()
	active_rows = (active_query.order_by(Marsey.name)
		.offset((page - 1) * ADMIN_EMOTES_PAGE_SIZE)
		.limit(ADMIN_EMOTES_PAGE_SIZE + 1).all())
	next_exists = len(active_rows) > ADMIN_EMOTES_PAGE_SIZE
	active = active_rows[:ADMIN_EMOTES_PAGE_SIZE]

	categories = get_emote_categories()
	category_map = get_emote_category_map()
	default_category = 'Community Emotes'
	valid_categories = set(categories)
	emote_categories = {
		emote.name: category_map.get(emote.name, default_category)
		if category_map.get(emote.name, default_category) in valid_categories
		else default_category
		for emote in active
	}
	custom_emotes = {emote.name for emote in active if custom_emote_exists(emote.name)}

	return render_template(
		'admin/emotes.html',
		v=v,
		pending=pending,
		active=active,
		categories=categories,
		emote_categories=emote_categories,
		custom_emotes=custom_emotes,
		page=page,
		next_exists=next_exists,
		q=query,
		msg=request.values.get('msg'),
		error=request.values.get('error'),
	)


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
		author_id, count, submitter_id, created_utc = marsey.author_id, marsey.count, marsey.submitter_id, marsey.created_utc
		rename_emote_files(old_name, new_name)
		g.db.delete(marsey); g.db.flush()
		marsey = Marsey(name=new_name, author_id=author_id, tags=tags, count=count, submitter_id=submitter_id, created_utc=created_utc)
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
	except ValueError as exc: return redirect(f'/admin/emotes?error={str(exc)}')
	return redirect('/admin/emotes?msg=Category created.')


@app.post('/admin/emotes/categories/rename')
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@admin_level_required(PERMS['MODERATE_PENDING_SUBMITTED_ASSETS'])
def admin_emote_category_rename(v):
	try: rename_emote_category(request.form.get('old'), request.form.get('new'), v.username)
	except ValueError as exc: return redirect(f'/admin/emotes?error={str(exc)}')
	_clear()
	return redirect('/admin/emotes?msg=Category renamed.')


@app.post('/admin/emotes/categories/delete')
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@admin_level_required(PERMS['MODERATE_PENDING_SUBMITTED_ASSETS'])
def admin_emote_category_delete(v):
	try: delete_emote_category(request.form.get('category'), v.username)
	except ValueError as exc: return redirect(f'/admin/emotes?error={str(exc)}')
	_clear()
	return redirect('/admin/emotes?msg=Category deleted.')
