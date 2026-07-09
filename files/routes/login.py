import secrets
from urllib.parse import urlencode

import requests

from files.__main__ import app, cache, get_CF, limiter
from files.classes.follows import Follow
from files.helpers.actions import *
from files.helpers.config.const import *
from files.helpers.settings import get_setting
from files.helpers.get import *
from files.helpers.mail import send_mail, send_verification_email
from files.helpers.logging import log_file
from files.helpers.regex import *
from files.helpers.security import *
from files.helpers.useractions import badge_grant
from files.routes.routehelpers import check_for_alts
from files.routes.wrappers import *


NO_LOGIN_REDIRECT_URLS = ("/login", "/logout", "/signup", "/forgot", "/reset", "/reset_2fa", "/lost_2fa")

@app.get("/login")
@auth_desired
def login_get(v:Optional[User]):
	redir = request.values.get("redirect", "").strip().rstrip('?').lower()
	if v:
		if redir and is_site_url(redir) and redir not in NO_LOGIN_REDIRECT_URLS:
			return redirect(redir)
		return redirect('/')
	return render_template("login/login.html", failed=False, redirect=redir), 401

def login_deduct_when(resp):
	if not g:
		return False
	elif not hasattr(g, 'login_failed'):
		return False
	return g.login_failed

@app.post("/login")
@auth_desired
@limiter.limit("6/minute;10/day", deduct_when=login_deduct_when)
def login_post(v:Optional[User]):
	if v: abort(400)
	g.login_failed = True

	username = request.values.get("username")

	if not username: abort(400)
	username = username.lstrip('@').replace('\\', '').replace('_', '\_').replace('%', '').strip()

	if not username: abort(400)
	if username.startswith('@'): username = username[1:]

	if "@" in username:
		try: account = g.db.query(User).filter(User.email.ilike(username)).one_or_none()
		except: abort(400, "Multiple usernames have this email attached;<br>Please specify the username you want to login to!")
	else: account = get_user(username, graceful=True)

	if not account:
		time.sleep(random.uniform(0, 2))
		return render_template("login/login.html", failed=True), 401


	if request.values.get("password"):
		if not account.verifyPass(request.values.get("password")):
			log_failed_admin_login_attempt(account, "password")
			time.sleep(random.uniform(0, 2))
			return render_template("login/login.html", failed=True), 401

		if account.mfa_secret:
			now = int(time.time())
			hash = generate_hash(f"{account.id}+{now}+2fachallenge")
			g.login_failed = False
			return render_template("login/login_2fa.html",
								v=account,
								time=now,
								hash=hash,
								redirect=request.values.get("redirect", "/")
								)
	elif request.values.get("2fa_token", "x"):
		now = int(time.time())

		try:
			if now - int(request.values.get("time")) > 600:
				return redirect('/login')
		except:
			abort(400)

		formhash = request.values.get("hash")
		if not validate_hash(f"{account.id}+{request.values.get('time')}+2fachallenge", formhash):
			return redirect("/login")

		if not account.validate_2fa(request.values.get("2fa_token", "").strip()):
			hash = generate_hash(f"{account.id}+{now}+2fachallenge")
			log_failed_admin_login_attempt(account, "2FA token")
			return render_template("login/login_2fa.html",
								v=account,
								time=now,
								hash=hash,
								failed=True,
								), 401
	else:
		abort(400)

	g.login_failed = False
	on_login(account)

	redir = request.values.get("redirect", "").strip().rstrip('?').lower()
	if redir and is_site_url(redir) and redir not in NO_LOGIN_REDIRECT_URLS:
		return redirect(redir)
	return redirect('/')

def log_failed_admin_login_attempt(account:User, type:str):
		if not account or account.admin_level < PERMS['SITE_WARN_ON_INVALID_AUTH']: return
		ip = get_CF()
		print(f"A site admin from {ip} failed to login to account @{account.user_name} (invalid {type})")
		t = time.strftime("%d/%B/%Y %H:%M:%S UTC", time.gmtime(time.time()))
		log_file(f"{t}, {ip}, {account.username}, {type}", "admin_failed_logins.log")

