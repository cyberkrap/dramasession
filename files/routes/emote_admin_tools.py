import time
from functools import wraps

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


def _active_emote_sort_times():
	"""Return the best known approval time for each active emote.

	New approval records are authoritative. Older approvals made through the
	legacy submit page did not create approval records, so their latest update
	action is used as a compatibility fallback before the original submission
	timestamp.
	"""
	approval_times = {}
	legacy_update_times = {}
	actions = (g.db.query(ModAction)
		.filter(ModAction.kind.in_(('approve_marsey', 'update_marsey')))
		.order_by(ModAction.created_utc.desc()).all())
	for action in actions:
		name = action.emoji_name_raw
		if not name or name == 'unknown':
			continue
		if action.kind == 'approve_marsey':
			approval_times.setdefault(name, action.created_utc or 0)
		else:
			legacy_update_times.setdefault(name, action.created_utc or 0)
	return approval_times, legacy_update_times


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

	pending = (pending_query
		.order_by(Marsey.created_utc.desc(), Marsey.name.asc())
		.limit(ADMIN_EMOTES_PAGE_SIZE).all())

	approval_times, legacy_update_times = _active_emote_sort_times()
	active_all = active_query.all()
	active_all.sort(key=lambda emote: emote.name)
	active_all.sort(
		key=lambda emote: approval_times.get(
			emote.name,
			legacy_update_times.get(emote.name, emote.created_utc or 0),
		),
		reverse=True,
	)
	start = (page - 1) * ADMIN_EMOTES_PAGE_SIZE
	end = start + ADMIN_EMOTES_PAGE_SIZE
	active = active_all[start:end]
	next_exists = len(active_all) > end

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
	marsey.created_utc = int(time.time())
	g.db.add(marsey)
	set_emote_category(marsey.name, request.form.get('category', 'Community Emotes'), v.username)
	g.db.add(ModAction(
		kind='approve_marsey',
		user_id=v.id,
		target_user_id=marsey.author_id,
		_note=marsey.name,
	))
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
	g.db.add(ModAction(kind='update_marsey', user_id=v.id, _note=new_name))
	_clear()
	return redirect('/admin/emotes?msg=Emote updated.')


@app.post('/admin/emotes/<name>/delete')
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@admin_level_required(PERMS['MODERATE_PENDING_SUBMITTED_ASSETS'])
def admin_emote_delete(name, v):
	marsey = g.db.get(Marsey, name.lower())
	if not marsey: abort(404)
	was_pending = marsey.submitter_id is not None
	emote_name = marsey.name
	author_id = marsey.author_id
	remove_emote_files(emote_name)
	g.db.delete(marsey)
	if was_pending:
		g.db.add(ModAction(
			kind='reject_marsey',
			user_id=v.id,
			target_user_id=author_id,
			_note=emote_name,
		))
		message = 'Emote rejected.'
	else:
		g.db.add(ModAction(kind='delete_marsey', user_id=v.id, _note=emote_name))
		message = 'Emote deleted.'
	_clear()
	return redirect(f'/admin/emotes?msg={message}')


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


def _install_legacy_approval_tracking():
	"""Stamp approvals performed from the older /submit/marseys interface."""
	original = app.view_functions.get('approve_marsey')
	if not original or getattr(original, '_tracks_emote_approval', False):
		return

	@wraps(original)
	def tracked(*args, **kwargs):
		response = original(*args, **kwargs)
		approved_name = (request.values.get('name') or kwargs.get('name') or '').lower().strip()
		marsey = g.db.query(Marsey).filter_by(name=approved_name).one_or_none()
		if marsey and marsey.submitter_id is None:
			now = int(time.time())
			marsey.created_utc = now
			g.db.add(marsey)
			actor = getattr(g, 'v', None)
			if actor:
				recent = (g.db.query(ModAction.id)
					.filter(
						ModAction.kind == 'approve_marsey',
						ModAction._note == marsey.name,
						ModAction.created_utc >= now - 10,
					).first())
				if not recent:
					g.db.add(ModAction(
						kind='approve_marsey',
						user_id=actor.id,
						target_user_id=marsey.author_id,
						_note=marsey.name,
					))
		_clear()
		return response

	tracked._tracks_emote_approval = True
	app.view_functions['approve_marsey'] = tracked


_install_legacy_approval_tracking()
