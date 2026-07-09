import time
from urllib.parse import quote, urlencode
from math import floor

from sqlalchemy.exc import IntegrityError
from psycopg2.errors import UniqueViolation

from files.__main__ import app, cache, limiter
from files.classes import *
from files.helpers.actions import *
from files.helpers.alerts import *
from files.helpers.cloudflare import *
from files.helpers.config.const import *
from files.helpers.get import *
from files.helpers.media import *
from files.helpers.sanitize import *
from files.helpers.security import *
from files.helpers.settings import get_settings, toggle_setting
from files.helpers.useractions import *
from files.routes.routehelpers import check_for_alts
from files.routes.wrappers import *
from files.routes.routehelpers import get_alt_graph, get_alt_graph_ids

from .front import frontlist, comment_idlist

@app.get('/admin/loggedin')
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@admin_level_required(PERMS['VIEW_ACTIVE_USERS'])
def loggedin_list(v):
	ids = [x for x,val in cache.get(f'{SITE}_loggedin').items() if time.time()-val < LOGGEDIN_ACTIVE_TIME]
	users = g.db.query(User).filter(User.id.in_(ids)).order_by(User.admin_level.desc(), User.truescore.desc()).all()
	return render_template("admin/loggedin.html", v=v, users=users)

@app.get('/admin/loggedout')
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@admin_level_required(PERMS['VIEW_ACTIVE_USERS'])
def loggedout_list(v):
	users = sorted([val[1] for x,val in cache.get(f'{SITE}_loggedout').items() if time.time()-val[0] < LOGGEDIN_ACTIVE_TIME])
	return render_template("admin/loggedout.html", v=v, users=users)

@app.get('/admin/dm_images')
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@admin_level_required(PERMS['VIEW_DM_IMAGES'])
def dm_images(v):
	with open(f"{LOG_DIRECTORY}/dm_images.log", "r", encoding="utf-8") as f:
		items=f.read().split("\n")[:-1]

	items = [x.split(", ") for x in items]

	return render_template("admin/dm_images.html", v=v, items=items)

@app.get('/admin/edit_rules')
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@admin_level_required(PERMS['EDIT_RULES'])
def edit_rules_get(v):
	try:
		with open(f'files/templates/rules_{SITE_NAME}.html', 'r', encoding="utf-8") as f:
			rules = f.read()
	except:
		rules = None
	return render_template('admin/edit_rules.html', v=v, rules=rules)


@app.post('/admin/edit_rules')
@limiter.limit("1/second;30/minute;200/hour;1000/day")
@limiter.limit("1/second;30/minute;200/hour;1000/day", key_func=get_ID)
@admin_level_required(PERMS['EDIT_RULES'])
def edit_rules_post(v):
	rules = request.values.get('rules', '').strip()
	rules = sanitize(rules, sidebar=True, showmore=False)

	with open(f'files/templates/rules_{SITE_NAME}.html', 'w+', encoding="utf-8") as f:
		f.write(rules)

	ma = ModAction(
		kind="edit_rules",
		user_id=v.id,
	)
	g.db.add(ma)
	return render_template('admin/edit_rules.html', v=v, rules=rules, msg='Rules edited successfully!')

@app.post("/@<username>/make_admin")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@admin_level_required(PERMS['ADMIN_ADD'])
def make_admin(v:User, username):
	user = get_user(username)

	user.admin_level = 1
	g.db.add(user)

	ma = ModAction(
		kind="make_admin",
		user_id=v.id,
		target_user_id=user.id
	)
	g.db.add(ma)

	send_repeatable_notification(user.id, f"@{v.username} added you as an admin!")

	return {"message": f"@{user.username} has been made admin!"}


@app.post("/@<username>/remove_admin")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@admin_level_required(PERMS['ADMIN_REMOVE'])
def remove_admin(v:User, username):
	if SITE == 'devrama.net':
		abort(403, "You can't remove admins on devrama!")

	user = get_user(username)

	if user.admin_level > v.admin_level:
		abort(403)

	if user.admin_level:
		user.admin_level = 0
		g.db.add(user)

		ma = ModAction(
			kind="remove_admin",
			user_id=v.id,
			target_user_id=user.id
		)
		g.db.add(ma)

		send_repeatable_notification(user.id, f"@{v.username} removed you as an admin!")

	return {"message": f"@{user.username} has been removed as admin!"}

@app.post("/distribute/<int:option_id>")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@admin_level_required(PERMS['POST_BETS_DISTRIBUTE'])
def distribute(v:User, option_id):
	autojanny = get_account(AUTOJANNY_ID)
	if autojanny.coins == 0: abort(400, "@AutoJanny has 0 coins")

	try: option_id = int(option_id)
	except: abort(400)

	try: option = g.db.get(SubmissionOption, option_id)
	except: abort(404)

	if option.exclusive != 2: abort(403)

	option.exclusive = 3
	g.db.add(option)

	post = option.post

	pool = 0
	for o in post.options:
		if o.exclusive >= 2: pool += o.upvotes
	pool *= POLL_BET_COINS

	autojanny.charge_account('coins', pool)
	if autojanny.coins < 0: autojanny.coins = 0
	g.db.add(autojanny)

	votes = option.votes
	coinsperperson = int(pool / len(votes))

	cid = notif_comment(f"You won {coinsperperson} coins betting on [{post.title}]({post.shortlink}) :marseyparty:")
	for vote in votes:
		u = vote.user
		u.pay_account('coins', coinsperperson)
		add_notif(cid, u.id)


	cid = notif_comment(f"You lost the {POLL_BET_COINS} coins you bet on [{post.title}]({post.shortlink}) :marseylaugh:")
	losing_voters = []
	for o in post.options:
		if o.exclusive == 2:
			losing_voters.extend([x.user_id for x in o.votes])
	for uid in losing_voters:
		add_notif(cid, uid)

	ma = ModAction(
		kind="distribute",
		user_id=v.id,
		target_submission_id=post.id
	)
	g.db.add(ma)

	return {"message": f"Each winner has received {coinsperperson} coins!"}

