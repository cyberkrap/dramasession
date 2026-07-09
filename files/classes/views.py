import time

from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import *

from files.classes import Base
from files.helpers.lazy import *
from files.helpers.sorting_and_time import make_age_string

class ViewerRelationship(Base):
	__tablename__ = "viewers"

	user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
	viewer_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
	last_view_utc = Column(Integer)
	created_utc = Column(Integer)

	viewer = relationship("User", primaryjoin="ViewerRelationship.viewer_id == User.id")

	def __init__(self, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		if 'last_view_utc' not in kwargs: kwargs['last_view_utc'] = int(time.time())
		super().__init__(**kwargs)

	def __repr__(self):
		return f"<{self.__class__.__name__}(user_id={self.user_id}, viewer_id={self.viewer_id})>"

	@property
	@lazy
	def last_view_since(self):
		return int(time.time()) - self.last_view_utc

	@property
	@lazy
	def last_view_string(self):
		return make_age_string(self.last_view_utc)
