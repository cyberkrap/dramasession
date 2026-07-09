import time
from flask import g, request, session

from files.classes.clients import ClientAuth
from files.helpers.alerts import *
from files.helpers.config.const import *
from files.helpers.get import get_account
from files.helpers.logging import log_file
from files.helpers.settings import get_setting
from files.routes.routehelpers import validate_formkey
from files.__main__ import app, db_session, limiter

def get_ID():
	if request.headers.get("Authorization"):
		x = request.headers.get("Authorization")
	elif session.get("lo_user"):
		x = session.get("lo_user")
	else:
		x = "logged_out"
	
	return f'{SITE}-{x}'

def get_logged_in_user():
	if hasattr(g, 'v'): return g.v
	if not getattr(g, 'db', None): g.db = db_session()
	g.desires_auth = True
	v = None
	token = request.headers.get("Authorization","").strip()
	if token:
		client = g.db.query(ClientAuth).filter(ClientAuth.access_token == token).one_or_none()
		if client:
			v = client.user
			v.client = client
	else:
		lo_user = session.get("lo_user")
		if lo_user:
			id = int(lo_user)
			v = get_account(id, graceful=True)
			if v:
				v.client = None
				nonce = session.get("login_nonce", 0)
				if nonce < v.login_nonce or v.id != id:
					session.pop("lo_user")
					v = None

				if v and request.method != "GET":
					submitted_key = request.values.get("formkey")
					if not validate_formkey(v, submitted_key):
						v = None
			else:
				session.pop("lo_user")

	# if SITE == 'devrama.net' and not (v and v.id == 7):
	# 	abort(403, "Only Aevann can access devrama for now!")

	if request.method.lower() != "get" and get_setting('read_only_mode') and not (v and v.admin_level >= PERMS['SITE_BYPASS_READ_ONLY_MODE']):
		abort(403)

	g.v = v

	if v:
		v.poor = session.get('poor')
		# Check against last_active + ACTIVE_TIME to reduce frequency of
		# UPDATEs in exchange for a ±ACTIVE_TIME margin of error.
		timestamp = int(time.time())
		if (v.last_active + LOGGEDIN_ACTIVE_TIME) < timestamp:
			v.last_active = timestamp
			g.db.add(v)

	if AEVANN_ID and request.headers.get("Cf-Ipcountry") == 'EG':
		if v and v.id != AEVANN_ID and not v.username.startswith('Aev') and v.truescore > 0:
			with open(f"{LOG_DIRECTORY}/eg.log", "a+", encoding="utf-8") as f:
				f.seek(0)
				ip = request.headers.get('CF-Connecting-IP')
				if f'@{v.username}, ' not in f.read():
					t = time.strftime("%d/%B/%Y %H:%M:%S UTC", time.gmtime(time.time()))
					log_file(f'@{v.username}, {v.truescore}, {ip}, {t}\n', 'eg.log')

	g.is_api_or_xhr = bool((v and v.client) or request.headers.get("xhr"))

	return v

def auth_desired(f):
	def wrapper(*args, **kwargs):
		v = get_logged_in_user()
		return make_response(f(*args, v=v, **kwargs))
	wrapper.__name__ = f.__name__
	return wrapper

def auth_desired_with_logingate(f):
	def wrapper(*args, **kwargs):
		v = get_logged_in_user()
		if get_setting('login_required') and not v: abort(401)

		if request.path.startswith('/logged_out'):
			redir = request.full_path.replace('/logged_out','')
			if not redir: redir = '/'
			return redirect(redir)

		return make_response(f(*args, v=v, **kwargs))
	wrapper.__name__ = f.__name__
	return wrapper

def auth_required(f):
	def wrapper(*args, **kwargs):
		v = get_logged_in_user()
		if not v: abort(401)
		return make_response(f(*args, v=v, **kwargs))
	wrapper.__name__ = f.__name__
	return wrapper

def is_not_permabanned(f):
	def wrapper(*args, **kwargs):
		v = get_logged_in_user()
		if not v: abort(401)
		if v.is_suspended_permanently: abort(403)
		return make_response(f(*args, v=v, **kwargs))
	wrapper.__name__ = f.__name__
	return wrapper

def admin_level_required(x):
	def wrapper_maker(f):
		def wrapper(*args, **kwargs):
			v = get_logged_in_user()
			if not v: abort(401)
			if v.admin_level < x: abort(403)
			if x and SITE != 'devrama.net' and not IS_LOCALHOST and not v.mfa_secret:
				abort(403, "You need to enable 2FA to use admin features!")
			return make_response(f(*args, v=v, **kwargs))

		wrapper.__name__ = f.__name__
		return wrapper
	return wrapper_maker

def feature_required(x):
	def wrapper_maker(f):
		def wrapper(*args, **kwargs):
			if not FEATURES[x]: abort(404)
			return make_response(f(*args, **kwargs))
		wrapper.__name__ = f.__name__
		return wrapper
	return wrapper_maker