def on_login(account, redir=None):
	session.permanent = True
	session["lo_user"] = account.id
	session["login_nonce"] = account.login_nonce
	check_for_alts(account, include_current_session=True)


@app.get("/me")
@app.get("/@me")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def me(v:User):
	if v.client: return v.json
	else: return redirect(v.url)


@app.post("/logout")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@auth_required
def logout(v):
	loggedin = cache.get(f'{SITE}_loggedin') or {}
	if session.get("lo_user") in loggedin: del loggedin[session["lo_user"]]
	cache.set(f'{SITE}_loggedin', loggedin)
	session.pop("lo_user", None)
	return {"message": "Logout successful!"}

@app.get("/signup")
@auth_desired
def sign_up_get(v:Optional[User]):
	if not get_setting('signups'):
		abort(403, "New account registration is currently closed. Please come back later!")

	if v: return redirect(SITE_FULL)
	ref = request.values.get("ref")

	if ref:
		ref = ref.replace('\\', '').replace('_', '\_').replace('%', '').strip()
		ref_user = g.db.query(User).filter(User.username.ilike(ref)).one_or_none()
	else:
		ref_user = None

	if ref_user and (ref_user.id in session.get("history", [])):
		return render_template("login/sign_up_failed_ref.html"), 403

	now = int(time.time())
	token = secrets.token_hex(16)
	session["signup_token"] = token

	formkey_hashstr = str(now) + token + g.agent

	formkey = hmac.new(key=bytes(SECRET_KEY, "utf-16"),
					msg=bytes(formkey_hashstr, "utf-16"),
					digestmod='md5'
					).hexdigest()

	error = request.values.get("error")

	redir = request.values.get("redirect", "/").strip().rstrip('?')
	if redir:
		if not is_site_url(redir): redir = "/"

	status_code = 200 if not error else 400

	return render_template("login/sign_up.html",
						formkey=formkey,
						now=now,
						ref_user=ref_user,
						turnstile=TURNSTILE_SITEKEY,
						error=error,
						redirect=redir
						), status_code


