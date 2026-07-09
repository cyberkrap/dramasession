import random
import re
from random import choice, choices
from typing import List, Optional, Union

from .config.const import *

valid_username_chars = 'a-zA-Z0-9_\-'
valid_username_regex = re.compile("^[a-zA-Z0-9_\-]{3,25}$", flags=re.A)
mention_regex = re.compile('(^|\s|>)@(([a-zA-Z0-9_\-]){1,30})(?![^<]*<\/(code|pre|a)>)', flags=re.A)

valid_password_regex = re.compile("^.{8,100}$", flags=re.A)

marseyaward_body_regex = re.compile(">[^<\s+]|[^>\s+]<", flags=re.A)

marseyaward_title_regex = re.compile("( *<img[^>]+>)+", flags=re.A)


marsey_regex = re.compile("marsey[a-z0-9]{1,24}", flags=re.A)
tags_regex = re.compile("[a-z0-9: ]{1,200}", flags=re.A)
hat_regex = re.compile("[a-zA-Z0-9\-() ,_]{1,50}", flags=re.A)
description_regex = re.compile("[^<>&\n\t]{1,300}", flags=re.A)

badge_name_regex = re.compile("[A-Za-z0-9 ]+", flags=re.A)

twitter_regex = re.compile("(https:\/\/twitter.com\/[A-Za-z0-9_/]+)\?[^\s)]*", flags=re.A)

valid_sub_regex = re.compile("^[a-zA-Z0-9_\-]{3,25}$", flags=re.A)

query_regex = re.compile("(\w+):(\S+)", flags=re.A)

poll_regex = re.compile("\s*\$\$([^\$\n]+)\$\$\s*(?!([^<]*<\/(code|pre|a)>|[^`]*`))", flags=re.A)
bet_regex = re.compile("\s*\$\$\$([^\$\n]+)\$\$\$\s*(?!([^<]*<\/(code|pre|a)>|[^`]*`))", flags=re.A)
choice_regex = re.compile("\s*&&([^\$\n]+)&&\s*(?!([^<]*<\/(code|pre|a)>|[^`]*`))", flags=re.A)

html_comment_regex = re.compile("<!--.*-->", flags=re.A)

title_regex = re.compile("[^\w ]", flags=re.A)

controversial_regex = re.compile('["> ](https:\/\/old\.reddit\.com/r/[a-zA-Z0-9_]{3,20}\/comments\/[\w\-.#&/=\?@%+]{5,250})["< ]', flags=re.A)

fishylinks_regex = re.compile("(https?:\/\/)?[\w\-.#&/=\?@%;+,:]{2,10}\.[\w\-.#&/=\?@%;+,:]{2,250}", flags=re.A)

spoiler_regex = re.compile('\|\|(.+?)\|\|(?![^<]*<\/(code|pre|a)>)', flags=re.A)
reddit_regex = re.compile('(^|\s|<p>)\/?((r|u)\/(\w|-){3,25})(?![^<]*<\/(code|pre|a)>)', flags=re.A)
sub_regex = re.compile('(^|\s|<p>)\/?(h\/(\w|-){3,25})(?![^<]*<\/(code|pre|a)>)', flags=re.A)

strikethrough_regex = re.compile('(^|\s|>)~{1,2}([^~]+)~{1,2}(?![^<]*<\/(code|pre|a)>)', flags=re.A)

mute_regex = re.compile("\/mute @?([a-z0-9_\-]{3,30}) ([0-9]+)", flags=re.A|re.I)

emoji_regex = re.compile(f"<p>\s*(:[!#@]{{0,3}}[{valid_username_chars}]+:\s*)+<\/p>", flags=re.A)
emoji_regex2 = re.compile(f'(?<!"):([!#@{valid_username_chars}]{{1,36}}?):(?![^<]*<\/(code|pre|a)>)', flags=re.A)
emoji_regex3 = re.compile(f'(?<!"):([!@{valid_username_chars}]{{1,35}}?):', flags=re.A)

snappy_url_regex = re.compile('<a href="(https?:\/\/.+?)".*?>(.+?)<\/a>', flags=re.A)
snappy_youtube_regex = re.compile('<lite-youtube videoid="(.+?)" params="autoplay=1', flags=re.A)

