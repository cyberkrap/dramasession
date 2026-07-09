import random
import time
from urllib.parse import urlparse
from flask import g

from sqlalchemy import Column, FetchedValue, ForeignKey
from sqlalchemy.orm import deferred, relationship, scoped_session
from sqlalchemy.sql.sqltypes import *

from files.classes import Base
from files.helpers.config.const import *
from files.helpers.lazy import lazy
from files.helpers.regex import *
from files.helpers.sorting_and_time import make_age_string

from .comment import normalize_urls_runtime
from .polls import *
from .sub import *
from .subscriptions import *

class Submission(Base):
	__tablename__ = "submissions"

	id = Column(Integer, primary_key=True)
	author_id = Column(Integer, ForeignKey("users.id"))
	edited_utc = Column(Integer, default=0)
	created_utc = Column(Integer)
	thumburl = Column(String)
	is_banned = Column(Boolean, default=False)
	bannedfor = Column(String)
	chuddedfor = Column(String)
	ghost = Column(Boolean, default=False)
	views = Column(Integer, default=0)
	deleted_utc = Column(Integer, default=0)
	distinguish_level = Column(Integer, default=0)
	stickied = Column(String)
	stickied_utc = Column(Integer)
	hole_pinned = Column(String)
	sub = Column(String, ForeignKey("subs.name"))
	is_pinned = Column(Boolean, default=False)
	private = Column(Boolean, default=False)
	comment_count = Column(Integer, default=0)
	is_approved = Column(Integer, ForeignKey("users.id"))
	over_18 = Column(Boolean, default=False)
	is_bot = Column(Boolean, default=False)
	upvotes = Column(Integer, default=1)
	downvotes = Column(Integer, default=0)
	realupvotes = Column(Integer, default=1)
	app_id=Column(Integer, ForeignKey("oauth_apps.id"))
	title = Column(String)
	title_html = Column(String)
	url = Column(String)
	body = Column(String)
	body_html = Column(String)
	flair = Column(String)
	ban_reason = Column(String)
	embed_url = Column(String)
	new = Column(Boolean)
	notify = Column(Boolean)

	author = relationship("User", primaryjoin="Submission.author_id==User.id")
	oauth_app = relationship("OauthApp")
	approved_by = relationship("User", uselist=False, primaryjoin="Submission.is_approved==User.id")
	awards = relationship("AwardRelationship", order_by="AwardRelationship.awarded_utc.desc()", back_populates="post")
	flags = relationship("Flag", order_by="Flag.created_utc")
	comments = relationship("Comment", primaryjoin="Comment.parent_submission==Submission.id", back_populates="post")
	subr = relationship("Sub", primaryjoin="foreign(Submission.sub)==remote(Sub.name)")
	options = relationship("SubmissionOption", order_by="SubmissionOption.id")

	bump_utc = deferred(Column(Integer, server_default=FetchedValue()))

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<{self.__class__.__name__}(id={self.id})>"

	@property
	@lazy
	def controversial(self):
		if self.downvotes > 5 and 0.25 < self.upvotes / self.downvotes < 4: return True
		return False

	@property
	@lazy
	def created_datetime(self):
		return time.strftime("%d/%B/%Y %H:%M:%S UTC", time.gmtime(self.created_utc))

	@property
	@lazy
	def age_string(self):
		return make_age_string(self.created_utc)

	@property
	@lazy
	def edited_string(self):
		return make_age_string(self.edited_utc)

	@property
	@lazy
	def score(self):
		return self.upvotes - self.downvotes

	@property
	@lazy
	def fullname(self):
		return f"p_{self.id}"

	@property
	@lazy
	def shortlink(self):
		link = f"/post/{self.id}"
		if self.sub: link = f"/h/{self.sub}{link}"

		if self.sub and self.sub in {'chudrama', 'countryclub', 'masterbaiters'}:
			output = '-'
		else:
			output = title_regex.sub('', self.title.lower())
			output = output.split()[:6]
			output = '-'.join(output)
			if not output: output = '-'

		return f"{link}/{output}"

	@property
	@lazy
	def permalink(self):
		return SITE_FULL + self.shortlink

	@property
	@lazy
	def domain(self):
		if not self.url: return ''
		if self.url.startswith('/'): return SITE
		domain = urlparse(self.url).netloc
		if domain.startswith("www."): domain = domain.split("www.")[1]
		return domain.replace("old.reddit.com", "reddit.com")

	@property
	@lazy
	def author_name(self):
		if self.ghost: return '👻'
		return self.author.user_name

	@property
	@lazy
	def is_youtube(self):
		return self.domain == "youtube.com" and self.embed_url and self.embed_url.startswith('<lite-youtube')

	@property
	@lazy
	def thumb_url(self):
		if self.over_18: return f"{SITE_FULL}/i/nsfw.webp?v=1"
		elif not self.url: return f"{SITE_FULL}/i/{SITE_NAME}/default_text.webp?v=2"
		elif self.thumburl:
			if self.thumburl.startswith('/'): return SITE_FULL + self.thumburl
			return self.thumburl
		elif self.is_youtube or self.is_video: return f"{SITE_FULL}/i/default_thumb_video.webp?v=2"
		elif self.is_audio: return f"{SITE_FULL}/i/default_thumb_audio.webp?v=1"
		elif self.domain.split('.')[0] == SITE.split('.')[0]:
			return f"{SITE_FULL}/i/{SITE_NAME}/site_preview.webp?v=3009"
		else: return f"{SITE_FULL}/i/default_thumb_link.webp?v=1"

	@lazy
	def json(self, db:scoped_session):
		if self.is_banned:
			return {'is_banned': True,
					'deleted_utc': self.deleted_utc,
					'ban_reason': self.ban_reason,
					'id': self.id,
					'title': self.title,
					'permalink': self.permalink,
					}

		if self.deleted_utc:
			return {'is_banned': bool(self.is_banned),
					'deleted_utc': True,
					'id': self.id,
					'title': self.title,
					'permalink': self.permalink,
					}

		flags = {}
		for f in self.flags: flags[f.user.username] = f.reason

		data = {'author_name': self.author_name if self.author else '',
				'permalink': self.permalink,
				'shortlink': self.shortlink,
				'is_banned': bool(self.is_banned),
				'deleted_utc': self.deleted_utc,
				'created_utc': self.created_utc,
				'id': self.id,
				'title': self.title,
				'is_nsfw': self.over_18,
				'is_bot': self.is_bot,
				'thumb_url': self.thumb_url,
				'domain': self.domain,
				'url': self.realurl(None),
				'body': self.body,
				'body_html': self.body_html,
				'edited_utc': self.edited_utc or 0,
				'comment_count': self.comment_count,
				'score': self.score,
				'upvotes': self.upvotes,
				'downvotes': self.downvotes,
				'stickied': self.stickied,
				'private' : self.private,
				'distinguish_level': self.distinguish_level,
				'voted': self.voted if hasattr(self, 'voted') else 0,
				'flags': flags,
				'author': '👻' if self.ghost else self.author.json
				}

		if "replies" in self.__dict__:
			data["replies"]=[x.json(db) for x in self.replies]

		return data

	@lazy
	def award_count(self, kind, v):
		if v and v.poor:
			return 0
		elif self.distinguish_level:
			if SITE_NAME == 'rDrama' and kind in {'glowie', 'tilt',}:
				return 0
			elif SITE_NAME == 'WPD':
				return 0
		return len([x for x in self.awards if x.kind == kind])

	@lazy
	def realurl(self, v):
		url = self.url

		if not url: return ''

		if url.startswith('/'): return SITE_FULL + url

		url = normalize_urls_runtime(url, v)

		if url.startswith("https://old.reddit.com/r/") and '/comments/' in url and "sort=" not in url:
			if "?" in url: url += "&context=9"
			else: url += "?context=8"
			if not v or v.controversial: url += "&sort=controversial"
		elif url.startswith("https://watchpeopledie.tv/videos/"):
			# Semi-temporary fix for self-hosted unproxied video serving
			url = url.replace("https://watchpeopledie.tv/videos/",
							  "https://videos.watchpeopledie.tv/", 1)

		return url

	@lazy
	def total_bet_voted(self, v):
		if "closed" in self.body.lower(): return True
		if v:
			for o in self.options:
				if o.exclusive == 3: return True
				if o.exclusive == 2 and o.voted(v): return True
		return False

	@lazy
	def total_poll_voted(self, v):
		if v:
			for o in self.options:
				if o.voted(v): return True
		return False

	@lazy
	def realbody(self, v, listing=False):
		if self.deleted_utc != 0 and not (v and (v.admin_level >= PERMS['POST_COMMENT_MODERATION'] or v.id == self.author.id)): return "[Deleted by user]"
		if self.is_banned and not (v and v.admin_level >= PERMS['POST_COMMENT_MODERATION']) and not (v and v.id == self.author.id): return ""

		body = self.body_html or ""

		body = censor_slurs(body, v)
		body = normalize_urls_runtime(body, v)

		if self.options:
			curr = [x for x in self.options if x.exclusive and x.voted(v)]
			if curr: curr = " value=post-" + str(curr[0].id)
			else: curr = ''
			body += f'<input class="d-none" id="current-post-{self.id}"{curr}>'
			winner = [x for x in self.options if x.exclusive == 3]

		for o in self.options:
			if o.exclusive > 1:
				body += f'''<div class="custom-control mt-2"><input name="option-{self.id}" autocomplete="off" class="custom-control-input bet" type="radio" id="{o.id}" data-nonce="{g.nonce}" data-onclick="bet_vote(this,'{o.id}')"'''
				if o.voted(v): body += " checked "
				if not (v and v.coins >= POLL_BET_COINS) or self.total_bet_voted(v): body += " disabled "

				body += f'''><label class="custom-control-label" for="{o.id}">{o.body_html}<span class="presult-{self.id}'''
				body += f'"> - <a href="/votes/post/option/{o.id}"><span id="option-{o.id}">{o.upvotes}</span> bets</a>'
				if not self.total_bet_voted(v):
					body += f'''<span class="cost"> (cost of entry: {POLL_BET_COINS} coins)</span>'''
				body += "</label>"

				if o.exclusive == 3:
					body += " - <b>WINNER!</b>"

				if not winner and v and v.admin_level >= PERMS['POST_BETS_DISTRIBUTE']:
					body += f'''<button class="btn btn-primary distribute" data-areyousure="postToastReload(this,'/distribute/{o.id}')" data-nonce="{g.nonce}" data-onclick="areyousure(this)">Declare winner</button>'''
				body += "</div>"
			else:
				input_type = 'radio' if o.exclusive else 'checkbox'
				body += f'<div class="custom-control mt-2"><input type="{input_type}" class="custom-control-input" id="post-{o.id}" name="option-{self.id}"'
				if o.voted(v): body += " checked"

				if v:
					sub = self.sub
					if sub in {'furry','vampire','racist','femboy'} and not v.house.lower().startswith(sub): body += ' disabled '
					body += f''' data-nonce="{g.nonce}" data-onclick="poll_vote_{o.exclusive}('{o.id}', '{self.id}', 'post')"'''
				else:
					body += f''' data-nonce="{g.nonce}" data-onclick="poll_vote_no_v()"'''

				body += f'''><label class="custom-control-label" for="post-{o.id}">{o.body_html}<span class="presult-{self.id}'''
				if not self.total_poll_voted(v): body += ' d-none'
				body += f'"> - <a href="/votes/post/option/{o.id}"><span id="score-post-{o.id}">{o.upvotes}</span> votes</a></label></div>'''


		if not listing and not self.ghost and self.author.show_sig(v):
			body += f'<section id="signature-{self.author.id}" class="user-signature"><hr>{self.author.sig_html}</section>'

		return body

	@lazy
	def plainbody(self, v):
		if self.deleted_utc != 0 and not (v and (v.admin_level >= PERMS['POST_COMMENT_MODERATION'] or v.id == self.author.id)): return "[Deleted by user]"
		if self.is_banned and not (v and v.admin_level >= PERMS['POST_COMMENT_MODERATION']) and not (v and v.id == self.author.id): return ""

		body = self.body
		if not body: return ""

		body = censor_slurs(body, v).replace('<img loading="lazy" data-bs-toggle="tooltip" alt=":marseytrain:" title=":marseytrain:" src="/e/marseytrain.webp">', ':marseytrain:') \
		.replace('<img loading="lazy" data-bs-toggle="tooltip" alt=":marseysleep:" title=":marseysleep:" src="/e/marseysleep.webp">', ':marseysleep:')

		body = normalize_urls_runtime(body, v)

		return body

	@lazy
	def realtitle(self, v):
		title = self.title_html

		title = censor_slurs(title, v)

		return title

	@lazy
	def plaintitle(self, v):
		title = self.title

		title = censor_slurs(title, v).replace('<img loading="lazy" data-bs-toggle="tooltip" alt=":marseytrain:" title=":marseytrain:" src="/e/marseytrain.webp">', ':marseytrain:') \
		.replace('<img loading="lazy" data-bs-toggle="tooltip" alt=":marseysleep:" title=":marseysleep:" src="/e/marseysleep.webp">', ':marseysleep:')

		return title

	@property
	@lazy
	def is_video(self):
		return self.url and any((self.url.lower().split('?')[0].endswith(f'.{x}') for x in VIDEO_FORMATS)) and is_safe_url(self.url)

	@property
	@lazy
	def is_audio(self):
		return self.url and any((self.url.lower().split('?')[0].endswith(f'.{x}') for x in AUDIO_FORMATS)) and is_safe_url(self.url)

	@property
	@lazy
	def is_image(self):
		return self.url and any((self.url.lower().split('?')[0].endswith(f'.{x}') for x in IMAGE_FORMATS)) and is_safe_url(self.url)

	@lazy
	def filtered_flags(self, v):
		return [f for f in self.flags if (v and v.shadowbanned) or not f.user.shadowbanned]

	@lazy
	def active_flags(self, v):
		return len(self.filtered_flags(v))
