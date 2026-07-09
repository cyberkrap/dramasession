import time

from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import *

from files.classes import Base

class Follow(Base):
	__tablename__ = "follows"
	target_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
	user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
	created_utc = Column(Integer)

	user = relationship("User", uselist=False, primaryjoin="User.id==Follow.user_id", back_populates="following")
	target = relationship("User", uselist=False, primaryjoin="User.id==Follow.target_id", back_populates="followers")

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<{self.__class__.__name__}(id={self.id})>"
