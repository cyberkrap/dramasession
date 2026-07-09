import time

from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import *

from files.classes import Base
from files.helpers.lazy import lazy
from files.helpers.regex import censor_slurs

class Flag(Base):
	__tablename__ = "flags"

	post_id = Column(Integer, ForeignKey("submissions.id"), primary_key=True)
	user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
	reason = Column(String)
	created_utc = Column(Integer)

	user = relationship("User", primaryjoin = "Flag.user_id == User.id", uselist = False)

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<{self.__class__.__name__}(user_id={self.user_id}, post_id={self.post_id})>"

	@lazy
	def realreason(self, v):
		return censor_slurs(self.reason, v)


class CommentFlag(Base):
	__tablename__ = "commentflags"

	comment_id = Column(Integer, ForeignKey("comments.id"), primary_key=True)
	user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
	reason = Column(String)
	created_utc = Column(Integer)

	user = relationship("User", primaryjoin = "CommentFlag.user_id == User.id", uselist = False)

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<{self.__class__.__name__}(user_id={self.user_id}, comment_id={self.comment_id})>"

	@lazy
	def realreason(self, v):
		return censor_slurs(self.reason, v)
