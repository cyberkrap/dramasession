import time
import secrets

from os import environ, listdir, path

import user_agents

from flask import g, session, has_request_context
from jinja2 import pass_context

from files.classes.user import User
from files.helpers.assetcache import assetcache_path
from files.helpers.config.const import *
from files.helpers.regex import *
from files.helpers.settings import get_settings, get_setting
from files.helpers.sorting_and_time import make_age_string
from files.routes.routehelpers import get_alt_graph, get_formkey
from files.__main__ import app, cache

@app.template_filter("formkey")
def formkey(u):
	return get_formkey(u)

@app.template_filter("post_embed")
def post_embed(id, v):
	from flask import render_template

	from files.helpers.get import get_post
	p = get_post(id, v, graceful=True)
	if p: return render_template("submission_listing.html", listing=[p], v=v)
	return ''

@app.template_filter("asset")
@pass_context
def template_asset(ctx, asset_path):
	return assetcache_path(asset_path)


@app.template_filter("asset_siteimg")
def template_asset_siteimg(asset_path):
	if SITE_NAME == "Obsession":
		asset_name = str(asset_path).lower()
		if asset_name in {"coins.webp", "wishcoin.webp"}:
			from files.helpers.wishcoin_asset import WISHCOIN_ASSET_URL
			return WISHCOIN_ASSET_URL
		if asset_name in {"marseybux.webp", "marseybux.png", "wishbux.webp"}:
			from files.helpers.wishcoin_asset import WISHBUX_ASSET_URL
			return WISHBUX_ASSET_URL
	# TODO: Add hashing for these using files.helpers.assetcache
	return f'/i/{SITE_NAME}/{asset_path}?v=3010'

@app.template_filter("timestamp")
def timestamp(timestamp):
	return make_age_string(timestamp)

@app.template_filter("number")
def number(value):
	if value is None or value == '':
		return ''
	try:
		return f'{int(value):,}'
	except (TypeError, ValueError):
		return value

@app.template_filter("house_icon")
def house_icon(house):
	if not house:
		return "/i/default-profile-pic.webp"
	filename = house.replace(" Founder", "")
	if filename not in HOUSES or filename == "None":
		return "/i/default-profile-pic.webp"
	asset = path.join("files", "assets", "images", SITE_NAME, "houses", f"{filename}.webp")
	if not path.isfile(asset):
		return "/i/default-profile-pic.webp"
	return f"/i/{SITE_NAME}/houses/{filename}.webp?v=2000"

@app.context_processor
def calc_users():
	loggedin_counter = 0
	loggedout_counter = 0
	loggedin_chat = 0
	v = getattr(g, 'v', None) if g else None
	if has_request_context and g and g.desires_auth and not g.is_api_or_xhr:
		loggedin = cache.get(LOGGED_IN_CACHE_KEY) or {}
		loggedout = cache.get(LOGGED_OUT_CACHE_KEY) or {}
		loggedin_chat = cache.get(CHAT_ONLINE_CACHE_KEY) or 0
		timestamp = int(time.time())

		if not session.get("session_id"):
			session.permanent = True
			session["session_id"] = secrets.token_hex(49)

		if v:
			if session["session_id"] in loggedout: del loggedout[session["session_id"]]
			loggedin[v.id] = timestamp
		else:
			ua = str(user_agents.parse(g.agent))
			if 'spider' not in ua.lower() and 'bot' not in ua.lower():
				loggedout[session["session_id"]] = (timestamp, ua)

		loggedin = {k: v for k, v in loggedin.items() if (timestamp - v) < LOGGEDIN_ACTIVE_TIME}
		loggedout = {k: v for k, v in loggedout.items() if (timestamp - v[0]) < LOGGEDIN_ACTIVE_TIME}
		cache.set(LOGGED_IN_CACHE_KEY, loggedin)
		cache.set(LOGGED_OUT_CACHE_KEY, loggedout)
		loggedin_counter = len(loggedin)
		loggedout_counter = len(loggedout)
	return {'loggedin_counter':loggedin_counter,
	        'loggedout_counter':loggedout_counter,
			'loggedin_chat':loggedin_chat}

