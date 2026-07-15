from sqlalchemy import Column, ForeignKey
from sqlalchemy.sql.sqltypes import Boolean, Integer, String, Text

from files.classes import Base


class ChatMessage(Base):
	__tablename__ = "chat_messages"

	id = Column(Integer, primary_key=True)
	channel = Column(String(32), nullable=False, default="public")
	user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
	username = Column(String(80), nullable=False)
	namecolor = Column(String(16), nullable=False, default="ffffff")
	hat = Column(String(255))
	body = Column(Text, nullable=False)
	body_html = Column(Text, nullable=False)
	body_censored = Column(Text, nullable=False)
	quotes = Column(Integer)
	created_utc = Column(Integer, nullable=False)
	has_attachment = Column(Boolean, nullable=False, default=False)
	removed_by_id = Column(Integer, ForeignKey("users.id"))
	removed_by_username = Column(String(80))
	distinguish_by_id = Column(Integer, ForeignKey("users.id"))
	distinguish_by_username = Column(String(80))