email_regex = re.compile(EMAIL_REGEX_PATTERN, flags=re.A)

utm_regex = re.compile('utm_[0-z]+=[0-z_]+&', flags=re.A)
utm_regex2 = re.compile('[?&]utm_[0-z]+=[0-z_]+', flags=re.A)

slur_regex = re.compile(f"<[^>]*>|{slur_single_words}", flags=re.I|re.A)
slur_regex_upper = re.compile(f"<[^>]*>|{slur_single_words.upper()}", flags=re.A)
profanity_regex = re.compile(f"<[^>]*>|{profanity_single_words}", flags=re.I|re.A)
profanity_regex_upper = re.compile(f"<[^>]*>|{profanity_single_words.upper()}", flags=re.A)

torture_regex = re.compile('(^|\s)(i|me) ', flags=re.I|re.A)
torture_regex2 = re.compile("(^|\s)i'm ", flags=re.I|re.A)
torture_regex_exclude = re.compile('^\s*>', flags=re.A)


image_check_regex = re.compile(f'!\[\]\(((?!(https:\/\/([a-z0-9-]+\.)*({hosts})\/|\/)).*?)\)', flags=re.A)

video_regex_extensions = '|'.join(VIDEO_FORMATS)
video_sub_regex = re.compile(f'(<p>[^<]*)(https:\/\/([a-z0-9-]+\.)*({hosts})\/[\w:~,()\-.#&\/=?@%;+]*?\.({video_regex_extensions}))', flags=re.A)

audio_regex_extensions = '|'.join(AUDIO_FORMATS)
audio_sub_regex = re.compile(f'(<p>[^<]*)(https:\/\/([a-z0-9-]+\.)*({hosts})\/[\w:~,()\-.#&\/=?@%;+]*?\.({audio_regex_extensions}))', flags=re.A)

image_regex_extensions = '|'.join(IMAGE_FORMATS)
image_regex = re.compile(f"(^|\s)(https:\/\/[\w\-.#&/=\?@%;+,:]{{5,250}}(\.|\?format=)({image_regex_extensions})((\?|&)[\w\-.#&/=\?@%;+,:]*)?)($|\s)", flags=re.I|re.A)
image_regex_extensions = image_regex_extensions.replace('|gif', '')
imgur_regex = re.compile(f'(https:\/\/i\.imgur\.com\/[a-z0-9]+)\.({image_regex_extensions})', flags=re.I|re.A)

giphy_regex = re.compile('(https:\/\/media\.giphy\.com\/media\/[a-z0-9]+\/giphy)\.gif', flags=re.I|re.A)

youtube_regex = re.compile('(<p>[^<]*)(https:\/\/youtube\.com\/watch\?[\w\-.#&/=?@%+]{7,})', flags=re.I|re.A)
yt_id_regex = re.compile('[a-z0-9-_]{5,20}', flags=re.I|re.A)

link_fix_regex = re.compile("(\[.*?\]\()(?!http|\/)(.*?\))(?!([^<]*<\/(code|pre|a)>|[^`]*`))", flags=re.A)

css_url_regex = re.compile('url\(\s*[\'"]?(.*?)[\'"]?\s*\)', flags=re.I|re.A)

marseybux_li = (0,2500,5000,10000,25000,50000,100000,250000)

linefeeds_regex = re.compile("([^\n])\n([^\n])", flags=re.A)

greentext_regex = re.compile("(\n|^)>([^ >][^\n]*)", flags=re.A)

ascii_only_regex = re.compile("[ -~]+", flags=re.A)

reddit_to_vreddit_regex = re.compile('(^|>|")https:\/\/old.reddit.com\/(r|u)\/', flags=re.A)
reddit_domain_regex = re.compile("(^|\s|\()https?:\/\/(reddit\.com|(?:(?:[A-z]{2})(?:-[A-z]{2})" "?|beta|i|m|pay|ssl|www|new|alpha)\.reddit\.com|libredd\.it|teddit\.net)\/(r|u)\/", flags=re.A)