@app.post("/@<username>/revert_actions")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@admin_level_required(PERMS['ADMIN_ACTIONS_REVERT'])
def revert_actions(v:User, username):
	revertee = get_user(username)

	if revertee.admin_level > v.admin_level:
		abort(403)

	ma = ModAction(
		kind="revert",
		user_id=v.id,
		target_user_id=revertee.id
	)
	g.db.add(ma)

	cutoff = int(time.time()) - 86400

	posts = [x[0] for x in g.db.query(ModAction.target_submission_id).filter(ModAction.user_id == revertee.id, ModAction.created_utc > cutoff, ModAction.kind == 'ban_post').all()]
	posts = g.db.query(Submission).filter(Submission.id.in_(posts)).all()

	comments = [x[0] for x in g.db.query(ModAction.target_comment_id).filter(ModAction.user_id == revertee.id, ModAction.created_utc > cutoff, ModAction.kind == 'ban_comment').all()]
	comments = g.db.query(Comment).filter(Comment.id.in_(comments)).all()

	for item in posts + comments:
		item.is_banned = False
		item.ban_reason = None
		item.is_approved = v.id
		g.db.add(item)

	users = (x[0] for x in g.db.query(ModAction.target_user_id).filter(ModAction.user_id == revertee.id, ModAction.created_utc > cutoff, ModAction.kind.in_(('shadowban', 'ban_user'))).all())
	users = g.db.query(User).filter(User.id.in_(users)).all()

	for user in users:
		user.shadowbanned = None
		user.unban_utc = 0
		user.ban_reason = None
		if user.is_banned:
			user.is_banned = None
			send_repeatable_notification(user.id, f"@{v.username} (a site admin) has unbanned you!")
		g.db.add(user)

		for u in get_alt_graph(user.id):
			u.shadowbanned = None
			u.unban_utc = 0
			u.ban_reason = None
			if u.is_banned:
				u.is_banned = None
				send_repeatable_notification(u.id, f"@{v.username} (a site admin) has unbanned you!")
			g.db.add(u)

	return {"message": f"@{revertee.username}'s admin actions have been reverted!"}

@app.get("/admin/shadowbanned")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@admin_level_required(PERMS['USER_SHADOWBAN'])
def shadowbanned(v):
	users = g.db.query(User) \
		.filter(
			User.shadowbanned != None,
		) \
		.order_by(User.ban_reason).all()

	return render_template("admin/shadowbanned.html", v=v, users=users)


@app.get("/admin/image_posts")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@admin_level_required(PERMS['POST_COMMENT_MODERATION'])
def image_posts_listing(v):

	try: page = int(request.values.get('page', 1))
	except: page = 1

	posts = g.db.query(Submission).order_by(Submission.id.desc())

	firstrange = PAGE_SIZE * (page - 1)
	secondrange = firstrange + PAGE_SIZE + 1
	posts = [x.id for x in posts if x.is_image][firstrange:secondrange]
	next_exists = (len(posts) > PAGE_SIZE)
	posts = get_posts(posts[:PAGE_SIZE], v=v)

	return render_template("admin/image_posts.html", v=v, listing=posts, next_exists=next_exists, page=page, sort="new")


@app.get("/admin/reported/posts")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@admin_level_required(PERMS['POST_COMMENT_MODERATION'])
def reported_posts(v):

	try: page = max(1, int(request.values.get("page", 1)))
	except: abort(400, "Invalid page input!")

	listing = g.db.query(Submission).filter_by(
		is_approved=None,
		is_banned=False,
		deleted_utc=0
	).join(Submission.flags).order_by(Submission.id.desc()).offset(PAGE_SIZE * (page - 1)).limit(PAGE_SIZE+1)

	listing = [p.id for p in listing]
	next_exists = len(listing) > PAGE_SIZE
	listing = listing[:PAGE_SIZE]

	listing = get_posts(listing, v=v)

	return render_template("admin/reported_posts.html",
						next_exists=next_exists, listing=listing, page=page, v=v)


@app.get("/admin/reported/comments")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@admin_level_required(PERMS['POST_COMMENT_MODERATION'])
def reported_comments(v):

	try: page = max(1, int(request.values.get("page", 1)))
	except: abort(400, "Invalid page input!")

	listing = g.db.query(Comment
					).filter_by(
		is_approved=None,
		is_banned=False,
		deleted_utc=0
	).join(Comment.flags).order_by(Comment.id.desc()).offset(PAGE_SIZE * (page - 1)).limit(PAGE_SIZE+1).all()

	listing = [c.id for c in listing]
	next_exists = len(listing) > PAGE_SIZE
	listing = listing[:PAGE_SIZE]

	listing = get_comments(listing, v=v)

	return render_template("admin/reported_comments.html",
						next_exists=next_exists,
						listing=listing,
						page=page,
						v=v,
						standalone=True)

@app.get("/admin")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@admin_level_required(PERMS['ADMIN_HOME_VISIBLE'])
def admin_home(v):
	under_attack = False

	if v.admin_level >= PERMS['SITE_SETTINGS_UNDER_ATTACK']:
		under_attack = (get_security_level() or 'high') == 'under_attack'

	return render_template("admin/admin_home.html", v=v,
		under_attack=under_attack)

@app.post("/admin/site_settings/<setting>")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@admin_level_required(PERMS['SITE_SETTINGS'])
def change_settings(v:User, setting):
	if SITE == 'devrama.net':
		abort(403, "Can't change this shit in devrama!")

	if setting not in get_settings().keys():
		abort(404, f"Setting '{setting}' not found")
	val = toggle_setting(setting)
	if val: word = 'enable'
	else: word = 'disable'

	if setting != 'login_required':
		ma = ModAction(
			kind=f"{word}_{setting}",
			user_id=v.id,
		)
		g.db.add(ma)

	return {'message': f"{setting.replace('_', ' ').title()} {word}d successfully!"}

@app.post("/admin/clear_cloudflare_cache")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@admin_level_required(PERMS['SITE_CACHE_PURGE_CDN'])
def clear_cloudflare_cache(v):
	if not clear_entire_cache():
		abort(400, 'Failed to clear cloudflare cache!')
	ma = ModAction(
		kind="clear_cloudflare_cache",
		user_id=v.id
	)
	g.db.add(ma)
	return {"message": "Cloudflare cache cleared!"}

@app.post("/admin/under_attack")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@admin_level_required(PERMS['SITE_SETTINGS_UNDER_ATTACK'])
def under_attack(v):
	response = get_security_level()
	if not response:
		abort(400, 'Could not retrieve the current security level')
	old_under_attack_mode = response == 'under_attack'
	enable_disable_str = 'disable' if old_under_attack_mode else 'enable'
	new_security_level = 'high' if old_under_attack_mode else 'under_attack'
	if not set_security_level(new_security_level):
		abort(400, f'Failed to {enable_disable_str} under attack mode')
	ma = ModAction(
		kind=f"{enable_disable_str}_under_attack",
		user_id=v.id,
	)
	g.db.add(ma)
	return {"message": f"Under attack mode {enable_disable_str}d!"}

