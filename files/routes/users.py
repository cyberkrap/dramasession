import io
import json
import math
import time
from collections import Counter
from typing import Literal

import gevent
import qrcode
from sqlalchemy.orm import aliased

from files.classes import *
from files.classes.leaderboard import Leaderboard
from files.classes.transactions import *
from files.classes.views import *
from files.helpers.actions import execute_blackjack, execute_under_siege
from files.helpers.alerts import *
from files.helpers.config.const import *
from files.helpers.mail import *
from files.helpers.sanitize import *
from files.helpers.sorting_and_time import *
from files.helpers.useractions import badge_grant
from files.routes.routehelpers import check_for_alts, add_alt
from files.routes.wrappers import *

from files.__main__ import app, cache, limiter


def upvoters_downvoters(v, username, uid, cls, vote_cls, vote_dir, template, standalone):
	u = get_user(username, v=v, include_shadowbanned=False)
	if not u.is_visible_to(v): abort(403)
	if not (v.id == u.id or v.admin_level >= PERMS['USER_VOTERS_VISIBLE']): abort(403)
	id = u.id
	try:
		uid = int(uid)
	except:
		abort(404)

	try: page = max(1, int(request.values.get("page", 1)))
	except: abort(400, "Invalid page input!")

	listing = g.db.query(cls).join(vote_cls).filter(cls.ghost == False, cls.is_banned == False, cls.deleted_utc == 0, vote_cls.vote_type==vote_dir, cls.author_id==id, vote_cls.user_id==uid).order_by(cls.created_utc.desc()).offset(PAGE_SIZE * (page - 1)).limit(PAGE_SIZE + 1).all()

	listing = [p.id for p in listing]
	next_exists = len(listing) > PAGE_SIZE
	listing = listing[:PAGE_SIZE]

	if cls == Submission:
		listing = get_posts(listing, v=v, eager=True)
	elif cls == Comment:
		listing = get_comments(listing, v=v)
	else:
		listing = []

	return render_template(template, next_exists=next_exists, listing=listing, page=page, v=v, standalone=standalone)

@app.get("/@<username>/upvoters/<int:uid>/posts")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def upvoters_posts(v:User, username, uid):
	return upvoters_downvoters(v, username, uid, Submission, Vote, 1, "userpage/voted_posts.html", None)


@app.get("/@<username>/upvoters/<int:uid>/comments")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def upvoters_comments(v:User, username, uid):
	return upvoters_downvoters(v, username, uid, Comment, CommentVote, 1, "userpage/voted_comments.html", True)


@app.get("/@<username>/downvoters/<int:uid>/posts")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def downvoters_posts(v:User, username, uid):
	return upvoters_downvoters(v, username, uid, Submission, Vote, -1, "userpage/voted_posts.html", None)


@app.get("/@<username>/downvoters/<int:uid>/comments")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def downvoters_comments(v:User, username, uid):
	return upvoters_downvoters(v, username, uid, Comment, CommentVote, -1, "userpage/voted_comments.html", True)

def upvoting_downvoting(v, username, uid, cls, vote_cls, vote_dir, template, standalone):
	u = get_user(username, v=v, include_shadowbanned=False)
	if not u.is_visible_to(v): abort(403)
	if not (v.id == u.id or v.admin_level >= PERMS['USER_VOTERS_VISIBLE']): abort(403)
	id = u.id
	try:
		uid = int(uid)
	except:
		abort(404)

	try: page = max(1, int(request.values.get("page", 1)))
	except: abort(400, "Invalid page input!")

	listing = g.db.query(cls).join(vote_cls).filter(cls.ghost == False, cls.is_banned == False, cls.deleted_utc == 0, vote_cls.vote_type==vote_dir, vote_cls.user_id==id, cls.author_id==uid).order_by(cls.created_utc.desc()).offset(PAGE_SIZE * (page - 1)).limit(PAGE_SIZE + 1).all()

	listing = [p.id for p in listing]
	next_exists = len(listing) > PAGE_SIZE
	listing = listing[:PAGE_SIZE]

	if cls == Submission:
		listing = get_posts(listing, v=v, eager=True)
	elif cls == Comment:
		listing = get_comments(listing, v=v)
	else:
		listing = []

	return render_template(template, next_exists=next_exists, listing=listing, page=page, v=v, standalone=standalone)

@app.get("/@<username>/upvoting/<int:uid>/posts")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def upvoting_posts(v:User, username, uid):
	return upvoting_downvoting(v, username, uid, Submission, Vote, 1, "userpage/voted_posts.html", None)


@app.get("/@<username>/upvoting/<int:uid>/comments")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def upvoting_comments(v:User, username, uid):
	return upvoting_downvoting(v, username, uid, Comment, CommentVote, 1, "userpage/voted_comments.html", True)


@app.get("/@<username>/downvoting/<int:uid>/posts")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def downvoting_posts(v:User, username, uid):
	return upvoting_downvoting(v, username, uid, Submission, Vote, -1, "userpage/voted_posts.html", None)


@app.get("/@<username>/downvoting/<int:uid>/comments")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def downvoting_comments(v:User, username, uid):
	return upvoting_downvoting(v, username, uid, Comment, CommentVote, -1, "userpage/voted_comments.html", True)

def user_voted(v, username, cls, vote_cls, template, standalone):
	u = get_user(username, v=v, include_shadowbanned=False)
	if not u.is_visible_to(v): abort(403)
	if not (v.id == u.id or v.admin_level >= PERMS['USER_VOTERS_VISIBLE']): abort(403)

	try: page = max(1, int(request.values.get("page", 1)))
	except: abort(400, "Invalid page input!")

	listing = g.db.query(cls).join(vote_cls).filter(
			cls.ghost == False,
			cls.is_banned == False,
			cls.deleted_utc == 0,
			cls.author_id != u.id,
			vote_cls.user_id == u.id,
		).order_by(cls.created_utc.desc()).offset(PAGE_SIZE * (page - 1)).limit(PAGE_SIZE + 1).all()

	listing = [i.id for i in listing]
	next_exists = len(listing) > PAGE_SIZE
	listing = listing[:PAGE_SIZE]
	if cls == Submission:
		listing = get_posts(listing, v=v, eager=True)
	elif cls == Comment:
		listing = get_comments(listing, v=v)
	else:
		listing = []

	return render_template(template, next_exists=next_exists, listing=listing, page=page, v=v, standalone=standalone)

@app.get("/@<username>/voted/posts")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def user_voted_posts(v:User, username):
	return user_voted(v, username, Submission, Vote, "userpage/voted_posts.html", None)


