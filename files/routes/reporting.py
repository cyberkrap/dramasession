from flask import g

from files.classes.flags import Flag, CommentFlag
from files.classes.mod_logs import ModAction
from files.classes.sub_logs import SubAction
from files.helpers.actions import *
from files.helpers.alerts import *
from files.helpers.get import *
from files.helpers.sanitize import filter_emojis_only
from files.routes.front import frontlist
from files.routes.wrappers import *
from files.__main__ import app, limiter, cache

@app.post("/report/post/<int:pid>")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@auth_required
def flag_post(pid, v):
	post = get_post(pid)
	reason = request.values.get("reason", "").strip()
	execute_under_siege(v, post, reason, 'flag')
	execute_blackjack(v, post, reason, 'flag')
	if v.is_muted: abort(403, "You are forbidden from making reports!")
	reason = reason[:100]
	og_flair = reason[1:]
	reason = filter_emojis_only(reason)
	if len(reason) > 350:
		abort(400, "Report reason too long!")

	if reason.startswith('!') and (v.admin_level >= PERMS['POST_COMMENT_MODERATION'] or post.sub and v.mods(post.sub)):
		post.flair = reason[1:]
		g.db.add(post)
		if v.admin_level >= PERMS['POST_COMMENT_MODERATION']:
			ma=ModAction(
				kind="flair_post",
				user_id=v.id,
				target_submission_id=post.id,
				_note=f'"{post.flair}"'
			)
			g.db.add(ma)
			position = 'a site admin'
		else:
			ma = SubAction(
				sub=post.sub,
				kind="flair_post",
				user_id=v.id,
				target_submission_id=post.id,
				_note=f'"{post.flair}"'
			)
			g.db.add(ma)
			position = f'a /h/{post.sub} mod'

		if v.id != post.author_id:
			message = f'@{v.username} ({position}) has flaired [{post.title}]({post.shortlink}) with the flair: `"{og_flair}"`'
			send_repeatable_notification(post.author_id, message)

		return {"message": "Post flaired successfully!"}

	moved = move_post(post, v, reason)
	if moved: return {"message": moved}

	existing = g.db.query(Flag.post_id).filter_by(user_id=v.id, post_id=post.id).one_or_none()
	if existing: abort(409, "You already reported this post!")
	flag = Flag(post_id=post.id, user_id=v.id, reason=reason)
	g.db.add(flag)

	return {"message": "Post reported!"}


@app.post("/report/comment/<int:cid>")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@auth_required
def flag_comment(cid, v):

	comment = get_comment(cid)

	existing = g.db.query(CommentFlag.comment_id).filter_by(user_id=v.id, comment_id=comment.id).one_or_none()
	if existing: abort(409, "You already reported this comment!")

	reason = request.values.get("reason", "").strip()
	execute_under_siege(v, comment, reason, 'flag')
	execute_blackjack(v, comment, reason, 'flag')
	reason = reason[:100]
	reason = filter_emojis_only(reason)

	if len(reason) > 350: abort(400, "Too long!")

	flag = CommentFlag(comment_id=comment.id, user_id=v.id, reason=reason)

	g.db.add(flag)

	return {"message": "Comment reported!"}


@app.post('/del_report/post/<int:pid>/<int:uid>')
@limiter.limit("4/second;100/minute;300/hour;2000/day")
@limiter.limit("4/second;100/minute;300/hour;2000/day", key_func=get_ID)
@admin_level_required(PERMS['FLAGS_REMOVE'])
def remove_report_post(v, pid, uid):
	try:
		pid = int(pid)
		uid = int(uid)
	except: abort(404)
	report = g.db.query(Flag).filter_by(post_id=pid, user_id=uid).one_or_none()

	if report:
		g.db.delete(report)

		ma=ModAction(
			kind="delete_report",
			user_id=v.id,
			target_submission_id=pid
		)

		g.db.add(ma)
	return {"message": "Report removed successfully!"}


@app.post('/del_report/comment/<int:cid>/<int:uid>')
@limiter.limit("4/second;100/minute;300/hour;2000/day")
@limiter.limit("4/second;100/minute;300/hour;2000/day", key_func=get_ID)
@admin_level_required(PERMS['FLAGS_REMOVE'])
def remove_report_comment(v, cid, uid):
	try:
		cid = int(cid)
		uid = int(uid)
	except: abort(404)
	report = g.db.query(CommentFlag).filter_by(comment_id=cid, user_id=uid).one_or_none()

	if report:
		g.db.delete(report)

		ma=ModAction(
			kind="delete_report",
			user_id=v.id,
			target_comment_id=cid
		)

		g.db.add(ma)
	return {"message": "Report removed successfully!"}

def move_post(post:Submission, v:User, reason:str) -> Union[bool, str]:
	if not reason.startswith('/h/'): return False
	sub_from = post.sub
	sub_to = get_sub_by_name(reason, graceful=True)
	sub_to = sub_to.name if sub_to else None

	can_move_post = v.admin_level >= PERMS['POST_COMMENT_MODERATION'] or (post.sub and v.mods(sub_from))
	if sub_from != 'chudrama': # posts can only be moved out of /h/chudrama by admins
		can_move_post = can_move_post or post.author_id == v.id
	if not can_move_post: return False

	if sub_from == sub_to: abort(409, f"Post is already in /h/{sub_to}")
	if post.author.exiled_from(sub_to):
		abort(403, f"User is exiled from this {HOLE_NAME}!")

	if sub_to in {'furry','vampire','racist','femboy'} and not v.client and not post.author.house.lower().startswith(sub_to):
		if v.id == post.author_id:
			abort(403, f"You need to be a member of House {sub_to.capitalize()} to post in /h/{sub_to}")
		else:
			abort(403, f"@{post.author.username} needs to be a member of House {sub_to.capitalize()} for their post to be moved to /h/{sub_to}")

	post.sub = sub_to
	post.hole_pinned = None
	g.db.add(post)

	if v.id != post.author_id:
		if v.admin_level:
			sub_from_str = 'main feed' if sub_from is None else \
				f'<a href="/h/{sub_from}">/h/{sub_from}</a>'
			sub_to_str = 'main feed' if sub_to is None else \
				f'<a href="/h/{sub_to}">/h/{sub_to}</a>'
			ma = ModAction(
				kind='move_hole',
				user_id=v.id,
				target_submission_id=post.id,
				_note=f'{sub_from_str} → {sub_to_str}',
			)
			g.db.add(ma)
		else:
			ma = SubAction(
				sub=sub_from,
				kind='move_chudrama',
				user_id=v.id,
				target_submission_id=post.id
			)
			g.db.add(ma)

		if v.admin_level >= PERMS['POST_COMMENT_MODERATION']: position = 'a site admin'
		else: position = f'a /h/{sub_from} mod'

		if post.sub == None:
			sub_to_in_notif = 'the main feed'
		else:
			sub_to_in_notif = f'/h/{post.sub}'

		if sub_from == None:
			sub_from_in_notif = 'the main feed'
		else:
			sub_from_in_notif = f'/h/{sub_from}'

		message = f"@{v.username} ({position}) has moved [{post.title}]({post.shortlink}) from {sub_from_in_notif} to {sub_to_in_notif}"
		send_repeatable_notification(post.author_id, message)

	cache.delete_memoized(frontlist)

	return f"Post moved to /h/{post.sub}"
