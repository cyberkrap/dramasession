import time

from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import *

from files.classes import Base
from files.helpers.lazy import lazy

class Vote(Base):
	__tablename__ = "votes"

	submission_id = Column(Integer, ForeignKey("submissions.id"), primary_key=True)
	user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
	vote_type = Column(Integer)
	app_id = Column(Integer, ForeignKey("oauth_apps.id"))
	real = Column(Boolean, default=True)
	coins = Column(Integer, default=1, nullable=False)
	created_utc = Column(Integer)

	user = relationship("User")

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<{self.__class__.__name__}(id={self.id}, vote_type={self.vote_type})>"

	@property
	@lazy
	def json(self):
		return {
			"user_id": self.user_id,
			"submission_id": self.submission_id,
			"vote_type": self.vote_type,
			"user": self.user.json,
		}

class CommentVote(Base):

	__tablename__ = "commentvotes"

	comment_id = Column(Integer, ForeignKey("comments.id"), primary_key=True)
	user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
	vote_type = Column(Integer)
	app_id = Column(Integer, ForeignKey("oauth_apps.id"))
	real = Column(Boolean, default=True)
	coins = Column(Integer, default=1, nullable=False)
	created_utc = Column(Integer)

	user = relationship("User")

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<{self.__class__.__name__}(id={self.id}, vote_type={self.vote_type})>"

	@property
	@lazy
	def json(self):
		return {
			"user_id": self.user_id,
			"submission_id": self.submission_id,
			"vote_type": self.vote_type,
			"user": self.user.json,
		}
