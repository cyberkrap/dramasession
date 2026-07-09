import os
from collections import Counter
from json import loads
from shutil import copyfile

import gevent

from files.classes import *
from files.helpers.actions import *
from files.helpers.alerts import *
from files.helpers.cloudflare import purge_files_in_cache
from files.helpers.config.const import *
from files.helpers.get import *
from files.helpers.marsify import marsify
from files.helpers.media import *
from files.helpers.owoify import owoify
from files.helpers.regex import *
from files.helpers.sanitize import filter_emojis_only
from files.helpers.slots import *
from files.helpers.treasure import *
from files.routes.front import comment_idlist
from files.routes.routehelpers import execute_shadowban_viewers_and_voters
from files.routes.wrappers import *
from files.__main__ import app, cache, limiter

WORDLE_COLOR_MAPPINGS = {-1: "🟥", 0: "🟨", 1: "🟩"}

@app.get("/comment/<int:cid>")
@app.get("/post/<int:pid>/<anything>/<int:cid>")
@app.get("/h/<sub>/comment/<int:cid>")
@app.get("/h/<sub>/post/<int:pid>/<anything>/<int:cid>")
@auth_desired_with_logingate
def post_pid_comment_cid(cid, pid=None, anything=None, v=None, sub=None):

	comment = get_comment(cid, v=v)
	if not User.can_see(v, comment): abort(403)

	if v and request.values.get("read"):
		notif = g.db.query(Notification).filter_by(comment_id=cid, user_id=v.id, read=False).one_or_none()
		if notif:
			notif.read = True
			g.db.add(notif)
			g.db.commit()

	if comment.parent_submission:
		post = comment.parent_submission
	else:
		post = NOTIFICATION_THREAD

	post = get_post(post, v=v)
	
	if post.over_18 and not (v and v.over_18) and not session.get('over_18', 0) >= int(time.time()):
		if v and v.client: abort(403, "This content is not suitable for some users and situations!")
		else: return render_template("errors/nsfw.html", v=v), 403

	try: context = min(int(request.values.get("context", 8)), 8)
	except: context = 8
	comment_info = comment
	c = comment
	while context and c.level > 1:
		c = c.parent_comment
		context -= 1
	top_comment = c

	if post.new: defaultsortingcomments = 'new'
	elif v: defaultsortingcomments = v.defaultsortingcomments
	else: defaultsortingcomments = "hot"
	sort=request.values.get("sort", defaultsortingcomments)

	if v:
		# this is required because otherwise the vote and block
		# props won't save properly unless you put them in a list
		output = get_comments_v_properties(v, False, None, Comment.top_comment_id == c.top_comment_id)[1]
	post.replies=[top_comment]

	execute_shadowban_viewers_and_voters(v, post)
	execute_shadowban_viewers_and_voters(v, comment)

	if v and v.client: return top_comment.json(db=g.db)
	else:
		if post.is_banned and not (v and (v.admin_level >= PERMS['POST_COMMENT_MODERATION'] or post.author_id == v.id)): template = "submission_banned.html"
		else: template = "submission.html"
		return render_template(template, v=v, p=post, sort=sort, comment_info=comment_info, render_replies=True, sub=post.subr)

