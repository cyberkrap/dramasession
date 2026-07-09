import time
from typing import Iterable
import itertools

import requests
from flask_caching import Cache
from flask import g
from sqlalchemy import or_

import files.helpers.config.const as const
from files.classes.badges import Badge
from files.classes.comment import Comment
from files.classes.user import User
from files.helpers.sanitize import sanitize
from files.classes.notifications import Notification

# Note: while https://api.pushshift.io/meta provides the key
# server_ratelimit_per_minute, in practice Cloudflare puts stricter,
# unofficially documented limits at around 60/minute. We get nowhere near this
# with current keyword quantities. If this ever changes, consider reading the
# value from /meta (or just guessing) and doing a random selection of keywords.

def offsite_mentions_task(cache:Cache):
	site_mentions = get_mentions(cache, const.REDDIT_NOTIFS_SITE)
	notify_mentions(site_mentions)

	if const.REDDIT_NOTIFS_USERS:
		for query, send_user in const.REDDIT_NOTIFS_USERS.items():
			user_mentions = get_mentions(cache, [query], reddit_notifs_users=True)
			notify_mentions(user_mentions, send_to=send_user, mention_str='mention of you')

	g.db.commit() # commit early otherwise localhost testing fails to commit

def get_mentions(cache:Cache, queries:Iterable[str], reddit_notifs_users=False):
	kinds = ['submission', 'comment']
	mentions = []
	exclude_subreddits = ['PokemonGoRaids', 'SubSimulatorGPT2', 'SubSimGPT2Interactive']
	try:
		after = int(cache.get(const.REDDIT_NOTIFS_CACHE_KEY) or time.time())
	except:
		print("Failed to retrieve last mention time from cache", flush=True)
		after = time.time()
	size = 1 if reddit_notifs_users else 100
	for kind in kinds:
		try:
			url = (
				f'https://api.pushshift.io/reddit/{kind}/search?html_decode=true'
				f'&q={"%7C".join(queries)}'
				# f'&subreddit=!{",!".join(exclude_subreddits)}'
				f'&after={after}'
				f'&size={size}')
			data = requests.get((
				f'https://api.pushshift.io/reddit/{kind}/search?html_decode=true'
				f'&q={"%7C".join(queries)}'
				# f'&subreddit=!{",!".join(exclude_subreddits)}'
				f'&after={after}'
				f'&size={size}'), timeout=15).json()['data']
		except Exception as e:
			continue

		for thing in data:
			if thing['subreddit'] in exclude_subreddits: continue
			if 'bot' in thing['author'].lower(): continue
			if 'AutoModerator' == thing['author']: continue
			after = max(after, thing["created_utc"]) if thing["created_utc"] else after
			if kind == 'comment':
				body = thing["body"].replace('>', '> ')
				text = f'<blockquote><p>{body}</p></blockquote>'
			else:
				title = thing["title"].replace('>', '> ')

				# Special case: a spambot says 'WPD' a lot unrelated to us.
				if 'Kathrine Mclaurin' in title: continue
				text = f'<blockquote><p>{title}</p></blockquote>'

				if thing["selftext"]:
					selftext = thing["selftext"].replace('>', '> ')[:5000]
					text += f'<br><blockquote><p>{selftext}</p></blockquote>'


			mentions.append({
				'permalink': thing['permalink'],
				'author': thing['author'],
				'text': text,
			})
	try:
		if not reddit_notifs_users:
			cache.set(const.REDDIT_NOTIFS_CACHE_KEY, after + 1)
	except:
		print("Failed to set cache value; there may be duplication of reddit notifications", flush=True)
	return mentions

def notify_mentions(mentions, send_to=None, mention_str='site mention'):
	for m in mentions:
		author = m['author']
		permalink = m['permalink']
		text = sanitize(m['text'], golden=False)
		notif_text = (
			f'<p>New {mention_str} by <a href="https://old.reddit.com/u/{author}" '
				f'rel="nofollow noopener" target="_blank">/u/{author}</a></p>'
			f'<p><a href="https://old.reddit.com{permalink}?context=89" '
				'rel="nofollow noopener" target="_blank">'
				f'https://old.reddit.com{permalink}?context=89</a></p>'
			f'{text}'
		)

		existing_comment = g.db.query(Comment.id).filter_by(
			author_id=const.AUTOJANNY_ID,
			parent_submission=None,
			body_html=notif_text).one_or_none()
		if existing_comment: break

		new_comment = Comment(
						author_id=const.AUTOJANNY_ID,
						parent_submission=None,
						body_html=notif_text,
						distinguish_level=6)
		g.db.add(new_comment)
		g.db.flush()
		new_comment.top_comment_id = new_comment.id

		if send_to:
			notif = Notification(comment_id=new_comment.id, user_id=send_to)
			g.db.add(notif)
