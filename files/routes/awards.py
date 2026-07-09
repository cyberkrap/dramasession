from copy import deepcopy

from flask import g, request
from sqlalchemy import func

from files.classes.award import AwardRelationship
from files.classes.userblock import UserBlock
from files.helpers.actions import *
from files.helpers.alerts import *
from files.helpers.config.const import *
from files.helpers.config.awards import AWARDS_ENABLED, HOUSE_AWARDS, LOOTBOX_ITEM_COUNT, LOOTBOX_CONTENTS
from files.helpers.get import *
from files.helpers.marsify import marsify
from files.helpers.owoify import owoify
from files.helpers.regex import *
from files.helpers.sanitize import filter_emojis_only
from files.helpers.useractions import *
from files.routes.wrappers import *
from files.__main__ import app, cache, limiter

from .front import frontlist

@app.get("/shop")
@app.get("/settings/shop")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def shop(v:User):
	AWARDS = deepcopy(AWARDS_ENABLED)

	if v.house:
		AWARDS[v.house] = deepcopy(HOUSE_AWARDS[v.house])

	for val in AWARDS.values(): val["owned"] = 0

	for useraward in g.db.query(AwardRelationship).filter(AwardRelationship.user_id == v.id, AwardRelationship.submission_id == None, AwardRelationship.comment_id == None).all():
		if useraward.kind in AWARDS: AWARDS[useraward.kind]["owned"] += 1

	for val in AWARDS.values():
		val["baseprice"] = int(val["price"])
		if val["kind"].endswith('Founder'):
			val["baseprice"] = int(val["baseprice"] / 0.75)
		val["price"] = int(val["price"] * v.discount)

	sales = g.db.query(func.sum(User.coins_spent)).scalar()
	return render_template("shop.html", awards=list(AWARDS.values()), v=v, sales=sales)


