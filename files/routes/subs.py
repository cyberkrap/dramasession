from files.classes import *
from files.helpers.alerts import *
from files.helpers.get import *
from files.helpers.regex import *
from files.routes.wrappers import *

from .front import frontlist
from files.__main__ import app, cache, limiter

@app.post("/exile/post/<int:pid>")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@is_not_permabanned
def exile_post(v:User, pid):
	if v.shadowbanned: abort(500)
	p = get_post(pid)
	sub = p.sub
	if not sub: abort(400)

	if not v.mods(sub): abort(403)

	u = p.author

	if u.mods(sub): abort(403)

	if not u.exiled_from(sub):
		exile = Exile(user_id=u.id, sub=sub, exiler_id=v.id)
		g.db.add(exile)

		send_notification(u.id, f"@{v.username} has exiled you from /h/{sub} for [{p.title}]({p.shortlink})")

		ma = SubAction(
			sub=sub,
			kind='exile_user',
			user_id=v.id,
			target_user_id=u.id,
			_note=f'for <a href="{p.permalink}">{p.title_html}</a>'
		)
		g.db.add(ma)

	return {"message": f"@{u.username} has been exiled from /h/{sub} successfully!"}

@app.post("/exile/comment/<int:cid>")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@is_not_permabanned
def exile_comment(v:User, cid):
	if v.shadowbanned: abort(500)
	c = get_comment(cid)
	sub = c.post.sub
	if not sub: abort(400)

	if not v.mods(sub): abort(403)

	u = c.author

	if u.mods(sub): abort(403)

	if not u.exiled_from(sub):
		exile = Exile(user_id=u.id, sub=sub, exiler_id=v.id)
		g.db.add(exile)

		send_notification(u.id, f"@{v.username} has exiled you from /h/{sub} for [{c.permalink}]({c.shortlink})")

		ma = SubAction(
			sub=sub,
			kind='exile_user',
			user_id=v.id,
			target_user_id=u.id,
			_note=f'for <a href="/comment/{c.id}#context">comment</a>'
		)
		g.db.add(ma)

	return {"message": f"@{u.username} has been exiled from /h/{sub} successfully!"}

@app.post("/h/<sub>/unexile/<int:uid>")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@is_not_permabanned
def unexile(v:User, sub, uid):
	u = get_account(uid)

	if not v.mods(sub): abort(403)
	if v.shadowbanned: return redirect(f'/h/{sub}/exilees')

	if u.exiled_from(sub):
		exile = g.db.query(Exile).filter_by(user_id=u.id, sub=sub).one_or_none()
		g.db.delete(exile)

		send_notification(u.id, f"@{v.username} has revoked your exile from /h/{sub}")

		ma = SubAction(
			sub=sub,
			kind='unexile_user',
			user_id=v.id,
			target_user_id=u.id
		)
		g.db.add(ma)

	if g.is_api_or_xhr:
		return {"message": f"@{u.username} has been unexiled from /h/{sub} successfully!"}


	return redirect(f'/h/{sub}/exilees')

@app.post("/h/<sub>/block")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def block_sub(v:User, sub):
	sub = get_sub_by_name(sub).name
	existing = g.db.query(SubBlock).filter_by(user_id=v.id, sub=sub).one_or_none()
	if not existing:
		block = SubBlock(user_id=v.id, sub=sub)
		g.db.add(block)
		cache.delete_memoized(frontlist)
	return {"message": f"/h/{sub} blocked successfully!"}

@app.post("/h/<sub>/unblock")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def unblock_sub(v:User, sub):
	sub = get_sub_by_name(sub)
	if not User.can_see(v, sub):
		abort(403)

	block = g.db.query(SubBlock).filter_by(user_id=v.id, sub=sub.name).one_or_none()

	if block:
		g.db.delete(block)
		cache.delete_memoized(frontlist)

	return {"message": f"/h/{sub.name} unblocked successfully!"}

@app.post("/h/<sub>/subscribe")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def subscribe_sub(v:User, sub):
	sub = get_sub_by_name(sub).name
	existing = g.db.query(SubJoin).filter_by(user_id=v.id, sub=sub).one_or_none()
	if not existing:
		subscribe = SubJoin(user_id=v.id, sub=sub)
		g.db.add(subscribe)
		cache.delete_memoized(frontlist)
	return {"message": f"/h/{sub} unblocked successfully!"}

