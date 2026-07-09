import sqlalchemy.exc

from files.classes import *
from files.helpers.alerts import *
from files.helpers.config.const import *
from files.helpers.get import *
from files.routes.wrappers import *
from files.__main__ import app, limiter

@app.get("/authorize")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def authorize_prompt(v:User):
	client_id = request.values.get("client_id")
	application = g.db.query(OauthApp).filter_by(client_id=client_id).one_or_none()
	if not application: return {"oauth_error": "Invalid `client_id`"}, 401
	return render_template("oauth.html", v=v, application=application)

@app.post("/authorize")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@auth_required
def authorize(v):
	client_id = request.values.get("client_id")
	application = g.db.query(OauthApp).filter_by(client_id=client_id).one_or_none()
	if not application: return {"oauth_error": "Invalid `client_id`"}, 401
	access_token = secrets.token_urlsafe(128)[:128]

	try:
		new_auth = ClientAuth(oauth_client = application.id, user_id = v.id, access_token=access_token)
		g.db.add(new_auth)
	except sqlalchemy.exc.IntegrityError:
		g.db.rollback()
		old_auth = g.db.query(ClientAuth).filter_by(oauth_client = application.id, user_id = v.id).one()
		access_token = old_auth.access_token

	return redirect(f"{application.redirect_uri}?token={access_token}")

@app.post("/rescind/<int:aid>")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@auth_required
def rescind(v, aid):

	auth = g.db.query(ClientAuth).filter_by(oauth_client = aid, user_id = v.id).one_or_none()
	if not auth: abort(400)
	g.db.delete(auth)
	return {"message": "Authorization revoked!"}


@app.post("/api_keys")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@is_not_permabanned
def request_api_keys(v):
	new_app = OauthApp(
		app_name=request.values.get('name').replace('<','').replace('>',''),
		redirect_uri=request.values.get('redirect_uri'),
		author_id=v.id,
		description=request.values.get("description")[:256]
	)

	g.db.add(new_app)

	body = f"@{v.username} has requested API keys for `{request.values.get('name')}`. You can approve or deny the request [here](/admin/apps)."
	body_html = sanitize(body)

	new_comment = Comment(author_id=AUTOJANNY_ID,
						parent_submission=None,
						level=1,
						body_html=body_html,
						sentto=MODMAIL_ID,
						distinguish_level=6,
						is_bot=True
						)
	g.db.add(new_comment)
	g.db.flush()

	new_comment.top_comment_id = new_comment.id

	for admin in g.db.query(User).filter(User.admin_level >= PERMS['APPS_MODERATION']).all():
		notif = Notification(comment_id=new_comment.id, user_id=admin.id)
		g.db.add(notif)



	return redirect('/settings/apps')


@app.post("/delete_app/<int:aid>")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@auth_required
def delete_oauth_app(v, aid):
	try:
		aid = int(aid)
	except:
		abort(404)
	app = g.db.get(OauthApp, aid)
	if not app: abort(404)

	if app.author_id != v.id: abort(403)

	for auth in g.db.query(ClientAuth).filter_by(oauth_client=app.id).all():
		g.db.delete(auth)

	g.db.delete(app)


	return redirect('/apps')


@app.post("/edit_app/<int:aid>")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@is_not_permabanned
def edit_oauth_app(v, aid):
	try:
		aid = int(aid)
	except:
		abort(404)
	app = g.db.get(OauthApp, aid)
	if not app: abort(404)

	if app.author_id != v.id: abort(403)

	app.redirect_uri = request.values.get('redirect_uri')
	app.app_name = request.values.get('name')
	app.description = request.values.get("description")[:256]

	g.db.add(app)


	return redirect('/settings/apps')


