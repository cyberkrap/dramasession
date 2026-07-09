import time

from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship, scoped_session
from sqlalchemy.sql.sqltypes import *

from files.classes import Base
from files.helpers.lazy import lazy
from files.helpers.regex import censor_slurs

class HatDef(Base):
	__tablename__ = "hat_defs"

	id = Column(Integer, primary_key=True)
	name = Column(String)
	description = Column(String)
	author_id = Column(Integer, ForeignKey('users.id'))
	price = Column(Integer)
	submitter_id = Column(Integer, ForeignKey("users.id"))
	created_utc = Column(Integer)

	author = relationship("User", primaryjoin="HatDef.author_id == User.id", back_populates="designed_hats")
	submitter = relationship("User", primaryjoin="HatDef.submitter_id == User.id")

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<{self.__class__.__name__}(id={self.id})>"

	@lazy
	def number_sold(self, db:scoped_session):
		return db.query(Hat).filter_by(hat_id=self.id).count()

	@lazy
	def censored_description(self, v):
		return censor_slurs(self.description, v)

	@property
	@lazy
	def is_purchasable(self):
		return self.price > 0


class Hat(Base):
	__tablename__ = "hats"

	user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
	hat_id = Column(Integer, ForeignKey('hat_defs.id'), primary_key=True)
	equipped = Column(Boolean, default=False)
	created_utc = Column(Integer)

	hat_def = relationship("HatDef")
	owners = relationship("User", back_populates="owned_hats")

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<{self.__class__.__name__}(user_id={self.user_id}, hat_id={self.hat_id})>"

	@property
	@lazy
	def name(self):
		return self.hat_def.name

	@lazy
	def censored_description(self, v):
		return self.hat_def.censored_description(v)
