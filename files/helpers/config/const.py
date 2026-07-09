from enum import Enum, auto
from os import environ, path

import tldextract
import datetime

t = datetime.datetime.now()

fistmas_begin = datetime.datetime.strptime(f'1/12/{t.year}', '%d/%m/%Y')
fistmas_end = datetime.datetime.strptime(f'30/12/{t.year}', '%d/%m/%Y')
def IS_FISTMAS():
	return fistmas_begin < datetime.datetime.now() < fistmas_end

homoween_begin = datetime.datetime.strptime(f'15/10/{t.year}', '%d/%m/%Y')
homoween_end = datetime.datetime.strptime(f'1/11/{t.year}', '%d/%m/%Y')
def IS_HOMOWEEN():
	return homoween_begin < datetime.datetime.now() < homoween_end

DEFAULT_TIME_FILTER = "all"
DEFAULT_THEME = "midnight"
DEFAULT_COLOR = "805ad5"
SPAM_SIMILARITY_THRESHOLD = 0.5
SPAM_URL_SIMILARITY_THRESHOLD = 0.1
SPAM_SIMILAR_COUNT_THRESHOLD = 10
COMMENT_SPAM_SIMILAR_THRESHOLD = 0.5
COMMENT_SPAM_COUNT_THRESHOLD = 10
DISABLE_DOWNVOTES = False
DESCRIPTION = "rdrama.net caters to drama in all forms such as: Real life, videos, photos, gossip, rumors, news sites, Reddit, and Beyond™. There isn't drama we won't touch, and we want it all!"
EMAIL = f"rdrama@rdrama.net"
TELEGRAM_ID = ""

DEFAULT_CONFIG_VALUE = "blahblahblah"
SITE = environ.get("SITE").strip()
SITE_NAME = environ.get("SITE_NAME").strip()
SECRET_KEY = environ.get("SECRET_KEY").strip()
PROXY_URL = environ.get("PROXY_URL").strip()
LOG_DIRECTORY = environ.get("LOG_DIRECTORY")
SETTINGS_FILENAME = environ.get("SETTINGS_FILENAME")
GIPHY_KEY = environ.get("GIPHY_KEY").strip()
TURNSTILE_SITEKEY = environ.get("TURNSTILE_SITEKEY").strip()
TURNSTILE_SECRET = environ.get("TURNSTILE_SECRET").strip()
YOUTUBE_KEY = environ.get("YOUTUBE_KEY").strip()
VAPID_PUBLIC_KEY = environ.get("VAPID_PUBLIC_KEY").strip()
VAPID_PRIVATE_KEY = environ.get("VAPID_PRIVATE_KEY").strip()
DONATE_SERVICE = environ.get("DONATE_SERVICE").strip()
DONATE_LINK = environ.get("DONATE_LINK").strip()
CF_KEY = environ.get("CF_KEY").strip()
CF_ZONE = environ.get("CF_ZONE").strip()
GLOBAL = environ.get("GLOBAL", "").strip()
blackjack = environ.get("BLACKJACK", "").strip()
blackjack2 = environ.get("BLACKJACK2", "").strip()
FP = environ.get("FP", "").strip()
PROGSTACK_MUL = float(environ.get("PROGSTACK_MUL", 2.0))
ENCOURAGED = environ.get("ENCOURAGED", "").strip().split()
ENCOURAGED2 = environ.get("ENCOURAGED2", "").strip().split()

class Service(Enum):
	RDRAMA = auto()
	CHAT = auto()

CLOUDFLARE_COOKIE_VALUE = "yes." # remember to change this in CloudFlare too

DEFAULT_RATELIMIT = "3/second;30/minute;200/hour;1000/day"
DEFAULT_RATELIMIT_SLOWER = "1/second;30/minute;200/hour;1000/day"

PUSH_NOTIF_LIMIT = 1000

IS_LOCALHOST = SITE == "localhost" or SITE == "127.0.0.1" or SITE.startswith("192.168.") or SITE.endswith(".local")

if IS_LOCALHOST: SITE_FULL = 'http://' + SITE
else: SITE_FULL = 'https://' + SITE

LOGGED_IN_CACHE_KEY = f"{SITE}_loggedin"
LOGGED_OUT_CACHE_KEY = f"{SITE}_loggedout"
CHAT_ONLINE_CACHE_KEY = f"{SITE}_online"
REDDIT_NOTIFS_CACHE_KEY = "reddit_notifications"
MARSEYS_CACHE_KEY = "marseys"
EMOJIS_CACHE_KEY = "emojis"

SESSION_LIFETIME = 60 * 60 * 24 * 365

CASINO_RELEASE_DAY = 1662825600

AJ_REPLACEMENTS = {
	' your ': " you're ",
	' to ': " too ",

	' Your ': " You're ",
	' To ': " Too ",

	' YOUR ': " YOU'RE ",
	' TO ': " TOO ",

	'everyone': 'everypony',
	'everybody': 'everypony',

	'Everyone': 'Everypony',
	'Everybody': 'Everypony',

	'EVERYONE': 'EVERYPONY',
	'EVERYBODY': 'EVERYPONY',
}

SLURS = {
	"nigger": "BIPOC",
	"negroid": "BIPOC",
	" coon ": " BIPOC ",
	" coons ": " BIPOCs ",
	"niglet": 'BIPOClet',
	"negress": "BIPOCette",
	'nigga': 'neighbor',
	"faggot": "cute twink",
	"fag": "strag",
	"spic ": "hard-working American ",
	"spics": "hard-working Americans",
	"trannie": '<img loading="lazy" data-bs-toggle="tooltip" alt=":marseytrain:" title=":marseytrain:" src="/e/marseytrain.webp">',
	"tranny": '<img loading="lazy" data-bs-toggle="tooltip" alt=":marseytrain:" title=":marseytrain:" src="/e/marseytrain.webp">',
	"troon": '<img loading="lazy" data-bs-toggle="tooltip" alt=":marseytrain:" title=":marseytrain:" src="/e/marseytrain.webp">',
	"tranner": '<img loading="lazy" data-bs-toggle="tooltip" alt=":marseytrain:" title=":marseytrain:" src="/e/marseytrain.webp">',
	"kike": "jewish chad",
	"heeb": "jewish chad",
	"daisy's destruction": "Cars 2",
	"daisys destruction": "Cars 2",
	"daisy destruction": "Cars 2",
	"pajeet": "sexy Indian dude",
}

BAN_EVASION_DOMAIN = 'stupidpol.site'
BAN_EVASION_FULL = f'https://{BAN_EVASION_DOMAIN}'

patron = "Patron"

REDDIT_NOTIFS_SITE = set()
REDDIT_NOTIFS_USERS = {}

if len(SITE_NAME) > 5:
	REDDIT_NOTIFS_SITE.add(SITE_NAME.lower())

if not IS_LOCALHOST:
	REDDIT_NOTIFS_SITE.add(SITE)

