import json
import time

from sqlalchemy import Column, ForeignKey
from sqlalchemy.sql.sqltypes import *

from files.classes import Base
from files.helpers.lazy import lazy

CASINO_GAME_KINDS = ['blackjack', 'slots', 'roulette']

class CasinoGame(Base):
	__tablename__ = "casino_games"

	id = Column(Integer, primary_key=True)
	user_id = Column(Integer, ForeignKey("users.id"))
	created_utc = Column(Integer)
	active = Column(Boolean, default=True)
	currency = Column(String)
	wager = Column(Integer)
	winnings = Column(Integer)
	kind = Column(String)
	game_state = Column(JSON)

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs:
			kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<{self.__class__.__name__}(id={self.id})>"

	@property
	@lazy
	def game_state_json(self):
		return json.loads(self.game_state)