@app.post("/comment")
@limiter.limit("1/second;20/minute;200/hour;1000/day")
@limiter.limit("1/second;20/minute;200/hour;1000/day", key_func=get_ID)
@auth_required
def comment(v:User):
	if v.is_suspended: abort(403, "You can't perform this action while banned!")

	parent_fullname = request.values.get("parent_fullname").strip()
	if len(parent_fullname) < 3: abort(400)
	id = parent_fullname[2:]
	parent_comment_id = None
	rts = False

	post_target = None
	parent = None

	if parent_fullname.startswith("u_"):
		parent = get_account(id, v=v)
		post_target = parent
		ghost = False
	elif parent_fullname.startswith("p_"):
		parent = get_post(id, v=v)
		post_target = parent
		if POLL_THREAD and parent.id == POLL_THREAD and v.admin_level < PERMS['POST_TO_POLL_THREAD']: abort(403)
		ghost = parent.ghost
	elif parent_fullname.startswith("c_"):
		parent = get_comment(id, v=v)
		post_target = get_post(parent.parent_submission, v=v, graceful=True) or get_account(parent.wall_user_id, v=v, include_blocks=True, include_shadowbanned=False)
		parent_comment_id = parent.id
		if parent.author_id == v.id: rts = True
		if not v.can_post_in_ghost_threads and isinstance(post_target, Submission) and post_target.ghost:
			abort(403, f"You need {TRUESCORE_GHOST_MINIMUM} truescore to post in ghost threads")
		ghost = parent.ghost
	else: abort(404)

	level = 1 if isinstance(parent, (Submission, User)) else int(parent.level) + 1
	parent_user = parent if isinstance(parent, User) else parent.author
	posting_to_submission = isinstance(post_target, Submission)

	if not User.can_see(v, parent): abort(403)
	if not isinstance(parent, User) and parent.deleted_utc != 0:
		if isinstance(parent, Submission):
			abort(403, "This post has been deleted!")
		else:
			abort(403, "This comment has been deleted!")

	if posting_to_submission:
		sub = post_target.sub
		if sub and v.exiled_from(sub): abort(403, f"You're exiled from /h/{sub}")
		if sub in {'furry','vampire','racist','femboy'} and not v.client and not v.house.lower().startswith(sub):
			abort(403, f"You need to be a member of House {sub.capitalize()} to comment in /h/{sub}")

	if level > COMMENT_MAX_DEPTH: abort(400, f"Max comment level is {COMMENT_MAX_DEPTH}")

	body = sanitize_raw_body(request.values.get("body", ""), False)

	if not posting_to_submission or post_target.id not in ADMIGGER_THREADS:
		if v.longpost and (len(body) < 280 or ' [](' in body or body.startswith('[](')):
			abort(403, "You have to type more than 280 characters!")
		elif v.bird and len(body) > 140:
			abort(403, "You have to type less than 140 characters!")

	if not body and not request.files.get('file'): abort(400, "You need to actually write something!")

	if not v.admin_level >= PERMS['POST_COMMENT_MODERATION'] and parent_user.any_block_exists(v):
		abort(403, "You can't reply to users who have blocked you or users that you have blocked!")

	body, _, options, choices = sanitize_poll_options(v, body, False)

	if request.files.get("file") and not g.is_tor:
		files = request.files.getlist('file')[:4]
		
		if files:
			media_ratelimit(v)

		for file in files:
			if file.content_type.startswith('image/'):
				oldname = f'/images/{time.time()}'.replace('.','') + '.webp'
				file.save(oldname)
				image = process_image(oldname, v)
				if image == "": abort(400, "Image upload failed")
				if posting_to_submission and v.admin_level >= PERMS['SITE_SETTINGS_SIDEBARS_BANNERS_BADGES']:
					def process_sidebar_or_banner(type, resize=0):
						li = sorted(os.listdir(f'files/assets/images/{SITE_NAME}/{type}'),
							key=lambda e: int(e.split('.webp')[0]))[-1]
						num = int(li.split('.webp')[0]) + 1
						filename = f'files/assets/images/{SITE_NAME}/{type}/{num}.webp'
						copyfile(oldname, filename)
						process_image(filename, v, resize=resize)

					if post_target.id == SIDEBAR_THREAD:
						process_sidebar_or_banner('sidebar', 400)
					elif post_target.id == BANNER_THREAD:
						banner_width = 1200
						process_sidebar_or_banner('banners', banner_width)
					elif post_target.id == BADGE_THREAD:
						try:
							badge_def = loads(body)
							name = badge_def["name"]

							if len(name) > 50:
								abort(400, "Badge name is too long!")

							if not badge_name_regex.fullmatch(name):
								abort(400, "Invalid badge name!")

							existing = g.db.query(BadgeDef).filter_by(name=name).one_or_none()
							if existing: abort(409, "A badge with this name already exists!")

							badge = BadgeDef(name=name, description=badge_def["description"])
							g.db.add(badge)
							g.db.flush()
							filename = f'files/assets/images/badges/{badge.id}.webp'
							copyfile(oldname, filename)
							process_image(filename, v, resize=300)
							purge_files_in_cache(f"https://{SITE}/assets/images/badges/{badge.id}.webp")
						except Exception as e:
							abort(400, str(e))
				body += f"\n\n![]({image})"
			elif file.content_type.startswith('video/'):
				body += f"\n\n{SITE_FULL}{process_video(file, v)}"
			elif file.content_type.startswith('audio/'):
				body += f"\n\n{SITE_FULL}{process_audio(file, v)}"
			else:
				abort(415)

	body = body.strip()[:COMMENT_BODY_LENGTH_LIMIT]

	if v.admin_level >= PERMS['SITE_SETTINGS_SNAPPY_QUOTES'] and posting_to_submission and post_target.id == SNAPPY_THREAD and level == 1 and body not in SNAPPY_QUOTES:
		with open(f"snappy_{SITE_NAME}.txt", "a", encoding="utf-8") as f:
			f.write('\n{[para]}\n' + body)

	body_for_sanitize = body
	if v.owoify: body_for_sanitize = owoify(body_for_sanitize)
	if v.marsify: body_for_sanitize = marsify(body_for_sanitize)

	torture = (v.agendaposter and not v.marseyawarded and not (posting_to_submission and post_target.sub == 'chudrama') and post_target.id not in ADMIGGER_THREADS)
	body_html = sanitize(body_for_sanitize, limit_pings=5, count_marseys=not v.marsify, torture=torture)

	if post_target.id not in ADMIGGER_THREADS and '!wordle' not in body.lower() and AGENDAPOSTER_PHRASE not in body.lower():
		existing = g.db.query(Comment.id).filter(
			Comment.author_id == v.id,
			Comment.deleted_utc == 0,
			Comment.parent_comment_id == parent_comment_id,
			Comment.parent_submission == post_target.id if posting_to_submission else None,
			Comment.wall_user_id == post_target.id if not posting_to_submission else None,
			Comment.body_html == body_html
		).first()
		if existing: abort(409, f"You already made that comment: /comment/{existing.id}")

	execute_antispam_comment_check(body, v)
	execute_antispam_duplicate_comment_check(v, body_html)

	if v.marseyawarded and posting_to_submission and post_target.id not in ADMIGGER_THREADS and marseyaward_body_regex.search(body_html):
		abort(403, "You can only type marseys!")

	if len(body_html) > COMMENT_BODY_HTML_LENGTH_LIMIT: abort(400)

	is_bot = v.client is not None and v.id not in PRIVILEGED_USER_BOTS

	c = Comment(author_id=v.id,
				parent_submission=post_target.id if posting_to_submission else None,
				wall_user_id=post_target.id if not posting_to_submission else None,
				parent_comment_id=parent_comment_id,
				level=level,
				over_18=post_target.over_18 if posting_to_submission else False,
				is_bot=is_bot,
				app_id=v.client.application.id if v.client else None,
				body_html=body_html,
				body=body,
				ghost=ghost,
				)

	c.upvotes = 1
	g.db.add(c)
	g.db.flush()

	execute_blackjack(v, c, c.body, "comment")
	execute_under_siege(v, c, c.body, "comment")

	if c.level == 1: c.top_comment_id = c.id
	else: c.top_comment_id = parent.top_comment_id

	process_poll_options(c, CommentOption, options, 0, "Poll", g.db)
	process_poll_options(c, CommentOption, choices, 1, "Poll", g.db)

	if post_target.id not in ADMIGGER_THREADS and v.agendaposter and not v.marseyawarded and AGENDAPOSTER_PHRASE not in c.body.lower() and not (posting_to_submission and post_target.sub == 'chudrama'):
		c.is_banned = True
		c.ban_reason = "AutoJanny"
		g.db.add(c)

		body = AGENDAPOSTER_MSG.format(username=v.username, type='comment', AGENDAPOSTER_PHRASE=AGENDAPOSTER_PHRASE)
		body_jannied_html = AGENDAPOSTER_MSG_HTML.format(id=v.id, username=v.username, type='comment', AGENDAPOSTER_PHRASE=AGENDAPOSTER_PHRASE)

		c_jannied = Comment(author_id=AUTOJANNY_ID,
			parent_submission=post_target.id if posting_to_submission else None,
			wall_user_id=post_target.id if not posting_to_submission else None,
			distinguish_level=6,
			parent_comment_id=c.id,
			level=level+1,
			is_bot=True,
			body=body,
			body_html=body_jannied_html,
			top_comment_id=c.top_comment_id,
			ghost=c.ghost
			)

		g.db.add(c_jannied)
		g.db.flush()

		n = Notification(comment_id=c_jannied.id, user_id=v.id)
		g.db.add(n)

	execute_longpostbot(c, level, body, body_html, post_target, v)
	execute_zozbot(c, level, post_target, v)

	if not v.shadowbanned:
		notify_users = NOTIFY_USERS(body, v)

		if c.level == 1 and posting_to_submission:
			subscribers = g.db.query(Subscription.user_id).filter(Subscription.submission_id == post_target.id, Subscription.user_id != v.id).all()

			for x in subscribers:
				notify_users.add(x[0])

		if parent_user.id != v.id:
			notify_users.add(parent_user.id)

		for x in notify_users-bots:
			n = Notification(comment_id=c.id, user_id=x)
			g.db.add(n)

		if VAPID_PUBLIC_KEY != DEFAULT_CONFIG_VALUE and parent_user.id != v.id and not v.shadowbanned:
			if isinstance(parent, User):
				title = f"New comment on your wall by @{c.author_name}"
			else:
				title = f'New reply by @{c.author_name}'

			if len(c.body) > PUSH_NOTIF_LIMIT: notifbody = c.body[:PUSH_NOTIF_LIMIT] + '...'
			else: notifbody = c.body

			if posting_to_submission:
				url = f'{SITE_FULL}/comment/{c.id}?read=true#context'
			else:
				url = f'{SITE_FULL}/@{c.wall_user.username}/wall/comment/{c.id}?read=true#context'

			if parent_user.id != AEVANN_ID:
				push_notif({parent_user.id}, title, notifbody, url)

	vote = CommentVote(user_id=v.id,
						 comment_id=c.id,
						 vote_type=1,
						 )
	g.db.add(vote)
	cache.delete_memoized(comment_idlist)

	v.comment_count = g.db.query(Comment).filter(
		Comment.author_id == v.id,
		or_(Comment.parent_submission != None, Comment.wall_user_id != None),
		Comment.deleted_utc == 0
	).count()
	g.db.add(v)

	c.voted = 1

	check_for_treasure(c, body)
	execute_wordle(c, body)
	check_slots_command(c, v, v)

	# Increment post count iff not self-reply and not a spammy comment game
	# Essentially a measure to make comment counts reflect "real" content
	if (posting_to_submission and not rts
			and not c.wordle_result and not c.slots_result):
		post_target.comment_count += 1
		g.db.add(post_target)

	if c.level > 5:
		n = g.db.query(Notification).filter_by(
			comment_id=c.parent_comment.parent_comment.parent_comment.parent_comment_id,
			user_id=c.parent_comment.author_id,
		).one_or_none()
		if n: g.db.delete(n)

	g.db.flush()

	if v.client: return c.json(db=g.db)
	return {"comment": render_template("comments.html", v=v, comments=[c])}

