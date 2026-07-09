import time

from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import *

from files.classes import Base
from files.helpers.config.const import *
from files.helpers.lazy import lazy
from files.helpers.regex import censor_slurs
from files.helpers.sorting_and_time import make_age_string

class SubAction(Base):
	__tablename__ = "subactions"
	id = Column(Integer, primary_key=True)
	sub = Column(String, ForeignKey("subs.name"))
	user_id = Column(Integer, ForeignKey("users.id"))
	kind = Column(String)
	target_user_id = Column(Integer, ForeignKey("users.id"))
	target_submission_id = Column(Integer, ForeignKey("submissions.id"))
	target_comment_id = Column(Integer, ForeignKey("comments.id"))
	_note=Column(String)
	created_utc = Column(Integer)

	user = relationship("User", primaryjoin="User.id==SubAction.user_id")
	target_user = relationship("User", primaryjoin="User.id==SubAction.target_user_id")
	target_post = relationship("Submission")

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<{self.__class__.__name__}(id={self.id})>"

	@property
	@lazy
	def age_string(self):
		return make_age_string(self.created_utc)

	@property
	@lazy
	def string(self):
		output = SUBACTION_TYPES[self.kind]["str"].format(self=self)
		if self._note: output += f" <i>({self._note})</i>"
		return output

	@property
	@lazy
	def target_link(self):
		if self.target_user: return f'<a href="{self.target_user.url}">{self.target_user.username}</a>'
		elif self.target_post:
			return censor_slurs(f'<a href="{self.target_post.permalink}">{self.target_post.title_html}</a>', None)
		elif self.target_comment_id: return f'<a href="/comment/{self.target_comment_id}#context">comment</a>'

	@property
	@lazy
	def icon(self):
		return SUBACTION_TYPES[self.kind]['icon']

	@property
	@lazy
	def color(self):
		return SUBACTION_TYPES[self.kind]['color']

	@property
	@lazy
	def permalink(self):
		return f"{SITE_FULL}/h/{self.sub}/log/{self.id}"

from files.helpers.config.subaction_types import SUBACTION_TYPES
