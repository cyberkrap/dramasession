from sqlalchemy import Column
from sqlalchemy.sql.sqltypes import *

from files.classes import Base

class Transaction(Base):
	__tablename__ = "transactions"
	id = Column(String, primary_key=True)
	created_utc = Column(Integer)
	type = Column(String)
	amount = Column(Integer)
	email = Column(String)
	claimed = Column(Boolean)

	def __repr__(self):
		return f"<{self.__class__.__name__}(id={self.id})>"