def admin_badges_grantable_list(v):
	query = g.db.query(BadgeDef)

	if BADGE_BLACKLIST and v.admin_level < PERMS['IGNORE_BADGE_BLACKLIST']:
		query = query.filter(BadgeDef.id.notin_(BADGE_BLACKLIST))

	badge_types = query.order_by(BadgeDef.id).all()
	return badge_types

@app.get("/admin/badge_grant")
@app.get("/admin/badge_remove")
@feature_required('BADGES')
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@admin_level_required(PERMS['USER_BADGES'])
def badge_grant_get(v):
	grant = request.url.endswith("grant")
	badge_types = admin_badges_grantable_list(v)

	return render_template("admin/badge_admin.html", v=v,
		badge_types=badge_types, grant=grant)

@app.post("/admin/badge_grant")
@feature_required('BADGES')
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@admin_level_required(PERMS['USER_BADGES'])
def badge_grant_post(v):
	badges = admin_badges_grantable_list(v)

	user = get_user(request.values.get("username"), graceful=True)
	if not user:
		return render_template("admin/badge_admin.html", v=v, badge_types=badges, grant=True, error="User not found!")

	try: badge_id = int(request.values.get("badge_id"))
	except: abort(400)

	if badge_id not in [b.id for b in badges]:
		abort(403, "You can't grant this badge!")

	description = request.values.get("description")
	url = request.values.get("url")

	if url:
		if '\\' in url: abort(400)
		if url.startswith(SITE_FULL):
			url = url.split(SITE_FULL, 1)[1]
		elif url.startswith(BAN_EVASION_FULL):
			url = url.split(BAN_EVASION_FULL, 1)[1]

	existing = user.has_badge(badge_id)
	if existing:
		if url or description:
			existing.url = url
			existing.description = description
			g.db.add(existing)
			return render_template("admin/badge_admin.html", v=v, badge_types=badges, grant=True, msg="Badge attributes edited successfully!")
		return render_template("admin/badge_admin.html", v=v, badge_types=badges, grant=True, error="User already has that badge!")

	new_badge = Badge(
		badge_id=badge_id,
		user_id=user.id,
		url=url,
		description=description
		)

	g.db.add(new_badge)
	g.db.flush()

	if v.id != user.id:
		text = f"@{v.username} (a site admin) has given you the following profile badge:\n\n![]({new_badge.path})\n\n**{new_badge.name}**\n\n{new_badge.badge.description}"
		send_repeatable_notification(user.id, text)

	ma = ModAction(
		kind="badge_grant",
		user_id=v.id,
		target_user_id=user.id,
		_note=new_badge.name
	)
	g.db.add(ma)

	return render_template("admin/badge_admin.html", v=v, badge_types=badges, grant=True, msg=f"{new_badge.name} Badge granted to @{user.username} successfully!")

@app.post("/admin/badge_remove")
@feature_required('BADGES')
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@admin_level_required(PERMS['USER_BADGES'])
def badge_remove_post(v):
	badges = admin_badges_grantable_list(v)

	user = get_user(request.values.get("username"), graceful=True)
	if not user:
		return render_template("admin/badge_admin.html", v=v, badge_types=badges, grant=False, error="User not found!")

	try: badge_id = int(request.values.get("badge_id"))
	except: abort(400)

	if badge_id not in [b.id for b in badges]:
		abort(403)

	badge = user.has_badge(badge_id)
	if not badge:
		return render_template("admin/badge_admin.html", v=v, badge_types=badges, grant=False, error="User doesn't have that badge!")

	if v.id != user.id:
		text = f"@{v.username} (a site admin) has removed the following profile badge from you:\n\n![]({badge.path})\n\n**{badge.name}**\n\n{badge.badge.description}"
		send_repeatable_notification(user.id, text)

	ma = ModAction(
		kind="badge_remove",
		user_id=v.id,
		target_user_id=user.id,
		_note=badge.name
	)
	g.db.add(ma)
	g.db.delete(badge)
	return render_template("admin/badge_admin.html", v=v, badge_types=badges, grant=False, msg=f"{badge.name} Badge removed from @{user.username} successfully!")


@app.get("/admin/alt_votes")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@admin_level_required(PERMS['VIEW_ALT_VOTES'])
def alt_votes_get(v):
	u1 = request.values.get("u1")
	u2 = request.values.get("u2")

	if not u1 or not u2:
		return render_template("admin/alt_votes.html", v=v)

	u1 = get_user(u1)
	u2 = get_user(u2)

	u1_post_ups = g.db.query(
		Vote.submission_id).filter_by(
		user_id=u1.id,
		vote_type=1).all()
	u1_post_downs = g.db.query(
		Vote.submission_id).filter_by(
		user_id=u1.id,
		vote_type=-1).all()
	u1_comment_ups = g.db.query(
		CommentVote.comment_id).filter_by(
		user_id=u1.id,
		vote_type=1).all()
	u1_comment_downs = g.db.query(
		CommentVote.comment_id).filter_by(
		user_id=u1.id,
		vote_type=-1).all()
	u2_post_ups = g.db.query(
		Vote.submission_id).filter_by(
		user_id=u2.id,
		vote_type=1).all()
	u2_post_downs = g.db.query(
		Vote.submission_id).filter_by(
		user_id=u2.id,
		vote_type=-1).all()
	u2_comment_ups = g.db.query(
		CommentVote.comment_id).filter_by(
		user_id=u2.id,
		vote_type=1).all()
	u2_comment_downs = g.db.query(
		CommentVote.comment_id).filter_by(
		user_id=u2.id,
		vote_type=-1).all()

	data = {}
	data['u1_only_post_ups'] = len(
		[x for x in u1_post_ups if x not in u2_post_ups])
	data['u2_only_post_ups'] = len(
		[x for x in u2_post_ups if x not in u1_post_ups])
	data['both_post_ups'] = len(list(set(u1_post_ups) & set(u2_post_ups)))

	data['u1_only_post_downs'] = len(
		[x for x in u1_post_downs if x not in u2_post_downs])
	data['u2_only_post_downs'] = len(
		[x for x in u2_post_downs if x not in u1_post_downs])
	data['both_post_downs'] = len(
		list(set(u1_post_downs) & set(u2_post_downs)))

	data['u1_only_comment_ups'] = len(
		[x for x in u1_comment_ups if x not in u2_comment_ups])
	data['u2_only_comment_ups'] = len(
		[x for x in u2_comment_ups if x not in u1_comment_ups])
	data['both_comment_ups'] = len(
		list(set(u1_comment_ups) & set(u2_comment_ups)))

	data['u1_only_comment_downs'] = len(
		[x for x in u1_comment_downs if x not in u2_comment_downs])
	data['u2_only_comment_downs'] = len(
		[x for x in u2_comment_downs if x not in u1_comment_downs])
	data['both_comment_downs'] = len(
		list(set(u1_comment_downs) & set(u2_comment_downs)))

	data['u1_post_ups_unique'] = 100 * \
		data['u1_only_post_ups'] // len(u1_post_ups) if u1_post_ups else 0
	data['u2_post_ups_unique'] = 100 * \
		data['u2_only_post_ups'] // len(u2_post_ups) if u2_post_ups else 0
	data['u1_post_downs_unique'] = 100 * \
		data['u1_only_post_downs'] // len(
			u1_post_downs) if u1_post_downs else 0
	data['u2_post_downs_unique'] = 100 * \
		data['u2_only_post_downs'] // len(
			u2_post_downs) if u2_post_downs else 0

	data['u1_comment_ups_unique'] = 100 * \
		data['u1_only_comment_ups'] // len(
			u1_comment_ups) if u1_comment_ups else 0
	data['u2_comment_ups_unique'] = 100 * \
		data['u2_only_comment_ups'] // len(
			u2_comment_ups) if u2_comment_ups else 0
	data['u1_comment_downs_unique'] = 100 * \
		data['u1_only_comment_downs'] // len(
			u1_comment_downs) if u1_comment_downs else 0
	data['u2_comment_downs_unique'] = 100 * \
		data['u2_only_comment_downs'] // len(
			u2_comment_downs) if u2_comment_downs else 0

	return render_template("admin/alt_votes.html",
						u1=u1,
						u2=u2,
						v=v,
						data=data
						)

