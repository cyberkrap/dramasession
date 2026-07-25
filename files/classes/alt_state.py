from flask import g
from sqlalchemy.orm import aliased
from sqlalchemy.sql.expression import or_

from .alts import Alt
from .user import User


def _known_alts(self):
	"""Return every known alt link, including deliberately delinked records.

	The admin page needs the relationship row itself so it can display the saved
	manual/deleted state. The active moderation graph is handled separately by
	get_alt_graph_ids and excludes deleted links.
	"""
	subq = g.db.query(Alt).filter(
		or_(Alt.user1 == self.id, Alt.user2 == self.id)
	).subquery()
	link = aliased(Alt, alias=subq)

	data = g.db.query(User, link).join(
		subq,
		or_(subq.c.user1 == User.id, subq.c.user2 == User.id)
	).filter(User.id != self.id).order_by(User.username).all()

	output = []
	for user, relationship in data:
		user._is_manual = bool(relationship.is_manual)
		user._is_deleted = bool(relationship.deleted)
		user._alt_created_utc = relationship.created_utc
		output.append(user)
	return output


# Override the legacy cached accessor after User has been declared. Keeping this
# as a fresh query prevents the admin table from showing a pre-delink snapshot.
User.alts = property(_known_alts)