if SITE_NAME == 'rDrama':
	DEFAULT_COLOR = "ff66ac"

	patron = "Paypig"

	TAGLINES = (
		"world's largest gay orgy",
		"world's largest shemale porn site",
		"world's largest cat fetish furfest",
		"world's largest basket-weaving forum",
		"world's largest autism support group",
		"the official site of Communist Party USA",
	)

	RDRAMA_SLURS = {
		"retarded": "r-slurred",
		"retard": "r-slur",
		"pedophile": "p-dophile",
		"kill youself": "keep yourself safe",
		"kill yourself": "keep yourself safe",
		"kill yourselves": "keep yourselves safe",
		"steve akins": "Dr. Penelope Verity Oaken",
		"steve joel akins": "Dr. Penelope Verity Oaken",
		"steven joel akins": "Dr. Penelope Verity Oaken",
		"latinos": "latinx",
		"latino": "latinx",
		"latinas": "latinx",
		"latina": "latinx",
		"hispanics": "latinx",
		"hispanic": "latinx",
		"i hate marsey": "i love marsey",
		"sodomite": "total dreamboat",
		"renter": "rentoid",
		"autistic": "neurodivergent",
		"i hate carp": "i love Carp",
		"gamer": "g*mer",
		"journalist": "journ*list",
		"journalism": "journ*lism",
		"elon musk": "Rocket Daddy",
		"fake and gay": "fake and straight",
		" rapist": " male feminist",
		" pedo ": " p-do ",
		" kys": " keep yourself safe",
		"kys ": "keep yourself safe ",
		"republican": 'rethuglican',
		"america": 'ameriKKKa',
		"it's almost as if": "I'm a retard but",
		"it's almost like": "I'm a retard but",
		"my brother in christ": "my brother in Allah",
		"kyle": "Kylie",
		"twitter files": 'twitter files <img loading="lazy" data-bs-toggle="tooltip" alt=":marseysleep:" title=":marseysleep:" src="/e/marseysleep.webp">',
		" cool (?!it)": " fetch ",
		"krayon": "krayon (sister toucher)",
		"discord": "groomercord",
		"allah(?! \()": "Allah (ﷻ)",
		"muhammad(?! \()": "Prophet Muhammad (ﷺ)"
	}
	SLURS.update(RDRAMA_SLURS)

	BOOSTED_SITES = {
		#youtube-like
		'bitchute.com',
		'goyimtv.tv',
		'odysee.com',

		#4chan-like
		'4chan.org',
		'boards.4channel.org',
		'boards.4chan.org',
		'archive.4plebs.org',
		'lolcow.farm',
		'8kun.top',
		'soyjak.party',
		'crystal.cafe',

		#forums
		'kiwifarms.net',
		'onionfarms.com',
		'clay.party',
		'tattle.life',
		'stormfront.org',
		'bluelight.org',
		'thecoli.com',
		'nairaland.com',
		'resetera.com',
		'steamcommunity.com',
		'lipstickalley.com',
		'tigerdroppings.com',
		'groups.google.com',
		'bungie.net',
		'gamefaqs.gamespot.com',
		'thefemaledatingstrategy.com',
		'econjobrumors.com',
		'incels.is',
		'looksmax.org',
		'sanctioned-suicide.org',

		#twitter-like
		'gab.com',
		'gettr.com',
		'parler.com',
		'truthsocial.com',
		'blacktwitterapp.com',
		'rdrama.cc',
		'marsey.club',
		'kiwifarms.cc',
		'freespeechextremist.com'
		'mstdn.social',
		'mastodon.social',
		'mastodon.online',
		'poa.st',
		'shitposter.club',
		'sneed.social',
		'seal.cafe',
		'trp.red',

		#nested-comments
		'news.ycombinator.com',
		'scored.co',
		'scrd.app',
		'steemit.com',
		'ovarit.com',
		'rdrama.net',
		BAN_EVASION_DOMAIN,
		'themotte.org',
		'hexbear.net',
		'cumtown.org',
		'hive.blog',
		'poal.co',
		'saidit.net',
		'lobste.rs',
		'retalk.com',
		'thepinkpill.co',
		'talk.lol',
		'lemmy.ml',
		'lemmygrad.ml',
		'raddle.me',
		'stacker.news',
		'tildes.net',
		'notabug.io',
		'syzitus.com',
		'phuks.co',
		'arete.network',
		'pcmemes.net',
		'discussions.app',
		'wolfballs.com',
		'dojo.press',
		'livefilter.com',
		'mainchan.com',
		'lesswrong.com',

		#misc
		'quora.com',
		'givesendgo.com',
		'groups.google.com',
		't.me',
		'web.telegram.org',
		'instagram.com',
		'facebook.com',
		'twitch.tv',
		'tiktok.com',
		'vm.tiktok.com',
		'github.com',
		'breitbart.com',
		'teamblind.com',
		'encyclopediadramatica.online',
		'datalounge.com',
		'metafilter.com',
		'sqwok.im',
		'thelayoff.com',
	}

	BOOSTED_HOLES = {
		'furry',
		'femboy',
		'anime',
		'gaybros',
		'againsthateholes',
		'masterbaiters',
		'changelog',
		'programming',
		'slackernews',
	}

	REDDIT_NOTIFS_SITE.add('marsey')
	REDDIT_NOTIFS_SITE.add('"r/drama"')
	REDDIT_NOTIFS_SITE.add('justice4darrell')
	REDDIT_NOTIFS_SITE.add('cringetopia.org')
elif SITE_NAME == 'WPD':
	TAGLINES = (
		"People dying and cartoon cats <3",
	)
	REDDIT_NOTIFS_SITE.update({'watchpeopledie', 'makemycoffin'})


SLURS_FOR_REPLACING = {}
for k, val in SLURS.items():
	SLURS_FOR_REPLACING[k.split('(')[0]] = val

PROFANITIES = {
	'motherfucker': 'motherlover',
	'fuck': 'frick',
	' ass ': ' butt ',
	'shitting': 'pooping',
	'damn': 'darn',
	'bitch ': 'b-word ',
	'toilet': 'potty',
	' asshole': ' butthole',
	' rape ': ' r*pe ',
	' hell ': ' heck ',
	' sex ': ' intercourse ',
	' cum ': ' c*m ',
	'orgasm': 'sexual climax',
	'dick': 'peepee',
	'cock ': 'peepee ',
	'cocks': 'peepees',
	'penis': 'peepee',
	'pussy': 'girl peepee',
	'pussies': 'girl peepees',
	'vagina': 'girl peepee',
	'cunt': 'girl peepee',
	' twat ': ' girl peepee ',
}

slur_single_words = "|".join([slur.lower() for slur in SLURS.keys()])
profanity_single_words = "|".join([profanity.lower() for profanity in PROFANITIES.keys()])

LONGPOST_REPLIES = ('Wow, you must be a JP fan.', 'This is one of the worst posts I have EVER seen. Delete it.', "No, don't reply like this, please do another wall of unhinged rant please.", '<h1>😴😴😴</h1>', "Ma'am we've been over this before. You need to stop.", "I've known more coherent downies.", "Your pulitzer's in the mail", "That's great and all, but I asked for my burger without cheese.", 'That degree finally paying off', "That's nice sweaty. Why don't you have a seat in the time out corner with Pizzashill until you calm down, then you can have your Capri Sun.", "All them words won't bring your pa back.", "You had a chance to not be completely worthless, but it looks like you threw it away. At least you're consistent.", 'Some people are able to display their intelligence by going on at length on a subject and never actually saying anything. This ability is most common in trades such as politics, public relations, and law. You have impressed me by being able to best them all, while still coming off as an absolute idiot.', "You can type 10,000 characters and you decided that these were the one's that you wanted.", 'Have you owned the libs yet?', "I don't know what you said, because I've seen another human naked.", 'Impressive. Normally people with such severe developmental disabilities struggle to write much more than a sentence or two. He really has exceded our expectations for the writing portion. Sadly the coherency of his writing, along with his abilities in the social skills and reading portions, are far behind his peers with similar disabilities.', "This is a really long way of saying you don't fuck.", "Sorry ma'am, looks like his delusions have gotten worse. We'll have to admit him.", 'If only you could put that energy into your relationships', 'Posts like this is why I do Heroine.', 'still unemployed then?', 'K', 'look im gunna have 2 ask u 2 keep ur giant dumps in the toilet not in my replys 😷😷😷', "Mommy is soooo proud of you, sweaty. Let's put this sperg out up on the fridge with all your other failures.", "Good job bobby, here's a star", "That was a mistake. You're about to find out the hard way why.", f'You sat down and wrote all this shit. You could have done so many other things with your life. What happened to your life that made you decide writing novels of bullshit here was the best option?', "I don't have enough spoons to read this shit", "All those words won't bring daddy back.", 'OUT!', "Damn, you're really mad over this, but thanks for the effort you put into typing that all out! Sadly I won't read it all.", "Jesse what the fuck are you talking about??", "▼you're fucking bananas if you think I'm reading all that, take my downvote and shut up idiot", "Are you feeling okay bud?", '<img loading="lazy" data-bs-toggle="tooltip" alt=":#marseywoah:" src="/e/marseywoah.webp" b title=":#marseywoah:">', 'At no point in your rambling, incoherent post were you even close to anything that could be considered a rational thought. Everyone on this site is now dumber for having read it. May God have mercy on your soul.', 'https://rdrama.net/videos/1671169024815045.mp4')

AGENDAPOSTER_PHRASE = 'trans lives matter'

AGENDAPOSTER_MSG = """Hi @{username},\n
Your {type} has been automatically removed because you forgot to include `{AGENDAPOSTER_PHRASE}`.\n
Don't worry, we're here to help! We won't let you post or comment anything that doesn't express your love and acceptance towards the trans community. Feel free to resubmit your {type} with `{AGENDAPOSTER_PHRASE}` included. \n
*This is an automated message; if you need help, you can message us [here](/contact).*"""