@app.post("/h/<sub>/unsubscribe")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def unsubscribe_sub(v:User, sub):
	sub = get_sub_by_name(sub).name
	subscribe = g.db.query(SubJoin).filter_by(user_id=v.id, sub=sub).one_or_none()
	if subscribe:
		g.db.delete(subscribe)
		cache.delete_memoized(frontlist)
	return {"message": f"/h/{sub} blocked successfully!"}

@app.post("/h/<sub>/follow")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def follow_sub(v:User, sub):
	sub = get_sub_by_name(sub)
	if not User.can_see(v, sub):
		abort(403)
	existing = g.db.query(SubSubscription).filter_by(user_id=v.id, sub=sub.name).one_or_none()
	if not existing:
		subscription = SubSubscription(user_id=v.id, sub=sub.name)
		g.db.add(subscription)
		cache.delete_memoized(frontlist)

	return {"message": f"/h/{sub} followed successfully!"}

@app.post("/h/<sub>/unfollow")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def unfollow_sub(v:User, sub):
	sub = get_sub_by_name(sub)
	subscription = g.db.query(SubSubscription).filter_by(user_id=v.id, sub=sub.name).one_or_none()
	if subscription:
		g.db.delete(subscription)
		cache.delete_memoized(frontlist)

	return {"message": f"/h/{sub} unfollowed successfully!"}

@app.get("/h/<sub>/mods")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def mods(v:User, sub):
	sub = get_sub_by_name(sub)
	if not User.can_see(v, sub):
		abort(403)
	users = g.db.query(User, Mod).join(Mod).filter_by(sub=sub.name).order_by(Mod.created_utc).all()

	return render_template("sub/mods.html", v=v, sub=sub, users=users)


@app.get("/h/<sub>/exilees")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def sub_exilees(v:User, sub):
	sub = get_sub_by_name(sub)
	if not User.can_see(v, sub):
		abort(403)
	users = g.db.query(User, Exile).join(Exile, Exile.user_id==User.id) \
				.filter_by(sub=sub.name) \
				.order_by(Exile.created_utc.desc(), User.username).all()

	return render_template("sub/exilees.html", v=v, sub=sub, users=users)


@app.get("/h/<sub>/blockers")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def sub_blockers(v:User, sub):
	sub = get_sub_by_name(sub)
	if not User.can_see(v, sub):
		abort(403)
	users = g.db.query(User, SubBlock).join(SubBlock) \
				.filter_by(sub=sub.name) \
				.order_by(SubBlock.created_utc.desc(), User.username).all()

	return render_template("sub/blockers.html",
		v=v, sub=sub, users=users, verb="blocking")


@app.get("/h/<sub>/followers")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def sub_followers(v:User, sub):
	sub = get_sub_by_name(sub)
	if not User.can_see(v, sub):
		abort(403)
	users = g.db.query(User, SubSubscription).join(SubSubscription) \
			.filter_by(sub=sub.name) \
			.order_by(SubSubscription.created_utc.desc(), User.username).all()

	return render_template("sub/blockers.html",
		v=v, sub=sub, users=users, verb="following")


@app.post("/h/<sub>/add_mod")
@limiter.limit("1/second;30/day")
@limiter.limit("1/second;30/day", key_func=get_ID)
@is_not_permabanned
def add_mod(v:User, sub):
	if SITE_NAME == 'WPD': abort(403)
	sub = get_sub_by_name(sub).name
	if not v.mods(sub): abort(403)
	if v.shadowbanned: return redirect(f'/h/{sub}/mods')

	user = request.values.get('user')

	if not user: abort(400)

	user = get_user(user, v=v, include_shadowbanned=False)

	if sub in {'furry','vampire','racist','femboy'} and not v.client and not user.house.lower().startswith(sub):
		abort(403, f"@{user.username} needs to be a member of House {sub.capitalize()} to be added as a mod there!")

	existing = g.db.query(Mod).filter_by(user_id=user.id, sub=sub).one_or_none()

	if not existing:
		mod = Mod(user_id=user.id, sub=sub)
		g.db.add(mod)

		if v.id != user.id:
			send_repeatable_notification(user.id, f"@{v.username} has added you as a mod to /h/{sub}")

		ma = SubAction(
			sub=sub,
			kind='make_mod',
			user_id=v.id,
			target_user_id=user.id
		)
		g.db.add(ma)

	return redirect(f'/h/{sub}/mods')

