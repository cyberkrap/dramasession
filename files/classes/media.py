import time

from sqlalchemy import Column, ForeignKey
from sqlalchemy.sql.sqltypes import *
from files.classes import Base

class Media(Base):
	__tablename__ = "media"
	kind = Column(String, primary_key=True)
	filename = Column(String, primary_key=True)
	user_id = Column(Integer, ForeignKey("users.id"))
	created_utc = Column(Integer)
	size = Column(Integer)

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<{self.__class__.__name__}(kind={self.kind}, filename={self.filename})>"