@app.get("/@<username>/voted/comments")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def user_voted_comments(v:User, username):
	abort(403, "Temporarily disabled!")
	return user_voted(v, username, Comment, CommentVote, "userpage/voted_comments.html", True)

@app.get("/banned")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def banned(v:User):
	users = g.db.query(User).filter(
		User.is_banned != None,
		or_(User.unban_utc == 0, User.unban_utc > time.time()),
	).order_by(User.ban_reason)
	if not v.can_see_shadowbanned:
		users = users.filter(User.shadowbanned == None)
	users = users.all()
	return render_template("banned.html", v=v, users=users)

@app.get("/grassed")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def grassed(v:User):
	users = g.db.query(User).filter(
		User.ban_reason.like('grass award used by @%'),
		User.unban_utc > time.time(),
	)
	if not v.can_see_shadowbanned:
		users = users.filter(User.shadowbanned == None)
	users = users.all()
	return render_template("grassed.html", v=v, users=users)

@app.get("/chuds")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def chuds(v:User):
	users = g.db.query(User).filter(
		or_(User.agendaposter == 1, User.agendaposter > time.time()),
	)
	if v.admin_level >= PERMS['VIEW_LAST_ACTIVE']:
		users = users.order_by(User.truescore.desc())
	if not v.can_see_shadowbanned:
		users = users.filter(User.shadowbanned == None)
	users = users.order_by(User.username).all()
	return render_template("chuds.html", v=v, users=users)

def all_upvoters_downvoters(v:User, username:str, vote_dir:int, is_who_simps_hates:bool):
	if username == 'Snappy':
		abort(403, "For performance reasons, you can't see Snappy statistics!")
	vote_str = 'votes'
	simps_haters = 'voters'
	vote_name = 'Neutral'
	if vote_dir == 1:
		vote_str = 'upvotes'
		simps_haters = 'simps for' if is_who_simps_hates else 'simps'
		vote_name = 'Up'
	elif vote_dir == -1:
		vote_str = 'downvotes'
		simps_haters = 'hates' if is_who_simps_hates else 'haters'
		vote_name = 'Down'

	id = get_user(username, v=v, include_shadowbanned=False).id
	if not (v.id == id or v.admin_level >= PERMS['USER_VOTERS_VISIBLE']):
		abort(403)
	votes = []
	votes2 = []
	if is_who_simps_hates:
		votes = g.db.query(Submission.author_id, func.count(Submission.author_id)).join(Vote).filter(Submission.ghost == False, Submission.is_banned == False, Submission.deleted_utc == 0, Vote.vote_type==vote_dir, Vote.user_id==id).group_by(Submission.author_id).order_by(func.count(Submission.author_id).desc()).all()
		# votes2 = g.db.query(Comment.author_id, func.count(Comment.author_id)).join(CommentVote).filter(Comment.ghost == False, Comment.is_banned == False, Comment.deleted_utc == 0, CommentVote.vote_type==vote_dir, CommentVote.user_id==id).group_by(Comment.author_id).order_by(func.count(Comment.author_id).desc()).all()
	else:
		votes = g.db.query(Vote.user_id, func.count(Vote.user_id)).join(Submission).filter(Submission.ghost == False, Submission.is_banned == False, Submission.deleted_utc == 0, Vote.vote_type==vote_dir, Submission.author_id==id).group_by(Vote.user_id).order_by(func.count(Vote.user_id).desc()).all()
		# votes2 = g.db.query(CommentVote.user_id, func.count(CommentVote.user_id)).join(Comment).filter(Comment.ghost == False, Comment.is_banned == False, Comment.deleted_utc == 0, CommentVote.vote_type==vote_dir, Comment.author_id==id).group_by(CommentVote.user_id).order_by(func.count(CommentVote.user_id).desc()).all()
	# votes = Counter(dict(votes)) + Counter(dict(votes2))
	votes = Counter(dict(votes))
	total = sum(votes.values())
	users = g.db.query(User).filter(User.id.in_(votes.keys()))
	if not v.can_see_shadowbanned:
		users = users.filter(User.shadowbanned == None)

	users2 = [(user, votes[user.id]) for user in users.all()]
	users = sorted(users2, key=lambda x: x[1], reverse=True)

	try:
		pos = [x[0].id for x in users].index(v.id)
		pos = (pos+1, users[pos][1])
	except: pos = (len(users)+1, 0)

	received_given = 'given' if is_who_simps_hates else 'received'
	if total == 1: vote_str = vote_str[:-1] # we want to unpluralize if only 1 vote
	total = f'{total} {vote_str} {received_given}'

	name2 = f'Who @{username} {simps_haters}' if is_who_simps_hates else f"@{username}'s {simps_haters}"

	try: page = int(request.values.get("page", 1))
	except: page = 1

	users = users[PAGE_SIZE * (page-1):]
	next_exists = (len(users) > PAGE_SIZE)
	users = users[:PAGE_SIZE]

	return render_template("userpage/voters.html", v=v, users=users, pos=pos, name=vote_name, name2=name2, total=total, page=page, next_exists=next_exists)

@app.get("/@<username>/upvoters")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def upvoters(v:User, username:str):
	return all_upvoters_downvoters(v, username, 1, False)

@app.get("/@<username>/downvoters")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def downvoters(v:User, username:str):
	return all_upvoters_downvoters(v, username, -1, False)

@app.get("/@<username>/upvoting")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def upvoting(v:User, username:str):
	return all_upvoters_downvoters(v, username, 1, True)

@app.get("/@<username>/downvoting")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def downvoting(v:User, username:str):
	return all_upvoters_downvoters(v, username, -1, True)

@app.post("/@<username>/suicide")
@feature_required('USERS_SUICIDE')
@limiter.limit("1/second;5/day")
@limiter.limit("1/second;5/day", key_func=get_ID)
@auth_required
def suicide(v:User, username:str):
	user = get_user(username)
	suicide = f"Hi there,\n\nA [concerned user](/id/{v.id}) reached out to us about you.\n\nWhen you're in the middle of something painful, it may feel like you don't have a lot of options. But whatever you're going through, you deserve help and there are people who are here for you.\n\nThere are resources available in your area that are free, confidential, and available 24/7:\n\n- Call, Text, or Chat with Canada's [Crisis Services Canada](https://www.crisisservicescanada.ca/en/)\n- Call, Email, or Visit the UK's [Samaritans](https://www.samaritans.org/)\n- Text CHAT to America's [Crisis Text Line](https://www.crisistextline.org/) at 741741.\nIf you don't see a resource in your area above, the moderators keep a comprehensive list of resources and hotlines for people organized by location. Find Someone Now\n\nIf you think you may be depressed or struggling in another way, don't ignore it or brush it aside. Take yourself and your feelings seriously, and reach out to someone.\n\nIt may not feel like it, but you have options. There are people available to listen to you, and ways to move forward.\n\nYour fellow users care about you and there are people who want to help."
	if not v.shadowbanned:
		send_notification(user.id, suicide)
	return {"message": f"Help message sent to @{user.username}"}