@app.post("/h/<sub>/remove_mod")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@is_not_permabanned
def remove_mod(v:User, sub):
	sub = get_sub_by_name(sub).name

	if not v.mods(sub): abort(403)
	if v.shadowbanned: abort(500)

	uid = request.values.get('uid')

	if not uid: abort(400)

	try: uid = int(uid)
	except: abort(400)

	user = get_account(uid)

	if not user: abort(404)

	mod = g.db.query(Mod).filter_by(user_id=user.id, sub=sub).one_or_none()
	if not mod: abort(400)

	if not (v.id == user.id or v.mod_date(sub) and v.mod_date(sub) < mod.created_utc): abort(403)

	g.db.delete(mod)

	if v.id != user.id:
		send_repeatable_notification(user.id, f"@{v.username} has removed you as a mod from /h/{sub}")

	ma = SubAction(
		sub=sub,
		kind='remove_mod',
		user_id=v.id,
		target_user_id=user.id
	)
	g.db.add(ma)

	return {"message": f"@{user.username} has been removed as a mod!"}

@app.get("/create_hole")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@is_not_permabanned
def create_sub(v):
	if not v.can_create_hole:
		abort(403)

	return render_template("sub/create_hole.html", v=v, cost=HOLE_COST, error=get_error())

@app.post("/create_hole")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@is_not_permabanned
def create_sub2(v):
	if not v.can_create_hole:
		abort(403)

	name = request.values.get('name')
	if not name: abort(400)
	name = name.strip().lower()

	if not valid_sub_regex.fullmatch(name):
		return redirect(f"/create_hole?error=Name does not match the required format!")

	sub = get_sub_by_name(name, graceful=True)
	if not sub:
		if not v.charge_account('coins', HOLE_COST):
			return redirect(f"/create_hole?error=You don't have enough coins!")

		g.db.add(v)
		if v.shadowbanned: abort(500)

		sub = Sub(name=name)
		g.db.add(sub)
		g.db.flush()
		mod = Mod(user_id=v.id, sub=sub.name)
		g.db.add(mod)

		admins = [x[0] for x in g.db.query(User.id).filter(User.admin_level >= PERMS['NOTIFICATIONS_HOLE_CREATION'], User.id != v.id).all()]
		for admin in admins:
			send_repeatable_notification(admin, f":!marseyparty: /h/{sub} has been created by @{v.username} :marseyparty:")

	return redirect(f'/h/{sub}')

@app.post("/kick/<int:pid>")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@is_not_permabanned
def kick(v:User, pid):
	post = get_post(pid)

	if not post.sub: abort(403)
	if not v.mods(post.sub): abort(403)
	if v.shadowbanned: abort(500)

	old = post.sub
	post.sub = None
	post.hole_pinned = None

	ma = SubAction(
		sub=old,
		kind='kick_post',
		user_id=v.id,
		target_submission_id=post.id
	)
	g.db.add(ma)

	if v.id != post.author_id:
		message = f"@{v.username} (a /h/{old} mod) has moved [{post.title}]({post.shortlink}) from /h/{old} to the main feed!"
		send_repeatable_notification(post.author_id, message)

	g.db.add(post)

	cache.delete_memoized(frontlist)

	return {"message": f"Post kicked from /h/{old} successfully!"}

@app.get('/h/<sub>/settings')
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@is_not_permabanned
def sub_settings(v:User, sub):
	sub = get_sub_by_name(sub)
	if not v.mods(sub.name): abort(403)
	return render_template('sub/settings.html', v=v, sidebar=sub.sidebar, sub=sub, css=sub.css)


@app.post('/h/<sub>/sidebar')
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@is_not_permabanned
def post_sub_sidebar(v:User, sub):
	sub = get_sub_by_name(sub)
	if not v.mods(sub.name): abort(403)
	if v.shadowbanned: return redirect(f'/h/{sub}/settings')

	sub.sidebar = request.values.get('sidebar', '').strip()[:10000]
	sub.sidebar_html = sanitize(sub.sidebar, showmore=False)
	if len(sub.sidebar_html) > 20000: abort(400, "Sidebar is too big!")

	g.db.add(sub)

	ma = SubAction(
		sub=sub.name,
		kind='edit_sidebar',
		user_id=v.id
	)
	g.db.add(ma)

	return redirect(f'/h/{sub}/settings')


