import time

from files.classes import *
from files.helpers.config.const import *
from files.helpers.get import *
from files.helpers.mail import *
from files.helpers.useractions import *
from files.routes.wrappers import *
from files.routes.users import claim_rewards
from files.__main__ import app, limiter

@app.post("/verify_email")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@auth_required
def verify_email(v):
	send_verification_email(v)
	return {"message": "Email has been sent. Check your spam folder if you can't find it!"}


@app.get("/activate")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def activate(v:User):
	email = request.values.get("email", "").strip().lower()

	if not email_regex.fullmatch(email):
		abort(400, "Invalid email")

	id = request.values.get("id", "").strip()
	timestamp = int(request.values.get("time", "0"))
	token = request.values.get("token", "").strip()

	if int(time.time()) - timestamp > 3600:
		abort(410, "This email verification link has expired. Visit your settings to send yourself a new one!")

	user = get_account(id)

	if not validate_hash(f"{email}+{id}+{timestamp}", token):
		abort(403)

	if user.is_activated and user.email == email:
		abort(400, "Email already verified!")

	user.email = email
	user.is_activated = True
	claim_rewards(user)

	badge_grant(user=user, badge_id=2)

	g.db.add(user)

	return render_template("message_success.html", v=v, title="Email verified!", message=f"Your email {email} has been verified. Thank you!")