@app.post("/admin/app/approve/<int:aid>")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@admin_level_required(PERMS['APPS_MODERATION'])
def admin_app_approve(v, aid):

	app = g.db.get(OauthApp, aid)
	if not app: abort(404)

	user = app.author

	if not app.client_id:
		app.client_id = secrets.token_urlsafe(64)[:64]
		g.db.add(app)

		access_token = secrets.token_urlsafe(128)[:128]
		new_auth = ClientAuth(
			oauth_client = app.id,
			user_id = user.id,
			access_token=access_token
		)

		g.db.add(new_auth)

		send_repeatable_notification(user.id, f"@{v.username} (a site admin) has approved your application `{app.app_name}`. Here's your access token: `{access_token}`\nPlease check the guide [here](/api) if you don't know what to do next!")

		ma = ModAction(
			kind="approve_app",
			user_id=v.id,
			target_user_id=user.id,
		)
		g.db.add(ma)


	return {"message": f"'{app.app_name}' approved!"}


@app.post("/admin/app/revoke/<int:aid>")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@admin_level_required(PERMS['APPS_MODERATION'])
def admin_app_revoke(v, aid):

	app = g.db.get(OauthApp, aid)
	if app:
		for auth in g.db.query(ClientAuth).filter_by(oauth_client=app.id).all(): g.db.delete(auth)

		if v.id != app.author.id:
			send_repeatable_notification(app.author.id, f"@{v.username} (a site admin) has revoked your application `{app.app_name}`.")

		g.db.delete(app)

		ma = ModAction(
			kind="revoke_app",
			user_id=v.id,
			target_user_id=app.author.id,
		)
		g.db.add(ma)


	return {"message": f"'{app.app_name}' revoked!"}


@app.post("/admin/app/reject/<int:aid>")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@admin_level_required(PERMS['APPS_MODERATION'])
def admin_app_reject(v, aid):

	app = g.db.get(OauthApp, aid)

	if app:
		for auth in g.db.query(ClientAuth).filter_by(oauth_client=app.id).all(): g.db.delete(auth)

		if v.id != app.author.id:
			send_repeatable_notification(app.author.id, f"@{v.username} (a site admin) has rejected your application `{app.app_name}`.")

		g.db.delete(app)

		ma = ModAction(
			kind="reject_app",
			user_id=v.id,
			target_user_id=app.author.id,
		)
		g.db.add(ma)


	return {"message": f"'{app.app_name}' rejected!"}


@app.get("/admin/app/<int:aid>/posts")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@admin_level_required(PERMS['APPS_MODERATION'])
def admin_app_id_posts(v, aid):
	aid=aid
	oauth = g.db.get(OauthApp, aid)
	if not oauth: abort(404)

	pids=oauth.idlist(g.db, page=int(request.values.get("page",1)))

	next_exists=len(pids)==101
	pids=pids[:100]

	posts=get_posts(pids, v=v)

	return render_template("admin/app.html",
						v=v,
						app=oauth,
						listing=posts,
						next_exists=next_exists
						)

@app.get("/admin/app/<int:aid>/comments")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@admin_level_required(PERMS['APPS_MODERATION'])
def admin_app_id_comments(v, aid):

	aid=aid

	oauth = g.db.get(OauthApp, aid)
	if not oauth: abort(404)

	cids=oauth.comments_idlist(g.db, page=int(request.values.get("page",1)))

	next_exists=len(cids)==101
	cids=cids[:100]

	comments=get_comments(cids, v=v)


	return render_template("admin/app.html",
						v=v,
						app=oauth,
						comments=comments,
						next_exists=next_exists,
						standalone=True
						)


@app.get("/admin/apps")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@admin_level_required(PERMS['APPS_MODERATION'])
def admin_apps_list(v):

	apps = g.db.query(OauthApp).order_by(OauthApp.id.desc()).all()

	return render_template("admin/apps.html", v=v, apps=apps)


@app.post("/reroll/<int:aid>")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@auth_required
def reroll_oauth_tokens(aid, v):

	aid = aid

	a = g.db.get(OauthApp, aid)
	if not a: abort(404)

	if a.author_id != v.id: abort(403)

	a.client_id = secrets.token_urlsafe(64)[:64]
	g.db.add(a)


	return {"message": f"Client ID for '{a.app_name}' has been rerolled!", "id": a.client_id}
