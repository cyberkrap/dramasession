import functools
import random
import re
import signal
from functools import partial
from os import path, listdir
from typing import Any
from urllib.parse import parse_qs, urlparse

import bleach
from bleach.css_sanitizer import CSSSanitizer
from bleach.linkifier import LinkifyFilter
from bs4 import BeautifulSoup
from mistletoe import markdown
from files.classes.domains import BannedDomain

from files.helpers.config.const import *
from files.helpers.const_stateful import *
from files.helpers.regex import *
from .get import *

TLDS = ( # Original gTLDs and ccTLDs
	'ac','ad','ae','aero','af','ag','ai','al','am','an','ao','aq','ar','arpa','as','asia','at',
	'au','aw','ax','az','ba','bb','bd','be','bf','bg','bh','bi','biz','bj','bm','bn','bo','br',
	'bs','bt','bv','bw','by','bz','ca','cafe','cat','cc','cd','cf','cg','ch','ci','ck','cl',
	'cm','cn','co','com','coop','cr','cu','cv','cx','cy','cz','de','dj','dk','dm','do','dz','ec',
	'edu','ee','eg','er','es','et','eu','fi','fj','fk','fm','fo','fr','ga','gb','gd','ge','gf',
	'gg','gh','gi','gl','gm','gn','gov','gp','gq','gr','gs','gt','gu','gw','gy','hk','hm','hn',
	'hr','ht','hu','id','ie','il','im','in','info','int','io','iq','ir','is','it','je','jm','jo',
	'jobs','jp','ke','kg','kh','ki','km','kn','kp','kr','kw','ky','kz','la','lb','lc','li','lk',
	'lr','ls','lt','lu','lv','ly','ma','mc','md','me','mg','mh','mil','mk','ml','mm','mn','mo',
	'mobi','mp','mq','mr','ms','mt','mu','museum','mv','mw','mx','my','mz','na','name',
	'nc','ne','net','nf','ng','ni','nl','no','np','nr','nu','nz','om','org','pa','pe','pf','pg',
	'ph','pk','pl','pm','pn','post','pr','pro','ps','pt','pw','py','qa','re','ro','rs','ru','rw',
	'sa','sb','sc','sd','se','sg','sh','si','sj','sk','sl','sm','sn','so','social','sr','ss','st',
	'su','sv','sx','sy','sz','tc','td','tel','tf','tg','th','tj','tk','tl','tm','tn','to','tp',
	'tr','travel','tt','tv','tw','tz','ua','ug','uk','us','uy','uz','va','vc','ve','vg','vi','vn',
	'vu','wf','ws','xn','xxx','ye','yt','yu','za','zm','zw',
	# New gTLDs
	'app','cleaning','club','dev','farm','florist','fun','gay','lgbt','life','lol',
	'moe','mom','monster','new','news','online','pics','press','pub','site','blog',
	'vip','win','world','wtf','xyz','video','host','art','media','wiki','tech','cooking'
	)

allowed_tags = ('b','blockquote','br','code','del','em','h1','h2','h3','h4','h5','h6','hr','i',
	'li','ol','p','pre','strong','sub','sup','table','tbody','th','thead','td','tr','ul',
	'marquee','a','span','ruby','rp','rt','spoiler','img','lite-youtube','video','audio','g')

allowed_styles = ['color', 'background-color', 'font-weight', 'text-align', 'filter',]