@app.post("/signup")
@limiter.limit("1/second;10/day")
@auth_desired
def sign_up_post(v:Optional[User]):
	if not get_setting('signups'):
		abort(403, "New account registration is currently closed. Please come back later!")

	if v: abort(403)

	form_timestamp = request.values.get("now", '0')
	form_formkey = request.values.get("formkey", "none")

	username = request.values.get("username")
	if not username: abort(400)
	username = username.strip()

	email = request.values.get("email").strip().lower()

	ref_id = 0
	try:
		ref_id = int(request.values.get("referred_by", 0))
	except:
		pass

	redir = request.values.get("redirect", "").strip().rstrip('?').lower()

	def signup_error(error):
		if ref_id:
			ref_user = g.db.get(User, ref_id)
		else:
			ref_user = None

		now = int(time.time())
		token = secrets.token_hex(16)
		session["signup_token"] = token
		formkey_hashstr = str(now) + token + g.agent
		formkey = hmac.new(key=bytes(SECRET_KEY, "utf-16"),
						msg=bytes(formkey_hashstr, "utf-16"),
						digestmod='md5'
						).hexdigest()

		return render_template("login/sign_up.html",
							formkey=formkey,
							now=now,
							ref_user=ref_user,
							turnstile=TURNSTILE_SITEKEY,
							error=error,
							redirect=redir,
							username=username,
							email=email,
							), 400

	submitted_token = session.get("signup_token", "")
	if not submitted_token:
		session.clear()
		return signup_error(f"An error occurred while attempting to signup. If you get this repeatedly, please make sure cookies are enabled!")

	correct_formkey_hashstr = form_timestamp + submitted_token + g.agent
	correct_formkey = hmac.new(key=bytes(SECRET_KEY, "utf-16"),
								msg=bytes(correct_formkey_hashstr, "utf-16"),
								digestmod='md5'
							).hexdigest()

	now = int(time.time())

	if now - int(form_timestamp) < 5:
		return signup_error("There was a problem. Please try again!")

	if not hmac.compare_digest(correct_formkey, form_formkey):
		if IS_LOCALHOST: return signup_error("There was a problem. Please try again!")
		return signup_error("There was a problem. Please try again!")

	if not request.values.get(
			"password") == request.values.get("password_confirm"):
		return signup_error("Passwords did not match. Please try again!")

	if not valid_username_regex.fullmatch(username):
		return signup_error("Invalid username")

	if not valid_password_regex.fullmatch(request.values.get("password")):
		return signup_error("Password must be between 8 and 100 characters!")

	if email:
		if not email_regex.fullmatch(email):
			return signup_error("Invalid email!")
	else: email = None

	existing_account = get_user(username, graceful=True)
	if existing_account:
		return signup_error("An account with that username already exists!")

	if TURNSTILE_SITEKEY != DEFAULT_CONFIG_VALUE:
		token = request.values.get("cf-turnstile-response")
		if not token:
			return signup_error("Unable to verify captcha [1].")

		data = {"secret": TURNSTILE_SECRET,
				"response": token,
				"sitekey": TURNSTILE_SITEKEY}
		url = "https://challenges.cloudflare.com/turnstile/v0/siteverify"

		x = requests.post(url, data=data, timeout=5)

		if not x.json()["success"]:
			return signup_error("Unable to verify captcha [2].")

	session.pop("signup_token")

	users_count = g.db.query(User).count()

	profileurl = None
	if PFP_DEFAULT_MARSEY:
		profileurl = '/e/' + random.choice(marseys_const) + '.webp'

	new_user = User(
		username=username,
		original_username = username,
		password=request.values.get("password"),
		email=email,
		referred_by=ref_id or None,
		profileurl=profileurl
		)

	if users_count == 4:
		new_user.admin_level = 5
		session["history"] = []

	g.db.add(new_user)

	g.db.commit()

	if ref_id:
		ref_user = get_account(ref_id)

		if ref_user:
			badge_grant(user=ref_user, badge_id=10)
			# off-by-one: newly referred user isn't counted
			if ref_user.referral_count >= 9:
				badge_grant(user=ref_user, badge_id=11)
			if ref_user.referral_count >= 99:
				badge_grant(user=ref_user, badge_id=12)

	if email:
		send_verification_email(new_user)


	session.permanent = True
	session["lo_user"] = new_user.id

	check_for_alts(new_user, include_current_session=True)
	send_notification(new_user.id, WELCOME_MSG)

	if SIGNUP_FOLLOW_ID:
		signup_autofollow = get_account(SIGNUP_FOLLOW_ID)
		new_follow = Follow(user_id=new_user.id, target_id=signup_autofollow.id)
		g.db.add(new_follow)
		signup_autofollow.stored_subscriber_count += 1
		g.db.add(signup_autofollow)
		send_notification(signup_autofollow.id, f"A new user - @{new_user.username} - has followed you automatically!")
	elif CARP_ID:
		send_notification(CARP_ID, f"A new user - @{new_user.username} - has signed up!")

	if redir and is_site_url(redir) and redir not in NO_LOGIN_REDIRECT_URLS:
		return redirect(redir)
	return redirect('/')


@app.get("/forgot")
def get_forgot():
	return render_template("login/forgot_password.html")


@app.post("/forgot")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
def post_forgot():

	username = request.values.get("username")
	if not username: abort(400)

	email = request.values.get("email",'').strip().lower()

	if not email_regex.fullmatch(email):
		return render_template("login/forgot_password.html", error="Invalid email!"), 400


	username = username.lstrip('@').replace('\\', '').replace('_', '\_').replace('%', '').strip()
	email = email.replace('\\', '').replace('_', '\_').replace('%', '').strip()

	user = g.db.query(User).filter(
		User.username.ilike(username),
		User.email.ilike(email)).one_or_none()

	if user:
		now = int(time.time())
		token = generate_hash(f"{user.id}+{now}+forgot+{user.login_nonce}")
		url = f"{SITE_FULL}/reset?id={user.id}&time={now}&token={token}"

		send_mail(to_address=user.email,
				subject="Password Reset Request",
				html=render_template("email/password_reset.html",
									action_url=url,
									v=user)
				)

	return render_template("login/forgot_password.html",
						msg="If the username and email matches an account, you will be sent a password reset email. Check your spam folder if you can't find it."), 202