@app.post("/edit_comment/<int:cid>")
@limiter.limit("1/second;10/minute;100/hour;200/day")
@limiter.limit("1/second;10/minute;100/hour;200/day", key_func=get_ID)
@is_not_permabanned
def edit_comment(cid, v):
	c = get_comment(cid, v=v)

	if time.time() - c.created_utc > 7*24*60*60 and not (c.post and c.post.private):
		abort(403, "You can't edit comments older than 1 week!")

	if c.author_id != v.id: abort(403)
	if not c.parent_submission and not c.wall_user_id:
		abort(403)

	body = sanitize_raw_body(request.values.get("body", ""), False)

	if len(body) < 1 and not (request.files.get("file") and not g.is_tor):
		abort(400, "You have to actually type something!")

	if body != c.body or request.files.get("file") and not g.is_tor:
		if v.longpost and (len(body) < 280 or ' [](' in body or body.startswith('[](')):
			abort(403, "You have to type more than 280 characters!")
		elif v.bird and len(body) > 140:
			abort(403, "You have to type less than 140 characters!")

		body, _, options, choices = sanitize_poll_options(v, body, False)
		process_poll_options(c, CommentOption, options, 0, "Poll", g.db)
		process_poll_options(c, CommentOption, choices, 1, "Poll", g.db)

		execute_antispam_comment_check(body, v)

		body += process_files(request.files, v)
		body = body.strip()[:COMMENT_BODY_LENGTH_LIMIT] # process_files potentially adds characters to the post

		body_for_sanitize = body
		if v.owoify:
			body_for_sanitize = owoify(body_for_sanitize)
		if v.marsify:
			body_for_sanitize = marsify(body_for_sanitize)

		torture = (v.agendaposter and not v.marseyawarded and not (c.parent_submission and c.post.sub == 'chudrama'))

		body_html = sanitize(body_for_sanitize, golden=False, limit_pings=5, torture=torture)

		if len(body_html) > COMMENT_BODY_HTML_LENGTH_LIMIT: abort(400)

		if v.marseyawarded and marseyaward_body_regex.search(body_html):
			abort(403, "You can only type marseys!")

		c.body = body
		c.body_html = body_html

		execute_blackjack(v, c, c.body, "comment")
		execute_under_siege(v, c, c.body, "comment")

		if not (c.parent_submission and c.post.id in ADMIGGER_THREADS) and v.agendaposter and not v.marseyawarded and AGENDAPOSTER_PHRASE not in c.body.lower() and not (c.parent_submission and c.post.sub == 'chudrama'):
			abort(403, f'You have to include "{AGENDAPOSTER_PHRASE}" in your comment!')


		if int(time.time()) - c.created_utc > 60 * 3: c.edited_utc = int(time.time())

		g.db.add(c)

		notify_users = NOTIFY_USERS(body, v)

		for x in notify_users-bots:
			notif = g.db.query(Notification).filter_by(comment_id=c.id, user_id=x).one_or_none()
			if not notif:
				n = Notification(comment_id=c.id, user_id=x)
				g.db.add(n)

	g.db.commit()
	return {"body": c.body, "comment": c.realbody(v)}