def allowed_attributes(tag, name, value):

	if name == 'style': return True

	if tag == 'marquee':
		if name in {'direction', 'behavior', 'scrollamount'}: return True
		if name in {'height', 'width'}:
			try: value = int(value.replace('px', ''))
			except: return False
			if 0 < value <= 250: return True

	if tag == 'a':
		if name == 'href' and '\\' not in value and 'xn--' not in value:
			return True
		if name == 'rel' and value == 'nofollow noopener': return True
		if name == 'target' and value == '_blank': return True

	if tag == 'img':
		if name in {'src','data-src'}: return is_safe_url(value)
		if name == 'loading' and value == 'lazy': return True
		if name == 'data-bs-toggle' and value == 'tooltip': return True
		if name in {'g','b','glow'} and not value: return True
		if name in {'alt','title'}: return True

	if tag == 'lite-youtube':
		if name == 'params' and value.startswith('autoplay=1&modestbranding=1'): return True
		if name == 'videoid': return True

	if tag == 'video':
		if name == 'controls' and value == '': return True
		if name == 'preload' and value == 'none': return True
		if name == 'src': return is_safe_url(value)

	if tag == 'audio':
		if name == 'src': return is_safe_url(value)
		if name == 'controls' and value == '': return True
		if name == 'preload' and value == 'none': return True

	if tag == 'p':
		if name == 'class' and value in {'mb-0','resizable'}: return True

	if tag == 'span':
		if name == 'data-bs-toggle' and value == 'tooltip': return True
		if name == 'title': return True
		if name == 'alt': return True

	if tag == 'table':
		if name == 'class' and value == 'table': return True

	return False

def build_url_re(tlds, protocols):
	"""Builds the url regex used by linkifier

	If you want a different set of tlds or allowed protocols, pass those in
	and stomp on the existing ``url_re``::

		from bleach import linkifier

		my_url_re = linkifier.build_url_re(my_tlds_list, my_protocols)

		linker = LinkifyFilter(url_re=my_url_re)

	"""
	return re.compile(
		r"""\(*# Match any opening parentheses.
		\b(?<![@.])(?:(?:{0}):/{{0,3}}(?:(?:\w+:)?\w+@)?)?# http://
		([\w-]+\.)+(?:{1})(?:\:[0-9]+)?(?!\.\w)\b# xx.yy.tld(:##)?
		(?:[/?][^#\s\{{\}}\|\\\^\[\]`<>"]*)?
			# /path/zz (excluding "unsafe" chars from RFC 1738,
			# except for ~, which happens in practice)
		(?:\#[^#\s\|\\\^\[\]`<>"]*)?
			# #hash (excluding "unsafe" chars from RFC 1738,
			# except for ~, which happens in practice)
		""".format(
			"|".join(sorted(protocols)), "|".join(sorted(tlds))
		),
		re.IGNORECASE | re.VERBOSE | re.UNICODE,
	)

url_re = build_url_re(tlds=TLDS, protocols=['http', 'https'])

def callback(attrs, new=False):
	if (None, "href") not in attrs:
		return # Incorrect <a> tag

	href = attrs[(None, "href")]

	# \ in href right after / makes most browsers ditch site hostname and allows for a host injection bypassing the check, see <a href="/\google.com">cool</a>
	if "\\" in href or not ascii_only_regex.fullmatch(href):
		attrs["_text"] = href # Laugh at this user
		del attrs[(None, "href")] # Make unclickable and reset harmful payload
		return attrs

	if not href.startswith('/') and not href.startswith(f'{SITE_FULL}/'):
		attrs[(None, "target")] = "_blank"
		attrs[(None, "rel")] = "nofollow noopener"

	return attrs


def render_emoji(html, regexp, golden, marseys_used, b=False):
	emojis = list(regexp.finditer(html))
	captured = set()

	for i in emojis:
		if i.group(0) in captured: continue
		captured.add(i.group(0))

		emoji = i.group(1).lower()
		attrs = ''
		if b: attrs += ' b'
		if golden and len(emojis) <= 20 and ('marsey' in emoji or emoji in marseys_const2):
			if random.random() < 0.0025: attrs += ' g'
			elif random.random() < 0.00125: attrs += ' glow'

		old = emoji
		emoji = emoji.replace('!','').replace('#','')
		if emoji == 'marseyrandom': emoji = random.choice(marseys_const2)

		emoji_partial_pat = '<img loading="lazy" alt=":{0}:" src="{1}"{2}>'
		emoji_partial = '<img loading="lazy" data-bs-toggle="tooltip" alt=":{0}:" title=":{0}:" src="{1}"{2}>'
		emoji_html = None

		if emoji.endswith('pat') and emoji != 'marseyunpettablepat':
			if path.isfile(f"files/assets/images/emojis/{emoji.replace('pat','')}.webp"):
				emoji_html = f'<span data-bs-toggle="tooltip" alt=":{old}:" title=":{old}:"><img loading="lazy" src="/i/hand.webp">{emoji_partial_pat.format(old, f"/e/{emoji[:-3]}.webp", attrs)}</span>'
			elif emoji.startswith('@'):
				if u := get_user(emoji[1:-3], graceful=True):
					emoji_html = f'<span data-bs-toggle="tooltip" alt=":{old}:" title=":{old}:"><img loading="lazy" src="/i/hand.webp">{emoji_partial_pat.format(old, f"/pp/{u.id}", attrs)}</span>'
		elif path.isfile(f'files/assets/images/emojis/{emoji}.webp'):
			emoji_html = emoji_partial.format(old, f'/e/{emoji}.webp', attrs)


		if emoji_html:
			marseys_used.add(emoji)
			html = re.sub(f'(?<!"){i.group(0)}(?![^<]*<\/(code|pre|a)>)', emoji_html, html)
	return html