@app.post('/h/<sub>/css')
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@is_not_permabanned
def post_sub_css(v:User, sub):
	sub = get_sub_by_name(sub)
	css = request.values.get('css', '').strip()

	if not sub: abort(404)
	if not v.mods(sub.name): abort(403)
	if v.shadowbanned: return redirect(f'/h/{sub}/settings')

	if len(css) > 6000:
		error = "CSS is too long (max 6000 characters)"
		return render_template('sub/settings.html', v=v, sidebar=sub.sidebar, sub=sub, error=error, css=css)

	valid, error = validate_css(css)
	if not valid:
		return render_template('sub/settings.html', v=v, sidebar=sub.sidebar, sub=sub, error=error, css=css)

	sub.css = css
	g.db.add(sub)

	ma = SubAction(
		sub=sub.name,
		kind='edit_css',
		user_id=v.id
	)
	g.db.add(ma)

	return redirect(f'/h/{sub}/settings')

@app.get("/h/<sub>/css")
def get_sub_css(sub):
	sub = g.db.query(Sub.css).filter_by(name=sub.strip().lower()).one_or_none()
	if not sub: abort(404)
	resp=make_response(sub.css or "")
	resp.headers.add("Content-Type", "text/css")
	return resp

@app.post("/h/<sub>/settings/banners/")
@limiter.limit("1/second;50/day")
@limiter.limit("1/second;50/day", key_func=get_ID)
@is_not_permabanned
def upload_sub_banner(v:User, sub:str):
	if g.is_tor: abort(403, "Image uploads are not allowed through Tor")

	sub = get_sub_by_name(sub)
	if not v.mods(sub.name): abort(403)
	if v.shadowbanned: return redirect(f'/h/{sub}/settings')

	file = request.files["banner"]

	name = f'/images/{time.time()}'.replace('.','') + '.webp'
	file.save(name)
	bannerurl = process_image(name, v, resize=1200)

	sub.bannerurls.append(bannerurl)

	g.db.add(sub)

	ma = SubAction(
		sub=sub.name,
		kind='upload_banner',
		user_id=v.id
	)
	g.db.add(ma)

	return redirect(f'/h/{sub}/settings')

@app.delete("/h/<sub>/settings/banners/<int:index>")
@limiter.limit("1/2 second;30/day")
@limiter.limit("1/2 second;30/day", key_func=get_ID)
@is_not_permabanned
def delete_sub_banner(v:User, sub:str, index:int):
	sub = get_sub_by_name(sub)
	if not v.mods(sub.name): abort(403)
	if v.shadowbanned: return redirect(f'/h/{sub}/settings')

	if not sub.bannerurls:
		abort(404, f"Banner not found (/h/{sub.name} has no banners)")
	if index < 0 or index >= len(sub.bannerurls):
		abort(404, f'Banner not found (banner index {index} is not between 0 and {len(sub.bannerurls)})')
	banner = sub.bannerurls[index]
	try:
		os.remove(banner)
	except FileNotFoundError:
		pass
	del sub.bannerurls[index]
	g.db.add(sub)

	ma = SubAction(
		sub=sub.name,
		kind='delete_banner',
		_note=index,
		user_id=v.id
	)
	g.db.add(ma)

	return {"message": f"Deleted banner {index} from /h/{sub} successfully"}

@app.delete("/h/<sub>/settings/banners/")
@limiter.limit("1/10 second;30/day")
@limiter.limit("1/10 second;30/day", key_func=get_ID)
@is_not_permabanned
def delete_all_sub_banners(v:User, sub:str):
	sub = get_sub_by_name(sub)
	if not v.mods(sub.name): abort(403)
	if v.shadowbanned: return redirect(f'/h/{sub}/settings')
	for banner in sub.banner_urls:
		try:
			os.remove(banner)
		except FileNotFoundError:
			pass
	sub.bannerurls = []
	g.db.add(sub)

	ma = SubAction(
		sub=sub.name,
		kind='delete_banner',
		_note='all',
		user_id=v.id
	)
	g.db.add(ma)

	return {"message": f"Deleted all banners from /h/{sub} successfully"}

