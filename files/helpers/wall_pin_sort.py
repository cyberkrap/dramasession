import time

from flask import abort, g, redirect, render_template, request
from sqlalchemy import case

from files.classes import Comment, User, ViewerRelationship
from files.helpers.config.const import PAGE_SIZE, PERMS
from files.helpers.get import get_comments_v_properties, get_user
from files.routes.wrappers import auth_desired_with_logingate


_INSTALLED_ATTR = "_obsession_wall_pin_sort_installed"


def install_wall_pin_sort(app):
	"""Make active Pin awards actually pin top-level profile-wall comments.

	The stock wall route sorts only by Comment.created_utc, so the Pin award's
	stickied_utc value has no effect there. Replace that one view while preserving
	the existing permissions, view tracking, pagination, JSON output, and template.
	"""
	if getattr(app, _INSTALLED_ATTR, False):
		return

	original = app.view_functions.get("u_username_wall")
	if not original:
		return

	@auth_desired_with_logingate
	def pinned_wall(v, username):
		u = get_user(username, v=v, include_blocks=True, include_shadowbanned=False)
		if username != u.username:
			return redirect(f"/@{u.username}")

		if v and hasattr(u, "is_blocking") and u.is_blocking:
			if g.is_api_or_xhr or request.path.endswith(".json"):
				abort(403, f"You are blocking @{u.username}.")
			return render_template("userpage/blocking.html", u=u, v=v), 403

		is_following = v and u.has_follower(v)

		if v and v.id != u.id and not v.admin_level:
			g.db.flush()
			view = g.db.query(ViewerRelationship).filter_by(
				viewer_id=v.id,
				user_id=u.id,
			).one_or_none()
			if view:
				view.last_view_utc = int(time.time())
			else:
				view = ViewerRelationship(viewer_id=v.id, user_id=u.id)
			g.db.add(view)
			g.db.commit()

		try:
			page = max(int(request.values.get("page", "1")), 1)
		except Exception:
			page = 1

		if v:
			comments, _ = get_comments_v_properties(
				v,
				True,
				None,
				Comment.wall_user_id == u.id,
			)
		else:
			comments = g.db.query(Comment).filter(Comment.wall_user_id == u.id)

		comments = comments.filter(Comment.level == 1)

		if not v or (v.id != u.id and v.admin_level < PERMS["POST_COMMENT_MODERATION"]):
			comments = comments.filter(
				Comment.is_banned == False,
				Comment.ghost == False,
				Comment.deleted_utc == 0,
			)

		now = int(time.time())
		active_pin_until = case(
			(Comment.stickied_utc > now, Comment.stickied_utc),
			else_=0,
		)
		comments = comments.order_by(
			active_pin_until.desc(),
			Comment.created_utc.desc(),
		).offset(PAGE_SIZE * (page - 1)).limit(PAGE_SIZE + 1).all()

		if v:
			comments = [c[0] for c in comments]

		next_exists = len(comments) > PAGE_SIZE
		comments = comments[:PAGE_SIZE]

		if (v and v.client) or request.path.endswith(".json"):
			return {"data": [c.json(g.db) for c in comments]}

		return render_template(
			"userpage/wall.html",
			u=u,
			v=v,
			listing=comments,
			page=page,
			next_exists=next_exists,
			is_following=is_following,
			standalone=True,
			render_replies=True,
			wall=True,
		)

	pinned_wall.__name__ = getattr(original, "__name__", "u_username_wall")
	app.view_functions["u_username_wall"] = pinned_wall

	try:
		from files.routes import users as users_routes
		users_routes.u_username_wall = pinned_wall
	except Exception:
		pass

	setattr(app, _INSTALLED_ATTR, True)