def with_sigalrm_timeout(timeout: int):
	'Use SIGALRM to raise an exception if the function executes for longer than timeout seconds'

	# while trying to test this using time.sleep I discovered that gunicorn does in fact do some
	# async so if we timeout on that (or on a db op) then the process is crashed without returning
	# a proper 500 error. Oh well.
	def sig_handler(signum, frame):
		print("Timeout!", flush=True)
		raise Exception("Timeout")

	def inner(func):
		@functools.wraps(func)
		def wrapped(*args, **kwargs):
			signal.signal(signal.SIGALRM, sig_handler)
			signal.alarm(timeout)
			try:
				return func(*args, **kwargs)
			finally:
				signal.alarm(0)
		return wrapped
	return inner


def sanitize_raw_title(sanitized:Optional[str]) -> str:
	if not sanitized: return ""
	sanitized = sanitized.replace('\u200e','').replace('\u200b','').replace("\ufeff", "").replace("\r","").replace("\n", "")
	sanitized = sanitized.strip()
	return sanitized[:POST_TITLE_LENGTH_LIMIT]

def sanitize_raw_body(sanitized:Optional[str], is_post:bool) -> str:
	if not sanitized: return ""
	sanitized = html_comment_regex.sub('', sanitized)
	sanitized = sanitized.replace('\u200e','').replace('\u200b','').replace("\ufeff", "").replace("\r\n", "\n")
	sanitized = sanitized.strip()
	return sanitized[:POST_BODY_LENGTH_LIMIT if is_post else COMMENT_BODY_LENGTH_LIMIT]


def sanitize_settings_text(sanitized:Optional[str], max_length:Optional[int]=None) -> str:
	if not sanitized: return ""
	sanitized = sanitized.replace('\u200e','').replace('\u200b','').replace("\ufeff", "").replace("\r", "").replace("\n","")
	sanitized = sanitized.strip()
	if max_length: sanitized = sanitized[:max_length]
	return sanitized


chud_images = listdir("files/assets/images/chud")
chud_images = [f'![](/i/chud/{f})' for f in chud_images]
chud_images.extend([':#trumpjaktalking:', ':#reposthorse:'])

def handle_youtube_links(url):
	html = None
	params = parse_qs(urlparse(url).query, keep_blank_values=True)

	id = params.get('v')

	if not id: return None

	id = id[0]

	t = None
	split = id.split('?t=')
	if len(split) == 2:
		id = split[0]
		t = split[1]

	if yt_id_regex.fullmatch(id):
		if not t:
			t = params.get('t', params.get('start', [0]))[0]
		if isinstance(t, str):
			t = t.replace('s','')
			split = t.split('m')
			if len(split) == 2:
				minutes = int(split[0])
				seconds = int(split[1])
				t = minutes*60 + seconds
		html = f'<lite-youtube videoid="{id}" params="autoplay=1&modestbranding=1'
		if t:
			html += f'&start={int(t)}'
		html += '"></lite-youtube>'
	return html