@app.post("/h/<sub>/sidebar_image")
@limiter.limit("1/second;10/day")
@limiter.limit("1/second;10/day", key_func=get_ID)
@is_not_permabanned
def sub_sidebar(v:User, sub):
	if g.is_tor: abort(403, "Image uploads are not allowed through TOR!")

	sub = get_sub_by_name(sub)
	if not v.mods(sub.name): abort(403)
	if v.shadowbanned: return redirect(f'/h/{sub}/settings')

	file = request.files["sidebar"]
	name = f'/images/{time.time()}'.replace('.','') + '.webp'
	file.save(name)
	sidebarurl = process_image(name, v, resize=400)

	if sidebarurl:
		if sub.sidebarurl:
			os.remove(sub.sidebarurl)
		sub.sidebarurl = sidebarurl
		g.db.add(sub)

	ma = SubAction(
		sub=sub.name,
		kind='change_sidebar_image',
		user_id=v.id
	)
	g.db.add(ma)

	return redirect(f'/h/{sub}/settings')

@app.post("/h/<sub>/marsey_image")
@limiter.limit("1/second;10/day")
@limiter.limit("1/second;10/day", key_func=get_ID)
@is_not_permabanned
def sub_marsey(v:User, sub):
	if g.is_tor: abort(403, "Image uploads are not allowed through TOR!")

	sub = get_sub_by_name(sub)
	if not v.mods(sub.name): abort(403)
	if v.shadowbanned: return redirect(f'/h/{sub}/settings')

	file = request.files["marsey"]
	name = f'/images/{time.time()}'.replace('.','') + '.webp'
	file.save(name)
	marseyurl = process_image(name, v, resize=200)

	if marseyurl:
		if sub.marseyurl:
			os.remove(sub.marseyurl)
		sub.marseyurl = marseyurl
		g.db.add(sub)

	ma = SubAction(
		sub=sub.name,
		kind='change_marsey',
		user_id=v.id
	)
	g.db.add(ma)

	return redirect(f'/h/{sub}/settings')

@app.get("/holes")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def subs(v:User):
	subs = g.db.query(Sub, func.count(Submission.sub)).outerjoin(Submission, Sub.name == Submission.sub).group_by(Sub.name).order_by(func.count(Submission.sub).desc()).all()
	total_users = g.db.query(User).count()
	return render_template('sub/subs.html', v=v, subs=subs, total_users=total_users)

@app.post("/hole_pin/<int:pid>")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@is_not_permabanned
def hole_pin(v:User, pid):
	p = get_post(pid)

	if not p.sub: abort(403)

	if not v.mods(p.sub): abort(403)

	p.hole_pinned = v.username
	g.db.add(p)

	if v.id != p.author_id:
		message = f"@{v.username} (a /h/{p.sub} mod) has pinned [{p.title}]({p.shortlink}) in /h/{p.sub}"
		send_repeatable_notification(p.author_id, message)

	ma = SubAction(
		sub=p.sub,
		kind='pin_post',
		user_id=v.id,
		target_submission_id=p.id
	)
	g.db.add(ma)

	cache.delete_memoized(frontlist)

	return {"message": f"Post pinned to /h/{p.sub} successfully!"}

@app.post("/hole_unpin/<int:pid>")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@is_not_permabanned
def hole_unpin(v:User, pid):
	p = get_post(pid)

	if not p.sub: abort(403)

	if not v.mods(p.sub): abort(403)

	p.hole_pinned = None
	g.db.add(p)

	if v.id != p.author_id:
		message = f"@{v.username} (a /h/{p.sub} mod) has unpinned [{p.title}]({p.shortlink}) in /h/{p.sub}"
		send_repeatable_notification(p.author_id, message)

	ma = SubAction(
		sub=p.sub,
		kind='unpin_post',
		user_id=v.id,
		target_submission_id=p.id
	)
	g.db.add(ma)

	cache.delete_memoized(frontlist)

	return {"message": f"Post unpinned from /h/{p.sub} successfully!"}