AGENDAPOSTER_MSG_HTML = """<p>Hi <a href="/id/{id}"><img loading="lazy" src="/pp/{id}">@{username}</a>,</p>
<p>Your {type} has been automatically removed because you forgot to include <code>{AGENDAPOSTER_PHRASE}</code>.</p>
<p>Don't worry, we're here to help! We won't let you post or comment anything that doesn't express your love and acceptance towards the trans community. Feel free to resubmit your {type} with <code>{AGENDAPOSTER_PHRASE}</code> included.</p>
<p><em>This is an automated message; if you need help, you can message us <a href="/contact">here</a>.</em></p>"""

PIN_AWARD_TEXT = " (pin award)"

THEMES = ["4chan","classic","classic_dark","coffee","dark","dramblr","light","midnight","tron","win98"]
BACKGROUND_CATEGORIES = ["glitter", "anime", "fantasy", "solarpunk", "pixelart"]
COMMENT_SORTS = ["hot", "new", "old", "top", "bottom", "controversial"]
SORTS = COMMENT_SORTS + ["bump", "comments"]
TIME_FILTERS = ["hour", "day", "week", "month", "year", "all"]
PAGE_SIZES = (10, 25, 50, 100)

################################################################################
### COLUMN INFO
################################################################################

SUB_NAME_COLUMN_LENGTH = 25
SUB_SIDEBAR_COLUMN_LENGTH = 10000
SUB_SIDEBAR_HTML_COLUMN_LENGTH = 20000
SUB_SIDEBAR_URL_COLUMN_LENGTH = 60
SUB_BANNER_URL_COLUMN_LENGTH = 60
SUB_CSS_COLUMN_LENGTH = 6000
SUB_MARSEY_URL_LENGTH = 60

################################################################################
### SITE SPECIFIC CONSTANTS
################################################################################

PERMS = { # Minimum admin_level to perform action.
	'CHAT': 0,
 	'HOLE_CREATE': 0,
 	'USER_BLOCKS_VISIBLE': 0,
 	'USER_FOLLOWS_VISIBLE': 0,
 	'USER_VOTERS_VISIBLE': 0,
 	'VIEW_PENDING_SUBMITTED_MARSEYS': 0,

 	'POST_COMMENT_INFINITE_PINGS': 1,
 	'POST_COMMENT_DISTINGUISH': 1,
 	'POST_BYPASS_REPOST_CHECKING': 1,
 	'POST_IN_GHOST_THREADS': 1,
 	'VIEW_CLUB': 1,
 	'VIEW_CHUDRAMA': 1,
 	'SITE_BYPASS_READ_ONLY_MODE': 1,
 	'SITE_BYPASS_UNDER_SIEGE_MODE': 1,
 	'SITE_WARN_ON_INVALID_AUTH': 1,
 	'NOTIFICATIONS_REDDIT': 1,
 	'NOTIFICATIONS_SPECIFIC_WPD_COMMENTS': 1,
 	'MESSAGE_BLOCKED_USERS': 1,
 	'ADMIN_MOP_VISIBLE': 1,
 	'ADMIN_HOME_VISIBLE': 1,
 	'FLAGS_REMOVE': 1,
 	'POST_COMMENT_MODERATION': 1,
 	'USER_BAN': 1,
 	'USER_SHADOWBAN': 1,
 	'USER_AGENDAPOSTER': 1,
 	'USER_MODERATION_TOOLS_VISIBLE': 1,
 	'VIEW_MODMAIL': 1,
 	'NOTIFICATIONS_MODMAIL': 1,
 	'VIEW_PRIVATE_PROFILES': 1,
 	'VIEW_ALTS': 1,
 	'VIEW_ACTIVE_USERS': 1,
 	'VIEW_ALT_VOTES': 1,
 	'VIEW_LAST_ACTIVE': 1,
 	'VIEW_VOTE_BUTTONS_ON_USER_PAGE': 1,
 	'NOTIFICATIONS_HOLE_INACTIVITY_DELETION': 1,
 	'NOTIFICATIONS_HOLE_CREATION': 1,
 	'NOTIFICATIONS_MODERATOR_ACTIONS': 1,

 	'POST_TO_CHANGELOG': 2,
 	'USER_BADGES': 2,
 	'USER_LINK': 2,
 	'USER_TITLE_CHANGE': 2,
 	'POST_TO_POLL_THREAD': 2,
 	'BUY_GHOST_AWARD': 2,
 	'LOTTERY_VIEW_PARTICIPANTS': 2,

 	'ADMIN_ADD': 3,
 	'ADMIN_REMOVE': 3,
 	'ADMIN_ACTIONS_REVERT': 3,
 	'DOMAINS_BAN': 3,
 	'EDIT_RULES': 3,
 	'POST_BETS': 3,
 	'POST_BETS_DISTRIBUTE': 3,
 	'VIEW_PENDING_SUBMITTED_HATS': 3,
 	'LOTTERY_ADMIN': 3,
 	'SITE_SETTINGS': 3,
 	'SITE_SETTINGS_SIDEBARS_BANNERS_BADGES': 3,
 	'SITE_SETTINGS_SNAPPY_QUOTES': 3,
 	'SITE_SETTINGS_UNDER_ATTACK': 3,
 	'SITE_CACHE_PURGE_CDN': 3,
 	'NOTIFICATIONS_FROM_SHADOWBANNED_USERS': 3,
 	'APPS_MODERATION': 3,

 	'MODERATE_PENDING_SUBMITTED_ASSETS': 4,

	'PROGSTACK': 5,

	'USER_BLACKLIST': 6,
 	'POST_EDITING': 6,
 	'UPDATE_ASSETS': 6,
 	'VIEW_PATRONS': 6,
 	'BLACKJACK_NOTIFICATIONS': 6,
 	'IGNORE_BADGE_BLACKLIST': 6,
	'UNDO_AWARD_PINS': 6,
 	'SEE_GHOST_VOTES': 6,
 	'MODS_EVERY_HOLE': 6,
 	'VIEW_DM_IMAGES': 6,
}

FEATURES = {
	'MARSEYS': True,
	'MARSEYBUX': True,
	'AWARDS': True,
	'CHAT': True,
	'PINS': True,
	'PRONOUNS': False,
	'BADGES': True,
	'HATS': True,
	'HOUSES': False,
	'GAMBLING': True,
	'WORDLE': True,
	'USERS_PROFILE_BANNER': True,
	'USERS_PROFILE_BODYTEXT': True,
	'USERS_PROFILE_SONG': True,
	'USERS_PERMANENT_WORD_FILTERS': False,
	'USERS_SUICIDE': True,
	'MARKUP_COMMANDS': True,
	'REPOST_DETECTION': True,
	'PATRON_ICONS': False,
	'ASSET_SUBMISSIONS': False,
	'NSFW_MARKING': True,
}

WERKZEUG_ERROR_DESCRIPTIONS = {
	400: "The browser (or proxy) sent a request that this server could not understand.",
	401: "The server could not verify that you are authorized to access the URL requested. You either supplied the wrong credentials (e.g. a bad password), or your browser doesn't understand how to supply the credentials required.",
	403: "You don't have the permission to access the requested resource. It is either read-protected or not readable by the server.",
	404: "The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again.",
	405: "The method is not allowed for the requested URL.",
	406: "The resource identified by the request is only capable of generating response entities which have content characteristics not acceptable according to the accept headers sent in the request.",
	409: "A conflict happened while processing the request. The resource might have been modified while the request was being processed.",
	410: "The requested URL is no longer available on this server and there is no forwarding address. If you followed a link from a foreign page, please contact the author of this page.",
	413: "The data value transmitted exceeds the capacity limit.",
	414: "The length of the requested URL exceeds the capacity limit for this server. The request cannot be processed.",
	415: "The server does not support the media type transmitted in the request.",
	417: "The server could not meet the requirements of the Expect header",
	418: "This server is a teapot, not a coffee machine",
	429: "This user has exceeded an allotted request count. Try again later.",
	500: "The server encountered an internal error and was unable to complete your request. Either the server is overloaded or there is an error in the application.",
}

ERROR_TITLES = {
	400: "Naughty Request",
	401: "🚫 Unauthorized 🚫",
	403: "Forbidden🙅‍♀️",
	404: "Not Found - where did it go?",
	405: "Method Not Allowed, BAD.",
	406: "Too Many Pings fuck off",
	409: "Cumflict",
	410: "Gone... and Forgotten",
	413: "Gayload Too Large",
	415: "Weird Media Type",
	418: "I'm a teapot",
	429: "Too Many Requests",
	500: "Balls-Deep Server Error",
}

