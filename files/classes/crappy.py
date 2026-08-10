import time

from sqlalchemy import Column, ForeignKey, Index, UniqueConstraint
from sqlalchemy.sql.sqltypes import Integer, String, Text

from files.classes import Base


class CrappyRequest(Base):
    __tablename__ = "crappy_requests"
    __table_args__ = (
        UniqueConstraint("source_type", "source_id", name="uq_crappy_requests_source"),
        Index("ix_crappy_requests_status_id", "status", "id"),
    )

    id = Column(Integer, primary_key=True)
    source_type = Column(String(16), nullable=False)
    source_id = Column(Integer, nullable=False)
    requester_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String(16), nullable=False, default="pending")
    attempts = Column(Integer, nullable=False, default=0)
    provider = Column(String(32))
    model = Column(String(128))
    provider_request_id = Column(String(255))
    response_comment_id = Column(Integer, ForeignKey("comments.id"))
    error = Column(Text)
    created_utc = Column(Integer, nullable=False)
    updated_utc = Column(Integer, nullable=False)
    available_utc = Column(Integer, nullable=False, default=0)

    def __init__(self, *args, **kwargs):
        now = int(time.time())
        kwargs.setdefault("created_utc", now)
        kwargs.setdefault("updated_utc", now)
        super().__init__(*args, **kwargs)