@app.get("/admin/alts/")
@app.get("/@<username>/alts/")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@admin_level_required(PERMS['USER_LINK'])
def admin_view_alts(v:User, username=None):
	u = get_user(username or request.values.get('username'), graceful=True)
	return render_template('admin/alts.html', v=v, u=u, alts=u.alts if u else None)

@app.post('/@<username>/alts/')
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@admin_level_required(PERMS['USER_LINK'])
def admin_add_alt(v:User, username):
	user1 = get_user(username)
	user2 = get_user(request.values.get('other_username'))
	if user1.id == user2.id: abort(400, "Can't add the same account as alts of each other")

	deleted = request.values.get('deleted', False, bool) or False
	ids = [user1.id, user2.id]
	a = g.db.query(Alt).filter(Alt.user1.in_(ids), Alt.user2.in_(ids)).one_or_none()
	if a: abort(409, f"@{user1.username} and @{user2.username} are already known {'linked' if not a.deleted else 'delinked'} alts")
	a = Alt(
		user1=user1.id,
		user2=user2.id,
		is_manual=True,
		deleted=deleted
	)
	g.db.add(a)
	g.db.flush()

	cache.delete_memoized(get_alt_graph_ids, user1.id)
	cache.delete_memoized(get_alt_graph_ids, user2.id)

	check_for_alts(user1)
	check_for_alts(user2)

	word = 'Delinked' if deleted else 'Linked'
	ma_word = 'delink' if deleted else 'link'
	note = f'from @{user2.username}' if deleted else f'with @{user2.username}'
	ma = ModAction(
		kind=f"{ma_word}_accounts",
		user_id=v.id,
		target_user_id=user1.id,
		_note=note
	)
	g.db.add(ma)
	return {"message": f"{word} @{user1.username} and @{user2.username} successfully!"}

@app.route('/@<username>/alts/<int:other>/deleted', methods=["PUT", "DELETE"])
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@admin_level_required(PERMS['USER_LINK'])
def admin_delink_relink_alt(v:User, username, other):
	is_delinking = request.method == 'PUT' # we're adding the 'deleted' state if a PUT request
	user1 = get_user(username)
	user2 = get_account(other)
	ids = [user1.id, user2.id]
	a = g.db.query(Alt).filter(Alt.user1.in_(ids), Alt.user2.in_(ids)).one_or_none()
	if not a: abort(404)
	a.deleted = is_delinking
	g.db.add(a)
	g.db.flush()
	check_for_alts(user1)
	check_for_alts(user2)
	word = 'Delinked' if is_delinking else 'Relinked'
	ma_word = 'delink' if is_delinking else 'link'
	note = f'from @{user2.username}' if is_delinking else f'with @{user2.username} (relinked)'

	ma = ModAction(
		kind=f"{ma_word}_accounts",
		user_id=v.id,
		target_user_id=user1.id,
		_note=note
	)
	g.db.add(ma)

	return {"message": f"{word} @{user1.username} and @{user2.username} successfully!"}


@app.get("/admin/removed/posts")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@admin_level_required(PERMS['POST_COMMENT_MODERATION'])
def admin_removed(v):
	try: page = int(request.values.get("page", 1))
	except: page = 1
	if page < 1: abort(400)
	ids = g.db.query(Submission.id).join(Submission.author).filter(or_(Submission.is_banned==True, User.shadowbanned != None)).order_by(Submission.id.desc()).offset(PAGE_SIZE * (page - 1)).limit(PAGE_SIZE + 1).all()
	ids=[x[0] for x in ids]
	next_exists = len(ids) > PAGE_SIZE
	ids = ids[:PAGE_SIZE]

	posts = get_posts(ids, v=v)

	return render_template("admin/removed_posts.html",
						v=v,
						listing=posts,
						page=page,
						next_exists=next_exists
						)


@app.get("/admin/removed/comments")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@admin_level_required(PERMS['POST_COMMENT_MODERATION'])
def admin_removed_comments(v):
	try: page = int(request.values.get("page", 1))
	except: page = 1

	ids = g.db.query(Comment.id).join(Comment.author).filter(or_(Comment.is_banned==True, User.shadowbanned != None)).order_by(Comment.id.desc()).offset(PAGE_SIZE * (page - 1)).limit(PAGE_SIZE + 1).all()
	ids=[x[0] for x in ids]
	next_exists = len(ids) > PAGE_SIZE
	ids = ids[:PAGE_SIZE]
	comments = get_comments(ids, v=v)
	return render_template("admin/removed_comments.html",
						v=v,
						listing=comments,
						page=page,
						next_exists=next_exists
						)

