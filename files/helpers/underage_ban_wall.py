from flask import redirect, render_template, request

from files.helpers.ban_hats import is_underage_banned
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

	@app.get("/underage-ban")
	def underage_ban_wall():
		viewer = get_logged_in_user()
		if not is_underage_banned(viewer):
			return redirect("/")
		return render_template("underage_ban_wall.html", v=None)

	@app.before_request
	def enforce_underage_ban_wall():
		path = _normalised_path()
		if _is_asset_or_health_request(path):
			return None

		viewer = get_logged_in_user()
		if not is_underage_banned(viewer):
			return None

		if path == "/underage-ban":
			return None

		if path == "/contact":
			if request.method == "GET":
				return render_template(
					"underage_contact.html",
					v=None,
					contact_user=viewer,
					msg=request.args.get("msg", ""),
				)
			return None

		status = 302 if request.method in {"GET", "HEAD"} else 303
		return redirect("/underage-ban", code=status)

	_INSTALLED = True
