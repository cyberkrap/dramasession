import time

from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import declared_attr
from sqlalchemy.sql.sqltypes import *

from files.classes import Base

class SubRelationship(Base):
	__tablename__ = NotImplemented
	__abstract__ = True

	@declared_attr
	def user_id(self):
		return Column(Integer, ForeignKey("users.id"), primary_key=True)

	@declared_attr
	def sub(self):
		return Column(String(20), ForeignKey("subs.name"), primary_key=True)

	@declared_attr
	def created_utc(self):
		return Column(Integer)

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<{self.__class__.__name__}(user_id={self.user_id}, sub={self.sub})>"

class SubJoin(SubRelationship):
	__tablename__ = "sub_joins"

class SubBlock(SubRelationship):
	__tablename__ = "sub_blocks"

class SubSubscription(SubRelationship):
	__tablename__ = "sub_subscriptions"