ERROR_MSGS = {
	400: "That request was bad and you should feel bad.",
	401: "What you're trying to do requires an account. I think. The original error message said something about a castle and I hated that. If you see this error and you're logged into an account, something went pretty wrong somewhere.",
	403: "YOU AREN'T WELCOME HERE GO AWAY",
	404: "Someone typed something wrong and it was probably you, please do better.",
	405: "idk how anyone gets this error but if you see this, remember to follow @carpathianflorist<br>the original error text here talked about internet gremlins and wtf",
	406: "Max limit is 5 for comments and 50 for posts (what is it referring to? what does it mean? no one knows)",
	409: "There's a conflict between what you're trying to do and what you or someone else has done and because of that you can't do what you're trying to do. So maybe like... don't try and do that? Sorry not sorry",
	410: "You were too slow. The link FUCKING DIED. Request a new one and be more efficient.",
	413: "That's a heckin' chonker of a file! Please make it smaller or maybe like upload it somewhere else idk<BR>jc wrote this one hi jc!<br>- carp",
	415: "Please upload only Image, Video, or Audio files!",
	418: "this really shouldn't happen now that we autoconvert webm files but if it does there's a cool teapot marsey so there's that",
	429: "go spam somewhere else nerd",
	500: "Hiiiii it's carp! I think this error means that there's a timeout error. And I think that means something took too long to load so it decided not to work at all. If you keep seeing this on the same page <I>but not other pages</I>, then something is probably wrong with that specific function. It may not be called a function, but that sounds right to me. Anyway, <s>ping me and I'll whine to someone smarter to fix it. Don't bother them.</s> <B>After a year and a half of infuriating pings, the new instructions are to quit whining and just wait until it works again oh my god shut UP.</B><BR><BR> Thanks ily &lt;3",
}

ERROR_MARSEYS = {
	400: "marseybrainlet",
	401: "marseydead",
	403: "marseytroll",
	404: "marseyconfused",
	405: "marseyretard",
	406: "marseyrage",
	409: "marseynoyou",
	410: "marseyrave",
	413: "marseychonker2",
	415: "marseydetective",
	418: "marseytea",
	429: "marseyrentfree",
	500: "marseycarp3",
}

EMOJI_SRCS = ['files/assets/emojis.json']

PIN_LIMIT = 3
POST_RATE_LIMIT = '1/second;10/hour;20/day'
POST_TITLE_LENGTH_LIMIT = 500 # do not make larger than 500 without altering the table
POST_TITLE_HTML_LENGTH_LIMIT = 1500 # do not make larger than 1500 without altering the table
POST_BODY_LENGTH_LIMIT = 20000 # do not make larger than 20000 without altering the table
POST_BODY_HTML_LENGTH_LIMIT = 40000 # do not make larger than 40000 without altering the table
COMMENT_BODY_LENGTH_LIMIT = 10000 # do not make larger than 10000 characters without altering the table
COMMENT_BODY_HTML_LENGTH_LIMIT = 20000 # do not make larger than 20000 characters without altering the table
CSS_LENGTH_LIMIT = 10000 # do not make larger than 20000 characters without altering the table
COMMENT_MAX_DEPTH = 200
TRANSFER_MESSAGE_LENGTH_LIMIT = 200 # do not make larger than 10000 characters (comment limit) without altering the table
MIN_REPOST_CHECK_URL_LENGTH = 9 # also change the constant in checkRepost() of submit.js
CHAT_LENGTH_LIMIT = 1000
SUB_BANNER_LIMIT = 10

COSMETIC_AWARD_COIN_AWARD_PCT = 0.10

TRUESCORE_CHAT_MINIMUM = 0
TRUESCORE_DONATE_MINIMUM = 100
TRUESCORE_GHOST_MINIMUM = 0
TRUESCORE_CHUDRAMA_MINIMUM = 1488
TRUESCORE_CLUB_MINIMUM = 1000
TRUESCORE_MASTERBAITERS_MINIMUM = 100

LOGGEDIN_ACTIVE_TIME = 15 * 60
PFP_DEFAULT_MARSEY = True
NEW_USER_HAT_AGE = 0 # seconds of age to show new-user forced hat
NOTIFICATION_SPAM_AGE_THRESHOLD = 0.5 * 86400
COMMENT_SPAM_LENGTH_THRESHOLD = 50
UNDER_SIEGE_AGE_THRESHOLD = 10 * 60

HOLE_NAME = 'hole'
HOLE_STYLE_FLAIR = False
HOLE_REQUIRED = False
HOLE_COST = 0
HOLE_INACTIVITY_DELETION = False

PRIVILEGED_USER_BOTS = ()

AUTOJANNY_ID = 1
SNAPPY_ID = 2
LONGPOSTBOT_ID = 3
ZOZBOT_ID = 4
PIZZASHILL_ID = 0
IMPASSIONATA_ID = 0
PROGSTACK_ID = 4

CARP_ID = 0
AEVANN_ID = 0
SNAKES_ID = 0
JUSTCOOL_ID = 0
LAWLZ_ID = 0
TGTW_ID = 0
IDIO_ID = 0
SNALLY_ID = 0

MODMAIL_ID = 2
GIFT_NOTIF_ID = 5
SIGNUP_FOLLOW_ID = 0

POLL_THREAD = 0
POLL_BET_COINS = 200
POLL_MAX_OPTIONS = 20
WELCOME_MSG = f"Welcome to {SITE_NAME}!"

LOTTERY_TICKET_COST = 12
LOTTERY_SINK_RATE = 3
LOTTERY_DURATION = 60 * 60 * 24 * 7

SIDEBAR_THREAD = 0
BANNER_THREAD = 0
BADGE_THREAD = 0
SNAPPY_THREAD = 0
NOTIFICATION_THREAD = 1

MAX_IMAGE_SIZE_BANNER_RESIZED_MB = 1
MAX_IMAGE_AUDIO_SIZE_MB = 8
MAX_IMAGE_AUDIO_SIZE_MB_PATRON = 16
MAX_VIDEO_SIZE_MB = 32
MAX_VIDEO_SIZE_MB_PATRON = 64
MAX_IMAGE_CONVERSION_TIMEOUT = 30 # seconds

ANTISPAM_BYPASS_IDS = set()

PAGE_SIZE = 25
LEADERBOARD_LIMIT = PAGE_SIZE

HOUSE_JOIN_COST = 500
HOUSE_SWITCH_COST = 2000

TIERS_ID_TO_NAME = {
	1: "Paypig",
	2: "Renthog",
	3: "Landchad",
	4: "Terminally online turboautist",
	5: "JIDF Bankroller",
	6: "Rich Bich",
}

BADGE_BLACKLIST = { # only grantable by admins higher than PERMS['IGNORE_BADGE_BLACKLIST']
	1, 2, 6, 10, 11, 12, # Alpha, Verified Email, Beta, Recruiter x3
	16, 17, 143, 21, 22, 23, 24, 25, 26, 27, # Marsey Artist x3 / Patron Tiers
	94, 95, 96, 97, 98, 109, 67, 68, 83, 84, 87, 90, 179, 185, # Award Status except Y'all-seeing eye
	137, # Lottery Winner
}

NOTIFIED_USERS = {}
DONT_SHADOWBAN = {}

