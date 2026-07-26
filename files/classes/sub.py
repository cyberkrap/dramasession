import random
import time
from typing import Optional
from urllib.parse import quote

from sqlalchemy import Column
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import relationship
from sqlalchemy.types import VARCHAR, Boolean, Integer
from sqlalchemy.dialects.postgresql import ARRAY

from files.classes import Base
from files.helpers.lazy import lazy
from files.helpers.config.const import *

from .sub_relationship import *

class Sub(Base):
	__tablename__ = "subs"
	name = Column(VARCHAR(SUB_NAME_COLUMN_LENGTH), primary_key=True)
	sidebar = Column(VARCHAR(SUB_SIDEBAR_COLUMN_LENGTH))
	sidebar_html = Column(VARCHAR(SUB_SIDEBAR_HTML_COLUMN_LENGTH))
	sidebarurl = Column(VARCHAR(SUB_SIDEBAR_URL_COLUMN_LENGTH))
	bannerurls = Column(MutableList.as_mutable(ARRAY(VARCHAR(SUB_BANNER_URL_COLUMN_LENGTH))), default=MutableList([]), nullable=False)
	marseyurl = Column(VARCHAR(SUB_MARSEY_URL_LENGTH))
	css = Column(VARCHAR(SUB_CSS_COLUMN_LENGTH))
	stealth = Column(Boolean)
	created_utc = Column(Integer)

	blocks = relationship("SubBlock", primaryjoin="SubBlock.sub==Sub.name")
	followers = relationship("SubSubscription", primaryjoin="SubSubscription.sub==Sub.name")
	joins = relationship("SubJoin", lazy="dynamic", primaryjoin="SubJoin.sub==Sub.name")

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return self.name

	@property
	@lazy
	def sidebar_url(self):
		if self.sidebarurl:
			return root_relative_url(self.sidebarurl)
		if SITE_NAME == "Obsession":
			try:
				from files.helpers.community_assets import active_community_asset_filenames
				filenames = active_community_asset_filenames("sidebar")
				if filenames:
					# Give each board a stable default from the site's approved sidebar art.
					index = sum(ord(character) for character in self.name) % len(filenames)
					return f"/i/Obsession/sidebar/{quote(filenames[index])}"
			except Exception:
				pass
		return f'/i/{SITE_NAME}/sidebar.webp?v=3009'

	@property
	@lazy
	def banner_urls(self):
		if self.bannerurls: return [root_relative_url(banner) for banner in self.bannerurls]
		return []

	@lazy
	def random_banner(self):
		if not self.banner_urls: return None
		return random.choice(self.banner_urls)

	@property
	@lazy
	def has_banners(self) -> bool:
		return bool(self.bannerurls)

	@property
	@lazy
	def marsey_url(self):
		if self.marseyurl:
			return root_relative_url(self.marseyurl)
		if SITE_NAME == "Obsession":
			return "/i/Obsession/official-logo.png?v=1"
		return f'/i/{SITE_NAME}/headericon.webp?v=3009'

	@property
	@lazy
	def join_num(self):
		return self.joins.count()

	@property
	@lazy
	def block_num(self):
		return len(self.blocks)

	@property
	@lazy
	def follow_num(self):
		return len(self.followers)
