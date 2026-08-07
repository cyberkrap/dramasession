from flask import abort, g, render_template, request

from files.classes import User
from files.classes.views import ViewerRelationship
from files.helpers.config.const import DEFAULT_RATELIMIT, PAGE_SIZE, PERMS
from files.helpers.get import get_user
from files.routes.wrappers import *
from files.__main__ import app, limiter


@app.get("/@<username>/viewed")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def profiles_viewed(v: User, username: str):
	u = get_user(username, v=v, include_shadowbanned=False)

	# Match the profile Activity visibility: users can inspect their own history,
	# while sufficiently privileged admins can inspect it for moderation.
	if not (v.id == u.id or v.admin_level >= PERMS['USER_VOTERS_VISIBLE']):
		abort(403)

	try:
		page = max(1, int(request.values.get("page", 1)))
	except (TypeError, ValueError):
		abort(400, "Invalid page input!")

	views = g.db.query(ViewerRelationship, User) \
		.join(User, User.id == ViewerRelationship.user_id) \
		.filter(ViewerRelationship.viewer_id == u.id)

	if not v.can_see_shadowbanned:
		views = views.filter(User.shadowbanned == None)

	views = views.order_by(ViewerRelationship.last_view_utc.desc()) \
		.offset(PAGE_SIZE * (page - 1)) \
		.limit(PAGE_SIZE + 1) \
		.all()

	next_exists = len(views) > PAGE_SIZE
	views = views[:PAGE_SIZE]

	return render_template(
		"userpage/viewed.html",
		v=v,
		u=u,
		views=views,
		next_exists=next_exists,
		page=page,
	)