@app.get("/reset")
def get_reset():
	user_id = request.values.get("id")
	timestamp = 0
	try:
		timestamp = int(request.values.get("time",0))
	except:
		pass
	token = request.values.get("token")
	now = int(time.time())

	if now - timestamp > 600:
		abort(410, "This password reset link has expired!")

	user = get_account(user_id)

	if not validate_hash(f"{user_id}+{timestamp}+forgot+{user.login_nonce}", token):
		abort(400)

	reset_token = generate_hash(f"{user.id}+{timestamp}+reset+{user.login_nonce}")

	return render_template("login/reset_password.html",
						v=user,
						token=reset_token,
						time=timestamp,
						)


@app.post("/reset")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@auth_desired
def post_reset(v:Optional[User]):
	if v: return redirect('/')
	user_id = request.values.get("user_id")
	timestamp = 0
	try:
		timestamp = int(request.values.get("time"))
	except:
		abort(400)
	token = request.values.get("token")
	password = request.values.get("password")
	confirm_password = request.values.get("confirm_password")

	now = int(time.time())

	if now - timestamp > 600:
		abort(410, "This password reset link has expired!")

	user = get_account(user_id)
	if not validate_hash(f"{user_id}+{timestamp}+reset+{user.login_nonce}", token):
		abort(400)

	if password != confirm_password:
		return render_template("login/reset_password.html",
							v=user,
							token=token,
							time=timestamp,
							error="Passwords didn't match."), 400

	user.passhash = hash_password(password)
	g.db.add(user)


	return render_template("message_success.html",
						title="Password reset successful!",
						message="Login normally to access your account.")

@app.get("/lost_2fa")
@auth_desired
def lost_2fa(v:Optional[User]):
	if v and not v.mfa_secret: abort(400, "You don't have 2FA enabled")
	return render_template("login/lost_2fa.html", v=v)

@app.post("/lost_2fa")
@limiter.limit("1/second;6/minute;200/hour;1000/day")
def lost_2fa_post():
	username=request.values.get("username")
	user=get_user(username, graceful=True)
	if not user or not user.email or not user.mfa_secret:
		return render_template("message.html",
						title="Removal request received",
						message="If username, password, and email match, we will send you an email."), 202


	email=request.values.get("email").strip().lower()

	if not email_regex.fullmatch(email):
		abort(400, "Invalid email")

	password =request.values.get("password")
	if not user.verifyPass(password):
		return render_template("message.html",
						title="Removal request received",
						message="If username, password, and email match, we will send you an email."), 202

	valid=int(time.time())
	token=generate_hash(f"{user.id}+{user.username}+disable2fa+{valid}+{user.mfa_secret}+{user.login_nonce}")

	action_url=f"{SITE_FULL}/reset_2fa?id={user.id}&t={valid}&token={token}"

	send_mail(to_address=user.email,
			subject="2FA Removal Request",
			html=render_template("email/2fa_remove.html",
								action_url=action_url,
								v=user)
			)

	return render_template("message.html",
						title="Removal request received",
						message="If the username, password, and email match, we will send you an email. Check your spam folder if you can't find it."), 202

@app.get("/reset_2fa")
def reset_2fa():
	now=int(time.time())
	t = request.values.get("t")
	if not t: abort(400)
	try:
		t = int(t)
	except:
		abort(400)

	if now > t+3600*24:
		abort(410, "This 2FA reset link has expired!")

	token=request.values.get("token")
	uid=request.values.get("id")

	user=get_account(uid)

	if not validate_hash(f"{user.id}+{user.username}+disable2fa+{t}+{user.mfa_secret}+{user.login_nonce}", token):
		abort(403)

	user.mfa_secret=None
	g.db.add(user)

	return render_template("message_success.html",
						title="Two-factor authentication removed.",
						message="Login normally to access your account.")
