from sqlalchemy import func

from files.classes.hats import *
from files.helpers.alerts import *
from files.helpers.config.const import *
from files.helpers.useractions import *
from files.routes.wrappers import *
from files.__main__ import app, limiter

@app.get("/hats")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def hats(v:User):
	owned_hat_ids = [x.hat_id for x in v.owned_hats]

	if v.equipped_hat_ids:
		equipped = g.db.query(HatDef, User).join(HatDef.author).filter(HatDef.submitter_id == None, HatDef.id.in_(owned_hat_ids), HatDef.id.in_(v.equipped_hat_ids)).order_by(HatDef.price, HatDef.name).all()
		not_equipped = g.db.query(HatDef, User).join(HatDef.author).filter(HatDef.submitter_id == None, HatDef.id.in_(owned_hat_ids), HatDef.id.notin_(v.equipped_hat_ids)).order_by(HatDef.price, HatDef.name).all()
		owned = equipped + not_equipped
	else:
		owned = g.db.query(HatDef, User).join(HatDef.author).filter(HatDef.submitter_id == None, HatDef.id.in_(owned_hat_ids)).order_by(HatDef.price, HatDef.name).all()

	not_owned = g.db.query(HatDef, User).join(HatDef.author).filter(HatDef.submitter_id == None, HatDef.id.notin_(owned_hat_ids)).order_by(HatDef.price == 0, HatDef.price, HatDef.name).all()
	hats = owned + not_owned

	sales = g.db.query(func.sum(User.coins_spent_on_hats)).scalar()
	num_of_hats = g.db.query(HatDef).filter(HatDef.submitter_id == None).count()
	return render_template("hats.html", owned_hat_ids=owned_hat_ids, hats=hats, v=v, sales=sales, num_of_hats=num_of_hats)

@app.post("/buy_hat/<int:hat_id>")
@limiter.limit('100/minute;1000/3 days')
@limiter.limit('100/minute;1000/3 days', key_func=get_ID)
@auth_required
def buy_hat(v:User, hat_id):
	try: hat_id = int(hat_id)
	except: abort(404, "Hat not found!")

	hat = g.db.query(HatDef).filter_by(submitter_id=None, id=hat_id).one_or_none()
	if not hat: abort(404, "Hat not found!")

	existing = g.db.query(Hat).filter_by(user_id=v.id, hat_id=hat.id).one_or_none()
	if existing: abort(409, "You already own this hat!")

	if not hat.is_purchasable:
		abort(403, "This hat is not for sale!")

	if request.values.get("mb"):
		charged = v.charge_account('marseybux', hat.price)
		if not charged: abort(400, "Not enough marseybux!")

		hat.author.pay_account('marseybux', hat.price * 0.1)
		currency = "marseybux"
	else:
		charged = v.charge_account('coins', hat.price)
		if not charged: abort(400, "Not enough coins!")

		v.coins_spent_on_hats += hat.price
		hat.author.pay_account('coins', hat.price * 0.1)
		currency = "coins"

	new_hat = Hat(user_id=v.id, hat_id=hat.id)
	g.db.add(new_hat)

	g.db.add(v)
	g.db.add(hat.author)

	send_repeatable_notification(
		hat.author.id,
		f":marseycapitalistmanlet: @{v.username} has just bought `{hat.name}`, you have received your 10% cut ({int(hat.price * 0.1)} {currency}) :!marseycapitalistmanlet:"
	)

	if v.num_of_owned_hats >= 250:
		badge_grant(user=v, badge_id=154)
	elif v.num_of_owned_hats >= 100:
		badge_grant(user=v, badge_id=153)
	elif v.num_of_owned_hats >= 25:
		badge_grant(user=v, badge_id=152)

	return {"message": f"'{hat.name}' bought!"}


@app.post("/equip_hat/<int:hat_id>")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def equip_hat(v:User, hat_id):
	try: hat_id = int(hat_id)
	except: abort(404, "Hat not found!")

	hat = g.db.query(Hat).filter_by(hat_id=hat_id, user_id=v.id).one_or_none()
	if not hat: abort(403, "You don't own this hat!")

	hat.equipped = True
	g.db.add(hat)

	return {"message": f"'{hat.name}' equipped!"}

@app.post("/unequip_hat/<int:hat_id>")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def unequip_hat(v:User, hat_id):
	try: hat_id = int(hat_id)
	except: abort(404, "Hat not found!")

	hat = g.db.query(Hat).filter_by(hat_id=hat_id, user_id=v.id).one_or_none()
	if not hat: abort(403, "You don't own this hat!")

	hat.equipped = False
	g.db.add(hat)

	return {"message": f"'{hat.name}' unequipped!"}

@app.get("/hat_owners/<int:hat_id>")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def hat_owners(v:User, hat_id):
	try: hat_id = int(hat_id)
	except: abort(404, "Hat not found!")

	try: page = int(request.values.get("page", 1))
	except: page = 1

	users = [x[1] for x in g.db.query(Hat, User).join(Hat.owners).filter(Hat.hat_id == hat_id).offset(PAGE_SIZE * (page - 1)).limit(PAGE_SIZE+1).all()]

	next_exists = (len(users) > PAGE_SIZE)
	users = users[:PAGE_SIZE]

	return render_template("user_cards.html",
						v=v,
						users=users,
						next_exists=next_exists,
						page=page,
						user_cards_title="Hat Owners",
						)
