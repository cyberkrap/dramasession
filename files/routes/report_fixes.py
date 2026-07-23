from flask import g, render_template, request
from sqlalchemy import or_

from files.__main__ import app, limiter
from files.classes.comment import Comment
from files.classes.flags import CommentFlag, Flag
from files.classes.submission import Submission
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


def install_report_fixes():
	app.view_functions['reported_posts'] = fixed_reported_posts
	app.view_functions['reported_comments'] = fixed_reported_comments

	remove_report_post = app.view_functions.get('remove_report_post')
	remove_report_comment = app.view_functions.get('remove_report_comment')
	remove_post = app.view_functions.get('remove_post')
	remove_comment = app.view_functions.get('remove_comment')

	if remove_report_post and not getattr(remove_report_post, '_report_notice', False):
		def wrapped_remove_report_post(*args, **kwargs):
			v = _route_arg(args, kwargs, 'v', 0)
			pid = _route_arg(args, kwargs, 'pid', 1)
			uid = _route_arg(args, kwargs, 'uid', 2)
			post = get_post(int(pid))
			reporter_id = int(uid)
			result = remove_report_post(*args, **kwargs)
			if v and reporter_id != v.id:
				send_repeatable_notification(
					reporter_id,
					f'@{v.username} (a site admin) has deleted your report on [this post]({post.shortlink})',
				)
			return result
		wrapped_remove_report_post._report_notice = True
		app.view_functions['remove_report_post'] = wrapped_remove_report_post

	if remove_report_comment and not getattr(remove_report_comment, '_report_notice', False):
		def wrapped_remove_report_comment(*args, **kwargs):
			v = _route_arg(args, kwargs, 'v', 0)
			cid = _route_arg(args, kwargs, 'cid', 1)
			uid = _route_arg(args, kwargs, 'uid', 2)
			comment = get_comment(int(cid))
			reporter_id = int(uid)
			result = remove_report_comment(*args, **kwargs)
			if v and reporter_id != v.id:
				send_repeatable_notification(
					reporter_id,
					f'@{v.username} (a site admin) has deleted your report on [this comment]({comment.shortlink})',
				)
			return result
		wrapped_remove_report_comment._report_notice = True
		app.view_functions['remove_report_comment'] = wrapped_remove_report_comment

	if remove_post and not getattr(remove_post, '_report_notice', False):
		def wrapped_remove_post(*args, **kwargs):
			v = _route_arg(args, kwargs, 'v', 0)
			post_id = _route_arg(args, kwargs, 'post_id', 1)
			post = get_post(int(post_id))
			reporters = {
				row[0] for row in g.db.query(Flag.user_id).filter_by(post_id=post.id).all()
			}
			result = remove_post(*args, **kwargs)
			if v:
				for reporter_id in reporters:
					if reporter_id == v.id:
						continue
					send_repeatable_notification(
						reporter_id,
						f'@{v.username} (a site admin) has removed a [post]({post.shortlink}) you reported',
					)
			return result
		wrapped_remove_post._report_notice = True
		app.view_functions['remove_post'] = wrapped_remove_post

	if remove_comment and not getattr(remove_comment, '_report_notice', False):
		def wrapped_remove_comment(*args, **kwargs):
			v = _route_arg(args, kwargs, 'v', 0)
			comment_id = _route_arg(args, kwargs, 'c_id', 1)
			comment = get_comment(int(comment_id))
			reporters = {
				row[0] for row in g.db.query(CommentFlag.user_id).filter_by(comment_id=comment.id).all()
			}
			result = remove_comment(*args, **kwargs)
			if v:
				for reporter_id in reporters:
					if reporter_id == v.id:
						continue
					send_repeatable_notification(
						reporter_id,
						f'@{v.username} (a site admin) has removed a [comment]({comment.shortlink}) you reported',
					)
			return result
		wrapped_remove_comment._report_notice = True
		app.view_functions['remove_comment'] = wrapped_remove_comment