if SITE == 'rdrama.net':
	TELEGRAM_ID = "rdramanet"
	DEFAULT_TIME_FILTER = "day"

	FEATURES['PRONOUNS'] = True
	FEATURES['HOUSES'] = True
	FEATURES['USERS_PERMANENT_WORD_FILTERS'] = True
	FEATURES['ASSET_SUBMISSIONS'] = True
	PERMS['ADMIN_ADD'] = 4

	SIDEBAR_THREAD = 37696
	BANNER_THREAD = 37697
	BADGE_THREAD = 37833
	SNAPPY_THREAD = 37749
	NOTIFICATION_THREAD = 6489

	TRUESCORE_CHAT_MINIMUM = 10
	TRUESCORE_GHOST_MINIMUM = 10
	NEW_USER_HAT_AGE = 7 * 86400

	HOLE_COST = 50000
	HOLE_INACTIVITY_DELETION = True

	PRIVILEGED_USER_BOTS = (12125,16049)

	AUTOJANNY_ID = 1046
	SNAPPY_ID = 261
	LONGPOSTBOT_ID = 1832
	ZOZBOT_ID = 1833
	PIZZASHILL_ID = 2424
	IMPASSIONATA_ID = 5800
	PROGSTACK_ID = 15531
	CARP_ID = 995
	AEVANN_ID = 1
	SNAKES_ID = 10288
	JUSTCOOL_ID = 4999
	LAWLZ_ID = 3833
	TGTW_ID = 2008
	IDIO_ID = 30
	SNALLY_ID = 3336

	NOTIFIED_USERS = {
		'aevan': AEVANN_ID,
		'avean': AEVANN_ID,
		' capy': AEVANN_ID,
		'carp': CARP_ID,
		'clit': CARP_ID,
		'snakes': SNAKES_ID,
		'sneks': SNAKES_ID,
		'snekky': SNAKES_ID,
		'snekchad': SNAKES_ID,
		'jc': JUSTCOOL_ID,
		'justcool': JUSTCOOL_ID,
		'lawlz': LAWLZ_ID,
		'transgirltradwife': TGTW_ID,
		'impassionata': IMPASSIONATA_ID,
		'pizzashill': PIZZASHILL_ID,

		'joan': 28,
		'pewkie': 28,
		'idio3': IDIO_ID,
		'idio ': IDIO_ID,
		'telegram ': IDIO_ID,
		'the_homocracy': 147,
		'donger': 541,
		'geese': 1710,
		'soren': 2546,
		'marseyismywaifu': 3377,
		'mimw': 3377,
		'heymoon': 3635,
		'jollymoon': 3635,
		'chiobu': 5214,
		'mccox': 8239,
		'snus': 5646,
	}

	ANTISPAM_BYPASS_IDS = {1703, 13427}

	DONT_SHADOWBAN = {253,3161,11163}

	GIFT_NOTIF_ID = CARP_ID

	POLL_THREAD = 79285

	WELCOME_MSG = "Hi there! It's me, your soon-to-be favorite rDrama user @carpathianflorist here to give you a brief rundown on some of the sick features we have here. You'll probably want to start by following me, though. So go ahead and click my name and then smash that Follow button. This is actually really important, so go on. Hurry.\n\nThanks!\n\nNext up: If you're a member of the media, similarly just shoot me a DM and I'll set about verifying you and then we can take care of your sad journalism stuff.\n\n**FOR EVERYONE ELSE**\n\n Begin by navigating to [the settings page](/settings/profile) (we'll be prettying this up so it's less convoluted soon, don't worry) and getting some basic customization done.\n\n### Themes\n\nDefinitely change your theme right away, the default one (Midnight) is pretty enough, but why not use something *exotic* like Win98, or *flashy* like Tron? Even Coffee is super tasteful and way more fun than the default. More themes to come when we get around to it!\n\n### Avatar/pfp\n\nYou'll want to set this pretty soon. Set the banner too while you're at it. Your profile is important!\n\n### Flairs\n\nSince you're already on the settings page, you may as well set a flair, too. As with your username, you can - obviously - choose the color of this, either with a hex value or just from the preset colors. And also like your username, you can change this at any time. Paypigs can even further relive the glory days of 90s-00s internet and set obnoxious signatures.\n\n### PROFILE ANTHEMS\n\nSpeaking of profiles, hey, remember MySpace? Do you miss autoplaying music assaulting your ears every time you visited a friend's page? Yeah, we brought that back. Enter a YouTube URL, wait a few seconds for it to process, and then BAM! you've got a profile anthem which people cannot mute. Unless they spend 20,000 dramacoin in the shop for a mute button. Which you can then remove from your profile by spending 40,000 dramacoin on an unmuteable anthem. Get fucked poors!\n\n### Dramacoin?\n\nDramacoin is basically our take on the karma system. Except unlike the karma system, it's not gay and boring and stupid and useless. Dramacoin can be spent at [Marsey's Dramacoin Emporium](/shop) on upgrades to your user experience (many more coming than what's already listed there), and best of all on tremendously annoying awards to fuck with your fellow dramautists. We're always adding more, so check back regularly in case you happen to miss one of the announcement posts.\n\nLike karma, dramacoin is obtained by getting upvotes on your threads and comments. *Unlike* karma, it's also obtained by getting downvotes on your threads and comments. Downvotes don't really do anything here - they pay the same amount of dramacoin and they increase thread/comment ranking just the same as an upvote. You just use them to express petty disapproval and hopefully start a fight. Because all votes are visible here. To hell with your anonymity.\n\nDramacoin can also be traded amongst users from their profiles. Note that there is a 3% transaction fee.\n\n### Badges\n\nRemember all those neat little metallic icons you saw on my profile when you were following me? If not, scroll back up and go have a look. And doublecheck to make sure you pressed the Follow button. Anyway, those are badges. You earn them by doing a variety of things. Some of them even offer benefits, like discounts at the shop. A [complete list of badges and their requirements can be found here](/badges), though I add more pretty regularly, so keep an eye on the [changelog](/h/changelog).\n\n### Other stuff\n\nWe're always adding new features, and we take a fun-first approach to development. If you have a suggestion for something that would be fun, funny, annoying - or best of all, some combination of all three - definitely make a thread about it. Or just DM me if you're shy. Weirdo. Anyway there's also the [leaderboards](/leaderboard), boring stuff like two-factor authentication you can toggle on somewhere in the settings page (psycho), the ability to save posts and comments, more than a thousand emojis already (most of which are rDrama originals), and on and on and on and on. This is just the basics, mostly to help you get acquainted with some of the things you can do here to make it more easy on the eyes, customizable, and enjoyable. If you don't enjoy it, just go away! We're not changing things to suit you! Get out of here loser! And no, you can't delete your account :na:\n\nI love you.<br>*xoxo Carp* 💋"

	REDDIT_NOTIFS_USERS = {
		'idio3': IDIO_ID,
		'aevann': AEVANN_ID,
		'carpflo': CARP_ID,
		'carpathianflorist': CARP_ID,
		'carpathian florist': CARP_ID,
		'the_homocracy': 147,
		'justcool393': JUSTCOOL_ID
	}
elif SITE == 'watchpeopledie.tv':
	EMAIL = f"wpd@watchpeopledie.tv"
	TELEGRAM_ID = "wpdtv"
	DEFAULT_TIME_FILTER = "day"

	DESCRIPTION = "People die and this is the place to see it. You only have one life, don't make the mistakes seen here."

	PIN_LIMIT = 4
	WELCOME_MSG = """Hi, you! Welcome to WatchPeopleDie.tv, this really cool site where you can go to watch people die. I'm @CLiTPEELER! If you have any questions about how things work here, or suggestions on how to make them work better than they already do, definitely slide on into my DMs (no fat chicks).\nThere's an enormously robust suite of fun features we have here and we're always looking for more to add. Way, way too many to go over in an automated welcome message. And you're probably here for the videos of people dying more than any sort of weird, paradoxical digital community aspect anyway, so I won't bore you with a tedious overview of them. Just head on over to [your settings page](https://watchpeopledie.tv/settings/profile) and have a look at some of the basic profile stuff, at least. You can change your profile picture, username, flair, colors, banners, bio, profile anthem (autoplaying song on your page, like it's MySpace or some shit, hell yeah), CSS, all sorts of things.\nOr you can just go back to the main feed and carry on with watching people die. That's what the site is for, after all. Have fun!\nAnyway, in closing, WPD is entirely open source. We don't really need new full-time coders or anything, but if you'd like to take a look at our repo - or even submit a PR to change, fix, or add some things - go right ahead! Our codebase lives at https://fsdfsd.net/rDrama/rDrama\nWell, that's all. Thanks again for signing up. It's an automated message and all, but I really do mean that. Thank you, specifically. I love you. Romantically. Deeply. Passionately.\nHave fun!"""

	FEATURES['PATRON_ICONS'] = True
	FEATURES['NSFW_MARKING'] = False

	PERMS['HOLE_CREATE'] = 2
	PERMS['POST_EDITING'] = 2
	PERMS['ADMIN_ADD'] = 4
	PERMS['USER_BLACKLIST'] = 6

	SUB_BANNER_LIMIT = 69420
	POLL_MAX_OPTIONS = 50

	ERROR_TITLES.update({
		400: "Bad Request",
		401: "Unauthorized",
		403: "Not Found",
		404: "Not Found",
		405: "Method Not Allowed",
		406: "Too Many Pings",
		409: "Mortal Conflict",
		410: "Dead",
		413: "Payload Too Large",
		415: "Unsupported Media Type",
		500: "Internal Server Error",
	})

	ERROR_MSGS.update({
		400: "That request is invalid.",
		401: "You need to login or sign up to do that.",
		403: "That wasn't found",
		404: "That wasn't found.",
		405: "You can't use this method here... if you keep getting this error tell us it's prolly something borked.",
		409: "There's a conflict between what you're trying to do and what you or someone else has done and because of that you can't do what you're trying to do.",
		410: "This link is dead. Request a new one to try again.",
		413: "You need to upload a smaller file please.",
		429: "Please wait a bit before doing that.",
	})

	ERROR_MARSEYS[403] = "marseyconfused"

	POLL_THREAD = 13225

	SIDEBAR_THREAD = 5403
	BANNER_THREAD = 9869

	TRUESCORE_CHAT_MINIMUM = 10
	TRUESCORE_GHOST_MINIMUM = 10

	HOLE_NAME = 'flair'
	HOLE_STYLE_FLAIR = True
	HOLE_REQUIRED = True

	AUTOJANNY_ID = 1
	SNAPPY_ID = 3
	LONGPOSTBOT_ID = 4
	ZOZBOT_ID = 5

	CARP_ID = 48
	AEVANN_ID = 9
	SNAKES_ID = 32

	GIFT_NOTIF_ID = CARP_ID
	SIGNUP_FOLLOW_ID = CARP_ID

	TIERS_ID_TO_NAME = {
		1: "Victim",
		2: "Corpse",
		3: "Zombie",
		4: "Ghost",
		5: "Survivor",
		6: "Jigsaw"
	}