@app.post("/unagendaposter/<id>")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@admin_level_required(PERMS['USER_AGENDAPOSTER'])
def unagendaposter(id, v):

	if id.startswith('p_'):
		post_id = id.split('p_')[1]
		post = g.db.get(Submission, post_id)
		user = post.author
	elif id.startswith('c_'):
		comment_id = id.split('c_')[1]
		comment = g.db.get(Comment, comment_id)
		user = comment.author
	else:
		user = get_account(id)

	if not user.chudded_by:
		abort(403, "Jannies can't undo chud awards anymore!")

	user.agendaposter = 0
	g.db.add(user)

	ma = ModAction(
		kind="unchud",
		user_id=v.id,
		target_user_id=user.id
	)

	g.db.add(ma)

	badge = user.has_badge(28)
	if badge: g.db.delete(badge)

	send_repeatable_notification(user.id, f"@{v.username} (a site admin) has unchudded you.")

	return {"message": f"@{user.username} has been unchudded!"}


@app.post("/shadowban/<int:user_id>")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@admin_level_required(PERMS['USER_SHADOWBAN'])
def shadowban(user_id, v):
	user = get_account(user_id)
	if user.admin_level > v.admin_level:
		abort(403)
	user.shadowbanned = v.id
	reason = request.values.get("reason", "").strip()[:256]

	if not reason:
		abort(400, "You need to submit a reason for shadowbanning!")

	reason = filter_emojis_only(reason)
	user.ban_reason = reason
	g.db.add(user)
	check_for_alts(user)

	ma = ModAction(
		kind="shadowban",
		user_id=v.id,
		target_user_id=user.id,
		_note=f'reason: "{reason}"'
	)
	g.db.add(ma)

	cache.delete_memoized(frontlist)

	return {"message": f"@{user.username} has been shadowbanned!"}

@app.post("/unshadowban/<int:user_id>")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@admin_level_required(PERMS['USER_SHADOWBAN'])
def unshadowban(user_id, v):
	user = get_account(user_id)
	user.shadowbanned = None
	if not user.is_banned: user.ban_reason = None
	g.db.add(user)

	for alt in get_alt_graph(user.id):
		alt.shadowbanned = None
		if not alt.is_banned: alt.ban_reason = None
		g.db.add(alt)

	ma = ModAction(
		kind="unshadowban",
		user_id=v.id,
		target_user_id=user.id,
	)
	g.db.add(ma)

	cache.delete_memoized(frontlist)

	return {"message": f"@{user.username} has been unshadowbanned!"}


@app.post("/admin/title_change/<int:user_id>")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@admin_level_required(PERMS['USER_TITLE_CHANGE'])
def admin_title_change(user_id, v):

	user = get_account(user_id)

	new_name=request.values.get("title").strip()[:256]

	user.customtitleplain=new_name
	new_name = filter_emojis_only(new_name)
	new_name = censor_slurs(new_name, None)

	user=get_account(user.id)
	user.customtitle=new_name
	if request.values.get("locked"): user.flairchanged = int(time.time()) + 2629746
	else:
		user.flairchanged = None
		badge = user.has_badge(96)
		if badge: g.db.delete(badge)

	g.db.add(user)

	if user.flairchanged: kind = "set_flair_locked"
	else: kind = "set_flair_notlocked"

	ma=ModAction(
		kind=kind,
		user_id=v.id,
		target_user_id=user.id,
		_note=f'"{new_name}"'
		)
	g.db.add(ma)

	return {"message": f"@{user.username}'s flair has been changed!"}

@app.post("/ban_user/<id>")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@admin_level_required(PERMS['USER_BAN'])
def ban_user(id, v):

	if id.startswith('p_'):
		post_id = id.split('p_')[1]
		post = g.db.get(Submission, post_id)
		user = post.author
	elif id.startswith('c_'):
		comment_id = id.split('c_')[1]
		comment = g.db.get(Comment, comment_id)
		user = comment.author
	else:
		user = get_account(id)

	if user.admin_level > v.admin_level:
		abort(403)

	days = 0.0
	try:
		days = float(request.values.get("days"))
	except:
		pass

	if days < 0:
		abort(400, "You can't bans people for negative days!")

	reason = request.values.get("reason", "").strip()[:256]

	if not reason:
		abort(400, "You need to submit a reason for banning!")

	reason = filter_emojis_only(reason)

	reason = reason_regex.sub(r'<a href="\1">\1</a>', reason)

	user.ban(admin=v, reason=reason, days=days)

	if request.values.get("alts"):
		for x in get_alt_graph(user.id):
			if x.admin_level > v.admin_level:
				continue
			x.ban(admin=v, reason=reason, days=days)

	duration = "permanently"
	if days:
		days_txt = str(days)
		if days_txt.endswith('.0'): days_txt = days_txt[:-2]
		duration = f"for {days_txt} day"
		if days != 1: duration += "s"
		if reason: text = f"@{v.username} (a site admin) has banned you for **{days_txt}** days for the following reason:\n\n> {reason}"
		else: text = f"@{v.username} (a site admin) has banned you for **{days_txt}** days."
	else:
		if reason: text = f"@{v.username} (a site admin) has banned you permanently for the following reason:\n\n> {reason}"
		else: text = f"@{v.username} (a site admin) has banned you permanently."

	send_repeatable_notification(user.id, text)

	note = f'duration: {duration}, reason: "{reason}"'
	ma=ModAction(
		kind="ban_user",
		user_id=v.id,
		target_user_id=user.id,
		_note=note
		)
	g.db.add(ma)

	if 'reason' in request.values:
		if request.values["reason"].startswith("/post/"):
			try: post = int(request.values["reason"].split("/post/")[1].split(None, 1)[0])
			except: abort(400)
			post = get_post(post)
			post.bannedfor = f'{duration} by @{v.username}'
			g.db.add(post)
		elif request.values["reason"].startswith("/comment/"):
			try: comment = int(request.values["reason"].split("/comment/")[1].split(None, 1)[0])
			except: abort(400)
			comment = get_comment(comment)
			comment.bannedfor = f'{duration} by @{v.username}'
			g.db.add(comment)

	return {"message": f"@{user.username} has been banned {duration}!"}


