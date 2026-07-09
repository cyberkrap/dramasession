import time
from math import floor
from random import randint
from urllib.parse import parse_qs, urlencode, urlparse
from flask import g

from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import relationship, scoped_session
from sqlalchemy.schema import FetchedValue
from sqlalchemy.sql.sqltypes import *

from files.classes import Base
from files.helpers.config.const import *
from files.helpers.lazy import lazy
from files.helpers.regex import *
from files.helpers.sorting_and_time import *


def normalize_urls_runtime(body, v):
	if not v: return body
	if v.reddit != 'old.reddit.com':
		body = reddit_to_vreddit_regex.sub(rf'\1https://{v.reddit}/\2/', body)
	if v.nitter:
		body = body.replace('https://twitter.com/', 'https://nitter.lacontrevoie.fr/')
		body = body.replace('https://nitter.lacontrevoie.fr/i/', 'https://twitter.com/i/')
	if v.imginn:
		body = body.replace('https://instagram.com/p/', 'https://imginn.com/p/')
	return body

class Comment(Base):
	__tablename__ = "comments"

	id = Column(Integer, primary_key=True)
	author_id = Column(Integer, ForeignKey("users.id"))
	parent_submission = Column(Integer, ForeignKey("submissions.id"))
	wall_user_id = Column(Integer, ForeignKey("users.id"))
	created_utc = Column(Integer)
	edited_utc = Column(Integer, default=0)
	is_banned = Column(Boolean, default=False)
	ghost = Column(Boolean, default=False)
	bannedfor = Column(String)
	chuddedfor = Column(String)
	distinguish_level = Column(Integer, default=0)
	deleted_utc = Column(Integer, default=0)
	is_approved = Column(Integer, ForeignKey("users.id"))
	level = Column(Integer, default=1)
	parent_comment_id = Column(Integer, ForeignKey("comments.id"))
	top_comment_id = Column(Integer)
	over_18 = Column(Boolean, default=False)
	is_bot = Column(Boolean, default=False)
	stickied = Column(String)
	stickied_utc = Column(Integer)
	stickied_child_id = Column(Integer)
	sentto = Column(Integer, ForeignKey("users.id"))
	app_id = Column(Integer, ForeignKey("oauth_apps.id"))
	upvotes = Column(Integer, default=1)
	downvotes = Column(Integer, default=0)
	realupvotes = Column(Integer, default=1)
	body = Column(String)
	body_html = Column(String)
	body_ts = Column(TSVECTOR(), server_default=FetchedValue())
	ban_reason = Column(String)
	wordle_result = Column(String)
	treasure_amount = Column(String)
	slots_result = Column(String)
	blackjack_result = Column(String)
	casino_game_id = Column(Integer, ForeignKey("casino_games.id"))

	oauth_app = relationship("OauthApp")
	post = relationship("Submission", back_populates="comments")
	author = relationship("User", primaryjoin="User.id==Comment.author_id")
	senttouser = relationship("User", primaryjoin="User.id==Comment.sentto")
	parent_comment = relationship("Comment", remote_side=[id])
	awards = relationship("AwardRelationship", order_by="AwardRelationship.awarded_utc.desc()", back_populates="comment")
	flags = relationship("CommentFlag", order_by="CommentFlag.created_utc")
	options = relationship("CommentOption", order_by="CommentOption.id")
	casino_game = relationship("CasinoGame")
	wall_user = relationship("User", primaryjoin="User.id==Comment.wall_user_id")

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs:
			kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<{self.__class__.__name__}(id={self.id})>"

	@lazy
	def top_comment(self, db:scoped_session):
		return db.get(Comment, self.top_comment_id)

	@property
	@lazy
	def controversial(self):
		if self.downvotes > 5 and 0.25 < self.upvotes / self.downvotes < 4: return True
		return False

	@property
	@lazy
	def age_string(self):
		notif_utc = self.__dict__.get("notif_utc")

		if notif_utc: timestamp = notif_utc
		elif self.created_utc: timestamp = self.created_utc
		else: return None
		return make_age_string(timestamp)

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
		return f"c_{self.id}"

	@lazy
	def parent(self, db:scoped_session):
		if not self.parent_submission: return None
		if self.level == 1: return self.post
		else: return db.get(Comment, self.parent_comment_id)

	@property
	@lazy
	def parent_fullname(self):
		if self.parent_comment_id: return f"c_{self.parent_comment_id}"
		elif self.parent_submission: return f"p_{self.parent_submission}"

	@lazy
	def replies(self, sort, v, db:scoped_session):
		if self.replies2 != None:
			return self.replies2

		replies = db.query(Comment).filter_by(parent_comment_id=self.id).order_by(Comment.stickied, Comment.stickied_child_id)
		if not self.parent_submission: sort='old'
		return sort_objects(sort, replies, Comment,
			include_shadowbanned=(v and v.can_see_shadowbanned)).all()


	@property
	def replies2(self):
		return self.__dict__.get("replies2")

	@replies2.setter
	def replies2(self, value):
		self.__dict__["replies2"] = value

	@property
	@lazy
	def shortlink(self):
		if self.wall_user_id:
			return f"/@{self.wall_user.username}/wall/comment/{self.id}#context"
		return f"{self.post.shortlink}/{self.id}#context"

	@property
	@lazy
	def permalink(self):
		return f"{SITE_FULL}{self.shortlink}"

	@property
	@lazy
	def log_link(self):
		return f"{SITE_FULL}/transfers/{self.id}"

	@property
	@lazy
	def more_comments(self):
		return f"{self.post.permalink}/{self.id}?context=0#context"

	@property
	@lazy
	def author_name(self):
		if self.ghost: return '👻'
		return self.author.user_name

	@lazy
	def award_count(self, kind, v):
		if v and v.poor and kind.islower(): return 0
		return len([x for x in self.awards if x.kind == kind])

	def json(self, db:scoped_session):
		if self.is_banned:
			data = {'is_banned': True,
					'ban_reason': self.ban_reason,
					'id': self.id,
					'post': self.post.id if self.post else 0,
					'level': self.level,
					'parent': self.parent_fullname
					}
		elif self.deleted_utc:
			data = {'deleted_utc': self.deleted_utc,
					'id': self.id,
					'post': self.post.id if self.post else 0,
					'level': self.level,
					'parent': self.parent_fullname
					}
		else:
			flags = {}
			for f in self.flags: flags[f.user.username] = f.reason

			data = {
				'id': self.id,
				'level': self.level,
				'author_name': self.author_name,
				'body': self.body,
				'body_html': self.body_html,
				'is_bot': self.is_bot,
				'created_utc': self.created_utc,
				'edited_utc': self.edited_utc or 0,
				'is_banned': bool(self.is_banned),
				'deleted_utc': self.deleted_utc,
				'is_nsfw': self.over_18,
				'permalink': f'/comment/{self.id}',
				'stickied': self.stickied,
				'distinguish_level': self.distinguish_level,
				'post_id': self.post.id if self.post else 0,
				'score': self.score,
				'upvotes': self.upvotes,
				'downvotes': self.downvotes,
				'is_bot': self.is_bot,
				'flags': flags,
				'author': '👻' if self.ghost else self.author.json,
				# 'replies': [x.json(db=db) for x in self.replies(sort="old", v=None, db=db)] # WORKER TIMEOUTS ON BUGTHREAD
				}

		if self.level >= 2: data['parent_comment_id'] = self.parent_comment_id

		return data

	@lazy
	def total_poll_voted(self, v):
		if v:
			for o in self.options:
				if o.voted(v): return True
		return False

	@lazy
	def realbody(self, v):
		if self.deleted_utc != 0 and not (v and (v.admin_level >= PERMS['POST_COMMENT_MODERATION'] or v.id == self.author.id)): return "[Deleted by user]"
		if self.is_banned and not (v and v.admin_level >= PERMS['POST_COMMENT_MODERATION']) and not (v and v.id == self.author.id): return ""

		body = self.body_html or ""

		if body:
			body = censor_slurs(body, v)
			body = normalize_urls_runtime(body, v)
			if not v or v.controversial:
				captured = []
				for i in controversial_regex.finditer(body):
					if i.group(1) in captured: continue
					captured.append(i.group(1))

					url = i.group(1)
					p = urlparse(url).query
					p = parse_qs(p, keep_blank_values=True)

					if 'sort' not in p: p['sort'] = ['controversial']

					url_noquery = url.split('?')[0]
					body = body.replace(f'"{url}"', f'"{url_noquery}?{urlencode(p, True)}"')
					body = body.replace(f'>{url}<', f'>{url_noquery}?{urlencode(p, True)}<')

		if self.options:
			curr = [x for x in self.options if x.exclusive and x.voted(v)]
			if curr: curr = " value=comment-" + str(curr[0].id)
			else: curr = ''
			body += f'<input class="d-none" id="current-comment-{self.id}"{curr}>'

		for o in self.options:
			input_type = 'radio' if o.exclusive else 'checkbox'
			body += f'<div class="custom-control"><input type="{input_type}" class="custom-control-input" id="comment-{o.id}" name="option-{self.id}"'
			if o.voted(v): body += " checked"

			if v:
				sub = self.post.sub
				if sub in {'furry','vampire','racist','femboy'} and not v.house.lower().startswith(sub): body += ' disabled '
				body += f''' data-nonce="{g.nonce}" data-onclick="poll_vote_{o.exclusive}('{o.id}', '{self.id}', 'comment')"'''
			else:
				body += f''' data-nonce="{g.nonce}" data-onclick="poll_vote_no_v()"'''

			body += f'''><label class="custom-control-label" for="comment-{o.id}">{o.body_html}<span class="presult-{self.id}'''
			if not self.total_poll_voted(v): body += ' d-none'
			body += f'"> - <a href="/votes/comment/option/{o.id}"><span id="score-comment-{o.id}">{o.upvotes}</span> votes</a></label></div>'''

		if not self.ghost and self.author.show_sig(v):
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

		return body

	@lazy
	def collapse_for_user(self, v, path):
		if v and self.author_id == v.id: return False

		if path == '/admin/removed/comments': return False

		if '?context' in path or f'/{self.id}' in path: return False

		if self.over_18 and not (v and v.over_18) and not (self.post and self.post.over_18): return True

		if self.is_banned: return True

		if self.author.shadowbanned and not (v and v.shadowbanned): return True

		if (self.wordle_result) and (not self.body or len(self.body_html) <= 100) and 9 > self.level > 1: return True

		if v and v.filter_words and self.body and any(x in self.body for x in v.filter_words): return True

		return False

	@property
	@lazy
	def is_op(self): return self.author_id==self.post.author_id

	@lazy
	def filtered_flags(self, v):
		return [f for f in self.flags if (v and v.shadowbanned) or not f.user.shadowbanned]

	@lazy
	def active_flags(self, v):
		return len(self.filtered_flags(v))

	@lazy
	def wordle_html(self, v):
		if not self.wordle_result: return ''

		split_wordle_result = self.wordle_result.split('_')
		wordle_guesses = split_wordle_result[0]
		wordle_status = split_wordle_result[1]
		wordle_answer = split_wordle_result[2]

		body = f"<span id='wordle-{self.id}' class='ml-2'><small>{wordle_guesses}</small>"

		if wordle_status == 'active' and v and v.id == self.author_id:
			body += f'''<input autocomplete="off" id="guess_box" type="text" name="guess" class="form-control" maxsize="4" style="width: 200px;display: initial"placeholder="5-letter guess"><button class="action-{self.id} btn btn-success small" style="text-transform: uppercase; padding: 2px"onclick="handle_action('wordle','{self.id}',document.getElementById('guess_box').value)">Guess</button>'''
		elif wordle_status == 'won':
			body += "<strong class='ml-2'>Correct!</strong>"
		elif wordle_status == 'lost':
			body += f"<strong class='ml-2'>Lost. The answer was: {wordle_answer}</strong>"

		body += '</span>'
		return body

	@property
	@lazy
	def blackjack_html(self):
		if not self.blackjack_result: return ''

		split_result = self.blackjack_result.split('_')
		blackjack_status = split_result[3]
		player_hand = split_result[0].replace('X', '10')
		dealer_hand = split_result[1].split('/')[0] if blackjack_status == 'active' else split_result[1]
		dealer_hand = dealer_hand.replace('X', '10')
		wager = int(split_result[4])
		try: kind = split_result[5]
		except: kind = "coins"
		currency_kind = "Coins" if kind == "coins" else "Marseybux"

		try: is_insured = split_result[6]
		except: is_insured = "0"

		body = f"<span id='blackjack-{self.id}' class='ml-2'><em>{player_hand} vs. {dealer_hand}</em>"

		if blackjack_status == 'push':
			body += f"<strong class='ml-2'>Pushed. Refunded {wager} {currency_kind}.</strong>"
		elif blackjack_status == 'bust':
			body += f"<strong class='ml-2'>Bust. Lost {wager} {currency_kind}.</strong>"
		elif blackjack_status == 'lost':
			body += f"<strong class='ml-2'>Lost {wager} {currency_kind}.</strong>"
		elif blackjack_status == 'won':
			body += f"<strong class='ml-2'>Won {wager} {currency_kind}.</strong>"
		elif blackjack_status == 'blackjack':
			body += f"<strong class='ml-2'>Blackjack! Won {floor(wager * 3/2)} {currency_kind}.</strong>"

		if is_insured == "1":
			body += f" <em class='text-success'>Insured.</em>"

		body += '</span>'
		return body
