import time

from sqlalchemy import Column, ForeignKey
from sqlalchemy.sql.sqltypes import *

from files.classes import Base

class Marsey(Base):
	__tablename__ = "marseys"

	name = Column(String, primary_key=True)
	author_id = Column(Integer, ForeignKey("users.id"))
	tags = Column(String)
	count = Column(Integer, default=0)
	submitter_id = Column(Integer, ForeignKey("users.id"))
	created_utc = Column(Integer)

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<{self.__class__.__name__}(name={self.name})>"

	def tags_list(self):
		return self.tags.split(" ") + [self.name[len("marsey"):]]  # type: ignore

	def json(self):
		data = {
			"name": self.name,
			"author_id": self.author_id,
			"submitter_id": self.submitter_id,
			"tags": self.tags_list(),
			"count": self.count,
			"created_utc": self.created_utc,
			"class": "Marsey",
		}
		if "author" in self.__dict__ and self.author:
			data["author"] = self.author
		return data