@app.post("/delete/comment/<int:cid>")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@auth_required
def delete_comment(cid, v):
	if v.id == 253: abort(403)
	c = get_comment(cid, v=v)
	if not c.deleted_utc:
		if c.author_id != v.id: abort(403)
		c.deleted_utc = int(time.time())
		g.db.add(c)
		cache.delete_memoized(comment_idlist)

		g.db.flush()
		v.comment_count = g.db.query(Comment).filter(
			Comment.author_id == v.id,
			or_(Comment.parent_submission != None, Comment.wall_user_id != None),
			Comment.deleted_utc == 0
		).count()
		g.db.add(v)
	return {"message": "Comment deleted!"}

@app.post("/undelete/comment/<int:cid>")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@auth_required
def undelete_comment(cid, v):
	c = get_comment(cid, v=v)
	if c.deleted_utc:
		if c.author_id != v.id: abort(403)
		c.deleted_utc = 0
		g.db.add(c)
		cache.delete_memoized(comment_idlist)
		g.db.flush()
		v.comment_count = g.db.query(Comment).filter(
			Comment.author_id == v.id,
			or_(Comment.parent_submission != None, Comment.wall_user_id != None),
			Comment.deleted_utc == 0
		).count()
		g.db.add(v)
	return {"message": "Comment undeleted!"}

