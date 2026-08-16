import time

from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import *

from files.classes import Base
from files.helpers.config.awards import AWARDS, HOUSE_AWARDS
from files.helpers.lazy import lazy


class AwardRelationship(Base):
	__tablename__ = "award_relationships"

	id = Column(Integer, primary_key=True)
	user_id = Column(Integer, ForeignKey("users.id"))
	submission_id = Column(Integer, ForeignKey("submissions.id"))
	comment_id = Column(Integer, ForeignKey("comments.id"))
	kind = Column(String, nullable=False)
	emoji_name = Column(String(80))
	awarded_utc = Column(Integer)
	created_utc = Column(Integer)
	price_paid = Column(Integer, default = 0, nullable=False)

	user = relationship("User", primaryjoin="AwardRelationship.user_id==User.id", back_populates="awards")
	post = relationship("Submission", primaryjoin="AwardRelationship.submission_id==Submission.id", back_populates="awards")
	comment = relationship("Comment", primaryjoin="AwardRelationship.comment_id==Comment.id", back_populates="awards")

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<{self.__class__.__name__}(id={self.id})>"

	@property
	@lazy
	def base_kind(self):
		# Legacy Emoji-award rows briefly encoded the selected emoji in `kind`.
		# Production startup normalizes those rows, but keep this tolerant so a
		# partially migrated database can still render safely.
		return str(self.kind or '').split(':', 1)[0]

	@property
	@lazy
	def effect_emoji_name(self):
		if self.base_kind != 'wholesome':
			return None

		name = str(self.emoji_name or '').strip()
		if not name and ':' in str(self.kind or ''):
			name = str(self.kind).split(':', 1)[1].strip()
		if not name or len(name) > 80:
			return None
		if not all(char.isalnum() or char in '_-' for char in name):
			return None
		return name

	@property
	@lazy
	def type(self):
		kind = self.base_kind
		if kind in AWARDS: return AWARDS[kind]
		elif kind in HOUSE_AWARDS: return HOUSE_AWARDS[kind]
		else: return AWARDS["fallback"]

	@property
	@lazy
	def title(self):
		return self.type['title']

	@property
	@lazy
	def awarded_date(self):
		if not self.awarded_utc:
			return None
		date = time.gmtime(self.awarded_utc)
		return f"{time.strftime('%b', date)} {date.tm_mday}, {date.tm_year}"

	@property
	@lazy
	def class_list(self):
		classes = self.type['icon']+' '+self.type['color']+f' award-kind-{self.base_kind}'
		if self.effect_emoji_name:
			classes += f' award-emoji-name-{self.effect_emoji_name}'
		return classes
