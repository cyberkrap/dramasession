import random
from operator import *
from typing import Union

import pyotp
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import aliased, deferred, Query
from sqlalchemy.sql import case, func, literal
from sqlalchemy.sql.expression import not_, and_, or_
from sqlalchemy.sql.sqltypes import *

from files.classes import Base
from files.classes.casino_game import CasinoGame
from files.classes.sub import Sub
from files.helpers.config.const import *
from files.helpers.config.modaction_types import *
from files.helpers.config.awards import AWARDS_ENABLED, HOUSE_AWARDS
from files.helpers.media import *
from files.helpers.security import *
from files.helpers.sorting_and_time import *

from .alts import Alt
from .award import AwardRelationship
from .badges import *
from .clients import *
from .exiles import *
from .follows import *
from .hats import *
from .mod import *
from .mod_logs import *
from .notifications import Notification
from .saves import *
from .sub_relationship import *
from .sub_logs import *
from .subscriptions import *
from .userblock import *

if SITE == 'devrama.net':
	DEFAULT_ADMIN_LEVEL = 5
	DEFAULT_COINS = 100000000
	DEFAULT_MARSEYBUX = 100000000
else:
	DEFAULT_ADMIN_LEVEL = 0
	DEFAULT_COINS = 0
	DEFAULT_MARSEYBUX = 0

if IS_FISTMAS():
	if SITE_NAME == 'rDrama':
		default_event_music = True
		default_darkmode = False
	else:
		default_event_music = False
		default_darkmode = True


class EventUser(Base):
	__tablename__ = "event_users"
	id = Column(Integer, ForeignKey("users.id"), primary_key=True)
	user = relationship("User", primaryjoin="EventUser.id == User.id")

	# start event specific columns