@app.post("/agendaposter/<id>")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@admin_level_required(PERMS['USER_AGENDAPOSTER'])
def agendaposter(id, v):

	if id.startswith('p_'):
		post_id = id.split('p_')[1]
		post = g.db.get(Submission, post_id)
		user = post.author
	elif id.startswith('c_'):
		comment_id = id.split('c_')[1]
		comment = g.db.get(Comment, comment_id)
		user = comment.author
	else:
		user = get_account(id)

	if user.admin_level > v.admin_level:
		abort(403)

	days = 0.0
	try:
		days = float(request.values.get("days"))
	except:
		pass

	if days < 0:
		abort(400, "You can't chud people for negative days!")

	reason = request.values.get("reason", "").strip()

	reason = filter_emojis_only(reason)

	reason = reason_regex.sub(r'<a href="\1">\1</a>', reason)

	duration = "permanently"
	if days:
		user.agendaposter = int(time.time()) + (days * 86400)
		days_txt = str(days)
		if days_txt.endswith('.0'): days_txt = days_txt[:-2]
		duration = f"for {days_txt} day"
		if days != 1: duration += "s"
		if reason: text = f"@{v.username} (a site admin) has chudded you for **{days_txt}** days for the following reason:\n\n> {reason}"
		else: text = f"@{v.username} (a site admin) has chudded you for **{days_txt}** days."
	else:
		user.agendaposter = 1
		if reason: text = f"@{v.username} (a site admin) has chudded you permanently for the following reason:\n\n> {reason}"
		else: text = f"@{v.username} (a site admin) has chudded you permanently."

	user.chudded_by = v.id
	g.db.add(user)

	send_repeatable_notification(user.id, text)

	note = f'duration: {duration}'
	if reason: note += f', reason: "{reason}"'

	ma=ModAction(
		kind="chud",
		user_id=v.id,
		target_user_id=user.id,
		_note=note
		)
	g.db.add(ma)

	badge_grant(user=user, badge_id=28)

	if 'reason' in request.values:
		if request.values["reason"].startswith("/post/"):
			try: post = int(request.values["reason"].split("/post/")[1].split(None, 1)[0])
			except: abort(400)
			post = get_post(post)
			if post.sub == 'chudrama':
				abort(403, "You can't chud people in /h/chudrama")
			post.chuddedfor = f'{duration} by @{v.username}'
			g.db.add(post)
		elif request.values["reason"].startswith("/comment/"):
			try: comment = int(request.values["reason"].split("/comment/")[1].split(None, 1)[0])
			except: abort(400)
			comment = get_comment(comment)
			if comment.post.sub == 'chudrama':
				abort(403, "You can't chud people in /h/chudrama")
			comment.chuddedfor = f'{duration} by @{v.username}'
			g.db.add(comment)

	return {"message": f"@{user.username} has been chudded {duration}!"}


@app.post("/unban_user/<id>")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@admin_level_required(PERMS['USER_BAN'])
def unban_user(id, v):

	if id.startswith('p_'):
		post_id = id.split('p_')[1]
		post = g.db.get(Submission, post_id)
		user = post.author
	elif id.startswith('c_'):
		comment_id = id.split('c_')[1]
		comment = g.db.get(Comment, comment_id)
		user = comment.author
	else:
		user = get_account(id)

	if not user.is_banned:
		abort(400)

	if FEATURES['AWARDS'] and user.ban_reason and user.ban_reason.startswith('1-Day ban award'):
		abort(403, "You can't undo a ban award!")

	user.is_banned = None
	user.unban_utc = 0
	user.ban_reason = None
	send_repeatable_notification(user.id, f"@{v.username} (a site admin) has unbanned you!")
	g.db.add(user)

	for x in get_alt_graph(user.id):
		if x.is_banned: send_repeatable_notification(x.id, f"@{v.username} (a site admin) has unbanned you!")
		x.is_banned = None
		x.unban_utc = 0
		x.ban_reason = None
		g.db.add(x)

	ma=ModAction(
		kind="unban_user",
		user_id=v.id,
		target_user_id=user.id,
		)
	g.db.add(ma)

	return {"message": f"@{user.username} has been unbanned!"}

@app.post("/mute_user/<int:user_id>")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@admin_level_required(PERMS['USER_BAN'])
def mute_user(v:User, user_id):
	user = get_account(user_id)

	if not user.is_muted:
		user.is_muted = True
		ma = ModAction(
				kind='mod_mute_user',
				user_id=v.id,
				target_user_id=user.id,
				)
		g.db.add(user)
		g.db.add(ma)
		check_for_alts(user)

	return {"message": f"@{user.username} has been muted!"}


@app.post("/unmute_user/<int:user_id>")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@admin_level_required(PERMS['USER_BAN'])
def unmute_user(v:User, user_id):
	user = get_account(user_id)

	if user.is_muted:
		user.is_muted = False
		ma = ModAction(
				kind='mod_unmute_user',
				user_id=v.id,
				target_user_id=user.id,
				)
		g.db.add(user)
		g.db.add(ma)

	return {"message": f"@{user.username} has been unmuted!"}

@app.post("/admin/progstack/post/<int:post_id>")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@admin_level_required(PERMS['PROGSTACK'])
def progstack_post(post_id, v):
	post = get_post(post_id)
	post.is_approved = PROGSTACK_ID
	post.realupvotes = floor(post.realupvotes * PROGSTACK_MUL)
	g.db.add(post)

	ma=ModAction(
		kind="progstack_post",
		user_id=v.id,
		target_submission_id=post.id,
		)
	g.db.add(ma)

	cache.delete_memoized(frontlist)
	return {"message": "Progressive stack applied on post!"}

@app.post("/admin/progstack/comment/<int:comment_id>")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@admin_level_required(PERMS['PROGSTACK'])
def progstack_comment(comment_id, v):
	comment = get_comment(comment_id)
	comment.is_approved = PROGSTACK_ID
	comment.realupvotes = floor(comment.realupvotes * PROGSTACK_MUL)
	g.db.add(comment)

	ma=ModAction(
		kind="progstack_comment",
		user_id=v.id,
		target_comment_id=comment.id,
		)
	g.db.add(ma)

	cache.delete_memoized(comment_idlist)
	return {"message": "Progressive stack applied on comment!"}

@app.post("/remove_post/<int:post_id>")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@admin_level_required(PERMS['POST_COMMENT_MODERATION'])
def remove_post(post_id, v):
	post = get_post(post_id)
	post.is_banned = True
	post.is_approved = None
	if not FEATURES['AWARDS'] or not post.stickied or not post.stickied.endswith(PIN_AWARD_TEXT):
		post.stickied = None
	post.is_pinned = False
	post.ban_reason = v.username
	g.db.add(post)

	ma=ModAction(
		kind="ban_post",
		user_id=v.id,
		target_submission_id=post.id,
		)
	g.db.add(ma)

	cache.delete_memoized(frontlist)

	v.pay_account('coins', 1)
	g.db.add(v)
	purge_files_in_cache(f"https://{SITE}/")
	return {"message": "Post removed!"}