else: # localhost or testing environment implied
	FEATURES['ASSET_SUBMISSIONS'] = True
	FEATURES['PRONOUNS'] = True
	FEATURES['HOUSES'] = True
	FEATURES['USERS_PERMANENT_WORD_FILTERS'] = True
	SUB_BANNER_LIMIT = 69420

HOUSES = ("None","Furry","Femboy","Vampire","Racist") if FEATURES['HOUSES'] else ("None")

bots = {AUTOJANNY_ID, SNAPPY_ID, LONGPOSTBOT_ID, ZOZBOT_ID}

COLORS = {'ff66ac','805ad5','62ca56','38a169','80ffff','2a96f3','eb4963','ff0000','f39731','30409f','3e98a7','e4432d','7b9ae4','ec72de','7f8fa6', 'f8db58','8cdbe6', DEFAULT_COLOR}

### COMMENT NOTIFICATIONS ###

FORTUNE_REPLIES = ('<b style="color:#6023f8">Your fortune: Allah Wills It</b>','<b style="color:#d302a7">Your fortune: Inshallah, Only Good Things Shall Come To Pass</b>','<b style="color:#e7890c">Your fortune: Allah Smiles At You This Day</b>','<b style="color:#7fec11">Your fortune: Your Bussy Is In For A Blasting</b>','<b style="color:#43fd3b">Your fortune: You Will Be Propositioned By A High-Tier Twink</b>','<b style="color:#9d05da">Your fortune: Repent, You Have Displeased Allah And His Vengeance Is Nigh</b>','<b style="color:#f51c6a">Your fortune: Reply Hazy, Try Again</b>','<b style="color:#00cbb0">Your fortune: lmao you just lost 100 coins</b>','<b style="color:#2a56fb">Your fortune: Yikes 😬</b>','<b style="color:#0893e1">Your fortune: You Will Be Blessed With Many Black Bulls</b>','<b style="color:#16f174">Your fortune: NEETmax, The Day Is Lost If You Venture Outside</b>','<b style="color:#fd4d32">Your fortune: A Taste Of Jannah Awaits You Today</b>','<b style="color:#bac200">Your fortune: Watch Your Back</b>','<b style="color:#6023f8">Your fortune: Outlook good</b>','<b style="color:#d302a7">Your fortune: Godly Luck</b>','<b style="color:#e7890c">Your fortune: Good Luck</b>','<b style="color:#7fec11">Your fortune: Bad Luck</b>','<b style="color:#43fd3b">Your fortune: Good news will come to you by mail</b>','<b style="color:#9d05da">Your fortune: Very Bad Luck</b>','<b style="color:#00cbb0">Your fortune: ｷﾀ━━━━━━(ﾟ∀ﾟ)━━━━━━ !!!!</b>','<b style="color:#2a56fb">Your fortune: Better not tell you now</b>','<b style="color:#0893e1">Your fortune: You will meet a dark handsome stranger</b>','<b style="color:#16f174">Your fortune: （　´_ゝ`）ﾌｰﾝ</b>','<b style="color:#fd4d32">Your fortune: Excellent Luck</b>','<b style="color:#bac200">Your fortune: Average Luck</b>')
FACTCHECK_REPLIES = ('<b style="color:#6023f8">Factcheck: This claim has been confirmed as correct by experts. </b>','<b style="color:#d302a7">Factcheck: This claim has been classified as misogynistic.</b>','<b style="color:#e7890c">Factcheck: This claim is currently being debunked.</b>','<b style="color:#7fec11">Factcheck: This claim is 100% true.</b>','<b style="color:#9d05da">Factcheck: This claim hurts trans lives.</b>','<b style="color:#f51c6a">Factcheck: [REDACTED].</b>','<b style="color:#00cbb0">Factcheck: This claim is both true and false.</b>','<b style="color:#2a56fb">Factcheck: You really believe that shit? Lmao dumbass nigga 🤣</b>','<b style="color:#0893e1">Factcheck: None of this is real.</b>','<b style="color:#16f174">Factcheck: Yes.</b>','<b style="color:#fd4d32">Factcheck: This claim has not been approved by experts.</b>','<b style="color:#bac200">Factcheck: This claim is a gross exageration of reality.</b>','<b style="color:#ff2200">Factcheck: WARNING! THIS CLAIM HAS BEEN CLASSIFIED AS DANGEROUS. PLEASE REMAIN STILL, AN AGENT WILL COME TO MEET YOU SHORTLY.</b>')
EIGHTBALL_REPLIES = ('<b style="color:#7FEC11">The 8-Ball Says: It is certain.</b>', '<b style="color:#7FEC11">The 8-Ball Says: It is decidedly so.</b>', '<b style="color:#7FEC11">The 8-Ball Says: Without a doubt.</b>', '<b style="color:#7FEC11">The 8-Ball Says: Yes definitely.</b>', '<b style="color:#7FEC11">The 8-Ball Says: You may rely on it.</b>', '<b style="color:#7FEC11">The 8-Ball Says: As I see it, yes.</b>', '<b style="color:#7FEC11">The 8-Ball Says: Most likely.</b>', '<b style="color:#7FEC11">The 8-Ball Says: Outlook good.</b>', '<b style="color:#7FEC11">The 8-Ball Says: Yes.</b>', '<b style="color:#7FEC11">The 8-Ball Says: Signs point to yes.</b>', '<b style="color:#E7890C">The 8-Ball Says: Reply hazy, try again.</b>', '<b style="color:#E7890C">The 8-Ball Says: Ask again later.</b>', '<b style="color:#E7890C">The 8-Ball Says: Better not tell you now.</b>', '<b style="color:#E7890C">The 8-Ball Says: Cannot predict now.</b>', '<b style="color:#E7890C">The 8-Ball Says: Concentrate and ask again.</b>', '<b style="color:#FD4D32">The 8-Ball Says: Don\'t count on it.</b>', '<b style="color:#FD4D32">The 8-Ball Says: My reply is no.</b>', '<b style="color:#FD4D32">The 8-Ball Says: My sources say no.</b>', '<b style="color:#FD4D32">The 8-Ball Says: Outlook not so good.</b>', '<b style="color:#FD4D32">The 8-Ball Says: Very doubtful.</b>')


### END COMMENT NOTIFICATIONS ###

discounts = {
	# Big Spender badges, 2pp additive discount each
	69: 0.02,
	70: 0.02,
	71: 0.02,
	72: 0.02,
	73: 0.02,
	# Lootbox badges, 1pp additive discount each
	76: 0.01,
	77: 0.01,
	78: 0.01,
}

CF_HEADERS = {"Authorization": f"Bearer {CF_KEY}", "Content-Type": "application/json"}

