from sqlalchemy import or_

from files.classes import Comment
from files.helpers.config.const import MODMAIL_ID


def get_user_modmail_history(db, user, limit=25):
	"""Return a user's modmail threads with every reply in chronological order."""
	if not user:
		return []

	threads = db.query(Comment).filter(
		Comment.author_id == user.id,
		Comment.sentto == MODMAIL_ID,
		Comment.parent_submission == None,
		Comment.parent_comment_id == None,
		Comment.level == 1,
	).order_by(Comment.id.desc()).all()

	history = []
	for thread in threads:
		messages = db.query(Comment).filter(
			or_(Comment.id == thread.id, Comment.top_comment_id == thread.id)
		).order_by(Comment.created_utc.asc(), Comment.id.asc()).all()

		if not messages:
			messages = [thread]

		history.append({
			"thread": thread,
			"messages": messages,
			"latest_utc": messages[-1].created_utc,
		})

	history.sort(key=lambda item: item["latest_utc"], reverse=True)
	return history[:limit]