@app.post('/h/<sub>/stealth')
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@is_not_permabanned
def sub_stealth(v:User, sub):
	sub = get_sub_by_name(sub)
	if sub.name in {'braincels','smuggies','ye24'}:
		abort(403)
	if not v.mods(sub.name): abort(403)

	sub.stealth = not sub.stealth
	g.db.add(sub)

	cache.delete_memoized(frontlist)

	if sub.stealth:
		ma = SubAction(
			sub=sub.name,
			kind='enable_stealth',
			user_id=v.id
		)
		g.db.add(ma)
		return {"message": f"Stealth mode has been enabled for /h/{sub} successfully!"}
	else:
		ma = SubAction(
			sub=sub.name,
			kind='disable_stealth',
			user_id=v.id
		)
		g.db.add(ma)
		return {"message": f"Stealth mode has been disabled for /h/{sub} successfully!"}


@app.post("/mod_pin/<int:cid>")
@feature_required('PINS')
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@is_not_permabanned
def mod_pin(cid, v):

	comment = get_comment(cid, v=v)

	if not comment.stickied:
		if not (comment.post.sub and v.mods(comment.post.sub)): abort(403)

		comment.stickied = v.username + " (Mod)"

		g.db.add(comment)

		ma = SubAction(
			sub=comment.post.sub,
			kind="pin_comment",
			user_id=v.id,
			target_comment_id=comment.id
		)
		g.db.add(ma)

		if v.id != comment.author_id:
			message = f"@{v.username} (a /h/{comment.post.sub} mod) has pinned your [comment]({comment.shortlink})"
			send_repeatable_notification(comment.author_id, message)

	return {"message": "Comment pinned!"}

@app.post("/unmod_pin/<int:cid>")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@is_not_permabanned
def mod_unpin(cid, v):

	comment = get_comment(cid, v=v)

	if comment.stickied:
		if not (comment.post.sub and v.mods(comment.post.sub)): abort(403)

		comment.stickied = None
		g.db.add(comment)

		ma = SubAction(
			sub=comment.post.sub,
			kind="unpin_comment",
			user_id=v.id,
			target_comment_id=comment.id
		)
		g.db.add(ma)

		if v.id != comment.author_id:
			message = f"@{v.username} (a /h/{comment.post.sub} mod) has unpinned your [comment]({comment.shortlink})"
			send_repeatable_notification(comment.author_id, message)
	return {"message": "Comment unpinned!"}


@app.get("/h/<sub>/log")
@app.get("/h/<sub>/modlog")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def hole_log(v:User, sub):
	sub = get_sub_by_name(sub)
	if not User.can_see(v, sub):
		abort(403)
	try: page = max(int(request.values.get("page", 1)), 1)
	except: page = 1

	mod = request.values.get("mod")
	if mod: mod_id = get_id(mod)
	else: mod_id = 0

	kind = request.values.get("kind")

	types = SUBACTION_TYPES

	if kind and kind not in types:
		kind = None
		actions = []
	else:
		actions = g.db.query(SubAction).filter_by(sub=sub.name)

		if mod_id:
			actions = actions.filter_by(user_id=mod_id)
			kinds = set([x.kind for x in actions])
			types2 = {}
			for k,val in types.items():
				if k in kinds: types2[k] = val
			types = types2
		if kind: actions = actions.filter_by(kind=kind)

		actions = actions.order_by(SubAction.id.desc()).offset(PAGE_SIZE*(page-1)).limit(PAGE_SIZE+1).all()

	next_exists=len(actions)>25
	actions=actions[:25]
	mods = [x[0] for x in g.db.query(Mod.user_id).filter_by(sub=sub.name).all()]
	mods = [x[0] for x in g.db.query(User.username).filter(User.id.in_(mods)).order_by(User.username).all()]

	return render_template("log.html", v=v, admins=mods, types=types, admin=mod, type=kind, actions=actions, next_exists=next_exists, page=page, sub=sub, single_user_url='mod')

@app.get("/h/<sub>/log/<int:id>")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def hole_log_item(id, v, sub):
	sub = get_sub_by_name(sub)
	if not User.can_see(v, sub):
		abort(403)
	try: id = int(id)
	except: abort(404)

	action=g.db.get(SubAction, id)

	if not action: abort(404)

	mods = [x[0] for x in g.db.query(Mod.user_id).filter_by(sub=sub.name).all()]
	mods = [x[0] for x in g.db.query(User.username).filter(User.id.in_(mods)).order_by(User.username).all()]

	types = SUBACTION_TYPES

	return render_template("log.html", v=v, actions=[action], next_exists=False, page=1, action=action, admins=mods, types=types, sub=sub, single_user_url='mod')
