from flask import g, render_template, request
from sqlalchemy import or_

from files.__main__ import app, limiter
from files.classes.comment import Comment
from files.classes.flags import CommentFlag, Flag
from files.classes.submission import Submission
from files.classes.votes import CommentVote, Vote
from files.helpers.alerts import send_repeatable_notification
from files.helpers.config.const import DEFAULT_RATELIMIT, PAGE_SIZE, PERMS
from files.helpers.get import get_comment, get_comments, get_post, get_posts
from files.routes.wrappers import admin_level_required, get_ID


@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@admin_level_required(PERMS['POST_COMMENT_MODERATION'])
def fixed_reported_posts(v):
	try:
		page = max(1, int(request.values.get('page', 1)))
	except Exception:
		page = 1
	ids = [row[0] for row in g.db.query(Flag.post_id).join(
		Submission, Submission.id == Flag.post_id
	).filter(
		or_(Submission.is_banned == False, Submission.is_banned == None),
		or_(Submission.deleted_utc == 0, Submission.deleted_utc == None),
	).distinct().order_by(Flag.post_id.desc()).offset(
		PAGE_SIZE * (page - 1)
	).limit(PAGE_SIZE + 1).all()]
	next_exists = len(ids) > PAGE_SIZE
	return render_template(
		'admin/reported_posts.html',
		next_exists=next_exists,
		listing=get_posts(ids[:PAGE_SIZE], v=v),
		page=page,
		v=v,
	)


@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@admin_level_required(PERMS['POST_COMMENT_MODERATION'])
def fixed_reported_comments(v):
	try:
		page = max(1, int(request.values.get('page', 1)))
	except Exception:
		page = 1
	ids = [row[0] for row in g.db.query(CommentFlag.comment_id).join(
		Comment, Comment.id == CommentFlag.comment_id
	).filter(
		or_(Comment.is_banned == False, Comment.is_banned == None),
		or_(Comment.deleted_utc == 0, Comment.deleted_utc == None),
	).distinct().order_by(CommentFlag.comment_id.desc()).offset(
		PAGE_SIZE * (page - 1)
	).limit(PAGE_SIZE + 1).all()]
	next_exists = len(ids) > PAGE_SIZE
	return render_template(
		'admin/reported_comments.html',
		next_exists=next_exists,
		listing=get_comments(ids[:PAGE_SIZE], v=v),
		page=page,
		v=v,
		standalone=True,
	)


def _route_arg(args, kwargs, name, position):
	if name in kwargs:
		return kwargs[name]
	if len(args) > position:
		return args[position]
	return None


def _actor_after_route():
	# The registered Flask endpoint is the outer admin/auth wrapper. It resolves
	# the acting user during the call and stores it on g; it is therefore not
	# available to this endpoint-level wrapper until the original route returns.
	return getattr(g, 'v', None)


def _earned_vote_coins(vote_cls, target_field, target_id):
	return sum(
		max(0, int(coins or 0))
		for (coins,) in g.db.query(vote_cls.coins).filter(
			getattr(vote_cls, target_field) == target_id
		).all()
	)


def _claw_back_vote_coins(author, amount):
	if amount <= 0:
		return 0
	author.charge_account(
		'coins', amount,
		should_check_balance=False,
		allow_unlimited=False,
	)
	return amount