@app.post("/approve_post/<int:post_id>")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@admin_level_required(PERMS['POST_COMMENT_MODERATION'])
def approve_post(post_id, v):
	post = get_post(post_id)

	if post.author.id == v.id and post.author.agendaposter and AGENDAPOSTER_PHRASE not in post.body.lower() and post.sub != 'chudrama':
		abort(400, "You can't bypass the chud award!")

	if post.is_banned:
		ma=ModAction(
			kind="unban_post",
			user_id=v.id,
			target_submission_id=post.id,
		)
		g.db.add(ma)

	post.is_banned = False
	post.ban_reason = None
	post.is_approved = v.id

	g.db.add(post)

	cache.delete_memoized(frontlist)

	v.charge_account('coins', 1)
	g.db.add(v)

	return {"message": "Post approved!"}


@app.post("/distinguish/<int:post_id>")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@admin_level_required(PERMS['POST_COMMENT_DISTINGUISH'])
def distinguish_post(post_id, v):
	post = get_post(post_id)

	if post.distinguish_level:
		post.distinguish_level = 0
		kind = 'undistinguish_post'
	else:
		post.distinguish_level = v.admin_level
		kind = 'distinguish_post'

	g.db.add(post)

	ma = ModAction(
		kind=kind,
		user_id=v.id,
		target_submission_id=post.id
	)
	g.db.add(ma)


	if post.distinguish_level: return {"message": "Post distinguished!"}
	else: return {"message": "Post undistinguished!"}


@app.post("/sticky/<int:post_id>")
@feature_required('PINS')
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@admin_level_required(PERMS['POST_COMMENT_MODERATION'])
def sticky_post(post_id, v):
	post = get_post(post_id)

	if post.is_banned:
		abort(403, "Can't sticky removed posts!")

	if FEATURES['AWARDS'] and post.stickied and post.stickied.endswith(PIN_AWARD_TEXT) and v.admin_level < PERMS["UNDO_AWARD_PINS"]:
		abort(403, "Can't pin award pins!")

	pins = g.db.query(Submission).filter(Submission.stickied != None, Submission.is_banned == False).count()

	if not post.stickied_utc:
		post.stickied_utc = int(time.time()) + 3600
		pin_time = 'for 1 hour'
		code = 200
		if v.id != post.author_id:
			send_repeatable_notification(post.author_id, f"@{v.username} (a site admin) has pinned [{post.title}](/post/{post_id})")
	else:
		if pins >= PIN_LIMIT + 1:
			abort(403, f"Can't exceed {PIN_LIMIT} pinned posts limit!")
		post.stickied_utc = None
		pin_time = 'permanently'
		code = 201

	post.stickied = v.username

	g.db.add(post)

	ma=ModAction(
		kind="pin_post",
		user_id=v.id,
		target_submission_id=post.id,
		_note=pin_time
	)
	g.db.add(ma)

	cache.delete_memoized(frontlist)

	return {"message": f"Post pinned {pin_time}!"}, code


@app.post("/unsticky/<int:post_id>")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@admin_level_required(PERMS['POST_COMMENT_MODERATION'])
def unsticky_post(post_id, v):
	post = get_post(post_id)
	if post.stickied:
		if FEATURES['AWARDS'] and post.stickied.endswith(PIN_AWARD_TEXT) and v.admin_level < PERMS["UNDO_AWARD_PINS"]:
			abort(403, "Can't unpin award pins!")

		if post.author_id == LAWLZ_ID and post.stickied_utc and SITE_NAME == 'rDrama':
			abort(403, "Can't unpin lawlzposts!")

		post.stickied = None
		post.stickied_utc = None
		g.db.add(post)

		ma=ModAction(
			kind="unpin_post",
			user_id=v.id,
			target_submission_id=post.id
		)
		g.db.add(ma)

		if v.id != post.author_id:
			send_repeatable_notification(post.author_id, f"@{v.username} (a site admin) has unpinned [{post.title}](/post/{post_id})")

		cache.delete_memoized(frontlist)
	return {"message": "Post unpinned!"}

@app.post("/sticky_comment/<int:cid>")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@admin_level_required(PERMS['POST_COMMENT_MODERATION'])
def sticky_comment(cid, v):
	comment = get_comment(cid, v=v)

	if comment.is_banned:
		abort(403, "Can't sticky removed comments!")

	if FEATURES['AWARDS'] and comment.stickied and comment.stickied.endswith(PIN_AWARD_TEXT) and v.admin_level < PERMS["UNDO_AWARD_PINS"]:
		abort(403, "Can't pin award pins!")

	if not comment.stickied:
		comment.stickied = v.username
		g.db.add(comment)

		ma=ModAction(
			kind="pin_comment",
			user_id=v.id,
			target_comment_id=comment.id
		)
		g.db.add(ma)

		if v.id != comment.author_id:
			message = f"@{v.username} (a site admin) has pinned your [comment]({comment.shortlink})"
			send_repeatable_notification(comment.author_id, message)

		c = comment
		while c.level > 2:
			c = c.parent_comment
			c.stickied_child_id = comment.id
			g.db.add(c)

	return {"message": "Comment pinned!"}


@app.post("/unsticky_comment/<int:cid>")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@admin_level_required(PERMS['POST_COMMENT_MODERATION'])
def unsticky_comment(cid, v):
	comment = get_comment(cid, v=v)

	if comment.stickied:
		if FEATURES['AWARDS'] and comment.stickied.endswith(PIN_AWARD_TEXT) and v.admin_level < PERMS["UNDO_AWARD_PINS"]:
			abort(403, "Can't unpin award pins!")

		comment.stickied = None
		g.db.add(comment)

		ma=ModAction(
			kind="unpin_comment",
			user_id=v.id,
			target_comment_id=comment.id
		)
		g.db.add(ma)

		if v.id != comment.author_id:
			message = f"@{v.username} (a site admin) has unpinned your [comment]({comment.shortlink})"
			send_repeatable_notification(comment.author_id, message)

		cleanup = g.db.query(Comment).filter_by(stickied_child_id=comment.id).all()
		for c in cleanup:
			c.stickied_child_id = None
			g.db.add(c)

	return {"message": "Comment unpinned!"}


