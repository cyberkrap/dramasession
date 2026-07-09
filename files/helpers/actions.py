import random
import time
from typing import Type
from urllib.parse import quote

import gevent
import requests
from flask import g
from files.classes.flags import Flag
from files.classes.mod_logs import ModAction
from files.classes.notifications import Notification
from files.classes.polls import CommentOption, SubmissionOption

from files.helpers.alerts import send_repeatable_notification
from files.helpers.config.const import *
from files.helpers.const_stateful import *
from files.helpers.get import *
from files.helpers.logging import log_file
from files.helpers.sanitize import *
from files.helpers.settings import get_setting
from files.helpers.slots import check_slots_command

post_target_type = Union[Submission, User]

def _archiveorg(url):
	headers = {'User-Agent': 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'}
	try:
		requests.get(f'https://web.archive.org/save/{url}',
			headers=headers, timeout=10, proxies=proxies)
	except: pass
	try:
		requests.post('https://ghostarchive.org/archive2', data={"archive": url},
			headers=headers, timeout=10, proxies=proxies)
	except: pass


def archive_url(url):
	gevent.spawn(_archiveorg, url)
	if url.startswith('https://twitter.com/'):
		url = url.replace('https://twitter.com/', 'https://nitter.lacontrevoie.fr/')
		gevent.spawn(_archiveorg, url)
	if url.startswith('https://instagram.com/'):
		url = url.replace('https://instagram.com/p/', 'https://imginn.com/p/')
		gevent.spawn(_archiveorg, url)

def execute_snappy(post:Submission, v:User):
	ghost = post.ghost

	snappy = get_account(SNAPPY_ID)

	if post.sub == 'dankchristianmemes' or post.sub == 'truth':
		body = random.choice(christian_emojis)
	elif v.id == CARP_ID:
		if random.random() < 0.02: body = "i love you carp"
		elif random.random() < 0.02: body = "![](/images/16614707883108485.webp)"
		else: body = ":#marseyfuckoffcarp:"
	elif v.id == LAWLZ_ID:
		if random.random() < 0.5: body = "wow, this lawlzpost sucks!"
		else: body = "wow, a good lawlzpost for once!"
	elif post.sub == 'masterbaiters' and random.random() < 0.33:
		body = "Can you people come up with any ideas that don't involve committing federal crimes"
	else:
		if SNAPPY_MARSEYS and SNAPPY_QUOTES:
			if IS_FISTMAS() or random.random() > 0.5:
				SNAPPY_CHOICES = SNAPPY_QUOTES
			else:
				SNAPPY_CHOICES = SNAPPY_MARSEYS
		elif SNAPPY_MARSEYS: SNAPPY_CHOICES = SNAPPY_MARSEYS
		elif SNAPPY_QUOTES: SNAPPY_CHOICES = SNAPPY_QUOTES
		else: SNAPPY_CHOICES = [""]

		body = random.choice(SNAPPY_CHOICES).strip()
		if body.startswith('▼') or body.startswith(':#marseydownvote'):
			if body.startswith('▼'): body = body[1:]
			vote = Vote(user_id=SNAPPY_ID,
						vote_type=-1,
						submission_id=post.id,
						real = True
						)
			g.db.add(vote)
			post.downvotes += 1
			if body.startswith('OP is a Trump supporter'):
				flag = Flag(post_id=post.id, user_id=SNAPPY_ID, reason='Trump supporter')
				g.db.add(flag)
			elif body.startswith('You had your chance. Downvoted and reported'):
				flag = Flag(post_id=post.id, user_id=SNAPPY_ID, reason='Retard')
				g.db.add(flag)
		elif body.startswith('▲') or body.startswith(':#marseyupvote'):
			if body.startswith('▲'): body = body[1:]
			vote = Vote(user_id=SNAPPY_ID,
						vote_type=1,
						submission_id=post.id,
						real = True
						)
			g.db.add(vote)
			post.upvotes += 1
		elif body == '!slots':
			body = f'!slots{snappy.coins}'
		elif body.startswith(':#marseyghost'):
			ghost = True

	body += "\n\n"

	if post.url and not post.url.startswith('/') and not post.url.startswith(SITE_FULL) and not post.url.startswith(BAN_EVASION_FULL):
		if post.url.startswith('https://old.reddit.com/r/'):
			rev = post.url.replace('https://old.reddit.com/', '')
			rev = f"* [unddit.com](https://unddit.com/{rev})\n"
		elif post.url.startswith("https://old.reddit.com/u/"):
			rev = post.url.replace('https://old.reddit.com/u/', '')
			rev = f"* [camas.unddit.com](https://camas.unddit.com/reddit-search/#\u007b\"author\":\"{rev}\",\"resultSize\":100\u007d)\n"
		else: rev = ''

		body += f"Snapshots:\n\n{rev}* [archive.org](https://web.archive.org/{post.url})\n* [ghostarchive.org](https://ghostarchive.org/search?term={quote(post.url)})\n* [archive.ph](https://archive.ph/?url={quote(post.url)}&run=1) (click to archive)\n\n"
		archive_url(post.url)

	captured = []
	body_for_snappy = post.body_html.replace(' data-src="', ' src="')


	for i in list(snappy_url_regex.finditer(body_for_snappy)):
		href = i.group(1)
		if href in [x[0] for x in captured]: continue
		title = i.group(2)
		captured.append((href, title))

	for i in list(snappy_youtube_regex.finditer(body_for_snappy)):
		href = f'https://youtube.com/watch?v={i.group(1)}'
		if href in [x[0] for x in captured]: continue
		captured.append((href, href))


	for href, title in captured:
		if href.startswith(SITE_FULL) or href.startswith(BAN_EVASION_FULL): continue
		if "Snapshots:\n\n" not in body: body += "Snapshots:\n\n"
		if f'**[{title}]({href})**:\n\n' not in body:
			addition = f'**[{title}]({href})**:\n\n'
			if href.startswith('https://old.reddit.com/r/'):
				rev = href.replace('https://old.reddit.com/', '')
				addition += f'* [unddit.com](https://unddit.com/{rev})\n'
			if href.startswith('https://old.reddit.com/u/'):
				rev = href.replace('https://old.reddit.com/u/', '')
				addition += f"* [camas.unddit.com](https://camas.unddit.com/reddit-search/#\u007b\"author\":\"{rev}\",\"resultSize\":100\u007d)\n"
			addition += f'* [archive.org](https://web.archive.org/{href})\n'
			addition += f'* [ghostarchive.org](https://ghostarchive.org/search?term={quote(href)})\n'
			addition += f'* [archive.ph](https://archive.ph/?url={quote(href)}&run=1) (click to archive)\n'
			addition += '\n'
			if len(f'{body}{addition}') > COMMENT_BODY_LENGTH_LIMIT: break
			body += addition
			archive_url(href)

	body = body.strip()[:COMMENT_BODY_LENGTH_LIMIT]
	body_html = sanitize(body, snappy=True)

	if len(body_html) == 0:
		return

	if len(body_html) < COMMENT_BODY_HTML_LENGTH_LIMIT:
		c = Comment(author_id=SNAPPY_ID,
			distinguish_level=6,
			parent_submission=post.id,
			level=1,
			over_18=False,
			is_bot=True,
			app_id=None,
			body=body,
			body_html=body_html,
			ghost=ghost
			)

		g.db.add(c)

		check_slots_command(c, v, snappy)

		snappy.comment_count += 1
		snappy.pay_account('coins', 1)
		g.db.add(snappy)

		if FEATURES['PINS'] and (body.startswith(':#marseypin:') or body.startswith(':#marseypin2:')):
			post.stickied = "Snappy"
			post.stickied_utc = int(time.time()) + 3600

		elif SITE_NAME == 'rDrama' and body.startswith(':#marseyban:'):
			days = 0.01
			reason = f'<a href="/post/{post.id}">/post/{post.id}</a>'
			v.ban(admin=snappy, reason=reason, days=days)
			text = f"@Snappy has banned you for **{days}** days for the following reason:\n\n> {reason}"
			send_repeatable_notification(v.id, text)
			duration = f"for {days} days"
			ma=ModAction(
				kind="ban_user",
				user_id=snappy.id,
				target_user_id=v.id,
				_note=f'duration: {duration}, reason: "{reason}"'
				)
			g.db.add(ma)
			post.bannedfor = f'{duration} by @Snappy'

		g.db.flush()

		c.top_comment_id = c.id

		post.comment_count += 1
		post.replies = [c]

def execute_zozbot(c:Comment, level:int, post_target:post_target_type, v):
	if SITE_NAME != 'rDrama': return
	posting_to_submission = isinstance(post_target, Submission)
	if random.random() >= 0.001: return
	c2 = Comment(author_id=ZOZBOT_ID,
		parent_submission=post_target.id if posting_to_submission else None,
		wall_user_id=post_target.id if not posting_to_submission else None,
		parent_comment_id=c.id,
		level=level+1,
		is_bot=True,
		body="zoz",
		body_html='<p class="zozbot">zoz</p>',
		top_comment_id=c.top_comment_id,
		ghost=c.ghost,
		distinguish_level=6
	)

	g.db.add(c2)
	g.db.flush()
	n = Notification(comment_id=c2.id, user_id=v.id)
	g.db.add(n)

	c3 = Comment(author_id=ZOZBOT_ID,
		parent_submission=post_target.id if posting_to_submission else None,
		wall_user_id=post_target.id if not posting_to_submission else None,
		parent_comment_id=c2.id,
		level=level+2,
		is_bot=True,
		body="zle",
		body_html='<p class="zozbot">zle</p>',
		top_comment_id=c.top_comment_id,
		ghost=c.ghost,
		distinguish_level=6
	)

	g.db.add(c3)
	g.db.flush()


	c4 = Comment(author_id=ZOZBOT_ID,
		parent_submission=post_target.id if posting_to_submission else None,
		wall_user_id=post_target.id if not posting_to_submission else None,
		parent_comment_id=c3.id,
		level=level+3,
		is_bot=True,
		body="zozzle",
		body_html='<p class="zozbot">zozzle</p>',
		top_comment_id=c.top_comment_id,
		ghost=c.ghost,
		distinguish_level=6
	)

	g.db.add(c4)

	zozbot = get_account(ZOZBOT_ID)
	zozbot.comment_count += 3
	zozbot.pay_account('coins', 1)
	g.db.add(zozbot)

def execute_longpostbot(c:Comment, level:int, body, body_html, post_target:post_target_type, v:User):
	if SITE_NAME != 'rDrama': return
	posting_to_submission = isinstance(post_target, Submission)
	if not len(c.body.split()) >= 200: return
	if "</blockquote>" in body_html: return
	body = random.choice(LONGPOST_REPLIES)
	if body.startswith('▼'):
		body = body[1:]
		vote = CommentVote(user_id=LONGPOSTBOT_ID,
			vote_type=-1,
			comment_id=c.id,
			real = True
		)
		g.db.add(vote)
		c.downvotes = 1

	c2 = Comment(author_id=LONGPOSTBOT_ID,
		parent_submission=post_target.id if posting_to_submission else None,
		wall_user_id=post_target.id if not posting_to_submission else None,
		parent_comment_id=c.id,
		level=level+1,
		is_bot=True,
		body=body,
		body_html=f"<p>{body}</p>",
		top_comment_id=c.top_comment_id,
		ghost=c.ghost
	)

	g.db.add(c2)

	longpostbot = get_account(LONGPOSTBOT_ID)
	longpostbot.comment_count += 1
	longpostbot.pay_account('coins', 1)
	g.db.add(longpostbot)
	g.db.flush()
	n = Notification(comment_id=c2.id, user_id=v.id)
	g.db.add(n)

def execute_antispam_submission_check(title, v, url):
	now = int(time.time())
	cutoff = now - 60 * 60 * 24

	similar_posts = g.db.query(Submission).filter(
					Submission.author_id == v.id,
					Submission.title.op('<->')(title) < SPAM_SIMILARITY_THRESHOLD,
					Submission.created_utc > cutoff
	).all()

	if url:
		similar_urls = g.db.query(Submission).filter(
					Submission.author_id == v.id,
					Submission.url.op('<->')(url) < SPAM_URL_SIMILARITY_THRESHOLD,
					Submission.created_utc > cutoff
		).all()
	else: similar_urls = []

	threshold = SPAM_SIMILAR_COUNT_THRESHOLD
	if v.age >= (60 * 60 * 24 * 7): threshold *= 3
	elif v.age >= (60 * 60 * 24): threshold *= 2

	if max(len(similar_urls), len(similar_posts)) >= threshold:
		text = "Your account has been banned for **1 day** for the following reason:\n\n> Too much spam!"
		send_repeatable_notification(v.id, text)

		v.ban(reason="Spamming.",
			  days=1)

		for post in similar_posts + similar_urls:
			post.is_banned = True
			post.is_pinned = False
			post.ban_reason = "AutoJanny"
			g.db.add(post)
			ma=ModAction(
					user_id=AUTOJANNY_ID,
					target_submission_id=post.id,
					kind="ban_post",
					_note="spam"
					)
			g.db.add(ma)
		return False
	return True

def execute_blackjack(v, target, body, type):
	if not body: return True

	execute = False
	if blackjack and any(i in body.lower() for i in blackjack.split()):
		execute = True
		shadowban = True
	elif blackjack2 and all(i in body.lower() for i in blackjack2.split()):
		execute = True
		shadowban = v.truescore < 100

	if execute:
		if shadowban:
			v.shadowbanned = AUTOJANNY_ID

			ma = ModAction(
				kind="shadowban",
				user_id=AUTOJANNY_ID,
				target_user_id=v.id,
				_note='reason: "Blackjack"'
			)
			g.db.add(ma)

			v.ban_reason = "Blackjack"
			g.db.add(v)
		elif type in {'submission', 'comment', 'message'}:
			target.is_banned = True

		notified_ids = [x[0] for x in g.db.query(User.id).filter(User.admin_level >= PERMS['BLACKJACK_NOTIFICATIONS'])]
		extra_info = "unknown entity"

		if type == 'submission':
			extra_info = target.permalink
		elif type == 'chat':
			extra_info = "chat message"
		elif type == 'flag':
			extra_info = f"reports on {target.permalink}"
		elif type == 'modmail':
			extra_info = "modmail"
		elif type in {'comment', 'message'}:
			for id in notified_ids:
				n = Notification(comment_id=target.id, user_id=id)
				g.db.add(n)
				g.db.flush()
			extra_info = None

		if extra_info:
			for id in notified_ids:
				send_repeatable_notification(id, f"Blackjack for @{v.username}: {extra_info}")
	return True

def execute_antispam_duplicate_comment_check(v:User, body_html:str):
	'''
	Sanity check for newfriends
	'''
	ANTISPAM_DUPLICATE_THRESHOLD = 3
	if v.id in ANTISPAM_BYPASS_IDS or v.admin_level: return
	if v.age >= NOTIFICATION_SPAM_AGE_THRESHOLD: return
	if len(body_html) < 16: return
	if body_html == '!wordle': return # wordle
	compare_time = int(time.time()) - 60 * 60 * 24
	count = g.db.query(Comment.id).filter(Comment.body_html == body_html,
										  Comment.created_utc >= compare_time).count()
	if count <= ANTISPAM_DUPLICATE_THRESHOLD: return
	v.ban(reason="Spamming.", days=0.0)
	send_repeatable_notification(v.id, "Your account has been banned **permanently** for the following reason:\n\n> Too much spam!")
	g.db.add(v)
	g.db.commit()
	abort(403, "Too much spam!")

def execute_antispam_comment_check(body:str, v:User):
	if v.id in ANTISPAM_BYPASS_IDS: return
	if len(body) <= COMMENT_SPAM_LENGTH_THRESHOLD: return
	now = int(time.time())
	cutoff = now - 60 * 60 * 24

	similar_comments = g.db.query(Comment).filter(
		Comment.author_id == v.id,
		Comment.body.op('<->')(body) < COMMENT_SPAM_SIMILAR_THRESHOLD,
		Comment.created_utc > cutoff
	).all()

	threshold = COMMENT_SPAM_COUNT_THRESHOLD
	if v.age >= (60 * 60 * 24 * 7):
		threshold *= 3
	elif v.age >= (60 * 60 * 24):
		threshold *= 2

	if len(similar_comments) <= threshold: return
	text = "Your account has been banned for **1 day** for the following reason:\n\n> Too much spam!"
	send_repeatable_notification(v.id, text)
	v.ban(reason="Spamming.",
			days=1)
	for comment in similar_comments:
		comment.is_banned = True
		comment.ban_reason = "AutoJanny"
		g.db.add(comment)
		ma=ModAction(
			user_id=AUTOJANNY_ID,
			target_comment_id=comment.id,
			kind="ban_comment",
			_note="spam"
		)
		g.db.add(ma)
	g.db.commit()
	abort(403, "Too much spam!")

def execute_under_siege(v:User, target:Optional[Union[Submission, Comment]], body, type:str) -> bool:
	if not get_setting("under_siege"): return True
	if not v.shadowbanned and v.age < UNDER_SIEGE_AGE_THRESHOLD and not v.admin_level >= PERMS['SITE_BYPASS_UNDER_SIEGE_MODE']:
		v.shadowbanned = AUTOJANNY_ID

		ma = ModAction(
			kind="shadowban",
			user_id=AUTOJANNY_ID,
			target_user_id=v.id,
			_note='reason: "Under Siege"'
		)
		g.db.add(ma)

		v.ban_reason = "Under Siege"
		g.db.add(v)
		t = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time()))
		log_file(f"[{t}] {v.id} @{v.username} {type} {v.age}s", "under_siege.log")
		return False
	return True