@with_sigalrm_timeout(10)
def sanitize(sanitized, golden=True, limit_pings=0, showmore=True, count_marseys=False, torture=False, sidebar=False, snappy=False, chat=False):
	sanitized = sanitized.strip()

	sanitized = utm_regex.sub('', sanitized)
	sanitized = utm_regex2.sub('', sanitized)

	if torture:
		sanitized = torture_ap(sanitized, g.v.username)
		to_add = random.choice(chud_images)
		sanitized += f'\n{to_add}'

	sanitized = normalize_url(sanitized)

	sanitized = twitter_regex.sub(r'\1', sanitized)

	if '```' not in sanitized and '<pre>' not in sanitized:
		sanitized = linefeeds_regex.sub(r'\1\n\n\2', sanitized)

	sanitized = greentext_regex.sub(r'\1<g>\>\2</g>', sanitized)
	sanitized = image_regex.sub(r'\1![](\2)', sanitized)
	sanitized = image_check_regex.sub(r'\1', sanitized)
	sanitized = link_fix_regex.sub(r'\1https://\2', sanitized)

	if FEATURES['MARKUP_COMMANDS']:
		sanitized = command_regex.sub(command_regex_matcher, sanitized)

	sanitized = numbered_list_regex.sub(r'\1\. ', sanitized)

	sanitized = markdown(sanitized)

	sanitized = strikethrough_regex.sub(r'\1<del>\2</del>', sanitized)

	# replacing zero width characters, overlines, fake colons
	sanitized = sanitized.replace('\u200e','').replace('\u200b','').replace("\ufeff", "").replace("\u033f","").replace("\u0589", ":")

	sanitized = reddit_regex.sub(r'\1<a href="https://old.reddit.com/\2" rel="nofollow noopener" target="_blank">/\2</a>', sanitized)
	sanitized = sub_regex.sub(r'\1<a href="/\2">/\2</a>', sanitized)

	v = getattr(g, 'v', None)

	names = set(m.group(2) for m in mention_regex.finditer(sanitized))
	if limit_pings and len(names) > limit_pings and not v.admin_level >= PERMS['POST_COMMENT_INFINITE_PINGS']: abort(406)
	users_list = get_users(names, graceful=True)
	users_dict = {}
	for u in users_list:
		users_dict[u.username.lower()] = u
		if u.original_username:
			users_dict[u.original_username.lower()] = u

	def replacer(m):
		u = users_dict.get(m.group(2).lower())
		if not u:
			return m.group(0)
		return f'{m.group(1)}<a href="/id/{u.id}"><img loading="lazy" src="/pp/{u.id}">@{u.username}</a>'

	sanitized = mention_regex.sub(replacer, sanitized)

	soup = BeautifulSoup(sanitized, 'lxml')

	for tag in soup.find_all("img"):
		if tag.get("src") and not tag["src"].startswith('/pp/'):
			if not is_safe_url(tag["src"]):
				a = soup.new_tag("a", href=tag["src"], rel="nofollow noopener", target="_blank")
				a.string = tag["src"]
				tag.replace_with(a)
				continue

			tag["loading"] = "lazy"
			tag["data-src"] = tag["src"]
			tag["src"] = "/i/l.webp"
			tag['alt'] = f'![]({tag["data-src"]})'

			if tag.parent.name != 'a':
				a = soup.new_tag("a", href=tag["data-src"])
				if not is_site_url(a["href"]):
					a["rel"] = "nofollow noopener"
					a["target"] = "_blank"
				tag = tag.replace_with(a)
				a.append(tag)

			tag["data-src"] = tag["data-src"].replace('/giphy.webp', '/200w.webp')

	for tag in soup.find_all("a"):
		if not tag.contents or not str(tag.contents[0]).strip():
			tag.extract()
		if not snappy and tag.get("href") and fishylinks_regex.fullmatch(str(tag.string)):
			tag.string = tag["href"]


	sanitized = str(soup)

	sanitized = spoiler_regex.sub(r'<spoiler>\1</spoiler>', sanitized)

	marseys_used = set()

	emojis = list(emoji_regex.finditer(sanitized))
	if len(emojis) > 20: golden = False

	captured = []
	for i in emojis:
		if i.group(0) in captured: continue
		captured.append(i.group(0))

		old = i.group(0)
		if 'marseylong1' in old or 'marseylong2' in old or 'marseyllama1' in old or 'marseyllama2' in old: new = old.lower().replace(">", " class='mb-0'>")
		else: new = old.lower()

		new = render_emoji(new, emoji_regex2, golden, marseys_used, True)

		sanitized = sanitized.replace(old, new)

	emojis = list(emoji_regex2.finditer(sanitized))
	if len(emojis) > 20: golden = False

	sanitized = render_emoji(sanitized, emoji_regex2, golden, marseys_used)

	sanitized = sanitized.replace('&amp;','&')

	captured = []
	for i in youtube_regex.finditer(sanitized):
		if i.group(0) in captured: continue
		captured.append(i.group(0))

		html = handle_youtube_links(i.group(2))
		if html:
			sanitized = sanitized.replace(i.group(0), i.group(1) + html)

	sanitized = video_sub_regex.sub(r'\1<p class="resizable"><video controls preload="none" src="\2"></video></p>', sanitized)
	sanitized = audio_sub_regex.sub(r'\1<audio controls preload="none" src="\2"></audio>', sanitized)

	if count_marseys:
		for marsey in g.db.query(Marsey).filter(Marsey.submitter_id==None, Marsey.name.in_(marseys_used)).all():
			marsey.count += 1
			g.db.add(marsey)

	sanitized = sanitized.replace('<p></p>', '')
	sanitized = sanitized.replace('<html><body>','').replace('</body></html>','')

	css_sanitizer = CSSSanitizer(allowed_css_properties=allowed_styles)
	sanitized = bleach.Cleaner(tags=allowed_tags,
								attributes=allowed_attributes,
								protocols=['http', 'https'],
								css_sanitizer=css_sanitizer,
								filters=[partial(LinkifyFilter, skip_tags=["pre"],
									parse_email=False, callbacks=[callback], url_re=url_re)]
								).clean(sanitized)

	soup = BeautifulSoup(sanitized, 'lxml')

	links = soup.find_all("a")

	domain_list = set()

	for link in links:
		href = link.get("href")
		if not href: continue
		url = urlparse(href)
		d = tldextract.extract(href).registered_domain + url.path
		domain_list.add(d.lower())

	def error(error):
		if chat:
			return error, 403
		else:
			abort(403, error)

	banned_domains = g.db.query(BannedDomain).all()
	for x in banned_domains:
		for y in domain_list:
			if y.startswith(x.domain):
				return error(f'Remove the banned link "{x.domain}" and try again!\nReason for link ban: "{x.reason}"')

	if discord_username_regex.match(sanitized):
		return error("Stop grooming!")

	if '<pre>' not in sanitized and not sidebar:
		sanitized = sanitized.replace('\n','')

	if showmore:
		# Insert a show more button if the text is too long or has too many paragraphs
		CHARLIMIT = 3000
		pos = 0
		for _ in range(20):
			pos = sanitized.find('</p>', pos + 4)
			if pos < 0:
				break
		if (pos < 0 and len(sanitized) > CHARLIMIT) or pos > CHARLIMIT:
			pos = CHARLIMIT - 500
		if pos >= 0:
			sanitized = (sanitized[:pos] +
				showmore_regex.sub(r'\1<p><button class="showmore">SHOW MORE</button></p><d class="d-none">\2</d>',
					sanitized[pos:], count=1))

	return sanitized.strip()