@app.post("/buy/<award>")
@limiter.limit("100/minute;200/hour;1000/day")
@limiter.limit("100/minute;200/hour;1000/day", key_func=get_ID)
@auth_required
def buy(v:User, award):
	if award == 'benefactor' and not request.values.get("mb"):
		abort(403, "You can only buy the Benefactor award with marseybux!")

	if award == 'ghost' and v.admin_level < PERMS['BUY_GHOST_AWARD']:
		abort(403, "Only admins can buy this award")

	AWARDS = deepcopy(AWARDS_ENABLED)

	if v.house:
		AWARDS[v.house] = HOUSE_AWARDS[v.house]

	if award not in AWARDS: abort(400)
	og_price = AWARDS[award]["price"]

	award_title = AWARDS[award]['title']
	price = int(og_price * v.discount)

	if request.values.get("mb"):
		if award == "grass":
			abort(403, "You can't buy the grass award with marseybux!")

		charged = v.charge_account('marseybux', price)
		if not charged:
			abort(400, "Not enough marseybux!")
	else:
		charged = v.charge_account('coins', price)
		if not charged:
			abort(400, "Not enough coins!")

		v.coins_spent += price
		if v.coins_spent >= 1000000:
			badge_grant(badge_id=73, user=v)
		elif v.coins_spent >= 500000:
			badge_grant(badge_id=72, user=v)
		elif v.coins_spent >= 250000:
			badge_grant(badge_id=71, user=v)
		elif v.coins_spent >= 100000:
			badge_grant(badge_id=70, user=v)
		elif v.coins_spent >= 10000:
			badge_grant(badge_id=69, user=v)
		g.db.add(v)


	if award == "lootbox":
		lootbox_items = []
		for _ in range(LOOTBOX_ITEM_COUNT): # five items per lootbox
			lb_award = random.choice(LOOTBOX_CONTENTS)
			lootbox_items.append(AWARDS[lb_award]['title'])
			lb_award = AwardRelationship(user_id=v.id, kind=lb_award, price_paid=price // LOOTBOX_ITEM_COUNT)
			g.db.add(lb_award)
			g.db.flush()

		v.lootboxes_bought += 1
		lootbox_msg = "You open your lootbox and receive: " + ', '.join(lootbox_items)
		send_repeatable_notification(v.id, lootbox_msg)

		if v.lootboxes_bought == 10:
			badge_grant(badge_id=76, user=v)
		elif v.lootboxes_bought == 50:
			badge_grant(badge_id=77, user=v)
		elif v.lootboxes_bought == 150:
			badge_grant(badge_id=78, user=v)

		return {"message": lootbox_msg}
	else:
		award_object = AwardRelationship(user_id=v.id, kind=award, price_paid=price)
		g.db.add(award_object)

	g.db.add(v)

	if CARP_ID and v.id != CARP_ID and og_price >= 5000:
		send_repeatable_notification(CARP_ID, f"@{v.username} has bought a `{award_title}` award!")


	return {"message": f"{award_title} award bought!"}

@app.post("/award/<thing_type>/<int:id>")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@is_not_permabanned
def award_thing(v, thing_type, id):
	kind = request.values.get("kind", "").strip()

	if thing_type == 'post':
		thing = get_post(id)
	else:
		thing = get_comment(id)
		if not thing.parent_submission and not thing.wall_user_id: abort(404) # don't let users award messages

	if v.shadowbanned: abort(500)
	author = thing.author
	if author.shadowbanned: abort(404)

	AWARDS = deepcopy(AWARDS_ENABLED)
	if v.house:
		AWARDS[v.house] = HOUSE_AWARDS[v.house]

	if kind not in AWARDS: abort(404, "This award doesn't exist")

	award = g.db.query(AwardRelationship).filter(
		AwardRelationship.kind == kind,
		AwardRelationship.user_id == v.id,
		AwardRelationship.submission_id == None,
		AwardRelationship.comment_id == None
	).first()

	if not award: abort(404, "You don't have that award")

	if thing_type == 'post': award.submission_id = thing.id
	else: award.comment_id = thing.id
	award.awarded_utc = int(time.time())

	g.db.add(award)

	note = request.values.get("note", "").strip()

	if thing.ghost and v.id != author.id:
		safe_username = "👻"
	else:
		safe_username = f"@{author.username}"

	if SITE == 'rdrama.net' and author.id in {PIZZASHILL_ID, CARP_ID}:
		abort(403, f"{safe_username} is immune to awards!")

	if kind == "benefactor" and author.id == v.id:
		abort(403, "You can't use this award on yourself!")

	if kind == 'marsify' and author.marsify == 1:
		abort(409, f"{safe_username} is already permanently marsified!")

	if kind == 'spider' and author.spider == 1:
		abort(409, f"{safe_username} already has a permanent spider friend!")

	if thing.ghost and not AWARDS[kind]['ghost']:
		abort(403, "This kind of award can't be used on ghost posts!")

	if v.id != author.id:
		if author.deflector and v.deflector and AWARDS[kind]['deflectable']:
			msg = f"@{v.username} has tried to give your [{thing_type}]({thing.shortlink}) the {AWARDS[kind]['title']} Award but it was deflected on them, they also had a deflector up, so it bounced back and forth until it vaporized!"
			send_repeatable_notification(author.id, msg)

			msg = f"{safe_username} is under the effect of a deflector award; your {AWARDS[kind]['title']} Award has been deflected back to you but your deflector protected you, the award bounced back and forth until it vaporized!"
			send_repeatable_notification(v.id, msg)

			g.db.delete(award)

			return {"message": f"{AWARDS[kind]['title']} award given to {thing_type} successfully!"}

		if author.deflector and AWARDS[kind]['deflectable']:
			msg = f"@{v.username} has tried to give your [{thing_type}]({thing.shortlink}) the {AWARDS[kind]['title']} Award but it was deflected and applied to them :marseytroll:"
			send_repeatable_notification(author.id, msg)
			msg = f"{safe_username} is under the effect of a deflector award; your {AWARDS[kind]['title']} Award has been deflected back to you :marseytroll:"
			send_repeatable_notification(v.id, msg)
			author = v
		elif kind != 'spider':
			awarded_coins = int(AWARDS[kind]['price'] * COSMETIC_AWARD_COIN_AWARD_PCT) if AWARDS[kind]['cosmetic'] and kind != 'shit' else 0
			if AWARDS[kind]['cosmetic'] and kind != 'shit':
				author.pay_account('coins', awarded_coins)

			msg = f"@{v.username} has given your [{thing_type}]({thing.shortlink}) the {AWARDS[kind]['title']} Award"
			if awarded_coins > 0:
				msg += f" and you have received {awarded_coins} coins as a result"
			msg += "!"
			if note: msg += f"\n\n> {note}"
			send_repeatable_notification(author.id, msg)

	link = f"[this {thing_type}]({thing.shortlink})"

	if kind == "ban":
		link = f"/{thing_type}/{thing.id}"
		link2 = link
		if thing_type == 'comment':
			link2 += '#context'
		ban_reason = f'1-Day ban award used by <a href="/@{v.username}">@{v.username}</a> on <a href="{link2}">{link}</a>'
		if not author.is_suspended:
			author.ban(reason=ban_reason, days=1)
			send_repeatable_notification(author.id, f"Your account has been banned for **a day** for {link}. It sucked and you should feel bad.")
		elif author.unban_utc:
			author.unban_utc += 86400
			author.ban_reason = ban_reason
			send_repeatable_notification(author.id, f"Your account has been banned for **yet another day** for {link}. Seriously man?")
	elif kind == "unban":
		if not author.is_suspended or not author.unban_utc or time.time() > author.unban_utc: abort(403)

		if author.unban_utc - time.time() > 86400:
			author.unban_utc -= 86400
			send_repeatable_notification(author.id, "Your ban duration has been reduced by 1 day!")
		else:
			author.unban_utc = 0
			author.is_banned = None
			author.ban_reason = None
			send_repeatable_notification(author.id, "You have been unbanned!")
	elif kind == "grass":
		author.is_banned = AUTOJANNY_ID
		author.ban_reason = f"grass award used by @{v.username} on /{thing_type}/{thing.id}"
		author.unban_utc = int(time.time()) + 30 * 86400
		send_repeatable_notification(author.id, f"Your account has been banned permanently for {link}. You must [provide the admins](/contact) a timestamped picture of you touching grass/snow/sand/ass to get unbanned!")
	elif kind == "pin":
		if not FEATURES['PINS']: abort(403)
		if thing.is_banned: abort(403)

		if thing_type == 'comment': add = 3600*6
		else: add = 3600

		if thing.stickied_utc:
			thing.stickied_utc += add
		else:
			thing.stickied_utc = int(time.time()) + add

		thing.stickied = f'{v.username}{PIN_AWARD_TEXT}'
		g.db.add(thing)
		cache.delete_memoized(frontlist)
	elif kind == "unpin":
		if not thing.stickied_utc: abort(400)
		if thing.author_id == LAWLZ_ID and SITE_NAME == 'rDrama': abort(403, "You can't unpin lawlzposts!")

		if thing_type == 'comment':
			t = thing.stickied_utc - 3600*6
		else:
			t = thing.stickied_utc - 3600

		if time.time() > t:
			thing.stickied = None
			thing.stickied_utc = None
			cache.delete_memoized(frontlist)
		else: thing.stickied_utc = t
		g.db.add(thing)
	elif kind == "agendaposter":
		if thing_type == 'post' and thing.sub == 'chudrama' \
			or thing_type == 'comment' and thing.post and thing.post.sub == 'chudrama':
			abort(403, "You can't give the chud award in /h/chudrama")

		if author.marseyawarded:
			abort(409, f"{safe_username} is under the effect of a conflicting award: Marsey award!")

		if author.agendaposter == 1:
			abort(409, f"{safe_username} is perma-chudded!")

		if author.agendaposter and time.time() < author.agendaposter: author.agendaposter += 86400
		else: author.agendaposter = int(time.time()) + 86400

		badge_grant(user=author, badge_id=28)
	elif kind == "flairlock":
		new_name = note[:100].replace("𒐪","").replace("﷽","").strip()
		if not new_name and author.flairchanged:
			author.flairchanged += 86400
		else:
			author.customtitleplain = new_name
			new_name = filter_emojis_only(new_name)
			new_name = censor_slurs(new_name, None)
			if len(new_name) > 1000: abort(403)
			author.customtitle = new_name
			author.flairchanged = int(time.time()) + 86400
			badge_grant(user=author, badge_id=96)
	elif kind == "pause":
		badge_grant(badge_id=68, user=author)
	elif kind == "unpausable":
		badge_grant(badge_id=67, user=author)
	elif kind == "marsey":
		if author.marseyawarded: author.marseyawarded += 86400
		else: author.marseyawarded = int(time.time()) + 86400
		badge_grant(user=author, badge_id=98)
	elif kind == "pizzashill":
		if author.bird:
			abort(409, f"{safe_username} is under the effect of a conflicting award: Bird Site award!")
		if author.longpost: author.longpost += 86400
		else: author.longpost = int(time.time()) + 86400
		badge_grant(user=author, badge_id=97)
	elif kind == "bird":
		if author.longpost:
			abort(409, f"{safe_username} is under the effect of a conflicting award: Pizzashill award!")
		if author.bird: author.bird += 86400
		else: author.bird = int(time.time()) + 86400
		badge_grant(user=author, badge_id=95)
	elif kind == "eye":
		badge_grant(badge_id=83, user=author)
	elif kind == "offsitementions":
		badge_grant(user=author, badge_id=140)
	elif kind == "alt":
		badge_grant(badge_id=84, user=author)
	elif kind == "unblockable":
		badge_grant(badge_id=87, user=author)
		for block in g.db.query(UserBlock).filter_by(target_id=author.id).all(): g.db.delete(block)
	elif kind == "fish":
		badge_grant(badge_id=90, user=author)
	elif kind == "progressivestack":
		if not FEATURES['PINS']:
			abort(403)

		if author.progressivestack != 1:
			if author.progressivestack: author.progressivestack += 21600
			else: author.progressivestack = int(time.time()) + 21600
			badge_grant(user=author, badge_id=94)
	elif kind == "benefactor":
		if author.patron and not author.patron_utc:
			abort(409, f"{safe_username} is already a {patron.lower()}!")
		author.patron = 1
		if author.patron_utc: author.patron_utc += 2629746
		else: author.patron_utc = int(time.time()) + 2629746
		author.pay_account('marseybux', 2500)
		badge_grant(user=v, badge_id=103)
	elif kind == "rehab":
		if author.rehab: author.rehab += 86400
		else: author.rehab = int(time.time()) + 86400
		badge_grant(user=author, badge_id=109)
	elif kind == "deflector":
		author.deflector = int(time.time()) + 36000
	elif kind == "beano":
		badge_grant(user=author, badge_id=128)
	elif kind == "checkmark":
		author.verified = "Verified"
		badge_grant(user=author, badge_id=150)
	elif kind == 'marsify':
		if not author.marsify or author.marsify != 1:
			if author.marsify: author.marsify += 86400
			else: author.marsify = int(time.time()) + 86400
		badge_grant(user=author, badge_id=170)

		if thing_type == 'comment' and not thing.author.deflector:
			body = thing.body
			if author.owoify: body = owoify(body)
			body = marsify(body)
			thing.body_html = sanitize(body, limit_pings=5)
			g.db.add(thing)
	elif "Vampire" in kind and kind == v.house:
		if author.bite: author.bite += 172800
		else: author.bite = int(time.time()) + 172800

		if not author.old_house:
			author.old_house = author.house

		if 'Vampire' not in author.house:
			author.house = 'Vampire'

		badge_grant(user=author, badge_id=168)
	elif "Racist" in kind and kind == v.house:
		if author.earlylife: author.earlylife += 86400
		else: author.earlylife = int(time.time()) + 86400
		badge_grant(user=author, badge_id=169)
	elif ("Furry" in kind and kind == v.house) or kind == 'owoify':
		if author.owoify: author.owoify += 21600
		else: author.owoify = int(time.time()) + 21600
		badge_grant(user=author, badge_id=167)

		if thing_type == 'comment' and not thing.author.deflector:
			body = thing.body
			body = owoify(body)
			if author.marsify: body = marsify(body)
			thing.body_html = sanitize(body, limit_pings=5)
			g.db.add(thing)
	elif ("Femboy" in kind and kind == v.house) or kind == 'rainbow':
		if author.rainbow: author.rainbow += 86400
		else: author.rainbow = int(time.time()) + 86400
		badge_grant(user=author, badge_id=171)
	elif kind == "spider":
		if author.spider: author.spider += 86400
		else: author.spider = int(time.time()) + 86400
		badge_grant(user=author, badge_id=179, notify=False)
	if kind == "grinch":
		badge_grant(badge_id=91, user=author)
		author.event_music = False


	if author.received_award_count: author.received_award_count += 1
	else: author.received_award_count = 1
	g.db.add(author)

	return {"message": f"{AWARDS[kind]['title']} award given to {thing_type} successfully!"}