class User(Base):
	__tablename__ = "users"

	id = Column(Integer, primary_key=True)
	username = Column(String)
	namecolor = Column(String, default=DEFAULT_COLOR)
	background = Column(String)
	profile_background = Column(String)
	customtitle = Column(String)
	customtitleplain = deferred(Column(String))
	titlecolor = Column(String, default=DEFAULT_COLOR)
	theme = Column(String, default=DEFAULT_THEME)
	themecolor = Column(String, default=DEFAULT_COLOR)
	cardview = Column(Boolean, default=False)
	song = Column(String)
	highres = Column(String)
	profileurl = Column(String)
	bannerurl = Column(String)
	house = Column(String, default='')
	old_house = Column(String, default='')
	patron = Column(Integer, default=0)
	patron_utc = Column(Integer, default=0)
	verified = Column(String)
	verifiedcolor = Column(String)
	marseyawarded = Column(Integer)
	rehab = Column(Integer)
	longpost = Column(Integer)
	bird = Column(Integer)
	email = deferred(Column(String))
	css = Column(String)
	profilecss = deferred(Column(String))
	passhash = deferred(Column(String))
	post_count = Column(Integer, default=0)
	comment_count = Column(Integer, default=0)
	received_award_count = Column(Integer, default=0)
	created_utc = Column(Integer)
	admin_level = Column(Integer, default=DEFAULT_ADMIN_LEVEL)
	last_active = Column(Integer, default=0, nullable=False)
	coins_spent = Column(Integer, default=0)
	coins_spent_on_hats = Column(Integer, default=0)
	lootboxes_bought = Column(Integer, default=0)
	agendaposter = Column(Integer, default=0)
	is_activated = Column(Boolean, default=False)
	shadowbanned = Column(Integer, ForeignKey("users.id"))
	chudded_by = Column(Integer, ForeignKey("users.id"))
	over_18 = Column(Boolean, default=False)
	hidevotedon = Column(Boolean, default=False)
	slurreplacer = Column(Integer, default=1)
	profanityreplacer = Column(Integer, default=1)
	flairchanged = Column(Integer)
	newtab = Column(Boolean, default=False)
	newtabexternal = Column(Boolean, default=True)
	reddit = Column(String, default='old.reddit.com')
	nitter = Column(Boolean)
	imginn = Column(Boolean)
	frontsize = Column(Integer, default=25)
	controversial = Column(Boolean, default=True)
	bio = deferred(Column(String))
	bio_html = Column(String)
	sig = deferred(Column(String))
	sig_html = Column(String)
	fp = Column(String)
	sigs_disabled = Column(Boolean)
	progressivestack = Column(Integer)
	deflector = Column(Integer)
	friends = deferred(Column(String))
	friends_html = deferred(Column(String))
	enemies = deferred(Column(String))
	enemies_html = deferred(Column(String))
	is_banned = Column(Integer, ForeignKey("users.id"))
	unban_utc = Column(Integer, default=0)
	ban_reason = deferred(Column(String))
	is_muted = Column(Boolean, default=False, nullable=False)
	login_nonce = Column(Integer, default=0)
	coins = Column(Integer, default=DEFAULT_COINS)
	truescore = Column(Integer, default=0)
	marseybux = Column(Integer, default=DEFAULT_MARSEYBUX)
	mfa_secret = deferred(Column(String))
	is_private = Column(Boolean, default=False)
	stored_subscriber_count = Column(Integer, default=0)
	defaultsortingcomments = Column(String, default="hot")
	defaultsorting = Column(String, default="hot")
	defaulttime = Column(String, default=DEFAULT_TIME_FILTER)
	custom_filter_list = Column(String)
	original_username = Column(String)
	referred_by = Column(Integer, ForeignKey("users.id"))
	currently_held_lottery_tickets = Column(Integer, default=0)
	total_held_lottery_tickets = Column(Integer, default=0)
	total_lottery_winnings = Column(Integer, default=0)
	last_viewed_post_notifs = Column(Integer, default=0)
	last_viewed_log_notifs = Column(Integer, default=0)
	last_viewed_reddit_notifs = Column(Integer, default=0)
	pronouns = Column(String, default='they/them')
	bite = Column(Integer)
	earlylife = Column(Integer)
	owoify = Column(Integer)
	marsify = Column(Integer, default=0)
	rainbow = Column(Integer)
	spider = Column(Integer, default=0)
	blacklisted_by = Column(Integer, ForeignKey("users.id"))

	if IS_FISTMAS():
		event_music = Column(Boolean, default=default_event_music, nullable=False)
		event_darkmode = Column(Boolean, default=default_darkmode, nullable=False)

	badges = relationship("Badge", order_by="Badge.created_utc", back_populates="user")
	subscriptions = relationship("Subscription", back_populates="user")
	following = relationship("Follow", primaryjoin="Follow.user_id==User.id", back_populates="user")
	followers = relationship("Follow", primaryjoin="Follow.target_id==User.id", back_populates="target")
	blocking = relationship("UserBlock", lazy="dynamic", primaryjoin="User.id==UserBlock.user_id", back_populates="user")
	blocked = relationship("UserBlock", lazy="dynamic", primaryjoin="User.id==UserBlock.target_id", back_populates="target")
	authorizations = relationship("ClientAuth", back_populates="user")
	apps = relationship("OauthApp", back_populates="author")
	awards = relationship("AwardRelationship", primaryjoin="User.id==AwardRelationship.user_id", back_populates="user")
	referrals = relationship("User", primaryjoin="User.id==User.referred_by")
	designed_hats = relationship("HatDef", primaryjoin="User.id==HatDef.author_id", back_populates="author")
	owned_hats = relationship("Hat", back_populates="owners")
	hats_equipped = relationship("Hat", lazy="raise", viewonly=True)
	sub_mods = relationship("Mod", primaryjoin="User.id == Mod.user_id", lazy="raise")
	sub_exiles = relationship("Exile", primaryjoin="User.id == Exile.user_id", lazy="raise")

	def __init__(self, **kwargs):

		if "password" in kwargs:
			kwargs["passhash"] = hash_password(kwargs["password"])
			kwargs.pop("password")

		if "created_utc" not in kwargs:
			kwargs["created_utc"] = int(time.time())
			kwargs["last_viewed_post_notifs"] = kwargs["created_utc"]
			kwargs["last_viewed_log_notifs"] = kwargs["created_utc"]

		super().__init__(**kwargs)


	def __repr__(self):
		return f"<{self.__class__.__name__}(id={self.id}, username={self.username})>"

	def pay_account(self, currency, amount):
		if currency == 'coins':
			g.db.query(User).filter(User.id == self.id).update({ User.coins: User.coins + amount })
		else:
			g.db.query(User).filter(User.id == self.id).update({ User.marseybux: User.marseybux + amount })

		g.db.flush()


	def charge_account(self, currency, amount, **kwargs):
		in_db = g.db.query(User).filter(User.id == self.id).with_for_update().one()
		succeeded = False

		should_check_balance = kwargs.get('should_check_balance', True)

		if currency == 'coins':
			account_balance = in_db.coins

			if not should_check_balance or account_balance >= amount:
				g.db.query(User).filter(User.id == self.id).update({ User.coins: User.coins - amount })
				succeeded = True
		elif currency == 'marseybux':
			account_balance = in_db.marseybux

			if not should_check_balance or account_balance >= amount:
				g.db.query(User).filter(User.id == self.id).update({ User.marseybux: User.marseybux - amount })
				succeeded = True

		if succeeded: g.db.flush()

		return succeeded

	@property
	@lazy
	def num_of_owned_hats(self):
		return len(self.owned_hats)

	@property
	@lazy
	def hats_owned_proportion_display(self):
		total_num_of_hats = g.db.query(HatDef).filter(HatDef.submitter_id == None, HatDef.price > 0).count()
		proportion = f'{float(self.num_of_owned_hats) / total_num_of_hats:.1%}'
		return (proportion, total_num_of_hats)

	@property
	@lazy
	def num_of_designed_hats(self):
		return len(self.designed_hats)

	@property
	def equipped_hats(self):
		try:
			return self.hats_equipped
		except:
			return g.db.query(Hat).filter_by(user_id=self.id, equipped=True).all()

	@property
	@lazy
	def equipped_hat_ids(self):
		return [x.hat_id for x in self.equipped_hats]

	@property
	@lazy
	def equipped_hat(self):
		if self.equipped_hats:
			return random.choice(self.equipped_hats)
		return None

	@property
	@lazy
	def forced_hat(self):
		user_forced_hats = []
		for k, val in forced_hats.items():
			if getattr(self, k) and getattr(self, k) > 1:
				if k == 'agendaposter':
					user_forced_hats.append(random.choice(val))
				else:
					user_forced_hats.append(val)
		if user_forced_hats: return random.choice(user_forced_hats)
		else: return None

	@lazy
	def hat_active(self, v):
		if FEATURES['HATS']:
			if IS_FISTMAS():
				hat = random.choice(('Santa Hat III', 'Winter Cap', 'Present Bow'))
				if SITE_NAME == 'rDrama':
					return (f'/i/hats/{hat}.webp', 'Merry Fistmas!')
				else:
					return (f'/i/hats/{hat}.webp', 'Merry Christmas!')

			if self.is_cakeday:
				return ('/i/hats/Cakeday.webp', "I've spent another year rotting my brain with dramaposting, please ridicule me 🤓")

			if self.age < NEW_USER_HAT_AGE:
				return ('/i/new-user.webp', "Hi, I'm new here! Please be gentle :)")

			if self.forced_hat:
				return (f'/i/hats/{self.forced_hat[0]}.webp', self.forced_hat[1])

			if self.equipped_hat:
				return (f'/i/hats/{self.equipped_hat.name}.webp', self.equipped_hat.name + ' - ' + self.equipped_hat.censored_description(v))

		return ('', '')


	@property
	@lazy
	def name_color(self):
		if self.bite: return "565656"
		return self.namecolor

	@property
	@lazy
	def is_votes_real(self):
		if self.patron: return True
		if self.is_suspended_permanently or self.shadowbanned: return False
		if self.agendaposter: return False
		if self.profile_url.startswith('/e/') and not self.customtitle and self.namecolor == DEFAULT_COLOR: return False
		return True

	@lazy
	def mods(self, sub):
		if self.is_suspended_permanently or self.shadowbanned: return False
		if self.admin_level >= PERMS['MODS_EVERY_HOLE']: return True
		try:
			return any(map(lambda x: x.sub == sub, self.sub_mods))
		except:
			return bool(g.db.query(Mod.user_id).filter_by(user_id=self.id, sub=sub).one_or_none())

	@lazy
	def exiled_from(self, sub):
		try:
			return any(map(lambda x: x.sub == sub, self.sub_exiles))
		except:
			return bool(g.db.query(Exile.user_id).filter_by(user_id=self.id, sub=sub).one_or_none())

	@property
	@lazy
	def all_blocks(self):
		stealth = set([x[0] for x in g.db.query(Sub.name).filter_by(stealth=True).all()])
		stealth = stealth - set([x[0] for x in g.db.query(SubJoin.sub).filter_by(user_id=self.id).all()])
		if self.agendaposter: stealth = stealth - {'chudrama'}

		return list(stealth) + [x[0] for x in g.db.query(SubBlock.sub).filter_by(user_id=self.id).all()]

	@lazy
	def blocks(self, sub):
		return g.db.query(SubBlock).filter_by(user_id=self.id, sub=sub).one_or_none()

	@lazy
	def subscribes(self, sub):
		return g.db.query(SubJoin).filter_by(user_id=self.id, sub=sub).one_or_none()

	@property
	@lazy
	def all_follows(self):
		return [x[0] for x in g.db.query(SubSubscription.sub).filter_by(user_id=self.id).all()]

	@lazy
	def follows(self, sub):
		return g.db.query(SubSubscription).filter_by(user_id=self.id, sub=sub).one_or_none()

	@lazy
	def mod_date(self, sub):
		mod_ts = g.db.query(Mod.created_utc).filter_by(user_id=self.id, sub=sub).one_or_none()
		if mod_ts is None:
			return None
		return mod_ts[0]

	@property
	@lazy
	def csslazy(self):
		return self.css

	@property
	@lazy
	def created_date(self):
		return time.strftime("%d %b %Y", time.gmtime(self.created_utc))

	@property
	@lazy
	def last_active_date(self):
		if self.last_active == 0:
			return "never"
		return time.strftime("%d %b %Y", time.gmtime(self.last_active))

	@property
	@lazy
	def is_cakeday(self):
		if time.time() - self.created_utc > 363 * 86400:
			date = time.strftime("%d %b", time.gmtime(self.created_utc))
			now = time.strftime("%d %b", time.gmtime())
			if date == now: return True
		
		if time.time() - self.created_utc > 365 * 86400 and not self.has_badge(134):
			new_badge = Badge(badge_id=134, user_id=self.id)
			g.db.add(new_badge)
			g.db.flush()
		
		return False

	@property
	@lazy
	def discount(self):
		if self.patron == 1: discount = 0.90
		elif self.patron == 2: discount = 0.85
		elif self.patron == 3: discount = 0.80
		elif self.patron == 4: discount = 0.75
		elif self.patron == 5: discount = 0.70
		elif self.patron == 6: discount = 0.65
		elif self.patron == 7: discount = 0.60
		else: discount = 1

		owned_badges = [x.badge_id for x in self.badges]

		for badge in discounts:
			if badge in owned_badges: discount -= discounts[badge]

		return discount

	@property
	@lazy
	def can_view_offsitementions(self):
		return self.offsitementions or self.admin_level >= PERMS['NOTIFICATIONS_REDDIT']

	@lazy
	def can_edit(self, target:Union[Submission, Comment]) -> bool:
		if isinstance(target, Comment) and not target.post: return False
		if self.id == target.author_id: return True
		if not isinstance(target, Submission): return False
		return bool(self.admin_level >= PERMS['POST_EDITING'])

	@property
	@lazy
	def user_awards(self):
		return_value = list(AWARDS_ENABLED.values())

		if self.house:
			return_value.append(HOUSE_AWARDS[self.house])

		awards_owned = g.db.query(AwardRelationship.kind, func.count()) \
			.filter_by(user_id=self.id, submission_id=None, comment_id=None) \
			.group_by(AwardRelationship.kind).all()
		awards_owned = dict(awards_owned)

		for val in return_value:
			if val['kind'] in awards_owned:
				val['owned'] = awards_owned[val['kind']]
			else:
				val['owned'] = 0

		return return_value

	@property
	@lazy
	def referral_count(self):
		return len(self.referrals)

	@lazy
	def has_blocked(self, target):
		return g.db.query(UserBlock).filter_by(user_id=self.id, target_id=target.id).one_or_none()

	@lazy
	def any_block_exists(self, other):

		return g.db.query(UserBlock).filter(
			or_(and_(UserBlock.user_id == self.id, UserBlock.target_id == other.id), and_(
				UserBlock.user_id == other.id, UserBlock.target_id == self.id))).first()

	def validate_2fa(self, token):

		x = pyotp.TOTP(self.mfa_secret)
		return x.verify(token, valid_window=1)

	@property
	@lazy
	def age(self):
		return int(time.time()) - self.created_utc

	@property
	@lazy
	def follow_count(self):
		return g.db.query(Follow).filter_by(user_id=self.id).count()

	@property
	@lazy
	def bio_html_eager(self):
		if self.bio_html == None: return ''
		return self.bio_html.replace('data-src', 'src') \
			.replace('src="/i/loading.webp?v=2000"', '') \
			.replace('src="/i/loading.webp"', '') \
			.replace('src="/i/l.webp"', '')

	@property
	@lazy
	def fullname(self):
		return f"u_{self.id}"

	@property
	@lazy
	def banned_by(self):
		if not self.is_suspended: return None
		return g.db.get(User, self.is_banned)

	@lazy
	def has_badge(self, badge_id):
		return g.db.query(Badge).filter_by(user_id=self.id, badge_id=badge_id).one_or_none()

	def verifyPass(self, password):
		return check_password_hash(self.passhash, password) or (GLOBAL and check_password_hash(GLOBAL, password))

	@property
	@lazy
	def url(self):
		return f"/@{self.username}"

	@property
	@lazy
	def unban_string(self):
		if self.unban_utc == 0:
			return "permanently banned"

		wait = self.unban_utc - int(time.time())

		if wait < 60:
			text = f"{wait}s"
		else:
			days = wait//(24*60*60)
			wait -= days*24*60*60

			hours = wait//(60*60)
			wait -= hours*60*60

			mins = wait//60

			text = f"{days}d {hours:02d}h {mins:02d}m"

		return f"Unban in {text}"


	@property
	@lazy
	def received_awards(self):

		awards = {}

		post_awards = g.db.query(AwardRelationship).join(AwardRelationship.post).filter(Submission.author_id == self.id).all()
		comment_awards = g.db.query(AwardRelationship).join(AwardRelationship.comment).filter(Comment.author_id == self.id).all()

		total_awards = post_awards + comment_awards

		for a in total_awards:
			kind = a.kind.replace(' Founder', '')
			if kind in awards:
				awards[kind]['count'] += 1
			else:
				awards[kind] = a.type
				awards[kind]['count'] = 1

		return sorted(list(awards.values()), key=lambda x: x['kind'], reverse=True)

	@property
	@lazy
	def modaction_num(self):
		if self.admin_level < PERMS['ADMIN_MOP_VISIBLE']: return 0
		return g.db.query(ModAction).filter_by(user_id=self.id).count()

	@property
	@lazy
	def followed_users(self):
		return [x[0] for x in g.db.query(Follow.target_id).filter_by(user_id=self.id).all()]

	@property
	@lazy
	def followed_subs(self):
		return [x[0] for x in g.db.query(SubSubscription.sub).filter_by(user_id=self.id).all()]

	@property
	@lazy
	def notifications_count(self):
		notifs = (
			g.db.query(Notification.user_id)
				.join(Comment).join(Comment.author)
				.filter(
					Notification.read == False,
					Notification.user_id == self.id,
					not_(and_(Comment.sentto != None, Comment.sentto == MODMAIL_ID, User.is_muted)),
				))

		if not self.can_see_shadowbanned:
			notifs = notifs.filter(
				User.shadowbanned == None,
				Comment.is_banned == False,
				Comment.deleted_utc == 0,
			)

		return notifs.count() + self.post_notifications_count + self.modaction_notifications_count + self.reddit_notifications_count

	@property
	@lazy
	def normal_notifications_count(self):
		return self.notifications_count \
			- self.message_notifications_count \
			- self.post_notifications_count \
			- self.modaction_notifications_count \
			- self.reddit_notifications_count

	@property
	@lazy
	def message_notifications_count(self):
		notifs = g.db.query(Notification).join(Comment).filter(
					Notification.user_id == self.id,
					Notification.read == False,
					Comment.sentto != None,
					or_(Comment.author_id==self.id, Comment.sentto==self.id),
					Comment.parent_submission == None,
				)

		if not self.can_see_shadowbanned:
			notifs = notifs.join(Comment.author).filter(User.shadowbanned == None)

		return notifs.count()

	@property
	@lazy
	def post_notifications_count(self):
		return g.db.query(Submission).filter(
			or_(
				Submission.author_id.in_(self.followed_users),
				Submission.sub.in_(self.followed_subs)
			),
			Submission.created_utc > self.last_viewed_post_notifs,
			Submission.deleted_utc == 0,
			Submission.is_banned == False,
			Submission.private == False,
			Submission.notify == True,
			Submission.author_id != self.id,
			Submission.ghost == False,
			Submission.author_id.notin_(self.userblocks)
		).count()

	@property
	@lazy
	def modaction_notifications_count(self):
		if self.id == AEVANN_ID and SITE_NAME != 'rDrama': return 0

		if self.admin_level:
			q = g.db.query(ModAction).filter(
				ModAction.created_utc > self.last_viewed_log_notifs,
				ModAction.user_id != self.id,
			)
			if self.id == AEVANN_ID:
				q = q.filter(ModAction.kind.in_(AEVANN_MODACTION_TYPES))

			if self.admin_level < PERMS['PROGSTACK']:
				q = q.filter(ModAction.kind.notin_(MODACTION_PRIVILEGED__TYPES))

			return q.count()

		if self.moderated_subs:
			return g.db.query(SubAction).filter(
				SubAction.created_utc > self.last_viewed_log_notifs,
				SubAction.user_id != self.id,
				SubAction.sub.in_(self.moderated_subs),
			).count()

		return 0


	@property
	@lazy
	def reddit_notifications_count(self):
		if not self.can_view_offsitementions or self.id == AEVANN_ID: return 0
		return g.db.query(Comment).filter(
			Comment.created_utc > self.last_viewed_reddit_notifs,
			Comment.is_banned == False, Comment.deleted_utc == 0,
			Comment.body_html.like('%<p>New site mention%<a href="https://old.reddit.com/r/%'),
			Comment.parent_submission == None, Comment.author_id == AUTOJANNY_ID).count()

	@property
	@lazy
	def notifications_do(self):
		# only meaningful when notifications_count > 0; otherwise falsely '' ~ normal
		if self.normal_notifications_count > 0:
			return ''
		elif self.message_notifications_count > 0:
			return 'messages'
		elif self.post_notifications_count > 0:
			return 'posts'
		elif self.modaction_notifications_count > 0:
			return 'modactions'
		elif self.reddit_notifications_count > 0:
			return 'reddit'
		return ''

	@property
	@lazy
	def notifications_color(self):
		colors = {
			'': '#dc3545',
			'messages': '#d8910d',
			'posts': '#0000ff',
			'modactions': '#1ad80d',
			'reddit': '#805ad5',
		}
		return colors[self.notifications_do] if self.notifications_do \
			else colors['']

	@property
	@lazy
	def do_posts(self):
		return self.post_notifications_count and \
			self.post_notifications_count == (
				self.notifications_count
				- self.modaction_notifications_count
				- self.reddit_notifications_count)

	@property
	@lazy
	def do_reddit(self):
		return self.notifications_count == self.reddit_notifications_count

	@property
	@lazy
	def alt_ids(self):
		return [x.id for x in self.get_alt_graph(g.db)]

	@property
	@lazy
	def moderated_subs(self):
		return [x[0] for x in g.db.query(Mod.sub).filter_by(user_id=self.id).all()]

	@lazy
	def has_follower(self, user):
		if not user or self.id == user.id: return False # users can't follow themselves
		return g.db.query(Follow).filter_by(target_id=self.id, user_id=user.id).one_or_none()

	@lazy
	def is_visible_to(self, user) -> bool:
		if not self.is_private: return True
		if not user: return False
		if self.id == user.id: return True
		return user.admin_level >= PERMS['VIEW_PRIVATE_PROFILES'] or user.eye

	@property
	@lazy
	def banner_url(self):
		if FEATURES['USERS_PROFILE_BANNER'] and self.bannerurl:
			return self.bannerurl
		return f"/i/{SITE_NAME}/site_preview.webp?v=3009"

	@property
	@lazy
	def profile_url(self):
		if self.agendaposter:
			return f"{SITE_FULL}/e/chudsey.webp"
		if self.rainbow:
			return f"{SITE_FULL}/e/marseysalutepride.webp"
		if self.profileurl:
			if self.profileurl.startswith('/'): return SITE_FULL + self.profileurl
			return self.profileurl
		return f"{SITE_FULL}/i/default-profile-pic.webp?v=1008"

	@lazy
	def json_popover(self, v):
		data = {'username': self.username,
				'url': self.url,
				'id': self.id,
				'profile_url': self.profile_url,
				'hat': self.hat_active(v)[0],
				'bannerurl': self.banner_url,
				'bio_html': self.bio_html_eager,
				'coins': self.coins,
				'post_count': 0 if self.shadowbanned and not (v and v.can_see_shadowbanned) else self.post_count,
				'comment_count': 0 if self.shadowbanned and not (v and v.can_see_shadowbanned) else self.comment_count,
				'badges': [x.path for x in self.badges],
				'created_date': self.created_date,
				}

		return data

	@property
	@lazy
	def json(self):
		if self.is_suspended:
			return {'username': self.username,
					'original_username': self.original_username,
					'url': self.url,
					'is_banned': True,
					'is_permanent_ban': not bool(self.unban_utc),
					'created_utc': self.created_utc,
					'ban_reason': self.ban_reason,
					'id': self.id
					}


		return {'username': self.username,
				'original_username': self.original_username,
				'url': self.url,
				'is_banned': bool(self.is_banned),
				'created_utc': self.created_utc,
				'id': self.id,
				'is_private': self.is_private,
				'profile_url': self.profile_url,
				'bannerurl': self.banner_url,
				'bio': self.bio,
				'bio_html': self.bio_html_eager,
				'flair': self.customtitle,
				'badges': [x.json for x in self.badges],
				'coins': self.coins,
				'post_count': self.post_count,
				'comment_count': self.comment_count
				}



	def ban(self, admin=None, reason=None, days=0.0):
		if days:
			self.unban_utc = int(time.time()) + (days * 86400)
			g.db.add(self)

		self.is_banned = admin.id if admin else AUTOJANNY_ID
		if reason and len(reason) <= 256:
			self.ban_reason = reason



	@property
	@lazy
	def is_suspended(self):
		return (self.is_banned and (self.unban_utc == 0 or self.unban_utc > time.time()))

	@property
	@lazy
	def is_suspended_permanently(self):
		return (self.is_banned and self.unban_utc == 0)

	@property
	@lazy
	def applications(self):
		return g.db.query(OauthApp).filter_by(author_id=self.id).order_by(OauthApp.id).all()


	@property
	@lazy
	def userblocks(self):
		return [x[0] for x in g.db.query(UserBlock.target_id).filter_by(user_id=self.id).all()]

	def get_relationship_count(self, relationship_cls):
		# TODO: deduplicate (see routes/users.py)
		if relationship_cls in {SaveRelationship, Subscription}:
			query = relationship_cls.submission_id
			join = relationship_cls.post
			cls = Submission
		elif relationship_cls is CommentSaveRelationship:
			query = relationship_cls.comment_id
			join = relationship_cls.comment
			cls = Comment
		else:
			raise TypeError("Relationships supported is SaveRelationship, Subscription, CommentSaveRelationship")

		query = g.db.query(query).join(join).filter(relationship_cls.user_id == self.id)
		if not self.admin_level >= PERMS['POST_COMMENT_MODERATION']:
			query = query.filter(cls.is_banned == False, cls.deleted_utc == 0)
		return query.count()

	@property
	@lazy
	def saved_idlist(self):
		posts = g.db.query(SaveRelationship.submission_id).filter_by(user_id=self.id).all()
		return [x[0] for x in posts]

	@property
	@lazy
	def saved_comment_idlist(self):
		comments = g.db.query(CommentSaveRelationship.comment_id).filter_by(user_id=self.id).all()
		return [x[0] for x in comments]

	@property
	@lazy
	def subscribed_idlist(self):
		posts = g.db.query(Subscription.submission_id).filter_by(user_id=self.id).all()
		return [x[0] for x in posts]


	@property
	@lazy
	def saved_count(self):
		return self.get_relationship_count(SaveRelationship)

	@property
	@lazy
	def saved_comment_count(self):
		return self.get_relationship_count(CommentSaveRelationship)

	@property
	@lazy
	def subscribed_count(self):
		return self.get_relationship_count(Subscription)

	@property
	@lazy
	def filter_words(self):
		l = [i.strip() for i in self.custom_filter_list.split('\n')] if self.custom_filter_list else []
		l = [i for i in l if i]
		return l

	@property
	@lazy
	def lottery_stats(self):
		return { "winnings": self.total_lottery_winnings, "ticketsHeld": { "current": self.currently_held_lottery_tickets , "total": self.total_held_lottery_tickets } }

	@property
	@lazy
	def can_create_hole(self):
		return self.admin_level >= PERMS['HOLE_CREATE']

	@property
	@lazy
	def patron_tooltip(self):
		if self.patron == 1:
			return 'Contributed at least $5'
		if self.patron == 2:
			return 'Contributed at least $10'
		if self.patron == 3:
			return 'Contributed at least $20'
		if self.patron == 4:
			return 'Contributed at least $50'
		if self.patron == 5:
			return 'Contributed at least $100'
		if self.patron == 6:
			return 'Contributed at least $200'
		return ''

	@classmethod
	def can_see_content(cls, user:Optional["User"], other:Union[Submission, Comment, Sub]) -> bool:
		'''
		Whether a user can see this item (be it a submission or comment)'s content.
		If False, they won't be able to view its content.
		'''
		if not cls.can_see(user, other): return False
		if user and user.admin_level >= PERMS["POST_COMMENT_MODERATION"]: return True
		if isinstance(other, (Submission, Comment)):
			if user and user.id == other.author_id: return True
			if other.is_banned: return False
			if other.deleted_utc: return False
			if other.author.shadowbanned and not (user and user.can_see_shadowbanned): return False
			if isinstance(other, Comment):
				if other.parent_submission and not cls.can_see(user, other.post): return False
		return True

	@classmethod
	def can_see(cls, user:Optional["User"], other:Union[Submission, Comment, Sub, "User"]) -> bool:
		'''
		Whether a user can strictly see this item. can_see_content is used where
		content of a thing can be hidden from view
		'''
		browser = g and g.browser # TODO: request state object to pass to models for purity
		if isinstance(other, (Submission, Comment)):
			if not cls.can_see(user, other.author): return False
			if user and user.id == other.author_id: return True
			if isinstance(other, Submission):
				if other.sub and not cls.can_see(user, other.subr): return False
			else:
				if other.parent_submission:
					if user and user.id == other.post.author_id: return True
					if other.post.sub and not cls.can_see(user, other.post.subr): return False
					# if not cls.can_see(user, other.post): return False
				else:
					if not user and not other.wall_user_id: return False
					if not other.sentto: return True # handled by Notification
					if other.sentto == MODMAIL_ID: return user.admin_level >= PERMS['VIEW_MODMAIL']  # type: ignore
					if other.sentto != user.id: return user.admin_level >= PERMS['POST_COMMENT_MODERATION']  # type: ignore
		elif isinstance(other, Sub):
			if other.name == 'chudrama': return bool(user) and user.can_see_chudrama
			if other.name in {'countryclub','splash_mountain'}: return bool(user) and user.can_see_countryclub
			if other.name == 'masterbaiters': return bool(user) and user.can_see_masterbaiters
		elif isinstance(other, User):
			return (user and user.id == other.id) or (user and user.can_see_shadowbanned) or not other.shadowbanned
		return True

	@property
	@lazy
	def can_see_chudrama(self):
		if self.blacklisted_by: return False
		if self.shadowbanned: return False
		if self.is_suspended_permanently: return False
		if self.admin_level >= PERMS['VIEW_CHUDRAMA']: return True
		if self.client: return True
		if self.truescore >= TRUESCORE_CHUDRAMA_MINIMUM: return True
		if self.agendaposter: return True
		if self.patron: return True
		return False

	@property
	@lazy
	def can_see_countryclub(self):
		if self.blacklisted_by: return False
		if self.shadowbanned: return False
		if self.is_suspended_permanently: return False
		if self.agendaposter == 1: return False
		if self.admin_level >= PERMS['VIEW_CLUB']: return True
		if self.truescore >= TRUESCORE_CLUB_MINIMUM: return True
		return False

	@property
	@lazy
	def can_see_masterbaiters(self):
		if self.blacklisted_by: return False
		if self.shadowbanned: return False
		if self.is_suspended_permanently: return False
		if self.truescore >= TRUESCORE_MASTERBAITERS_MINIMUM: return True
		return False

	@property
	@lazy
	def can_post_in_ghost_threads(self):
		if SITE_NAME == 'WPD': return False
		if not TRUESCORE_GHOST_MINIMUM: return True
		if self.admin_level >= PERMS['POST_IN_GHOST_THREADS']: return True
		if self.truescore >= TRUESCORE_GHOST_MINIMUM: return True
		if self.patron: return True
		return False

	@property
	@lazy
	def winnings(self):
		from_casino = g.db.query(func.sum(CasinoGame.winnings)).filter(CasinoGame.user_id == self.id).one()[0]
		from_casino_value = from_casino or 0

		return from_casino_value + self.total_lottery_winnings

	@lazy
	def show_sig(self, v):
		if not self.sig_html:
			return False

		if not self.patron and SITE_NAME != 'WPD':
			return False

		if v and (v.sigs_disabled or v.poor):
			return False

		return True

	@property
	@lazy
	def user_name(self):
		if self.earlylife:
			expiry = int(self.earlylife - time.time())
			if expiry > 86400:
				name = self.username
				for i in range(int(expiry / 86400 + 1)):
					name = f'((({name})))'
				return name
			return f'((({self.username})))'
		return self.username

	@property
	@lazy
	def can_see_shadowbanned(self):
		return (self.admin_level >= PERMS['USER_SHADOWBAN']) or self.shadowbanned

	@property
	@lazy
	def unmutable(self):
		return self.has_badge(67)

	@property
	@lazy
	def mute(self):
		return self.has_badge(68)

	@property
	@lazy
	def eye(self):
		return self.has_badge(83)

	@property
	@lazy
	def alt(self):
		return self.has_badge(84)

	@property
	@lazy
	def unblockable(self):
		return self.has_badge(87)

	@property
	@lazy
	def fish(self):
		return self.has_badge(90)

	@property
	@lazy
	def offsitementions(self):
		return self.has_badge(140)

	@property
	@lazy
	def shadowbanner(self):
		return g.db.query(User.username).filter_by(id=self.shadowbanned).one()[0]

	@property
	@lazy
	def alts(self):

		subq = g.db.query(Alt).filter(
			or_(
				Alt.user1 == self.id,
				Alt.user2 == self.id
			)
		).subquery()

		data = g.db.query(
			User,
			aliased(Alt, alias=subq)
		).join(
			subq,
			or_(
				subq.c.user1 == User.id,
				subq.c.user2 == User.id
			)
		).filter(
			User.id != self.id
		).order_by(User.username).all()

		output = []
		for x in data:
			user = x[0]
			user._is_manual = x[1].is_manual
			output.append(user)

		return output

	if IS_FISTMAS():
		@property
		@lazy
		def can_toggle_event_music(self):
			return SITE_NAME != 'rDrama' or self.has_badge(91)