color_regex = re.compile("[a-f0-9]{6}", flags=re.A)

# lazy match on the .*?, only match if there is trailing stuff
# Specifically match Snappy's way of formatting, this might break some losers' comments.
showmore_regex = re.compile(r"^(.*?</p>(?:</li></ul>)?)(\s*<p>.*)", flags=re.A|re.DOTALL)

search_token_regex = re.compile('"([^"]*)"|(\S+)', flags=re.A)

git_regex = re.compile("ref: (refs/.+)", flags=re.A)

pronouns_regex = re.compile("([a-z]{1,5})/[a-z]{1,5}(/[a-z]{1,5})?", flags=re.A|re.I)

knowledgebase_page_regex = re.compile("[a-zA-Z0-9_\-]+", flags=re.A)

html_title_regex = re.compile("<title>(.{1,200})</title>", flags=re.I)

def sub_matcher(match:re.Match, upper=False, replace_with:Union[dict[str, str], dict[str, List[str]]]=SLURS_FOR_REPLACING):
	group_num = 0
	match_str = match.group(group_num)
	if match_str.startswith('<'):
		return match_str
	else:
		repl = replace_with[match_str.lower()]
		return repl if not upper or "<img" in repl else repl.upper()

def sub_matcher_upper(match, replace_with:Union[dict[str, str], dict[str, List[str]]]=SLURS_FOR_REPLACING):
	return sub_matcher(match, upper=True, replace_with=replace_with)


# TODO: make censoring a bit better
def sub_matcher_slurs(match, upper=False):
	return sub_matcher(match, upper, replace_with=SLURS_FOR_REPLACING)

def sub_matcher_slurs_upper(match):
	return sub_matcher_slurs(match, upper=True)

def sub_matcher_profanities(match, upper=False):
	return sub_matcher(match, upper, replace_with=PROFANITIES)

def sub_matcher_profanities_upper(match):
	return sub_matcher_profanities(match, upper=True)

def censor_slurs(body:Optional[str], logged_user):
	if not body: return ""
	def replace_re(body:str, regex:re.Pattern, regex_upper:re.Pattern, sub_func, sub_func_upper):
		body = regex_upper.sub(sub_func_upper, body)
		return regex.sub(sub_func, body)

	if not logged_user or logged_user == 'chat' or logged_user.slurreplacer:
		body = replace_re(body, slur_regex, slur_regex_upper, sub_matcher_slurs, sub_matcher_slurs_upper)
	if SITE_NAME == 'rDrama':
		if not logged_user or logged_user == 'chat' or logged_user.profanityreplacer:
			body = replace_re(body, profanity_regex, profanity_regex_upper, sub_matcher_profanities, sub_matcher_profanities_upper)

	return body

def torture_ap(body, username):
	lines = body.splitlines(keepends=True)

	for i in range(len(lines)):
		if torture_regex_exclude.match(lines[i]):
			continue
		for k, l in AJ_REPLACEMENTS.items():
			lines[i] = lines[i].replace(k, l)
		lines[i] = torture_regex.sub(rf'\1@{username} ', lines[i])
		lines[i] = torture_regex2.sub(rf'\1@{username} is ', lines[i])

	return ''.join(lines).strip()


commands = {
	"fortune": FORTUNE_REPLIES,
	"factcheck": FACTCHECK_REPLIES,
	"8ball": EIGHTBALL_REPLIES,
	"roll": range(1, 10000)
}

command_regex = re.compile("(\s|^)#(fortune|factcheck|8ball|roll)", flags=re.A|re.I)

def command_regex_matcher(match, upper=False):
	result = str(choice(commands[match.group(2).lower()]))
	if match.group(2) == 'roll':
		color = tuple(choices(range(256), k=3))
		result = f'<b style="color:rgb{color}">Your roll: {result}</b>'
	return match.group(1) + result

reason_regex = re.compile('(/(post|comment)/[0-9]+)', flags=re.A)

discord_username_regex = re.compile("(\s|^|>).{2,32}#[0-9]{4}(?=[^0-9]|$)", flags=re.A)

numbered_list_regex = re.compile('((\s|^)[0-9]+)\. ', flags=re.A)
