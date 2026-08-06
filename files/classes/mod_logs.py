import re
import time
from html import escape

from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import *

from files.classes import Base
from files.helpers.config.const import *
from files.helpers.lazy import lazy
from files.helpers.regex import censor_slurs
from files.helpers.sorting_and_time import make_age_string


EMOTE_MODACTION_TYPES = {
	'approve_marsey': {
		"str": 'approved an emoji made by {self.emoji_author_link} ({self.emoji_html})',
		"icon": 'fa-cat',
		"color": 'bg-success'
	},
	'reject_marsey': {
		"str": 'rejected an emoji made by {self.emoji_author_link} ({self.emoji_name})',
		"icon": 'fa-cat',
		"color": 'bg-danger'
	},
	'update_marsey': {
		"str": 'updated emoji ({self.emoji_html})',
		"icon": 'fa-cat',
		"color": 'bg-success'
	},
	'delete_marsey': {
		"str": 'deleted emoji ({self.emoji_name})',
		"icon": 'fa-cat',
		"color": 'bg-danger'
	},
}
EMOTE_MODACTION_KINDS = frozenset(EMOTE_MODACTION_TYPES)


class ModAction(Base):
	__tablename__ = "modactions"
	id = Column(Integer, primary_key=True)
	user_id = Column(Integer, ForeignKey("users.id"))
	kind = Column(String)
	target_user_id = Column(Integer, ForeignKey("users.id"))
	target_submission_id = Column(Integer, ForeignKey("submissions.id"))
	target_comment_id = Column(Integer, ForeignKey("comments.id"))
	_note=Column(String)
	created_utc = Column(Integer)

	user = relationship("User", primaryjoin="User.id==ModAction.user_id")
	target_user = relationship("User", primaryjoin="User.id==ModAction.target_user_id")
	target_post = relationship("Submission")

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<{self.__class__.__name__}(id={self.id})>"

	@property
	@lazy
	def age_string(self):
		return make_age_string(self.created_utc)

	@property
	def note(self):
		if self.kind=="ban_user":
			if self.target_post: return f'for <a href="{self.target_post.permalink}">post</a>'
			elif self.target_comment_id: return f'for <a href="/comment/{self.target_comment_id}">comment</a>'
			else: return self._note
		else:
			return self._note or ""

	@property
	@lazy
	def action_type(self):
		action_type = MODACTION_TYPES.get(self.kind)
		if action_type: return action_type
		return {
			"str": f'performed moderator action <code>{escape(self.kind or "unknown")}</code>',
			"icon": 'fa-question-circle',
			"color": 'bg-muted'
		}

	@property
	@lazy
	def string(self):
		output = self.action_type["str"].format(self=self)
		if self.note and self.kind not in EMOTE_MODACTION_KINDS and self.kind != "chat_timeout":
			output += f" <i>({self.note})</i>"
		return output

	@property
	@lazy
	def target_link(self):
		if self.target_user: return f'<a href="{self.target_user.url}">{self.target_user.username}</a>'
		elif self.target_post:
			return censor_slurs(f'<a href="{self.target_post.permalink}">{self.target_post.title_html}</a>', None)
		elif self.target_comment_id: return f'<a href="/comment/{self.target_comment_id}#context">comment</a>'

	@property
	@lazy
	def emoji_name_raw(self):
		note = str(self._note or '').strip()

		# Older update logs stored an entire link, for example:
		# <a href="/e/example.webp">example</a>. Extract the URL target before
		# sanitizing so the HTML does not become a fake filename.
		legacy_url = re.search(
			r'/(?:e|community-emote|emote-preview)/([a-zA-Z0-9_-]+)(?:\.webp|/webp)',
			note,
			re.IGNORECASE,
		)
		if legacy_url:
			return legacy_url.group(1).lower()

		if ' -> ' in note:
			note = note.rsplit(' -> ', 1)[-1].strip()

		# Accept plain names and colon-wrapped emoji syntax while rejecting any
		# leftover markup or punctuation.
		colon_name = re.fullmatch(r':?([a-zA-Z0-9_-]+):?', note)
		if colon_name:
			return colon_name.group(1).lower()

		name = re.sub(r'[^a-zA-Z0-9_-]', '', note).lower()
		return name or 'unknown'

	@property
	@lazy
	def emoji_name(self):
		return escape(self.emoji_name_raw)

	@property
	@lazy
	def emoji_html(self):
		name = self.emoji_name_raw
		return (
			f'<img loading="lazy" class="modlog-emote" '
			f'src="/emote-preview/{name}.webp" alt=":{escape(name)}:" '
			f'title=":{escape(name)}:">'
		)

	@property
	@lazy
	def emoji_author(self):
		if self.target_user:
			return self.target_user
		if self.kind != 'approve_marsey':
			return None
		try:
			from flask import g
			from files.classes.marsey import Marsey
			marsey = g.db.get(Marsey, self.emoji_name_raw)
			if not marsey or not marsey.author_id:
				return None
			return g.db.get(self.user.__class__, marsey.author_id)
		except Exception:
			return None

	@property
	@lazy
	def emoji_author_link(self):
		author = self.emoji_author
		if not author:
			return '<span class="text-muted">@unknown</span>'
		return (
			f'<a href="{escape(author.url, quote=True)}">'
			f'@{escape(author.username)}</a>'
		)

	@property
	@lazy
	def icon(self):
		return self.action_type['icon']

	@property
	@lazy
	def color(self):
		return self.action_type['color']

	@property
	@lazy
	def permalink(self):
		return f"/log/{self.id}"


from files.helpers.config.modaction_types import MODACTION_TYPES, MODACTION_TYPES_FILTERED
MODACTION_TYPES.update(EMOTE_MODACTION_TYPES)
MODACTION_TYPES_FILTERED.update(EMOTE_MODACTION_TYPES)

MODMAIL_MODACTION_TYPES = {
	'mod_mute_user': {
		"str": 'muted modmails from {self.target_link}',
		"icon": 'fa-envelope',
		"color": 'bg-danger'
	},
	'mod_unmute_user': {
		"str": 'unmuted modmails from {self.target_link}',
		"icon": 'fa-envelope-open',
		"color": 'bg-success'
	},
}
MODACTION_TYPES.update(MODMAIL_MODACTION_TYPES)
MODACTION_TYPES_FILTERED.update(MODMAIL_MODACTION_TYPES)