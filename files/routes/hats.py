from sqlalchemy import func

from files.classes.hats import *
from files.helpers.alerts import *
from files.helpers.config.const import *
from files.helpers.get import get_user
from files.helpers.useractions import *
from files.routes.wrappers import *
from files.__main__ import app, limiter

@app.get("/hats")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def hats(v:User):
	owned_hats = list(v.owned_hats)
	owned_hat_ids = [x.hat_id for x in owned_hats]
	obtained_utc_by_hat = {x.hat_id: x.created_utc or 0 for x in owned_hats}
	owner_counts = dict(
		g.db.query(Hat.hat_id, func.count(Hat.user_id))
		.group_by(Hat.hat_id)
		.all()
	)

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
	return render_template(
		"hats.html",
		owned_hat_ids=owned_hat_ids,
		owner_counts=owner_counts,
		obtained_utc_by_hat=obtained_utc_by_hat,
		hats=hats,
		v=v,
		sales=sales,
		num_of_hats=num_of_hats,
	)

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
		if not charged: abort(400, "Not enough Wishbux!")

		hat.author.pay_account('marseybux', hat.price * 0.1)
		currency = "Wishbux"
	else:
		charged = v.charge_account('coins', hat.price)
		if not charged: abort(400, "Not enough Wishcoins!")

		v.coins_spent_on_hats += hat.price
		hat.author.pay_account('coins', hat.price * 0.1)
		currency = "Wishcoins"

	new_hat = Hat(user_id=v.id, hat_id=hat.id)
	g.db.add(new_hat)

	g.db.add(v)
	g.db.add(hat.author)

	send_repeatable_notification(
		hat.author.id,
		f"@{v.username} bought the hat {hat.name}; you received a 10% creator share ({int(hat.price * 0.1)} {currency})."
	)

	if v.num_of_owned_hats >= 250:
		badge_grant(user=v, badge_id=154)
	elif v.num_of_owned_hats >= 100:
		badge_grant(user=v, badge_id=153)
	elif v.num_of_owned_hats >= 25:
		badge_grant(user=v, badge_id=152)

	return {"message": f"'{hat.name}' bought!"}


@app.post("/gift_hat/<int:hat_id>")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@auth_required
def gift_hat(v:User, hat_id):
	try: hat_id = int(hat_id)
	except: abort(404, "Hat not found!")

	hat_def = g.db.query(HatDef).filter_by(submitter_id=None, id=hat_id).one_or_none()
	if not hat_def: abort(404, "Hat not found!")

	username = str(request.values.get("username") or "").strip().lstrip("@")
	if not username: abort(400, "Enter a username to receive the gift.")

	recipient_lookup = get_user(username, graceful=True)
	if not recipient_lookup: abort(404, "That user does not exist.")
	if recipient_lookup.id == v.id: abort(400, "You cannot gift a hat to yourself.")

	locked_users = {
		user.id: user
		for user in g.db.query(User)
		.filter(User.id.in_([v.id, recipient_lookup.id]))
		.with_for_update()
		.all()
	}
	sender = locked_users.get(v.id)
	recipient = locked_users.get(recipient_lookup.id)
	if not sender or not recipient: abort(404, "One of those accounts no longer exists.")

	owned_hat = g.db.query(Hat).filter_by(user_id=sender.id, hat_id=hat_id).with_for_update().one_or_none()
	if not owned_hat: abort(403, "You can only gift a hat you currently own.")

	recipient_hat = g.db.query(Hat).filter_by(user_id=recipient.id, hat_id=hat_id).one_or_none()
	if recipient_hat: abort(409, f"@{recipient.username} already owns {hat_def.name}.")

	g.db.delete(owned_hat)
	g.db.flush()
	g.db.add(Hat(user_id=recipient.id, hat_id=hat_id, equipped=False))
	g.db.flush()

	recipient_hat_count = g.db.query(func.count(Hat.hat_id)).filter(Hat.user_id == recipient.id).scalar() or 0
	if recipient_hat_count >= 250:
		badge_grant(user=recipient, badge_id=154)
	elif recipient_hat_count >= 100:
		badge_grant(user=recipient, badge_id=153)
	elif recipient_hat_count >= 25:
		badge_grant(user=recipient, badge_id=152)

	send_repeatable_notification(
		recipient.id,
		f"@{sender.username} has gifted you the hat {hat_def.name}. You can equip it in the [Hats Shop](/hats)."
	)

	return {"message": f"'{hat_def.name}' transferred to @{recipient.username}."}


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