@app.get("/@<username>/coins")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def get_coins(v:User, username:str):
	user = get_user(username, v=v, include_shadowbanned=False)
	return {"coins": user.coins}

def transfer_currency(v:User, username:str, currency_name:Literal['coins', 'marseybux'], apply_tax:bool):
	MIN_CURRENCY_TRANSFER = 100
	TAX_PCT = 0.03
	receiver = get_user(username, v=v, include_shadowbanned=False)
	if receiver.id == v.id: abort(400, f"You can't transfer {currency_name} to yourself!")
	amount = request.values.get("amount", "").strip()
	amount = int(amount) if amount.isdigit() else None

	if amount is None or amount <= 0: abort(400, f"Invalid number of {currency_name}")
	if amount < MIN_CURRENCY_TRANSFER: abort(400, f"You have to gift at least {MIN_CURRENCY_TRANSFER} {currency_name}")
	tax = 0
	if apply_tax and not v.patron and not receiver.patron:
		tax = math.ceil(amount*TAX_PCT)

	reason = request.values.get("reason", "").strip()
	log_message = f"@{v.username} has transferred {amount} {currency_name} to @{receiver.username}"
	notif_text = f":marseycapitalistmanlet: @{v.username} has gifted you {amount-tax} {currency_name}!"

	if reason:
		if len(reason) > TRANSFER_MESSAGE_LENGTH_LIMIT:
			abort(400, f"Reason is too long, max {TRANSFER_MESSAGE_LENGTH_LIMIT} characters")
		notif_text += f"\n\n> {reason}"
		log_message += f"\n\n> {reason}"

	if not v.charge_account(currency_name, amount):
		abort(400, f"You don't have enough {currency_name}")

	if not v.shadowbanned:
		if currency_name == 'marseybux':
			receiver.pay_account('marseybux', amount - tax)
		elif currency_name == 'coins':
			receiver.pay_account('coins', amount - tax)
		else:
			raise ValueError(f"Invalid currency '{currency_name}' got when transferring {amount} from {v.id} to {receiver.id}")
		g.db.add(receiver)
		if GIFT_NOTIF_ID: send_repeatable_notification(GIFT_NOTIF_ID, log_message)
		send_repeatable_notification(receiver.id, notif_text)
	g.db.add(v)
	return {"message": f"{amount - tax} {currency_name} have been transferred to @{receiver.username}"}

@app.post("/@<username>/transfer_coins")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@is_not_permabanned
def transfer_coins(v:User, username:str):
	return transfer_currency(v, username, 'coins', True)

@app.post("/@<username>/transfer_bux")
@feature_required('MARSEYBUX')
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@is_not_permabanned
def transfer_bux(v:User, username:str):
	return transfer_currency(v, username, 'marseybux', False)

@app.get("/leaderboard")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def leaderboard(v:User):
	users = g.db.query(User)
	if not v.can_see_shadowbanned:
		users = users.filter(User.shadowbanned == None)

	coins = Leaderboard("Coins", "coins", "coins", "Coins", None, Leaderboard.get_simple_lb, User.coins, v, lambda u:u.coins, g.db, users)
	subscribers = Leaderboard("Followers", "followers", "followers", "Followers", "followers", Leaderboard.get_simple_lb, User.stored_subscriber_count, v, lambda u:u.stored_subscriber_count, g.db, users)
	posts = Leaderboard("Posts", "post count", "posts", "Posts", "", Leaderboard.get_simple_lb, User.post_count, v, lambda u:u.post_count, g.db, users)
	comments = Leaderboard("Comments", "comment count", "comments", "Comments", "comments", Leaderboard.get_simple_lb, User.comment_count, v, lambda u:u.comment_count, g.db, users)
	received_awards = Leaderboard("Awards", "received awards", "awards", "Awards", None, Leaderboard.get_simple_lb, User.received_award_count, v, lambda u:u.received_award_count, g.db, users)
	coins_spent = Leaderboard("Spent in shop", "coins spent in shop", "spent", "Coins", None, Leaderboard.get_simple_lb, User.coins_spent, v, lambda u:u.coins_spent, g.db, users)
	truescore = Leaderboard("Truescore", "truescore", "truescore", "Truescore", None, Leaderboard.get_simple_lb, User.truescore, v, lambda u:u.truescore, g.db, users)

	badges = Leaderboard("Badges", "badges", "badges", "Badges", None, Leaderboard.get_badge_marsey_lb, Badge.user_id, v, None, g.db, None)

	blocks = Leaderboard("Blocked", "most blocked", "blocked", "Blocked By", "blockers", Leaderboard.get_blockers_lb, UserBlock.target_id, v, None, g.db, None)

	owned_hats = Leaderboard("Owned hats", "owned hats", "owned-hats", "Owned Hats", None, Leaderboard.get_hat_lb, User.owned_hats, v, None, g.db, None)

	leaderboards = [coins, coins_spent, truescore, subscribers, posts, comments, received_awards, badges, blocks, owned_hats]

	if SITE == 'rdrama.net':
		leaderboards.append(Leaderboard("Designed hats", "designed hats", "designed-hats", "Designed Hats", None, Leaderboard.get_hat_lb, User.designed_hats, v, None, g.db, None))
		leaderboards.append(Leaderboard("Marseys", "Marseys made", "marseys", "Marseys", None, Leaderboard.get_badge_marsey_lb, Marsey.author_id, v, None, g.db, None))

	return render_template("leaderboard.html", v=v, leaderboards=leaderboards)

@app.get("/<int:id>/css")
def get_css(id):
	try: id = int(id)
	except: abort(404)

	css, bg = g.db.query(User.css, User.background).filter_by(id=id).one_or_none()

	if bg:
		if not css: css = ''
		css += f'''
			body {{
				background: url("{bg}") center center fixed;
			}}
		'''
		if 'anime/' not in bg and not bg.startswith('/images/'):
			css += 'body {background-size: cover}'

	if not css: abort(404)

	resp = make_response(css)
	resp.headers["Content-Type"] = "text/css"
	return resp

