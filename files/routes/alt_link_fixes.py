from flask import abort, g, request
from sqlalchemy.sql.expression import and_, or_

from files.__main__ import app, limiter
from files.classes import Alt, ModAction
from files.helpers.config.const import DEFAULT_RATELIMIT_SLOWER, PERMS
from files.helpers.get import get_account, get_user
from files.routes.routehelpers import check_for_alts
from files.routes.wrappers import admin_level_required, get_ID


def _get_alt_link(user1_id, user2_id):
	return g.db.query(Alt).filter(
		or_(
			and_(Alt.user1 == user1_id, Alt.user2 == user2_id),
			and_(Alt.user1 == user2_id, Alt.user2 == user1_id),
		)
	).one_or_none()


def _save_alt_state(user1, user2, link, deleted):
	link.deleted = bool(deleted)
	link.is_manual = True
	g.db.add(link)
	g.db.flush()

	# get_alt_graph_ids deliberately reads live database state and is no longer
	# memoized. Trying to delete a memoized entry for it raises AttributeError
	# inside Flask-Caching and turns a successful delink into a 500 response.
	# No cache invalidation is needed here.

	# Only propagate moderation state when the accounts are actively linked.
	if not link.deleted:
		check_for_alts(user1)
		check_for_alts(user2)


def _record_alt_action(actor, user1, user2, deleted, relinked=False):
	kind = 'delink_accounts' if deleted else 'link_accounts'
	if deleted:
		note = f'from @{user2.username}'
	else:
		note = f'with @{user2.username}'
		if relinked:
			note += ' (relinked)'

	g.db.add(ModAction(
		kind=kind,
		user_id=actor.id,
		target_user_id=user1.id,
		_note=note,
	))


@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@admin_level_required(PERMS['USER_LINK'])
def _admin_add_alt_fixed(v, username):
	user1 = get_user(username)
	user2 = get_user(request.values.get('other_username'))
	if user1.id == user2.id:
		abort(400, "Can't add the same account as alts of each other")

	deleted_value = str(request.values.get('deleted', '')).strip().lower()
	deleted = deleted_value in {'1', 'true', 'yes', 'on'}
	link = _get_alt_link(user1.id, user2.id)

	if link:
		was_deleted = bool(link.deleted)
		if was_deleted == deleted:
			state = 'delinked' if deleted else 'linked'
			return {'message': f'@{user1.username} and @{user2.username} are already {state}.'}
		_save_alt_state(user1, user2, link, deleted)
		_record_alt_action(v, user1, user2, deleted, relinked=not deleted)
	else:
		link = Alt(
			user1=user1.id,
			user2=user2.id,
			is_manual=True,
			deleted=deleted,
		)
		_save_alt_state(user1, user2, link, deleted)
		_record_alt_action(v, user1, user2, deleted)

	word = 'Delinked' if deleted else 'Linked'
	return {'message': f'{word} @{user1.username} and @{user2.username} successfully!'}


@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@admin_level_required(PERMS['USER_LINK'])
def _admin_delink_relink_alt_fixed(v, username, other):
	deleted = request.method == 'PUT'
	user1 = get_user(username)
	user2 = get_account(other)
	link = _get_alt_link(user1.id, user2.id)
	if not link:
		abort(404)

	was_deleted = bool(link.deleted)
	if was_deleted == deleted:
		state = 'delinked' if deleted else 'linked'
		return {'message': f'@{user1.username} and @{user2.username} are already {state}.'}

	_save_alt_state(user1, user2, link, deleted)
	_record_alt_action(v, user1, user2, deleted, relinked=not deleted)
	word = 'Delinked' if deleted else 'Relinked'
	return {'message': f'{word} @{user1.username} and @{user2.username} successfully!'}


def install_alt_link_fixes():
	"""Replace the legacy alt handlers after admin routes have been registered."""
	app.view_functions['admin_add_alt'] = _admin_add_alt_fixed
	app.view_functions['admin_delink_relink_alt'] = _admin_delink_relink_alt_fixed
