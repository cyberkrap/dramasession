"""Obsession-specific board pricing, canonical URLs, and compatibility aliases."""

import sys
from urllib.parse import urlsplit, urlunsplit

from flask import abort, g, has_request_context, redirect, render_template, request

from files.helpers.config.const import SITE_NAME


_BOARD_COST = 15_000
_ADMIN_ONLY_BOARD = "onlymods"
_INSTALLED_ATTR = "_obsession_board_branding_installed"


def _route_key(rule, endpoint, methods):
	return rule, endpoint, frozenset(methods)


def _is_site_admin(user):
	return bool(user and int(getattr(user, "admin_level", 0) or 0) > 0)


def _is_admin_only_board(value):
	return str(value or "").strip().lower() == _ADMIN_ONLY_BOARD


def _is_admin_only_board_path(path):
	path = str(path or "")
	return (
		path in {f"/b/{_ADMIN_ONLY_BOARD}", f"/h/{_ADMIN_ONLY_BOARD}"}
		or path.startswith(f"/b/{_ADMIN_ONLY_BOARD}/")
		or path.startswith(f"/h/{_ADMIN_ONLY_BOARD}/")
	)


def _request_viewer(explicit_viewer=None):
	if explicit_viewer is not None:
		return explicit_viewer
	if not has_request_context():
		return None
	if hasattr(g, "v"):
		return g.v
	from files.routes.wrappers import get_logged_in_user
	return get_logged_in_user()


def _replace_loaded_function(original, replacement):
	for module_name, module in list(sys.modules.items()):
		if not module_name.startswith("files.") or module is None:
			continue
		if getattr(module, original.__name__, None) is original:
			setattr(module, original.__name__, replacement)


def _install_admin_only_content_guards():
	"""Keep onlymods content inaccessible outside administrator sessions."""
	from files.classes import Sub, User
	from files.helpers import get as get_helpers

	current_can_see = User.can_see
	original_can_see = getattr(current_can_see, "__func__", current_can_see)
	if not getattr(original_can_see, "_obsession_admin_only_board", False):
		def can_see(cls, user, other):
			if isinstance(other, Sub) and _is_admin_only_board(other.name):
				return _is_site_admin(user)
			return original_can_see(cls, user, other)

		can_see._obsession_admin_only_board = True
		User.can_see = classmethod(can_see)

	original_get_post = get_helpers.get_post
	if not getattr(original_get_post, "_obsession_admin_only_board", False):
		def get_post(*args, **kwargs):
			post = original_get_post(*args, **kwargs)
			if post and _is_admin_only_board(getattr(post, "sub", None)) and has_request_context():
				explicit_viewer = kwargs.get("v", args[1] if len(args) > 1 else None)
				if not _is_site_admin(_request_viewer(explicit_viewer)):
					graceful = kwargs.get("graceful", args[2] if len(args) > 2 else False)
					if graceful:
						return None
					abort(403, "This board is for administrators only.")
			return post

		get_post._obsession_admin_only_board = True
		get_helpers.get_post = get_post
		_replace_loaded_function(original_get_post, get_post)

	original_get_posts = get_helpers.get_posts
	if not getattr(original_get_posts, "_obsession_admin_only_board", False):
		def get_posts(*args, **kwargs):
			posts = original_get_posts(*args, **kwargs)
			if not has_request_context():
				return posts
			explicit_viewer = kwargs.get("v", args[1] if len(args) > 1 else None)
			if _is_site_admin(_request_viewer(explicit_viewer)):
				return posts
			return [post for post in posts if not _is_admin_only_board(getattr(post, "sub", None))]

		get_posts._obsession_admin_only_board = True
		get_helpers.get_posts = get_posts
		_replace_loaded_function(original_get_posts, get_posts)

	original_get_comment = get_helpers.get_comment
	if not getattr(original_get_comment, "_obsession_admin_only_board", False):
		def get_comment(*args, **kwargs):
			comment = original_get_comment(*args, **kwargs)
			post = getattr(comment, "post", None) if comment else None
			if post and _is_admin_only_board(getattr(post, "sub", None)) and has_request_context():
				explicit_viewer = kwargs.get("v", args[1] if len(args) > 1 else None)
				if not _is_site_admin(_request_viewer(explicit_viewer)):
					graceful = kwargs.get("graceful", args[2] if len(args) > 2 else False)
					if graceful:
						return None
					abort(403, "This board is for administrators only.")
			return comment

		get_comment._obsession_admin_only_board = True
		get_helpers.get_comment = get_comment
		_replace_loaded_function(original_get_comment, get_comment)


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
	_install_admin_only_content_guards()

	@app.before_request
	def obsession_canonical_board_redirect():
		path = request.path

		if _is_admin_only_board_path(path):
			from files.routes.wrappers import get_logged_in_user
			v = get_logged_in_user()
			if not _is_site_admin(v):
				if request.method == "GET" and not g.is_api_or_xhr:
					return render_template("errors/admin_only_board.html", v=v), 403
				abort(403, "This board is for administrators only.")

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
