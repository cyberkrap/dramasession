import gevent.monkey

gevent.monkey.patch_all()

import faulthandler
from os import environ
from sys import argv, stdout

import gevent
from flask import Flask
from flask_caching import Cache
from flask_compress import Compress
from flask_limiter import Limiter
from sqlalchemy import *
from sqlalchemy.orm import scoped_session, sessionmaker

from files.helpers.config.const import *
from files.helpers.const_stateful import const_initialize
from files.helpers.settings import reload_settings, start_watching_settings

app = Flask(__name__, template_folder='templates')
app.url_map.strict_slashes = False
app.jinja_env.cache = {}
app.jinja_env.auto_reload = True
app.jinja_env.add_extension('jinja2.ext.do')
faulthandler.enable()

def _startup_check():
	'''
	Performs some sanity checks on startup to make sure we aren't attempting
	to startup with obviously invalid values that won't work anyway
	'''
	if not SITE: raise TypeError("SITE environment variable must exist and not be None")
	if SITE.startswith('.'): raise ValueError("Domain must not start with a dot")

app.config['SERVER_NAME'] = SITE
app.config['SECRET_KEY'] = environ.get('SECRET_KEY').strip()
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 3153600
_startup_check()
if not IS_LOCALHOST:
	app.config["SESSION_COOKIE_SECURE"] = True

app.config["SESSION_COOKIE_NAME"] = "session_" + environ.get("SITE_NAME").strip().lower()
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["PERMANENT_SESSION_LIFETIME"] = SESSION_LIFETIME
app.config['SESSION_REFRESH_EACH_REQUEST'] = False

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URL'] = environ.get("DATABASE_URL").strip()

app.config["CACHE_TYPE"] = "RedisCache"
app.config["CACHE_REDIS_URL"] = environ.get("REDIS_URL").strip()
app.config["CACHE_DEFAULT_TIMEOUT"] = 604800

app.config['SERVICE'] = Service.RDRAMA
if "load_chat" in argv:
	app.config['SERVICE'] = Service.CHAT

def get_CF():
	with app.app_context():
		x = request.headers.get('CF-Connecting-IP')
		if x: return x
		return request.remote_addr

limiter = Limiter(
	app=app,
	key_func=get_CF,
	default_limits=[DEFAULT_RATELIMIT],
	application_limits=["10/second;200/minute;5000/hour;10000/day"],
	storage_uri=environ.get("REDIS_URL", "redis://localhost"),
)

engine = create_engine(app.config['SQLALCHEMY_DATABASE_URL'])

db_session = scoped_session(sessionmaker(bind=engine, autoflush=False))

const_initialize(db_session)

reload_settings()
start_watching_settings()

cache = Cache(app)
Compress(app)

from files.routes.allroutes import *

if app.config['SERVICE'] == Service.RDRAMA:
	from files.routes import *

elif app.config['SERVICE'] == Service.CHAT:
	from files.routes.chat import *

stdout.flush()
