from flask import g, render_template, request

from files.classes import Comment
from files.helpers.ban_hats import is_underage_banned
from files.helpers.config.const import MODMAIL_ID
from files.helpers.get import get_msg
from files.helpers.modmail_history import get_user_modmail_history
from files.routes.wrappers import get_logged_in_user


_INSTALLED = False
_ASSET_PREFIXES = (
	"/assets/",
	"/i/",
	"/static/",
	"/pp/",
	"/images/",
	"/dm_images/",
	"/e/",
	"/emote-preview/",
	"/favicon",
	"/manifest",
	"/service-worker",
)
_PUBLIC_PATHS = {
	"/healthz",
	"/robots.txt",
	"/site-banner",
}
_MUTED_MESSAGE = "Your modmails have been muted by admins, so you cannot message them."


def _normalised_path():
	path = request.path.rstrip("/")
	return path or "/"


def _is_asset_or_health_request(path):
	return path in _PUBLIC_PATHS or path.startswith(_ASSET_PREFIXES)


def _render_contact(viewer, underage_banned, *, msg="", status=200):
	context = {
		"v": viewer,
		"msg": msg,
		"modmail_history": get_user_modmail_history(g.db, viewer),
		"modmail_muted": bool(viewer.is_muted),
	}
	if underage_banned:
		context["contact_user"] = viewer
		return render_template("underage_contact.html", **context), status
	return render_template("contact.html", **context), status


def _is_owned_modmail_reply(viewer):
	try:
		parent_id = int(request.values.get("parent_id", ""))
	except (TypeError, ValueError):
		return False

	parent = g.db.get(Comment, parent_id)
	if not parent:
		return False

	top_id = parent.top_comment_id or parent.id
	top = parent if parent.id == top_id else g.db.get(Comment, top_id)
	return bool(
		top
		and top.sentto == MODMAIL_ID
		and top.author_id == viewer.id
	)


def install_underage_ban_wall(app):
	global _INSTALLED
	if _INSTALLED:
		return

	@app.before_request
	def enforce_underage_ban_wall():
		path = _normalised_path()
		if _is_asset_or_health_request(path):
			return None

		viewer = get_logged_in_user()
		underage_banned = is_underage_banned(viewer)

		if path == "/contact" and viewer:
			# Handle muted accounts before Flask-Limiter runs on the POST route. This
			# keeps the user on their modmail page with an explicit explanation
			# instead of eventually surfacing an unrelated 429 response.
			if request.method == "POST" and viewer.is_muted:
				return _render_contact(
					viewer,
					underage_banned,
					msg=_MUTED_MESSAGE,
					status=403,
				)

			if request.method == "GET":
				return _render_contact(viewer, underage_banned, msg=get_msg())

		if not underage_banned:
			return None

		# Restricted users may reply only inside modmail threads they originally
		# opened. Every other /reply request remains blocked by the wall.
		if path == "/reply" and request.method == "POST" and _is_owned_modmail_reply(viewer):
			if viewer.is_muted:
				return _render_contact(
					viewer,
					True,
					msg=_MUTED_MESSAGE,
					status=403,
				)
			return None

		# An unmuted restricted account may still submit the contact form.
		if path == "/contact" and request.method == "POST":
			return None

		# Render the restriction at the requested URL. There is no dedicated
		# destination to bypass, and no normal page content is executed.
		return render_template("underage_ban_wall.html", v=viewer), 403

	_INSTALLED = True
