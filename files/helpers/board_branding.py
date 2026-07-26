"""Obsession-specific board pricing, canonical URLs, and compatibility aliases."""

from urllib.parse import urlsplit, urlunsplit

from flask import redirect, request

from files.helpers.config.const import SITE_NAME


_BOARD_COST = 15_000
_INSTALLED_ATTR = "_obsession_board_branding_installed"


def _add_alias(app, rule, endpoint, methods):
	if any(existing.rule == rule and existing.endpoint == endpoint for existing in app.url_map.iter_rules()):
		return
	view_func = app.view_functions.get(endpoint)
	if not view_func:
		return
	app.add_url_rule(rule, endpoint=endpoint, view_func=view_func, methods=methods)


def _install_board_route_aliases(app):
	"""Expose every legacy /h/ route under the canonical /b/ prefix."""
	existing_rules = {rule.rule for rule in app.url_map.iter_rules()}
	for rule in list(app.url_map.iter_rules()):
		if "/h/" not in rule.rule:
			continue
		alias = rule.rule.replace("/h/", "/b/", 1)
		if alias in existing_rules:
			continue
		view_func = app.view_functions.get(rule.endpoint)
		if not view_func:
			continue
		methods = sorted(set(rule.methods or ()) - {"HEAD", "OPTIONS"})
		app.add_url_rule(
			alias,
			endpoint=rule.endpoint,
			view_func=view_func,
			methods=methods,
			defaults=rule.defaults,
			strict_slashes=rule.strict_slashes,
		)
		existing_rules.add(alias)

	_add_alias(app, "/boards", "subs", ["GET"])
	_add_alias(app, "/create_board", "create_sub", ["GET"])
	_add_alias(app, "/create_board", "create_sub2", ["POST"])


def _canonical_path(path):
	if path == "/holes":
		return "/boards"
	if path == "/create_hole":
		return "/create_board"
	if path.startswith("/h/"):
		return "/b/" + path[3:]
	return None


def _rewrite_location(location):
	if not location:
		return location
	parts = urlsplit(location)
	path = parts.path
	canonical = _canonical_path(path)
	if canonical:
		path = canonical
	else:
		path = path.replace("/h/", "/b/")
	return urlunsplit((parts.scheme, parts.netloc, path, parts.query, parts.fragment))


def install_board_branding(app):
	"""Install Obsession board pricing and make /b/ the public URL namespace."""
	if SITE_NAME != "Obsession" or getattr(app, _INSTALLED_ATTR, False):
		return
	setattr(app, _INSTALLED_ATTR, True)

	# Route functions read HOLE_COST from their module globals at request time.
	# Overriding it here changes both the displayed price and the actual charge.
	from files.routes import subs as subs_routes
	subs_routes.HOLE_COST = _BOARD_COST

	_install_board_route_aliases(app)

	@app.before_request
	def obsession_canonical_board_redirect():
		canonical = _canonical_path(request.path)
		if not canonical:
			return None
		if request.query_string:
			canonical += "?" + request.query_string.decode("utf-8", "ignore")
		return redirect(canonical, code=308)

	@app.after_request
	def obsession_rewrite_board_urls(response):
		location = response.headers.get("Location")
		if location:
			response.headers["Location"] = _rewrite_location(location)

		if response.mimetype == "text/html" and not response.direct_passthrough:
			body = response.get_data(as_text=True)
			body = body.replace("/h/", "/b/")
			body = body.replace("/create_hole", "/create_board")
			body = body.replace("/holes", "/boards")
			response.set_data(body)
		return response