@app.post("/pin_comment/<int:cid>")
@feature_required('PINS')
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def pin_comment(cid, v):

	comment = get_comment(cid, v=v)

	if not comment.stickied:
		if v.id != comment.post.author_id: abort(403)

		if comment.post.ghost: comment.stickied = "(OP)"
		else: comment.stickied = v.username + " (OP)"

		g.db.add(comment)

		if v.id != comment.author_id:
			if comment.post.ghost: message = f"OP has pinned your [comment]({comment.shortlink})"
			else: message = f"@{v.username} (OP) has pinned your [comment]({comment.shortlink})"
			send_repeatable_notification(comment.author_id, message)

	return {"message": "Comment pinned!"}


@app.post("/unpin_comment/<int:cid>")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def unpin_comment(cid, v):

	comment = get_comment(cid, v=v)

	if comment.stickied:
		if v.id != comment.post.author_id: abort(403)

		if not comment.stickied.endswith(" (OP)"):
			abort(403, "You can only unpin comments you have pinned!")

		comment.stickied = None
		g.db.add(comment)

		if v.id != comment.author_id:
			message = f"@{v.username} (OP) has unpinned your [comment]({comment.shortlink})"
			send_repeatable_notification(comment.author_id, message)
	return {"message": "Comment unpinned!"}