@app.get("/<int:id>/profilecss")
def get_profilecss(id):
	try: id = int(id)
	except: abort(404)

	css, bg = g.db.query(User.profilecss, User.profile_background).filter_by(id=id).one_or_none()

	if bg:
		if not css: css = ''
		css += f'''
			body {{
				background: url("{bg}") center center fixed;
				background-size: auto;
			}}
		'''
	if not css: abort(404)

	resp = make_response(css)
	resp.headers["Content-Type"] = "text/css"
	return resp

@app.get("/@<username>/song")
def usersong(username:str):
	user = get_user(username)
	if user.song: return redirect(f"/songs/{user.song}.mp3")
	else: abort(404)

@app.post("/subscribe/<int:post_id>")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@auth_required
def subscribe(v, post_id):
	existing = g.db.query(Subscription).filter_by(user_id=v.id, submission_id=post_id).one_or_none()
	if not existing:
		new_sub = Subscription(user_id=v.id, submission_id=post_id)
		g.db.add(new_sub)
	return {"message": "Subscribed to post successfully!"}

@app.post("/unsubscribe/<int:post_id>")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@auth_required
def unsubscribe(v, post_id):
	existing = g.db.query(Subscription).filter_by(user_id=v.id, submission_id=post_id).one_or_none()
	if existing:
		g.db.delete(existing)
	return {"message": "Unsubscribed from post successfully!"}

@app.post("/@<username>/message")
@limiter.limit("1/second;10/minute;20/hour;50/day")
@limiter.limit("1/second;10/minute;20/hour;50/day", key_func=get_ID)
@is_not_permabanned
def message2(v:User, username:str):
	user = get_user(username, v=v, include_blocks=True, include_shadowbanned=False)

	if user.id == MODMAIL_ID:
		abort(403, "Please use /contact to contact the admins")

	if hasattr(user, 'is_blocking') and user.is_blocking:
		abort(403, f"You're blocking @{user.username}")

	if v.admin_level <= PERMS['MESSAGE_BLOCKED_USERS'] and hasattr(user, 'is_blocked') and user.is_blocked:
		abort(403, f"@{user.username} is blocking you!")

	message = sanitize_raw_body(request.values.get("message"), False)

	message += process_dm_images(v, user)

	if not message: abort(400, "Message is empty!")

	body_html = sanitize(message)

	existing = g.db.query(Comment.id).filter(
		Comment.author_id == v.id,
		Comment.sentto == user.id,
		Comment.body_html == body_html
	).first()

	if existing: abort(403, "Message already exists!")

	c = Comment(author_id=v.id,
						parent_submission=None,
						level=1,
						sentto=user.id,
						body_html=body_html
						)
	g.db.add(c)
	g.db.flush()
	execute_blackjack(v, c, c.body_html, 'message')
	execute_under_siege(v, c, c.body_html, 'message')
	c.top_comment_id = c.id

	if user.id not in bots:
		notif = g.db.query(Notification).filter_by(comment_id=c.id, user_id=user.id).one_or_none()
		if not notif:
			notif = Notification(comment_id=c.id, user_id=user.id)
			g.db.add(notif)


	if VAPID_PUBLIC_KEY != DEFAULT_CONFIG_VALUE and not v.shadowbanned:
		title = f'New message from @{v.username}'

		if len(message) > 500: notifbody = message[:500] + '...'
		else: notifbody = message

		url = f'{SITE_FULL}/notifications/messages'

		push_notif({user.id}, title, notifbody, url)

	return {"message": "Message sent!"}


@app.post("/reply")
@limiter.limit("1/second;6/minute;50/hour;200/day")
@limiter.limit("1/second;6/minute;50/hour;200/day", key_func=get_ID)
@auth_required
def messagereply(v:User):
	body = sanitize_raw_body(request.values.get("body"), False)

	id = request.values.get("parent_id")
	parent = get_comment(id, v=v)
	user_id = parent.author.id

	if v.is_suspended_permanently and parent.sentto != MODMAIL_ID:
		abort(403, "You are permabanned and may not reply to messages!")
	elif v.is_muted and parent.sentto == MODMAIL_ID:
		abort(403, "You are forbidden from replying to modmail!")

	if parent.sentto == MODMAIL_ID: user_id = None
	elif v.id == user_id: user_id = parent.sentto

	user = None

	if user_id:
		user = get_account(user_id, v=v, include_blocks=True)
		if hasattr(user, 'is_blocking') and user.is_blocking:
			abort(403, f"You're blocking @{user.username}")
		elif (v.admin_level <= PERMS['MESSAGE_BLOCKED_USERS']
				and hasattr(user, 'is_blocked') and user.is_blocked):
			abort(403, f"You're blocked by @{user.username}")

	body += process_dm_images(v, user)

	body = body.strip()

	if not body: abort(400, "Message is empty!")

	body_html = sanitize(body)

	c = Comment(author_id=v.id,
							parent_submission=None,
							parent_comment_id=id,
							top_comment_id=parent.top_comment_id,
							level=parent.level + 1,
							sentto=user_id,
							body_html=body_html,
							)
	g.db.add(c)
	g.db.flush()
	execute_blackjack(v, c, c.body_html, 'message')
	execute_under_siege(v, c, c.body_html, 'message')

	if user_id and user_id not in {v.id, MODMAIL_ID} | bots:
		notif = g.db.query(Notification).filter_by(comment_id=c.id, user_id=user_id).one_or_none()
		if not notif:
			notif = Notification(comment_id=c.id, user_id=user_id)
			g.db.add(notif)

		if VAPID_PUBLIC_KEY != DEFAULT_CONFIG_VALUE and not v.shadowbanned:
			title = f'New message from @{v.username}'

			if len(body) > 500: notifbody = body[:500] + '...'
			else: notifbody = body

			url = f'{SITE_FULL}/notifications/messages'

			push_notif({user_id}, title, notifbody, url)

	top_comment = c.top_comment(g.db)

	if top_comment.sentto == MODMAIL_ID:
		admins = g.db.query(User.id).filter(User.admin_level >= PERMS['NOTIFICATIONS_MODMAIL'], User.id != v.id, User.id != AEVANN_ID)

		admins = [x[0] for x in admins.all()]

		if parent.author.id not in admins + [v.id]:
			admins.append(parent.author.id)

		for admin in admins:
			notif = Notification(comment_id=c.id, user_id=admin)
			g.db.add(notif)

		ids = [top_comment.id] + [x.id for x in top_comment.replies(sort="old", v=v, db=g.db)]
		notifications = g.db.query(Notification).filter(Notification.comment_id.in_(ids), Notification.user_id.in_(admins))
		for n in notifications:
			g.db.delete(n)


	return {"comment": render_template("comments.html", v=v, comments=[c])}

