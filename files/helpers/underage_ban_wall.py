from flask import g, render_template, request

from files.helpers.alerts import get_msg
from files.helpers.ban_hats import is_underage_banned
from files.helpers.modmail_history import get_user_modmail_history
from files.routes.wrappers import get_logged_in_user


_INSTALLED = False
_ASSET_PREFIXES = (
	"/assets/",
	"/i/",
	"/static/",
	"/favicon",
	"/manifest",
	"/service-worker",
)
_PUBLIC_PATHS = {
	"/healthz",
	"/robots.txt",
	"/site-banner",
}


def _normalised_path():
	path = request.path.rstrip("/")
	return path or "/"


def _is_asset_or_health_request(path):
	return path in _PUBLIC_PATHS or path.startswith(_ASSET_PREFIXES)


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

		# Logged-in users see their complete modmail history directly on /contact.
		# This also gives restricted accounts a durable place to read admin replies.
		if path == "/contact" and request.method == "GET" and viewer:
			modmail_history = get_user_modmail_history(g.db, viewer)
			if underage_banned:
				return render_template(
					"underage_contact.html",
					v=viewer,
					contact_user=viewer,
					msg=get_msg(),
					modmail_history=modmail_history,
				)

			return render_template(
				"contact.html",
				v=viewer,
				msg=get_msg(),
				modmail_history=modmail_history,
			)

		if not underage_banned:
			return None

		# The modmail submission itself must reach the existing contact route.
		if path == "/contact" and request.method == "POST":
			return None

		# Render the restriction at the requested URL. There is no dedicated
		# destination to bypass, and no normal page content is executed.
		return render_template("underage_ban_wall.html", v=viewer), 403

	_INSTALLED = True
