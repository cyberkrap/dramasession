import random
import time
from typing import Optional

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
		if self.sidebarurl: return SITE_FULL + self.sidebarurl
		return f'/i/{SITE_NAME}/sidebar.webp?v=3009'

	@property
	@lazy
	def banner_urls(self):
		if self.bannerurls: return [f"{SITE_FULL}{banner}" for banner in self.bannerurls]
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
		if self.marseyurl: return SITE_FULL + self.marseyurl
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