@app.get("/2faqr/<secret>")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def mfa_qr(v:User, secret:str):
	x = pyotp.TOTP(secret)
	qr = qrcode.QRCode(
		error_correction=qrcode.constants.ERROR_CORRECT_L
	)
	qr.add_data(x.provisioning_uri(v.username, issuer_name=SITE))
	img = qr.make_image(fill_color="#000000", back_color="white")

	mem = io.BytesIO()

	img.save(mem, format="PNG")
	mem.seek(0, 0)

	return send_file(mem, mimetype="image/png", as_attachment=False)


@app.get("/is_available/<name>")
@limiter.limit("100/day")
@limiter.limit("100/day", key_func=get_ID)
def is_available(name:str):

	name=name.strip()

	if len(name)<3 or len(name)>25:
		return {name:False}

	name2 = name.replace('\\', '').replace('_','\_').replace('%','')

	x = g.db.query(User).filter(
		or_(
			User.username.ilike(name2),
			User.original_username.ilike(name2)
			)
		).one_or_none()

	if x:
		return {name: False}
	else:
		return {name: True}

@app.get("/id/<int:id>")
def user_id(id):
	user = get_account(id)
	return redirect(user.url)

@app.get("/u/<username>")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def redditor_moment_redirect(v:User, username:str):
	return redirect(f"/@{username}")

@app.get("/@<username>/followers")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def followers(v:User, username:str):
	u = get_user(username, v=v, include_shadowbanned=False)

	if not (v.id == u.id or v.admin_level >= PERMS['USER_FOLLOWS_VISIBLE']):
		abort(403)

	try: page = int(request.values.get("page", 1))
	except: page = 1

	users = g.db.query(Follow, User).join(Follow, Follow.target_id == u.id) \
		.filter(Follow.user_id == User.id) \
		.order_by(Follow.created_utc.desc()) \
		.offset(PAGE_SIZE * (page - 1)).limit(PAGE_SIZE + 1).all()

	next_exists = (len(users) > PAGE_SIZE)
	users = users[:PAGE_SIZE]

	return render_template("userpage/followers.html", v=v, u=u, users=users, page=page, next_exists=next_exists)

@app.get("/@<username>/blockers")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def blockers(v:User, username:str):
	u = get_user(username, v=v, include_shadowbanned=False)

	try: page = int(request.values.get("page", 1))
	except: page = 1

	users = g.db.query(UserBlock, User).join(UserBlock, UserBlock.target_id == u.id) \
		.filter(UserBlock.user_id == User.id) \
		.order_by(UserBlock.created_utc.desc()) \
		.offset(PAGE_SIZE * (page - 1)).limit(PAGE_SIZE + 1).all()

	next_exists = (len(users) > PAGE_SIZE)
	users = users[:PAGE_SIZE]

	return render_template("userpage/blockers.html", v=v, u=u, users=users, page=page, next_exists=next_exists)

@app.get("/@<username>/following")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def following(v:User, username:str):
	u = get_user(username, v=v, include_shadowbanned=False)
	if not (v.id == u.id or v.admin_level >= PERMS['USER_FOLLOWS_VISIBLE']):
		abort(403)

	try: page = int(request.values.get("page", 1))
	except: page = 1

	users = g.db.query(User).join(Follow, Follow.user_id == u.id) \
		.filter(Follow.target_id == User.id) \
		.order_by(Follow.created_utc.desc()) \
		.offset(PAGE_SIZE * (page - 1)).limit(PAGE_SIZE + 1).all()

	next_exists = (len(users) > PAGE_SIZE)
	users = users[:PAGE_SIZE]

	return render_template("userpage/following.html", v=v, u=u, users=users, page=page, next_exists=next_exists)

@app.get("/@<username>/views")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def visitors(v:User, username:str):
	u = get_user(username, v=v, include_shadowbanned=False)

	try: page = int(request.values.get("page", 1))
	except: page = 1

	views = g.db.query(ViewerRelationship).filter_by(user_id=u.id).order_by(ViewerRelationship.last_view_utc.desc()).offset(PAGE_SIZE * (page - 1)).limit(PAGE_SIZE + 1).all()

	next_exists = (len(views) > PAGE_SIZE)
	views = views[:PAGE_SIZE]

	return render_template("userpage/views.html", v=v, u=u, views=views, next_exists=next_exists, page=page)

@cache.memoize()
def userpagelisting(user:User, site=None, v=None, page:int=1, sort="new", t="all"):
	if user.shadowbanned and not (v and v.can_see_shadowbanned): return []
	posts = g.db.query(Submission.id).filter_by(author_id=user.id, is_pinned=False)
	if not (v and (v.admin_level >= PERMS['POST_COMMENT_MODERATION'] or v.id == user.id)):
		posts = posts.filter_by(is_banned=False, private=False, ghost=False, deleted_utc=0)
	posts = apply_time_filter(t, posts, Submission)
	posts = sort_objects(sort, posts, Submission, include_shadowbanned=v and v.can_see_shadowbanned)
	posts = posts.offset(PAGE_SIZE * (page - 1)).limit(PAGE_SIZE+1).all()
	return [x[0] for x in posts]

@app.get("/@<username>")
@app.get("/@<username>.json")
@auth_desired_with_logingate
def u_username_wall(v:Optional[User], username:str):
	u = get_user(username, v=v, include_blocks=True, include_shadowbanned=False)
	if username != u.username:
		return redirect(f"/@{u.username}")

	if v and hasattr(u, 'is_blocking') and u.is_blocking:
		if g.is_api_or_xhr or request.path.endswith(".json"):
			abort(403, f"You are blocking @{u.username}.")
		return render_template("userpage/blocking.html", u=u, v=v), 403

	is_following = v and u.has_follower(v)

	if v and v.id != u.id and not v.admin_level:
		g.db.flush()
		view = g.db.query(ViewerRelationship).filter_by(viewer_id=v.id, user_id=u.id).one_or_none()
		if view: view.last_view_utc = int(time.time())
		else: view = ViewerRelationship(viewer_id=v.id, user_id=u.id)
		g.db.add(view)
		g.db.commit()

	try: page = max(int(request.values.get("page", "1")), 1)
	except: page = 1

	if v:
		comments, output = get_comments_v_properties(v, True, None, Comment.wall_user_id == u.id)
	else:
		comments = g.db.query(Comment).filter(Comment.wall_user_id == u.id)
	comments = comments.filter(Comment.level == 1)

	if not v or (v.id != u.id and v.admin_level < PERMS['POST_COMMENT_MODERATION']):
		comments = comments.filter(
			Comment.is_banned == False,
			Comment.ghost == False,
			Comment.deleted_utc == 0
		)

	comments = comments.order_by(Comment.created_utc.desc()) \
		.offset(PAGE_SIZE * (page - 1)).limit(PAGE_SIZE+1).all()
	if v:
		comments = [c[0] for c in comments]

	next_exists = (len(comments) > PAGE_SIZE)
	comments = comments[:PAGE_SIZE]

	if (v and v.client) or request.path.endswith(".json"):
		return {"data": [c.json(g.db) for c in comments]}

	return render_template("userpage/wall.html", u=u, v=v, listing=comments, page=page, next_exists=next_exists, is_following=is_following, standalone=True, render_replies=True, wall=True)