@app.post("/save_comment/<int:cid>")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@auth_required
def save_comment(cid, v):

	comment=get_comment(cid)

	save=g.db.query(CommentSaveRelationship).filter_by(user_id=v.id, comment_id=comment.id).one_or_none()

	if not save:
		new_save=CommentSaveRelationship(user_id=v.id, comment_id=comment.id)
		g.db.add(new_save)


	return {"message": "Comment saved!"}

@app.post("/unsave_comment/<int:cid>")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@auth_required
def unsave_comment(cid, v):

	comment=get_comment(cid)

	save=g.db.query(CommentSaveRelationship).filter_by(user_id=v.id, comment_id=comment.id).one_or_none()

	if save:
		g.db.delete(save)

	return {"message": "Comment unsaved!"}


def diff_words(answer, guess):
	"""
	Return a list of numbers corresponding to the char's relevance.
	-1 means char is not in solution or the character appears too many times in the guess
	0 means char is in solution but in the wrong spot
	1 means char is in the correct spot
	"""
	diffs = [
			1 if cs == cg else -1 for cs, cg in zip(answer, guess)
		]
	char_freq = Counter(
		c_guess for c_guess, diff, in zip(answer, diffs) if diff == -1
	)
	for i, cg in enumerate(guess):
		if diffs[i] == -1 and cg in char_freq and char_freq[cg] > 0:
			char_freq[cg] -= 1
			diffs[i] = 0
	return diffs


@app.post("/wordle/<int:cid>")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@auth_required
def handle_wordle_action(cid, v):
	comment = get_comment(cid)

	if v.id != comment.author_id:
		abort(403)

	guesses, status, answer = comment.wordle_result.split("_")
	count = len(guesses.split(" -> "))

	try: guess = request.values.get("thing").strip().lower()
	except: abort(400)

	if len(guess) != 5: abort(400, "Not a valid guess!")

	if status == "active":
		guesses += "".join(cg + WORDLE_COLOR_MAPPINGS[diff] for cg, diff in zip(guess, diff_words(answer, guess)))

		if (guess == answer): status = "won"
		elif (count == 6): status = "lost"
		else: guesses += ' -> '

		comment.wordle_result = f'{guesses}_{status}_{answer}'

		g.db.add(comment)

	return {"response" : comment.wordle_html(v)}


@app.post("/toggle_comment_nsfw/<int:cid>")
@feature_required('NSFW_MARKING')
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def toggle_comment_nsfw(cid, v):
	comment = get_comment(cid)

	if comment.author_id != v.id and not v.admin_level >= PERMS['POST_COMMENT_MODERATION'] and not (comment.post.sub and v.mods(comment.post.sub)):
		abort(403)

	if comment.over_18 and v.is_suspended_permanently:
		abort(403)

	comment.over_18 = not comment.over_18
	g.db.add(comment)

	if comment.author_id != v.id:
		if v.admin_level >= PERMS['POST_COMMENT_MODERATION']:
			ma = ModAction(
					kind = "set_nsfw_comment" if comment.over_18 else "unset_nsfw_comment",
					user_id = v.id,
					target_comment_id = comment.id,
				)
			g.db.add(ma)
		else:
			ma = SubAction(
					sub = comment.post.sub,
					kind = "set_nsfw_comment" if comment.over_18 else "unset_nsfw_comment",
					user_id = v.id,
					target_comment_id = comment.id,
				)
			g.db.add(ma)

	if comment.over_18: return {"message": "Comment has been marked as +18!"}
	else: return {"message": "Comment has been unmarked as +18!"}