def execute_lawlz_actions(v:User, p:Submission):
	if v.id != LAWLZ_ID: return
	if SITE_NAME != 'rDrama': return
	if not FEATURES['PINS']: return
	p.stickied_utc = int(time.time()) + 86400
	p.stickied = "AutoJanny"
	p.distinguish_level = 6
	p.flair = filter_emojis_only(":ben10: Required Reading")
	ma_1=ModAction(
		kind="pin_post",
		user_id=AUTOJANNY_ID,
		target_submission_id=p.id,
		_note='for 1 day'
	)
	ma_2=ModAction(
		kind="distinguish_post",
		user_id=AUTOJANNY_ID,
		target_submission_id=p.id
	)
	ma_3=ModAction(
		kind="flair_post",
		user_id=AUTOJANNY_ID,
		target_submission_id=p.id,
		_note=f'"{p.flair}"'
	)
	g.db.add(p)
	g.db.add(ma_1)
	g.db.add(ma_2)
	g.db.add(ma_3)

def process_poll_options(target:Union[Submission, Comment],
						cls:Union[Type[SubmissionOption], Type[CommentOption]],
						options:Iterable[str], exclusive:int, friendly_name:str,
						db:scoped_session) -> None:
		for option in options:
			if len(option) > 500: abort(400, f"{friendly_name} option too long!")
			if cls is SubmissionOption:
				option = cls(
					submission_id=target.id,
					body_html=option,
					exclusive=exclusive,
				)
			else:
				option = cls(
					comment_id=target.id,
					body_html=option,
					exclusive=exclusive,
				)
			db.add(option)

def execute_wordle(c:Comment, body:str):
	if not FEATURES['WORDLE']: return
	if not "!wordle" in body: return
	answer = random.choice(WORDLE_LIST)
	c.wordle_result = f'_active_{answer}'