@app.get("/@<username>/wall/comment/<int:cid>")
@app.get("/@<username>/wall/comment/<int:cid>.json")
@auth_desired_with_logingate
def u_username_wall_comment(v:User, username:str, cid):
	comment = get_comment(cid, v=v)
	if not comment.wall_user_id: abort(400)
	if not User.can_see(v, comment): abort(403)

	u = comment.wall_user

	if v and hasattr(u, 'is_blocking') and u.is_blocking:
		if g.is_api_or_xhr or request.path.endswith(".json"):
			abort(403, f"You are blocking @{u.username}.")
		return render_template("userpage/blocking.html", u=u, v=v), 403

	is_following = v and u.has_follower(v)

	if v and v.id != u.id and not v.admin_level:
		g.db.flush()
		view = g.db.query(ViewerRelationship).filter_by(viewer_id=v.id, user_id=u.id).one_or_none()
		if view: view.last_view_utc = int(time.time())
		else: view = ViewerRelationship(viewer_id=v.id, user_id=u.id)
		g.db.add(view)
		g.db.commit()

	if v and request.values.get("read"):
		notif = g.db.query(Notification).filter_by(comment_id=cid, user_id=v.id, read=False).one_or_none()
		if notif:
			notif.read = True
			g.db.add(notif)
			g.db.commit()

	try: context = min(int(request.values.get("context", 8)), 8)
	except: context = 8
	comment_info = comment
	c = comment
	while context and c.level > 1:
		c = c.parent_comment
		context -= 1
	top_comment = c

	if v:
		# this is required because otherwise the vote and block
		# props won't save properly unless you put them in a list
		output = get_comments_v_properties(v, False, None, Comment.top_comment_id == c.top_comment_id)[1]

	if v and v.client: return top_comment.json(db=g.db)

	return render_template("userpage/wall.html", u=u, v=v, listing=[top_comment], page=1, is_following=is_following, standalone=True, render_replies=True, wall=True, comment_info=comment_info)


@app.get("/@<username>/posts")
@app.get("/@<username>/posts.json")
@auth_desired_with_logingate
def u_username(v:Optional[User], username:str):
	u = get_user(username, v=v, include_blocks=True, include_shadowbanned=False)
	if username != u.username:
		return redirect(SITE_FULL + request.full_path.replace(username, u.username))

	if v and hasattr(u, 'is_blocking') and u.is_blocking:
		if g.is_api_or_xhr or request.path.endswith(".json"):
			abort(403, f"You are blocking @{u.username}.")
		return render_template("userpage/blocking.html", u=u, v=v), 403

	is_following = v and u.has_follower(v)

	if not u.is_visible_to(v):
		if g.is_api_or_xhr or request.path.endswith(".json"):
			abort(403, f"@{u.username}'s userpage is private")
		return render_template("userpage/private.html", u=u, v=v, is_following=is_following), 403

	if v and v.id != u.id and not v.admin_level:
		g.db.flush()
		view = g.db.query(ViewerRelationship).filter_by(viewer_id=v.id, user_id=u.id).one_or_none()
		if view: view.last_view_utc = int(time.time())
		else: view = ViewerRelationship(viewer_id=v.id, user_id=u.id)
		g.db.add(view)
		g.db.commit()


	sort = request.values.get("sort", "new")
	t = request.values.get("t", "all")
	try: page = max(int(request.values.get("page", 1)), 1)
	except: page = 1

	ids = userpagelisting(u, site=SITE, v=v, page=page, sort=sort, t=t)

	next_exists = (len(ids) > PAGE_SIZE)
	ids = ids[:PAGE_SIZE]

	if page == 1 and sort == 'new':
		sticky = []
		sticky = g.db.query(Submission).filter_by(is_pinned=True, author_id=u.id, is_banned=False).all()
		if sticky:
			for p in sticky:
				ids = [p.id] + ids

	listing = get_posts(ids, v=v, eager=True)

	if u.unban_utc:
		if (v and v.client) or request.path.endswith(".json"):
			return {"data": [x.json(g.db) for x in listing]}

		return render_template("userpage/submissions.html",
												unban=u.unban_string,
												u=u,
												v=v,
												listing=listing,
												page=page,
												sort=sort,
												t=t,
												next_exists=next_exists,
												is_following=is_following)

	if (v and v.client) or request.path.endswith(".json"):
		return {"data": [x.json(g.db) for x in listing]}

	return render_template("userpage/submissions.html",
									u=u,
									v=v,
									listing=listing,
									page=page,
									sort=sort,
									t=t,
									next_exists=next_exists,
									is_following=is_following)


