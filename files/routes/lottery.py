from files.helpers.alerts import *
from files.helpers.config.const import *
from files.helpers.get import *
from files.helpers.lottery import *
from files.routes.wrappers import *

from files.__main__ import app, limiter

@app.post("/lottery/end")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@admin_level_required(PERMS['LOTTERY_ADMIN'])
def lottery_end(v):
	success, message = end_lottery_session()
	return {"message": message} if success else {"error": message}


@app.post("/lottery/start")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@admin_level_required(PERMS['LOTTERY_ADMIN'])
def lottery_start(v):
	start_new_lottery_session()
	return {"message": "Lottery started!"}


@app.post("/lottery/buy")
@limiter.limit("3/second;100/minute;500/hour;1000/day")
@limiter.limit("3/second;100/minute;500/hour;1000/day", key_func=get_ID)
@auth_required
def lottery_buy(v:User):
	try: quantity = int(request.values.get("quantity"))
	except: abort(400, "Invalid ticket quantity!")

	success, message = purchase_lottery_tickets(v, quantity)
	lottery, participants = get_active_lottery_stats()


	if success:
		return {"message": message, "stats": {"user": v.lottery_stats, "lottery": lottery, "participants": participants}}
	else:
		return {"error": message, "stats": {"user": v.lottery_stats, "lottery": lottery, "participants": participants}}


@app.get("/lottery/active")
@limiter.limit("3/second;100/minute;500/hour;1000/day")
@limiter.limit("3/second;100/minute;500/hour;1000/day", key_func=get_ID)
@auth_required
def lottery_active(v:User):
	lottery, participants = get_active_lottery_stats()

	return {"message": "", "stats": {"user": v.lottery_stats, "lottery": lottery, "participants": participants}}

@app.get("/admin/lottery/participants")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@admin_level_required(PERMS['LOTTERY_VIEW_PARTICIPANTS'])
def lottery_admin(v):
	participants = get_users_participating_in_lottery()
	return render_template("admin/lottery.html", v=v, participants=participants)