@app.post("/remove_comment/<int:c_id>")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@admin_level_required(PERMS['POST_COMMENT_MODERATION'])
def remove_comment(c_id, v):
	comment = get_comment(c_id)

	comment.is_banned = True
	comment.is_approved = None
	comment.ban_reason = v.username
	g.db.add(comment)
	ma=ModAction(
		kind="ban_comment",
		user_id=v.id,
		target_comment_id=comment.id,
		)
	g.db.add(ma)

	return {"message": "Comment removed!"}


@app.post("/approve_comment/<int:c_id>")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@admin_level_required(PERMS['POST_COMMENT_MODERATION'])
def approve_comment(c_id, v):
	comment = get_comment(c_id)

	if comment.author.id == v.id and comment.author.agendaposter and AGENDAPOSTER_PHRASE not in comment.body.lower() and not (comment.parent_submission and comment.post.sub == 'chudrama'):
		abort(400, "You can't bypass the chud award!")

	if comment.is_banned:
		ma=ModAction(
			kind="unban_comment",
			user_id=v.id,
			target_comment_id=comment.id,
			)
		g.db.add(ma)

	comment.is_banned = False
	comment.ban_reason = None
	comment.is_approved = v.id

	g.db.add(comment)

	return {"message": "Comment approved!"}


@app.post("/distinguish_comment/<int:c_id>")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@admin_level_required(PERMS['POST_COMMENT_DISTINGUISH'])
def admin_distinguish_comment(c_id, v):
	comment = get_comment(c_id, v=v)

	if comment.distinguish_level:
		comment.distinguish_level = 0
		kind = 'undistinguish_comment'
	else:
		comment.distinguish_level = v.admin_level
		kind = 'distinguish_comment'

	g.db.add(comment)

	ma = ModAction(
		kind=kind,
		user_id=v.id,
		target_comment_id=comment.id
	)
	g.db.add(ma)


	if comment.distinguish_level: return {"message": "Comment distinguished!"}
	else: return {"message": "Comment undistinguished!"}

@app.get("/admin/banned_domains/")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@admin_level_required(PERMS['DOMAINS_BAN'])
def admin_banned_domains(v):
	banned_domains = g.db.query(BannedDomain) \
		.order_by(BannedDomain.reason).all()
	return render_template("admin/banned_domains.html", v=v,
		banned_domains=banned_domains)

@app.post("/admin/ban_domain")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@admin_level_required(PERMS['DOMAINS_BAN'])
def ban_domain(v):

	domain=request.values.get("domain", "").strip().lower()
	if not domain: abort(400)

	reason=request.values.get("reason", "").strip()
	if not reason: abort(400, 'Reason is required!')

	if len(reason) > 100:
		abort(400, 'Reason is too long (max 100 characters)!')

	if len(reason) > 100:
		abort(400, 'Reason is too long!')

	existing = g.db.get(BannedDomain, domain)
	if not existing:
		d = BannedDomain(domain=domain, reason=reason)
		g.db.add(d)
		ma = ModAction(
			kind="ban_domain",
			user_id=v.id,
			_note=filter_emojis_only(f'{domain}, reason: {reason}')
		)
		g.db.add(ma)

	return redirect("/admin/banned_domains/")


@app.post("/admin/unban_domain/<path:domain>")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@admin_level_required(PERMS['DOMAINS_BAN'])
def unban_domain(v:User, domain):
	existing = g.db.get(BannedDomain, domain)
	if not existing: abort(400, 'Domain is not banned!')

	g.db.delete(existing)
	ma = ModAction(
		kind="unban_domain",
		user_id=v.id,
		_note=filter_emojis_only(domain)
	)
	g.db.add(ma)

	return {"message": f"{domain} has been unbanned!"}



@app.post("/admin/nuke_user")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@admin_level_required(PERMS['POST_COMMENT_MODERATION'])
def admin_nuke_user(v):

	user=get_user(request.values.get("user"))

	for post in g.db.query(Submission).filter_by(author_id=user.id).all():
		if post.is_banned:
			continue

		post.is_banned = True
		post.ban_reason = v.username
		g.db.add(post)

	for comment in g.db.query(Comment).filter_by(author_id=user.id).all():
		if comment.is_banned:
			continue

		comment.is_banned = True
		comment.ban_reason = v.username
		g.db.add(comment)

	ma=ModAction(
		kind="nuke_user",
		user_id=v.id,
		target_user_id=user.id,
		)
	g.db.add(ma)

	return {"message": f"@{user.username}'s content has been removed!"}


@app.post("/admin/unnuke_user")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@admin_level_required(PERMS['POST_COMMENT_MODERATION'])
def admin_nunuke_user(v):

	user=get_user(request.values.get("user"))

	for post in g.db.query(Submission).filter_by(author_id=user.id).all():
		if not post.is_banned:
			continue

		post.is_banned = False
		post.ban_reason = None
		post.is_approved = v.id
		g.db.add(post)

	for comment in g.db.query(Comment).filter_by(author_id=user.id).all():
		if not comment.is_banned:
			continue

		comment.is_banned = False
		comment.ban_reason = None
		comment.is_approved = v.id
		g.db.add(comment)

	ma=ModAction(
		kind="unnuke_user",
		user_id=v.id,
		target_user_id=user.id,
		)
	g.db.add(ma)

	return {"message": f"@{user.username}'s content has been approved!"}

@app.post("/blacklist/<int:user_id>")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@admin_level_required(PERMS['USER_BLACKLIST'])
def blacklist_user(user_id, v):
	user = get_account(user_id)
	if user.admin_level > v.admin_level:
		abort(403)
	user.blacklisted_by = v.id
	g.db.add(user)
	check_for_alts(user)

	ma = ModAction(
		kind="blacklist_user",
		user_id=v.id,
		target_user_id=user.id
	)
	g.db.add(ma)

	return {"message": f"@{user.username} has been blacklisted from restricted holes!"}

@app.post("/unblacklist/<int:user_id>")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@admin_level_required(PERMS['USER_BLACKLIST'])
def unblacklist_user(user_id, v):
	user = get_account(user_id)
	user.blacklisted_by = None
	g.db.add(user)

	for alt in get_alt_graph(user.id):
		alt.blacklisted_by = None
		g.db.add(alt)

	ma = ModAction(
		kind="unblacklist_user",
		user_id=v.id,
		target_user_id=user.id
	)
	g.db.add(ma)

	return {"message": f"@{user.username} has been unblacklisted from restricted holes!"}