@app.get("/@<username>/comments")
@app.get("/@<username>/comments.json")
@auth_desired_with_logingate
def u_username_comments(username, v=None):
	u = get_user(username, v=v, include_blocks=True, include_shadowbanned=False)
	if username != u.username:
		return redirect(f"/@{u.username}/comments")

	if v and hasattr(u, 'is_blocking') and u.is_blocking:
		if g.is_api_or_xhr or request.path.endswith(".json"):
			abort(403, f"You are blocking @{u.username}.")
		return render_template("userpage/blocking.html", u=u, v=v), 403

	is_following = v and u.has_follower(v)

	if not u.is_visible_to(v):
		if g.is_api_or_xhr or request.path.endswith(".json"):
			abort(403, f"@{u.username}'s userpage is private")
		return render_template("userpage/private.html", u=u, v=v, is_following=is_following), 403

	if v and v.id != u.id and not v.admin_level:
		g.db.flush()
		view = g.db.query(ViewerRelationship).filter_by(viewer_id=v.id, user_id=u.id).one_or_none()
		if view: view.last_view_utc = int(time.time())
		else: view = ViewerRelationship(viewer_id=v.id, user_id=u.id)
		g.db.add(view)
		g.db.commit()

	try: page = max(int(request.values.get("page", "1")), 1)
	except: page = 1

	sort=request.values.get("sort","new")
	t=request.values.get("t","all")

	comment_post_author = aliased(User)
	comments = g.db.query(Comment.id) \
				.outerjoin(Comment.post) \
				.outerjoin(comment_post_author, Submission.author) \
				.filter(
					Comment.author_id == u.id,
					or_(Comment.parent_submission != None, Comment.wall_user_id != None),
				)

	if not v or (v.id != u.id and v.admin_level < PERMS['POST_COMMENT_MODERATION']):
		comments = comments.filter(
			Comment.is_banned == False,
			Comment.ghost == False,
			Comment.deleted_utc == 0
		)

	comments = apply_time_filter(t, comments, Comment)

	comments = sort_objects(sort, comments, Comment,
		include_shadowbanned=(v and v.can_see_shadowbanned))

	comments = comments.offset(PAGE_SIZE * (page - 1)).limit(PAGE_SIZE+1).all()
	ids = [x.id for x in comments]

	next_exists = (len(ids) > PAGE_SIZE)
	ids = ids[:PAGE_SIZE]

	listing = get_comments(ids, v=v)

	if (v and v.client) or request.path.endswith(".json"):
		return {"data": [c.json(g.db) for c in listing]}

	return render_template("userpage/comments.html", u=u, v=v, listing=listing, page=page, sort=sort, t=t,next_exists=next_exists, is_following=is_following, standalone=True)


@app.get("/@<username>/info")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def u_username_info(username, v=None):

	user=get_user(username, v=v, include_blocks=True, include_shadowbanned=False)

	if hasattr(user, 'is_blocking') and user.is_blocking:
		abort(401, f"You're blocking @{user.username}")
	elif hasattr(user, 'is_blocked') and user.is_blocked:
		abort(403, f"@{user.username} is blocking you!")

	return user.json

@app.get("/<int:id>/info")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def u_user_id_info(id, v=None):

	user=get_account(id, v=v, include_blocks=True, include_shadowbanned=False)

	if hasattr(user, 'is_blocking') and user.is_blocking:
		abort(403, f"You're blocking @{user.username}")
	elif hasattr(user, 'is_blocked') and user.is_blocked:
		abort(403, f"@{user.username} is blocking you!")

	return user.json

@app.post("/follow/<username>")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@auth_required
def follow_user(username, v):

	target = get_user(username, v=v, include_shadowbanned=False)

	if target.id==v.id:
		abort(400, "You can't follow yourself!")

	if g.db.query(Follow).filter_by(user_id=v.id, target_id=target.id).one_or_none():
		return {"message": f"@{target.username} has been followed!"}

	new_follow = Follow(user_id=v.id, target_id=target.id)
	g.db.add(new_follow)

	g.db.flush()
	target.stored_subscriber_count = g.db.query(Follow).filter_by(target_id=target.id).count()
	g.db.add(target)

	if not v.shadowbanned:
		send_notification(target.id, f"@{v.username} has followed you!")


	return {"message": f"@{target.username} has been followed!"}

@app.post("/unfollow/<username>")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@auth_required
def unfollow_user(username, v):

	target = get_user(username)

	if target.fish:
		if not v.shadowbanned:
			send_notification(target.id, f"@{v.username} has tried to unfollow you and failed because of your fish award!")
		abort(400, f"You can't unfollow @{target.username}")

	follow = g.db.query(Follow).filter_by(user_id=v.id, target_id=target.id).one_or_none()

	if follow:
		g.db.delete(follow)

		g.db.flush()
		target.stored_subscriber_count = g.db.query(Follow).filter_by(target_id=target.id).count()
		g.db.add(target)

		if not v.shadowbanned:
			send_notification(target.id, f"@{v.username} has unfollowed you!")


	return {"message": f"@{target.username} has been unfollowed!"}

@app.post("/remove_follow/<username>")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@auth_required
def remove_follow(username, v):
	target = get_user(username)

	follow = g.db.query(Follow).filter_by(user_id=target.id, target_id=v.id).one_or_none()

	if not follow: return {"message": f"@{target.username} has been removed as a follower!"}

	g.db.delete(follow)

	g.db.flush()
	v.stored_subscriber_count = g.db.query(Follow).filter_by(target_id=v.id).count()
	g.db.add(v)

	send_repeatable_notification(target.id, f"@{v.username} has removed your follow!")


	return {"message": f"@{target.username} has been removed as a follower!"}


@app.get("/pp/<int:id>")
@app.get("/uid/<int:id>/pic")
@app.get("/uid/<int:id>/pic/profile")
@limiter.exempt
def user_profile_uid(id):
	return redirect(get_profile_picture(id))

@app.get("/@<username>/pic")
@limiter.exempt
def user_profile_name(username):
	return redirect(get_profile_picture(username))


def get_saves_and_subscribes(v, template, relationship_cls, page:int, standalone=False):
	if relationship_cls in {SaveRelationship, Subscription}:
		query = relationship_cls.submission_id
		join = relationship_cls.post
		cls = Submission
	elif relationship_cls is CommentSaveRelationship:
		query = relationship_cls.comment_id
		join = relationship_cls.comment
		cls = Comment
	else:
		raise TypeError("Relationships supported is SaveRelationship, Subscription, CommentSaveRelationship")
	ids = [x[0] for x in g.db.query(query).join(join).filter(relationship_cls.user_id == v.id).order_by(cls.created_utc.desc()).offset(PAGE_SIZE * (page - 1)).limit(PAGE_SIZE + 1).all()]
	next_exists = len(ids) > PAGE_SIZE
	ids = ids[:PAGE_SIZE]

	extra = None
	if not v.admin_level >= PERMS['POST_COMMENT_MODERATION']:
		extra = lambda q:q.filter(cls.is_banned == False, cls.deleted_utc == 0)

	if cls is Submission:
		listing = get_posts(ids, v=v, eager=True, extra=extra)
	elif cls is Comment:
		listing = get_comments(ids, v=v, extra=extra)
	else:
		raise TypeError("Only supports Submissions and Comments. This is probably the result of a bug with *this* function")

	if v.client: return {"data": [x.json(g.db) for x in listing]}
	return render_template(template, u=v, v=v, listing=listing, page=page, next_exists=next_exists, standalone=standalone)

@app.get("/@<username>/saved/posts")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def saved_posts(v:User, username):
	try: page = max(1, int(request.values.get("page", 1)))
	except: abort(400, "Invalid page input!")

	return get_saves_and_subscribes(v, "userpage/submissions.html", SaveRelationship, page, False)