WORDLE_LIST = ('aaron','about','above','abuse','acids','acres','actor','acute','adams','added','admin','admit','adopt','adult','after','again','agent','aging','agree','ahead','aimed','alarm','album','alert','alias','alice','alien','align','alike','alive','allah','allan','allen','allow','alloy','alone','along','alpha','alter','amber','amend','amino','among','angel','anger','angle','angry','anime','annex','annie','apart','apple','apply','april','areas','arena','argue','arise','armed','armor','array','arrow','aruba','ascii','asian','aside','asked','asset','atlas','audio','audit','autos','avoid','award','aware','awful','babes','bacon','badge','badly','baker','balls','bands','banks','barry','based','bases','basic','basin','basis','batch','baths','beach','beads','beans','bears','beast','beats','began','begin','begun','being','belle','belly','below','belts','bench','berry','betty','bible','bikes','bills','billy','bingo','birds','birth','bitch','black','blade','blair','blake','blame','blank','blast','blend','bless','blind','blink','block','blogs','blond','blood','bloom','blues','board','boats','bobby','bonds','bones','bonus','boobs','books','boost','booth','boots','booty','bored','bound','boxed','boxes','brain','brake','brand','brass','brave','bread','break','breed','brian','brick','bride','brief','bring','broad','broke','brook','brown','bruce','brush','bryan','bucks','buddy','build','built','bunch','bunny','burke','burns','burst','buses','busty','butts','buyer','bytes','cabin','cable','cache','cakes','calif','calls','camel','camps','canal','candy','canon','cards','carey','cargo','carlo','carol','carry','cases','casey','casio','catch','cause','cedar','cells','cents','chain','chair','chaos','charm','chart','chase','cheap','cheat','check','chess','chest','chevy','chick','chief','child','chile','china','chips','choir','chose','chris','chuck','cindy','cisco','cited','civic','civil','claim','clara','clark','class','clean','clear','clerk','click','cliff','climb','clips','clock','clone','close','cloth','cloud','clubs','coach','coast','cocks','codes','cohen','coins','colin','colon','color','combo','comes','comic','condo','congo','const','coral','corps','costa','costs','could','count','court','cover','crack','craft','craig','craps','crash','crazy','cream','creek','crest','crime','crops','cross','crowd','crown','crude','cubic','curve','cyber','cycle','czech','daddy','daily','dairy','daisy','dance','danny','dated','dates','david','davis','deals','dealt','death','debug','debut','decor','delay','delhi','delta','dense','depot','depth','derby','derek','devel','devil','devon','diana','diane','diary','dicke','dicks','diego','diffs','digit','dildo','dirty','disco','discs','disks','dodge','doing','dolls','donna','donor','doors','doubt','dover','dozen','draft','drain','rDrama','drawn','draws','dream','dress','dried','drill','drink','drive','drops','drove','drugs','drums','drunk','dryer','dubai','dutch','dying','dylan','eagle','early','earth','ebony','ebook','eddie','edgar','edges','egypt','eight','elder','elect','elite','ellen','ellis','elvis','emacs','email','emily','empty','ended','endif','enemy','enjoy','enter','entry','epson','equal','error','essay','essex','euros','evans','event','every','exact','exams','excel','exist','extra','faced','faces','facts','fails','fairy','faith','falls','false','fancy','fares','farms','fatal','fatty','fault','favor','fears','feeds','feels','fence','ferry','fever','fewer','fiber','fibre','field','fifth','fifty','fight','filed','files','filme','films','final','finds','fired','fires','firms','first','fixed','fixes','flags','flame','flash','fleet','flesh','float','flood','floor','flour','flows','floyd','fluid','flush','flyer','focal','focus','folks','fonts','foods','force','forge','forms','forth','forty','forum','found','frame','frank','fraud','fresh','front','frost','fruit','fully','funds','funky','funny','fuzzy','gains','games','gamma','gates','gauge','genes','genre','ghana','ghost','giant','gifts','girls','given','gives','glass','glenn','globe','glory','gnome','goals','going','gonna','goods','gotta','grace','grade','grain','grams','grand','grant','graph','grass','grave','great','greek','green','grill','gross','group','grove','grown','grows','guard','guess','guest','guide','guild','hairy','haiti','hands','handy','happy','harry','haven','hayes','heads','heard','heart','heath','heavy','helen','hello','helps','hence','henry','herbs','highs','hills','hindu','hints','hired','hobby','holds','holes','holly','homes','honda','honey','honor','hoped','hopes','horny','horse','hosts','hotel','hours','house','human','humor','icons','idaho','ideal','ideas','image','inbox','index','india','indie','inner','input','intel','inter','intro','iraqi','irish','isaac','islam','issue','italy','items','ivory','jacob','james','jamie','janet','japan','jason','jeans','jenny','jerry','jesse','jesus','jewel','jimmy','johns','joins','joint','jokes','jones','joyce','judge','juice','julia','julie','karen','karma','kathy','katie','keeps','keith','kelly','kenny','kenya','kerry','kevin','kills','kinda','kinds','kings','kitty','klein','knife','knock','known','knows','kodak','korea','label','labor','laden','lakes','lamps','lance','lands','lanes','lanka','large','larry','laser','later','latex','latin','laugh','laura','layer','leads','learn','lease','least','leave','leeds','legal','lemon','leone','level','lewis','lexus','light','liked','likes','limit','linda','lined','lines','links','linux','lions','lists','lived','liver','lives','lloyd','loads','loans','lobby','local','locks','lodge','logan','logic','login','logos','looks','loops','loose','lopez','lotus','louis','loved','lover','loves','lower','lucas','lucia','lucky','lunch','lycos','lying','lyric','macro','magic','mails','maine','major','maker','makes','males','malta','mambo','manga','manor','maple','march','marco','mardi','maria','marie','mario','marks','mason','match','maybe','mayor','mazda','meals','means','meant','medal','media','meets','menus','mercy','merge','merit','merry','metal','meter','metro','meyer','miami','micro','might','milan','miles','milfs','mills','minds','mines','minor','minus','mixed','mixer','model','modem','modes','money','monte','month','moore','moral','moses','motel','motor','mount','mouse','mouth','moved','moves','movie','mpegs','msgid','multi','music','myers','nails','naked','named','names','nancy','nasty','naval','needs','nepal','nerve','never','newer','newly','niger','night','nikon','noble','nodes','noise','nokia','north','noted','notes','notre','novel','nurse','nylon','oasis','occur','ocean','offer','often','older','olive','omaha','omega','onion','opens','opera','orbit','order','organ','oscar','other','ought','outer','owned','owner','oxide','ozone','packs','pages','paint','pairs','panel','panic','pants','paper','papua','paris','parks','parts','party','pasta','paste','patch','paths','patio','paxil','peace','pearl','peers','penis','penny','perry','perth','peter','phase','phone','photo','phpbb','piano','picks','piece','pills','pilot','pipes','pitch','pixel','pizza','place','plain','plane','plans','plant','plate','plays','plaza','plots','poems','point','poker','polar','polls','pools','porno','ports','posts','pound','power','press','price','pride','prime','print','prior','prize','probe','promo','proof','proud','prove','proxy','pulse','pumps','punch','puppy','purse','pussy','qatar','queen','query','quest','queue','quick','quiet','quilt','quite','quote','races','racks','radar','radio','raise','rally','ralph','ranch','randy','range','ranks','rapid','rated','rates','ratio','reach','reads','ready','realm','rebel','refer','rehab','relax','relay','remix','renew','reply','reset','retro','rhode','rider','rides','ridge','right','rings','risks','river','roads','robin','robot','rocks','rocky','roger','roles','rolls','roman','rooms','roots','roses','rouge','rough','round','route','rover','royal','rugby','ruled','rules','rural','safer','sagem','saint','salad','salem','sales','sally','salon','samba','samoa','sandy','santa','sanyo','sarah','satin','sauce','saudi','saved','saver','saves','sbjct','scale','scary','scene','scoop','scope','score','scott','scout','screw','scuba','seats','seeds','seeks','seems','sells','sends','sense','serum','serve','setup','seven','shade','shaft','shake','shall','shame','shape','share','shark','sharp','sheep','sheer','sheet','shelf','shell','shift','shine','ships','shirt','shock','shoes','shoot','shops','shore','short','shots','shown','shows','sides','sight','sigma','signs','silly','simon','since','singh','sites','sixth','sized','sizes','skill','skins','skirt','skype','slave','sleep','slide','slope','slots','sluts','small','smart','smell','smile','smith','smoke','snake','socks','solar','solid','solve','songs','sonic','sorry','sorts','souls','sound','south','space','spain','spank','sparc','spare','speak','specs','speed','spell','spend','spent','sperm','spice','spies','spine','split','spoke','sport','spots','spray','squad','stack','staff','stage','stamp','stand','stars','start','state','stats','stays','steal','steam','steel','steps','steve','stick','still','stock','stone','stood','stops','store','storm','story','strap','strip','stuck','study','stuff','style','sucks','sudan','sugar','suite','suits','sunny','super','surge','susan','sweet','swift','swing','swiss','sword','syria','table','tahoe','taken','takes','tales','talks','tamil','tampa','tanks','tapes','tasks','taste','taxes','teach','teams','tears','teddy','teens','teeth','tells','terms','terry','tests','texas','texts','thank','thats','theft','their','theme','there','these','thick','thing','think','third','thong','those','three','throw','thumb','tiger','tight','tiles','timer','times','tions','tired','tires','title','today','token','tokyo','tommy','toner','tones','tools','tooth','topic','total','touch','tough','tours','tower','towns','toxic','trace','track','tract','tracy','trade','trail','train','trans','trash','treat','trees','trend','trial','tribe','trick','tried','tries','trips','trout','truck','truly','trunk','trust','truth','tubes','tulsa','tumor','tuner','tunes','turbo','turns','tvcom','twice','twiki','twins','twist','tyler','types','ultra','uncle','under','union','units','unity','until','upper','upset','urban','usage','users','using','usual','utils','valid','value','valve','vault','vegas','venue','verde','verse','video','views','villa','vinyl','viral','virus','visit','vista','vital','vocal','voice','volvo','voted','votes','vsnet','wages','wagon','wales','walks','walls','wanna','wants','waste','watch','water','watts','waves','wayne','weeks','weird','wells','welsh','wendy','whale','whats','wheat','wheel','where','which','while','white','whole','whore','whose','wider','width','wiley','winds','wines','wings','wired','wires','witch','wives','woman','women','woods','words','works','world','worry','worse','worst','worth','would','wound','wrist','write','wrong','wrote','xanax','xerox','xhtml','yacht','yahoo','yards','years','yeast','yemen','yield','young','yours','youth','yukon','zones','gypsy','etika','funko','abort','gabby','soros','twink','biden','janny','chapo','4chan','tariq','tweet','trump','bussy','sneed','chink','nigga','wigga','caulk','putin','negus','gussy','soren')

