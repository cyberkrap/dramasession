import time
from pathlib import Path

from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import *

from files.classes import Base
from files.helpers.config.const import SITE_NAME
from files.helpers.lazy import lazy


_OBSESSION_BADGE_ASSETS = {
	16: "emoji-master.webp",
	17: "emoji-artisan.webp",
	21: "nikki-supporter.webp",
	22: "bear-insider.webp",
	23: "sandy-devoted.webp",
	24: "curry-obsession.webp",
	25: "ian-bankroller.webp",
	99: "sidebar.webp",
	366: "366.webp",
	367: "367.webp",
}
_OBSESSION_BADGE_ASSETS_BY_NAME = {
	"Minor Strike": "minor-strike.png",
}
_BADGE_ASSET_DIRECTORY = Path(__file__).resolve().parents[1] / "assets" / "images" / SITE_NAME / "badges"


class BadgeDef(Base):
	__tablename__ = "badge_defs"

	id = Column(Integer, primary_key_key=True, autoincrement=True)
	name = Column(String)
	description = Column(String)
	created_utc = Column(Integer)

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<{self.__class__.__name__}(id={self.id})>"

	@property
	@lazy
	def path(self):
		badge_name = str(self.name or "").strip()
		if SITE_NAME == "Obsession" and badge_name == "Minor Strike":
			return "/assets/images/Obsession/badges/minor-strike.png?v=20260803-minor-strike-png"
		asset_name = _OBSESSION_BADGE_ASSETS.get(self.id)
		if not asset_name:
			asset_name = _OBSESSION_BADGE_ASSETS_BY_NAME.get(badge_name)
		if asset_name and (_BADGE_ASSET_DIRECTORY / asset_name).is_file():
			return f"/i/{SITE_NAME}/badges/{asset_name}?v=20260808-casino-million"
		if 20 < self.id < 28 or self.id == 222:
			return f"/i/{SITE_NAME}/badges/{self.id}.webp"
		return f"/i/badges/{self.id}.webp"


class Badge(Base):

	__tablename__ = "badges"

	user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
	badge_id = Column(Integer, ForeignKey('badge_defs.id'), primary_key=True)
	description = Column(String)
	url = Column(String)
	created_utc = Column(Integer)

	user = relationship("User", back_populates="badges")
	badge = relationship("BadgeDef", primaryjoin="Badge.badge_id == BadgeDef.id", lazy="joined", innerjoin=True)

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs:
			kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<{self.__class__.__name__}(user_id={self.user_id}, badge_id={self.badge_id})>"

	@property
	@lazy
	def until(self):
		if self.badge_id == 28 and self.user.agendaposter != 1: return self.user.agendaposter
		if self.badge_id == 170 and self.user.marsify != 1: return self.user.marsify

		if self.badge_id == 94: return self.user.progressivestack
		if self.badge_id == 95: return self.user.bird
		if self.badge_id == 96: return self.user.flairchanged
		if self.badge_id == 97: return self.user.longpost
		if self.badge_id == 98: return self.user.marseyawarded
		if self.badge_id == 109: return self.user.rehab
		if self.badge_id == 167: return self.user.owoify
		if self.badge_id == 168: return self.user.bite
		if self.badge_id == 169: return self.user.earlylife
		if self.badge_id == 171: return self.user.rainbow

		return None

	@property
	@lazy
	def text(self):
		if self.until:
			text = self.badge.description + " until"
		elif self.badge_id in {28, 170, 179}:
			text = self.badge.description + " permanently"
		elif self.description:
			text = self.description
		elif self.badge.description:
			text = self.badge.description
		else:
			return self.name

		return f'{self.name} - {text}'

	@property
	@lazy
	def name(self):
		return self.badge.name

	@property
	@lazy
	def path(self):
		return self.badge.path

	@property
	@lazy
	def json(self):
		return {'text': self.text,
				'name': self.name,
				'url': self.url,
				'icon_url':self.path
				}