@app.get("/@<username>/saved/comments")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def saved_comments(v:User, username):
	try: page = max(1, int(request.values.get("page", 1)))
	except: abort(400, "Invalid page input!")

	return get_saves_and_subscribes(v, "userpage/comments.html", CommentSaveRelationship, page, True)

@app.get("/@<username>/subscribed/posts")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def subscribed_posts(v:User, username):
	try: page = max(1, int(request.values.get("page", 1)))
	except: abort(400, "Invalid page input!")

	return get_saves_and_subscribes(v, "userpage/submissions.html", Subscription, page, False)

@app.post("/fp/<fp>")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def fp(v:User, fp):
	v.fp = fp
	users = g.db.query(User).filter(User.fp == fp, User.id != v.id).all()
	if users: print(f'{v.username}: fp', flush=True)
	if v.email and v.is_activated:
		alts = g.db.query(User).filter(User.email == v.email, User.is_activated, User.id != v.id).all()
		if alts:
			print(f'{v.username}: email', flush=True)
			users += alts
	for u in users:
		li = [v.id, u.id]
		existing = g.db.query(Alt).filter(Alt.user1.in_(li), Alt.user2.in_(li)).one_or_none()
		if existing: continue
		add_alt(user1=v.id, user2=u.id)
		print(v.username + ' + ' + u.username, flush=True)

	check_for_alts(v, include_current_session=True)
	g.db.add(v)
	return '', 204

@app.get("/toggle_pins/<sort>")
def toggle_pins(sort):
	if sort == 'hot': default = True
	else: default = False

	pins = session.get(sort, default)
	session[sort] = not pins

	if is_site_url(request.referrer):
		return redirect(request.referrer)
	return redirect('/')


@app.get("/toggle_holes")
def toggle_holes():
	holes = session.get('holes', True)
	session["holes"] = not holes

	if is_site_url(request.referrer):
		return redirect(request.referrer)
	return redirect('/')


@app.get("/badge_owners/<int:bid>")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def bid_list(v:User, bid):

	try: bid = int(bid)
	except: abort(400)

	try: page = int(request.values.get("page", 1))
	except: page = 1

	users = g.db.query(User).join(User.badges).filter(Badge.badge_id==bid).offset(PAGE_SIZE * (page - 1)).limit(PAGE_SIZE + 1).all()

	next_exists = (len(users) > PAGE_SIZE)
	users = users[:PAGE_SIZE]

	return render_template("user_cards.html",
						v=v,
						users=users,
						next_exists=next_exists,
						page=page,
						user_cards_title="Badge Owners",
						)



tiers={
	3: 1,
	5: 1,
	10: 2,
	20: 3,
	50: 4,
	100: 5,
	200: 6
	}

def claim_rewards(v):
	g.db.flush()
	transactions = g.db.query(Transaction).filter_by(email=v.email, claimed=None).all()

	highest_tier = 0
	marseybux = 0

	for transaction in transactions:
		tier = tiers[transaction.amount]
		marseybux += marseybux_li[tier]
		if tier > highest_tier:
			highest_tier = tier
		transaction.claimed = True
		g.db.add(transaction)

	v.pay_account('marseybux', marseybux)

	send_repeatable_notification(v.id, f"You have received {marseybux} Marseybux! You can use them to buy awards or hats in the [shop](/shop) or gamble them in the [casino](/casino).")
	g.db.add(v)


	if highest_tier > v.patron:
		v.patron = highest_tier
		v.patron_utc = time.time() + 2937600
		for badge in g.db.query(Badge).filter(Badge.user_id == v.id, Badge.badge_id > 20, Badge.badge_id < 28).all():
			g.db.delete(badge)
		badge_grant(badge_id=20+highest_tier, user=v)

	print(f'@{v.username} rewards claimed successfully!', flush=True)


def claim_rewards_all_users():
	emails = [x[0] for x in g.db.query(Transaction.email).filter_by(claimed=None).all()]
	users = g.db.query(User).filter(User.email.in_(emails)).all()
	for user in users:
		claim_rewards(user)


KOFI_TOKEN = environ.get("KOFI_TOKEN", "").strip()
if KOFI_TOKEN:
	@app.post("/kofi")
	def kofi():
		data = json.loads(request.values['data'])
		verification_token = data['verification_token']
		if verification_token != KOFI_TOKEN: abort(400)

		id = data['kofi_transaction_id']
		created_utc = int(time.mktime(time.strptime(data['timestamp'].split('.')[0], "%Y-%m-%dT%H:%M:%SZ")))
		type = data['type']
		amount = 0
		try:
			amount = int(float(data['amount']))
		except:
			abort(400, 'invalid amount')
		email = data['email']

		transaction = Transaction(
			id=id,
			created_utc=created_utc,
			type=type,
			amount=amount,
			email=email
		)

		g.db.add(transaction)

		claim_rewards_all_users()

		return ''

@app.post("/gumroad")
def gumroad():
	data = request.values
	ip = request.headers.get('CF-Connecting-IP')
	if ip != '34.193.146.117':
		print(f'\n\n\n★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★\n\n\n/gumroad fail: {ip}\n\n\n★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★\n\n\n', flush=True)
		abort(400)

	id = data['sale_id']
	created_utc = time.time()
	type = data['recurrence']
	amount = int(data['price']) / 100
	email = data['email']
	
	transaction = Transaction(
		id=id,
		created_utc=created_utc,
		type=type,
		amount=amount,
		email=email
	)

	g.db.add(transaction)

	claim_rewards_all_users()

	print("/gumroad done\n\n\n-----------------------\n\n\n", flush=True)

	return ''




@app.post("/settings/claim_rewards")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@auth_required
def settings_claim_rewards(v:User):
	if not (v.email and v.is_activated):
		abort(400, f"You must have a verified email to verify {patron} status and claim your rewards!")

	transactions = g.db.query(Transaction).filter_by(email=v.email, claimed=None).all()

	if not transactions:
		abort(400, f"{patron} rewards already claimed!")

	claim_rewards(v)

	return {"message": f"{patron} rewards claimed!"}

@app.get("/users")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def users_list(v):

	try: page = int(request.values.get("page", 1))
	except: page = 1

	users = g.db.query(User).order_by(User.id.desc()).offset(PAGE_SIZE * (page - 1)).limit(PAGE_SIZE + 1).all()

	next_exists = (len(users) > PAGE_SIZE)
	users = users[:PAGE_SIZE]

	return render_template("user_cards.html",
						v=v,
						users=users,
						next_exists=next_exists,
						page=page,
						user_cards_title="Users Feed",
						)