christian_emojis = [':#marseyjesus:',':#marseyimmaculate:',':#marseymothermary:',
	':#marseyfatherjoseph:',':#gigachadorthodox:',':#marseyorthodox:',':#marseyorthodoxpat:',
	':#marseycrucified:',':#chadjesus:',':#marseyandjesus:',':#marseyjesus2:',
	':#marseyorthodoxsmug:',':#marseypastor:',':#marseypope:',]

ADMIGGER_THREADS = {SIDEBAR_THREAD, BANNER_THREAD, BADGE_THREAD, SNAPPY_THREAD}

proxies = {"http":PROXY_URL,"https":PROXY_URL}

approved_embed_hosts = {
	### GENERAL PRINCIPLES #####################################################
	# 0) The goal is to prevent user info leaks. Worst is a username + IP.
	# 1) Cannot point to a server controlled by a site user.
	# 2) Cannot have open redirects based on query string. (tightest constraint)
	# 3) #2 but pre-stored, ex: s.lain.la 302 with jannie DM attack.
	### TODO: Run a media proxy and kill most of these. Impossible to review.

	### First-Party
	SITE,
	'rdrama.net',
	BAN_EVASION_DOMAIN,
	'watchpeopledie.tv',
	'fsdfsd.net',

	### Third-Party Image Hosts
	# TODO: Might be able to keep these even if we media proxy?
	'imgur.com', # possibly restrict to i.imgur.com
	'pomf2.lain.la', # DO NOT generalize to lain.la. s.lain.la open redirect
	'giphy.com', # used by the GIF Modal
	'tenor.com',
	'gfycat.com',
	'postimg.cc', # WPD chat seems to like it
	'files.catbox.moe',
	'b1.thefileditch.ch',
	's1.fileditch.ch',

	### Third-Party Media
	# TODO: Preferably kill these. Media proxy.
	# DO NOT ADD: wordpress.com, wp.com (maybe) | Or frankly anything. No more.
	'redd.it', # disconcerting surface size {i, preview, external-preview, &c} but believed safe
	'redditmedia.com', # similar to above
	'twimg.com',
	'pinimg.com',
	'kiwifarms.net', # how sure are we Jersh doesn't have an open redirect?
	'upload.wikimedia.org',
	'staticflickr.com',
	'substackcdn.com',
	'wixmp.com', # image CDN: deviantart, others?
	'kym-cdn.com',
	'tumblr.com', # concerningly broad.
	'ytimg.com',
	'yt3.ggpht.com',

	### Third-Party Resources (For e.g. Profile Customization)
	# TODO: Any reasonable way to proxy these instead?
	'use.typekit.net', # Adobe font CDN
	'p.typekit.net', # Adobe font CDN
	'fonts.googleapis.com', # Google font CDN
	'githubusercontent.com', # using repos as media sources. no obvious exploit
	'kindpng.com',
	'pngfind.com',
}


def is_site_url(url):
	return (url
		and '\\' not in url
		and ((url.startswith('/') and not url.startswith('//'))
			or url.startswith(f'{SITE_FULL}/')))

def is_safe_url(url):
	domain = tldextract.extract(url)
	return (is_site_url(url)
		or domain.registered_domain in approved_embed_hosts
		or domain.fqdn in approved_embed_hosts)


hosts = "|".join(approved_embed_hosts).replace('.','\.')

tiers={
	"(Paypig)": 1,
	"(Renthog)": 2,
	"(Landchad)": 3,
	"(Terminally online turboautist)": 4,
	"(Marsey's Sugar Daddy)": 5,
	"(JIDF Bankroller)": 6,
	"(Rich Bich)": 7,
	"(LlamaBean)": 1,
	"(Victim)": 1,
	"(Corpse)": 2,
	"(Zombie)": 3,
	"(Ghost)": 4,
	"(Survivor)": 5,
	"(Jigsaw)": 6,
	}

has_sidebar = path.exists(f'files/templates/sidebar_{SITE_NAME}.html')
has_logo = path.exists(f'files/assets/images/{SITE_NAME}/logo.webp')

forced_hats = {
	"rehab": ("Roulette", "I'm a recovering ludomaniac!"),
	"progressivestack": ("Attention Whore", "I won the oppression olympics!"),
	"longpost": ("The Pizzashill", "We need to get rid of the character limit!"),
	"bird": ("Bluecheck", "Three sentences is too much for me..."),
	"marseyawarded": ("Three Lil Marseys", ":marseynotes: :marseynotes: :I prefer to speak in cats:"),
	"bite": ("Vampire Mask", "When other little girls wanted to be ballet dancers I kind of wanted to be a vampire."),
	"rainbow": ("Globohomo", "Homosexuality is no longer optional!"),
	"owoify": ("Cat Ears (wiggly)", "Nuzzles, pounces on you, UwU, you're so warm!.."),
	"earlylife": ("The Merchant", "SHUT IT DOWN, the goys know!"),
	"marsify": ("Marsified", "I can't pick my own Marseys, help!"),
	"is_suspended": ("Behind Bars", "This user is banned and needs to do better!"),
	"agendaposter": (("Egg_irl", "This user is getting in touch with xir identity!"),
				("Trans Flag", "Just in case you forgot, trans lives matter."),
				("Trans Flag II", "Your egg is cracked; wear it with pride!"),
				("Pride Flag", "Never forget that this is a primarily gay community. Dude bussy lmao."),
				("Pride Flag II", "This user is a proud supporter of LGBTQ+ rights."))

}

EMAIL_REGEX_PATTERN = '[A-Za-z0-9._%+-]{1,64}@[A-Za-z0-9.-]{2,63}\.[A-Za-z]{2,63}'

IMAGE_FORMATS = ('png','gif','jpg','jpeg','webp')
VIDEO_FORMATS = ('mp4','webm','mov','avi','mkv','flv','m4v','3gp')
AUDIO_FORMATS = ('mp3','wav','ogg','aac','m4a','flac')

if not IS_LOCALHOST and SECRET_KEY == DEFAULT_CONFIG_VALUE:
	from warnings import warn
	warn("Secret key is the default value! Please change it to a secure random number. Thanks <3", RuntimeWarning)