def allowed_attributes_emojis(tag, name, value):
	if tag == 'img':
		if name == 'src' and value.startswith('/') and '\\' not in value: return True
		if name == 'loading' and value == 'lazy': return True
		if name == 'data-bs-toggle' and value == 'tooltip': return True
		if name in {'g','glow'} and not value: return True
		if name in {'alt','title'}: return True

	if tag == 'span':
		if name == 'data-bs-toggle' and value == 'tooltip': return True
		if name == 'title': return True
		if name == 'alt': return True
	return False


@with_sigalrm_timeout(1)
def filter_emojis_only(title, golden=True, count_marseys=False, graceful=False, torture=False):
	title = title.strip()

	if torture:
		title = torture_ap(title, g.v.username)

	title = title.replace('‎','').replace('​','').replace("\ufeff", "").replace("𒐪","").replace("\n", "").replace("\r", "").replace("\t", "").replace("&", "&amp;").replace('<','&lt;').replace('>','&gt;').replace('"', '&quot;').replace("'", "&#039;").replace("﷽","").strip()

	marseys_used = set()

	title = render_emoji(title, emoji_regex3, golden, marseys_used)

	if count_marseys:
		for marsey in g.db.query(Marsey).filter(Marsey.submitter_id==None, Marsey.name.in_(marseys_used)).all():
			marsey.count += 1
			g.db.add(marsey)

	title = strikethrough_regex.sub(r'\1<del>\2</del>', title)

	title = bleach.clean(title, tags=['img','del','span'], attributes=allowed_attributes_emojis, protocols=['http','https']).replace('\n','').strip()

	if len(title) > POST_TITLE_HTML_LENGTH_LIMIT and not graceful: abort(400)
	else: return title

