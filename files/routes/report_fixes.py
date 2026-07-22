from flask import g, render_template, request

from files.__main__ import app
from files.classes import Comment, CommentFlag, Flag, Submission
from files.helpers.alerts import send_repeatable_notification
from files.helpers.config.const import PAGE_SIZE
from files.helpers.get import get_comment, get_comments, get_post, get_posts


def fixed_reported_posts(v):
	try: page = max(1, int(request.values.get('page', 1)))
	except Exception: page = 1
	ids = [row[0] for row in g.db.query(Flag.post_id).join(Submission, Submission.id == Flag.post_id).filter(Submission.is_banned == False, Submission.deleted_utc == 0).distinct().order_by(Flag.post_id.desc()).offset(PAGE_SIZE * (page - 1)).limit(PAGE_SIZE + 1).all()]
	next_exists = len(ids) > PAGE_SIZE
	return render_template('admin/reported_posts.html', next_exists=next_exists, listing=get_posts(ids[:PAGE_SIZE], v=v), page=page, v=v)


def fixed_reported_comments(v):
	try: page = max(1, int(request.values.get('page', 1)))
	except Exception: page = 1
	ids = [row[0] for row in g.db.query(CommentFlag.comment_id).join(Comment, Comment.id == CommentFlag.comment_id).filter(Comment.is_banned == False, Comment.deleted_utc == 0).distinct().order_by(CommentFlag.comment_id.desc()).offset(PAGE_SIZE * (page - 1)).limit(PAGE_SIZE + 1).all()]
	next_exists = len(ids) > PAGE_SIZE
	return render_template('admin/reported_comments.html', next_exists=next_exists, listing=get_comments(ids[:PAGE_SIZE], v=v), page=page, v=v, standalone=True)


def install_report_fixes():
	app.view_functions['reported_posts'] = fixed_reported_posts
	app.view_functions['reported_comments'] = fixed_reported_comments

	remove_report_post = app.view_functions.get('remove_report_post')
	remove_report_comment = app.view_functions.get('remove_report_comment')
	remove_post = app.view_functions.get('remove_post')
	remove_comment = app.view_functions.get('remove_comment')

	if remove_report_post and not getattr(remove_report_post, '_report_notice', False):
		def wrapped_remove_report_post(*args, **kwargs):
			v = kwargs.get('v'); pid = kwargs.get('pid'); uid = kwargs.get('uid')
			post = get_post(pid)
			result = remove_report_post(*args, **kwargs)
			if v and uid and int(uid) != v.id:
				send_repeatable_notification(int(uid), f'@{v.username} (a site admin) has deleted your report on [this post]({post.shortlink})')
			return result
		wrapped_remove_report_post._report_notice = True
		app.view_functions['remove_report_post'] = wrapped_remove_report_post

	if remove_report_comment and not getattr(remove_report_comment, '_report_notice', False):
		def wrapped_remove_report_comment(*args, **kwargs):
			v = kwargs.get('v'); cid = kwargs.get('cid'); uid = kwargs.get('uid')
			comment = get_comment(cid)
			result = remove_report_comment(*args, **kwargs)
			if v and uid and int(uid) != v.id:
				send_repeatable_notification(int(uid), f'@{v.username} (a site admin) has deleted your report on [this comment]({comment.shortlink})')
			return result
		wrapped_remove_report_comment._report_notice = True
		app.view_functions['remove_report_comment'] = wrapped_remove_report_comment

	if remove_post and not getattr(remove_post, '_report_notice', False):
		def wrapped_remove_post(*args, **kwargs):
			v = kwargs.get('v'); post_id = kwargs.get('post_id')
			post = get_post(post_id)
			reporters = [row[0] for row in g.db.query(Flag.user_id).filter_by(post_id=post.id).all()]
			result = remove_post(*args, **kwargs)
			for uid in reporters:
				if not v or uid == v.id: continue
				send_repeatable_notification(uid, f'@{v.username} (a site admin) has removed a [post]({post.shortlink}) you reported')
			return result
		wrapped_remove_post._report_notice = True
		app.view_functions['remove_post'] = wrapped_remove_post

	if remove_comment and not getattr(remove_comment, '_report_notice', False):
		def wrapped_remove_comment(*args, **kwargs):
			v = kwargs.get('v'); c_id = kwargs.get('c_id')
			comment = get_comment(c_id)
			reporters = [row[0] for row in g.db.query(CommentFlag.user_id).filter_by(comment_id=comment.id).all()]
			result = remove_comment(*args, **kwargs)
			for uid in reporters:
				if not v or uid == v.id: continue
				send_repeatable_notification(uid, f'@{v.username} (a site admin) has removed a [comment]({comment.shortlink}) you reported')
			return result
		wrapped_remove_comment._report_notice = True
		app.view_functions['remove_comment'] = wrapped_remove_comment