def install_report_fixes():
	app.view_functions['reported_posts'] = fixed_reported_posts
	app.view_functions['reported_comments'] = fixed_reported_comments

	remove_report_post = app.view_functions.get('remove_report_post')
	remove_report_comment = app.view_functions.get('remove_report_comment')
	remove_post = app.view_functions.get('remove_post')
	remove_comment = app.view_functions.get('remove_comment')

	if remove_report_post and not getattr(remove_report_post, '_report_notice_v2', False):
		def wrapped_remove_report_post(*args, **kwargs):
			pid = int(_route_arg(args, kwargs, 'pid', 0))
			uid = int(_route_arg(args, kwargs, 'uid', 1))
			post = get_post(pid)
			report_exists = g.db.query(Flag).filter_by(post_id=pid, user_id=uid).one_or_none() is not None
			result = remove_report_post(*args, **kwargs)
			actor = _actor_after_route()
			if report_exists and actor and uid != actor.id:
				send_repeatable_notification(
					uid,
					f'@{actor.username} (a site admin) has deleted your report on [this post]({post.shortlink})',
				)
			return result
		wrapped_remove_report_post._report_notice_v2 = True
		app.view_functions['remove_report_post'] = wrapped_remove_report_post

	if remove_report_comment and not getattr(remove_report_comment, '_report_notice_v2', False):
		def wrapped_remove_report_comment(*args, **kwargs):
			cid = int(_route_arg(args, kwargs, 'cid', 0))
			uid = int(_route_arg(args, kwargs, 'uid', 1))
			comment = get_comment(cid)
			report_exists = g.db.query(CommentFlag).filter_by(comment_id=cid, user_id=uid).one_or_none() is not None
			result = remove_report_comment(*args, **kwargs)
			actor = _actor_after_route()
			if report_exists and actor and uid != actor.id:
				send_repeatable_notification(
					uid,
					f'@{actor.username} (a site admin) has deleted your report on [this comment]({comment.shortlink})',
				)
			return result
		wrapped_remove_report_comment._report_notice_v2 = True
		app.view_functions['remove_report_comment'] = wrapped_remove_report_comment

	if remove_post and not getattr(remove_post, '_report_notice_v2', False):
		def wrapped_remove_post(*args, **kwargs):
			post_id = int(_route_arg(args, kwargs, 'post_id', 0))
			post = get_post(post_id)
			was_active = not bool(post.is_banned)
			reporters = {
				row[0] for row in g.db.query(Flag.user_id).filter_by(post_id=post.id).all()
			}
			earned = _earned_vote_coins(Vote, 'submission_id', post.id) if was_active else 0
			author_id = post.author_id
			author = post.author
			link = post.shortlink
			result = remove_post(*args, **kwargs)
			actor = _actor_after_route()
			if actor and was_active:
				lost = _claw_back_vote_coins(author, earned)
				if author_id != actor.id:
					message = f'@{actor.username} (a site admin) has removed your [post]({link})'
					if lost:
						message += f" and you've lost {lost:,} Wishcoins earned from its votes as a result"
					send_repeatable_notification(author_id, message)
				for reporter_id in reporters:
					if reporter_id in {actor.id, author_id}:
						continue
					send_repeatable_notification(
						reporter_id,
						f'@{actor.username} (a site admin) has removed a [post]({link}) you reported',
					)
			return result
		wrapped_remove_post._report_notice_v2 = True
		app.view_functions['remove_post'] = wrapped_remove_post

	if remove_comment and not getattr(remove_comment, '_report_notice_v2', False):
		def wrapped_remove_comment(*args, **kwargs):
			comment_id = int(_route_arg(args, kwargs, 'c_id', 0))
			comment = get_comment(comment_id)
			was_active = not bool(comment.is_banned)
			reporters = {
				row[0] for row in g.db.query(CommentFlag.user_id).filter_by(comment_id=comment.id).all()
			}
			earned = _earned_vote_coins(CommentVote, 'comment_id', comment.id) if was_active else 0
			author_id = comment.author_id
			author = comment.author
			link = comment.shortlink
			result = remove_comment(*args, **kwargs)
			actor = _actor_after_route()
			if actor and was_active:
				lost = _claw_back_vote_coins(author, earned)
				if author_id != actor.id:
					message = f'@{actor.username} (a site admin) has removed your [comment]({link})'
					if lost:
						message += f" and you've lost {lost:,} Wishcoins earned from its votes as a result"
					send_repeatable_notification(author_id, message)
				for reporter_id in reporters:
					if reporter_id in {actor.id, author_id}:
						continue
					send_repeatable_notification(
						reporter_id,
						f'@{actor.username} (a site admin) has removed a [comment]({link}) you reported',
					)
			return result
		wrapped_remove_comment._report_notice_v2 = True
		app.view_functions['remove_comment'] = wrapped_remove_comment