def normalize_url(url):
	url = reddit_domain_regex.sub(r'\1https://old.reddit.com/\3/', url)

	url = url.replace("https://youtu.be/", "https://youtube.com/watch?v=") \
			 .replace("https://music.youtube.com/watch?v=", "https://youtube.com/watch?v=") \
			 .replace("https://www.youtube.com", "https://youtube.com") \
			 .replace("https://m.youtube.com", "https://youtube.com") \
			 .replace("https://youtube.com/shorts/", "https://youtube.com/watch?v=") \
			 .replace("https://youtube.com/v/", "https://youtube.com/watch?v=") \
			 .replace("https://mobile.twitter.com", "https://twitter.com") \
			 .replace("https://m.facebook.com", "https://facebook.com") \
			 .replace("https://m.wikipedia.org", "https://wikipedia.org") \
			 .replace("https://www.twitter.com", "https://twitter.com") \
			 .replace("https://www.instagram.com", "https://instagram.com") \
			 .replace("https://www.tiktok.com", "https://tiktok.com") \
			 .replace("https://www.streamable.com", "https://streamable.com") \
			 .replace("https://streamable.com/", "https://streamable.com/e/") \
			 .replace("https://streamable.com/e/e/", "https://streamable.com/e/") \
			 .replace("https://search.marsey.cat/#", "https://camas.unddit.com/#") \
			 .replace("https://imgur.com/", "https://i.imgur.com/") \
			 .replace("https://nitter.net/", "https://twitter.com/") \
			 .replace("https://nitter.42l.fr/", "https://twitter.com/") \
			 .replace("https://nitter.lacontrevoie.fr/", "https://twitter.com/") \
			 .replace("/giphy.gif", "/giphy.webp")

	url = imgur_regex.sub(r'\1_d.webp?maxwidth=9999&fidelity=grand', url)
	url = giphy_regex.sub(r'\1.webp', url)

	return url

def validate_css(css):
	if '@import' in css:
		return False, "@import statements are not allowed!"

	for i in css_url_regex.finditer(css):
		url = i.group(1)
		if not is_safe_url(url):
			domain = tldextract.extract(url).registered_domain
			return False, f"The domain '{domain}' is not allowed, please use one of these domains\n\n{approved_embed_hosts}."

	return True, ""

def sanitize_poll_options(v:User, body:str, allow_bets:bool) -> tuple[str, List[Any], List[Any], List[Any]]:
	def sanitize_poll_type(body:str, re:re.Pattern) -> tuple[str, List[str]]:
		opts = []
		for i in list(re.finditer(body))[:POLL_MAX_OPTIONS] if POLL_MAX_OPTIONS else list(re.finditer(body)):
			opts.append(filter_emojis_only(i.group(1)))
			body = body.replace(i.group(0), "")
		return (body, opts)

	bets = []
	if allow_bets and v and v.admin_level >= PERMS['POST_BETS']:
		body, bets = sanitize_poll_type(body, bet_regex)
	body, options = sanitize_poll_type(body, poll_regex)
	body, choices = sanitize_poll_type(body, choice_regex)
	return (body, bets, options, choices)