def current_registered_users():
	return "{:,}".format(g.db.query(User).count())

def git_head():
	# Downloaded archives may not include Git metadata, but templates still render
	# the commit display. Keep local setup working with a harmless placeholder.
	try:
		with open('.git/HEAD', encoding='utf_8') as head_f:
			head_txt = head_f.read()
	except FileNotFoundError:
		return ('local', 'local')

	# Note: doing zero sanitization. Git branch names are extremely permissive.
	# However, they forbid '..', so I don't see an obvious dir traversal attack.
	# Also, a malicious branch name would mean someone already owned the server
	# or repo, so I think this isn't a weak link.
	try:
		head_path = git_regex.match(head_txt).group(1)
		with open('.git/' + head_path, encoding='utf_8') as ref_f:
			gitref = ref_f.read()[:7]
	except:
		gitref = 'Error'
	return (gitref, head_txt)

@app.context_processor
def inject_constants():
	return {"environ":environ, "SITE":SITE, "SITE_NAME":SITE_NAME, "SITE_FULL":SITE_FULL,
			"AUTOJANNY_ID":AUTOJANNY_ID, "MODMAIL_ID":MODMAIL_ID, "VAPID_PUBLIC_KEY":VAPID_PUBLIC_KEY,
			"listdir":listdir, "os_path":path,
			"PIZZASHILL_ID":PIZZASHILL_ID, "DEFAULT_COLOR":DEFAULT_COLOR,
			"COLORS":COLORS, "time":time, "PERMS":PERMS, "FEATURES":FEATURES,
			"HOLE_NAME":HOLE_NAME, "HOLE_STYLE_FLAIR":HOLE_STYLE_FLAIR, "HOLE_REQUIRED":HOLE_REQUIRED,
			"DEFAULT_THEME":DEFAULT_THEME, "DESCRIPTION":DESCRIPTION,
			"has_sidebar":has_sidebar, "has_logo":has_logo,
			"FP":FP, "patron":patron, "get_setting": get_setting,
			"SIDEBAR_THREAD":SIDEBAR_THREAD, "BANNER_THREAD":BANNER_THREAD,
			"BADGE_THREAD":BADGE_THREAD, "SNAPPY_THREAD":SNAPPY_THREAD,
			"approved_embed_hosts":approved_embed_hosts,
			"site_settings":get_settings(), "EMAIL":EMAIL, "max": max, "min": min, "user_can_see":User.can_see,
			"TELEGRAM_ID":TELEGRAM_ID, "EMAIL_REGEX_PATTERN":EMAIL_REGEX_PATTERN,
			"TRUESCORE_DONATE_MINIMUM":TRUESCORE_DONATE_MINIMUM, "PROGSTACK_ID":PROGSTACK_ID,
			"DONATE_LINK":DONATE_LINK, "DONATE_SERVICE":DONATE_SERVICE, "BAN_EVASION_DOMAIN":BAN_EVASION_DOMAIN,
			"HOUSE_JOIN_COST":HOUSE_JOIN_COST, "HOUSE_SWITCH_COST":HOUSE_SWITCH_COST, "IMAGE_FORMATS":','.join(IMAGE_FORMATS),
			"PAGE_SIZES":PAGE_SIZES, "THEMES":THEMES, "COMMENT_SORTS":COMMENT_SORTS, "SORTS":SORTS,
			"TIME_FILTERS":TIME_FILTERS, "HOUSES":HOUSES, "TIERS_ID_TO_NAME":TIERS_ID_TO_NAME,
			"DEFAULT_CONFIG_VALUE":DEFAULT_CONFIG_VALUE, "IS_LOCALHOST":IS_LOCALHOST, "BACKGROUND_CATEGORIES":BACKGROUND_CATEGORIES, "PAGE_SIZE":PAGE_SIZE, "TAGLINES":TAGLINES, "IS_FISTMAS":IS_FISTMAS, "get_alt_graph":get_alt_graph, "current_registered_users":current_registered_users, "gitref":git_head()
			}
