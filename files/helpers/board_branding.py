"""Obsession-specific board pricing, canonical URLs, and compatibility aliases."""

import sys
from urllib.parse import urlsplit, urlunsplit

from flask import redirect, request

from files.helpers.config.const import SITE_NAME


_BOARD_COST = 15_000
_INSTALLED_ATTR = "_obsession_board_branding_installed"


def _route_key(rule, endpoint, methods):
	return rule, endpoint, frozenset(methods)


def _add_alias(app, rule, endpoint, methods):
	methods = sorted(set(methods) - {"HEAD", "OPTIONS"})
	key = _route_key(rule, endpoint, methods)
	for existing in app.url_map.iter_rules():
		existing_methods = set(existing.methods or ()) - {"HEAD", "OPTIONS"}
		if _route_key(existing.rule, existing.endpoint, existing_methods) == key:
			return
	view_func = app.view_functions.get(endpoint)
	if not view_func:
		return
	app.add_url_rule(rule, endpoint=endpoint, view_func=view_func, methods=methods)


def _install_board_route_aliases(app):
	"""Expose every legacy /h/ route under the canonical /b/ prefix."""
	existing_keys = {
		_route_key(
			rule.rule,
			rule.endpoint,
			set(rule.methods or ()) - {"HEAD", "OPTIONS"},
		)
		for rule in app.url_map.iter_rules()
	}
	for rule in list(app.url_map.iter_rules()):
		if "/h/" not in rule.rule:
			continue
		alias = rule.rule.replace("/h/", "/b/", 1)
		methods = sorted(set(rule.methods or ()) - {"HEAD", "OPTIONS"})
		key = _route_key(alias, rule.endpoint, methods)
		if key in existing_keys:
			continue
		view_func = app.view_functions.get(rule.endpoint)
		if not view_func:
			continue
		app.add_url_rule(
			alias,
			endpoint=rule.endpoint,
			view_func=view_func,
			methods=methods,
			defaults=rule.defaults,
			strict_slashes=rule.strict_slashes,
		)
		existing_keys.add(key)

	_add_alias(app, "/boards", "subs", ["GET"])
	_add_alias(app, "/create_board", "create_sub", ["GET"])
	_add_alias(app, "/create_board", "create_sub2", ["POST"])


def _install_board_cost(app):
	"""Update every loaded copy of HOLE_COST used by routes, users, and templates."""
	for module_name, module in list(sys.modules.items()):
		if not module_name.startswith("files.") or module is None:
			continue
		if hasattr(module, "HOLE_COST"):
			setattr(module, "HOLE_COST", _BOARD_COST)
	app.jinja_env.globals["HOLE_COST"] = _BOARD_COST


def _install_canonical_submission_links():
	"""Return /b/ links from post and comment permalink properties and APIs."""
	from files.classes.submission import Submission

	legacy_shortlink = Submission.shortlink
	if getattr(legacy_shortlink.fget, "_obsession_board_link", False):
		return

	def canonical_shortlink(post):
		value = legacy_shortlink.__get__(post, Submission)
		return value.replace("/h/", "/b/", 1)

	canonical_shortlink._obsession_board_link = True
	Submission.shortlink = property(canonical_shortlink)


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

	_install_board_cost(app)
	_install_board_route_aliases(app)
	_install_canonical_submission_links()

	@app.before_request
	def obsession_canonical_board_redirect():
		path = request.path
		canonical = _canonical_path(path)
		if canonical:
			if request.query_string:
				canonical += "?" + request.query_string.decode("utf-8", "ignore")
			return redirect(canonical, code=308)

		# The old route handlers sometimes inspect request.path directly. Keep
		# those checks working after Flask has matched the public /b/ alias.
		if path.startswith("/b/"):
			request.environ["PATH_INFO"] = "/h/" + path[3:]
		return None

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
