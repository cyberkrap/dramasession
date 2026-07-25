from flask import abort, g, has_request_context, request
from sqlalchemy import Boolean, Column, inspect, text

from files.classes import Comment, Submission
from files.helpers.config.const import PERMS


_COLUMN_NAME = 'admin_only_comments'


def _current_user():
	from files.routes.wrappers import get_logged_in_user
	return get_logged_in_user()


def _requested_admin_only_comments():
	if not has_request_context() or request.method != 'POST' or not request.path.endswith('/submit'):
		return False
	requested = str(request.values.get(_COLUMN_NAME) or '').strip().lower()
	if requested not in {'1', 'true', 'on', 'yes'}:
		return False
	user = _current_user()
	return bool(user and user.admin_level >= PERMS['POST_COMMENT_MODERATION'])


def _install_model_column():
	if hasattr(Submission, _COLUMN_NAME):
		return
	Submission.admin_only_comments = Column(
		Boolean,
		nullable=False,
		default=_requested_admin_only_comments,
		server_default=text('false'),
	)


def _install_database_column(engine):
	inspector = inspect(engine)
	if not inspector.has_table(Submission.__tablename__):
		return
	existing = {column['name'] for column in inspector.get_columns(Submission.__tablename__)}
	if _COLUMN_NAME in existing:
		return
	with engine.begin() as connection:
		if engine.dialect.name == 'postgresql':
			connection.exec_driver_sql(
				'ALTER TABLE submissions ADD COLUMN IF NOT EXISTS '
				'admin_only_comments BOOLEAN NOT NULL DEFAULT FALSE'
			)
		else:
			connection.exec_driver_sql(
				'ALTER TABLE submissions ADD COLUMN '
				'admin_only_comments BOOLEAN NOT NULL DEFAULT 0'
			)


def _submission_id_from_comment_request():
	parent_fullname = str(request.values.get('parent_fullname') or '').strip()
	if len(parent_fullname) < 3:
		return None
	identifier = parent_fullname[2:]
	if not identifier.isdigit():
		return None
	identifier = int(identifier)
	if parent_fullname.startswith('p_'):
		return identifier
	if parent_fullname.startswith('c_'):
		return g.db.query(Comment.parent_submission).filter(Comment.id == identifier).scalar()
	return None


def install_submission_comment_permissions(app, engine):
	if getattr(app, '_submission_comment_permissions_installed', False):
		return
	_install_model_column()
	_install_database_column(engine)

	@app.before_request
	def enforce_admin_only_post_comments():
		if request.method != 'POST' or request.path != '/comment':
			return None
		user = _current_user()
		submission_id = _submission_id_from_comment_request()
		if not submission_id:
			return None
		locked = g.db.query(Submission.admin_only_comments).filter(
			Submission.id == submission_id
		).scalar()
		if not locked:
			return None
		if not user or user.admin_level < PERMS['POST_COMMENT_MODERATION']:
			abort(403, 'Only admins can comment on this post!')
		return None

	app._submission_comment_permissions_installed = True
