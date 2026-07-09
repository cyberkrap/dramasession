import time

from flask import g

from files.classes.user import User
from files.helpers.alerts import send_repeatable_notification
from files.helpers.config.const import bots, patron, SITE_NAME

def award_timers(v, bot=False):
	now = time.time()

	def notify_if_not_bot(msg):
		if not bot:
			send_repeatable_notification(v.id, msg)

	if v.patron_utc and v.patron_utc < now:
		v.patron = 0
		v.patron_utc = 0
		notify_if_not_bot(f"Your {patron} status has expired!")
	if v.unban_utc and v.unban_utc < now:
		v.is_banned = None
		v.unban_utc = 0
		v.ban_reason = None
		notify_if_not_bot("You have been unbanned!")
	if v.agendaposter and v.agendaposter != 1 and v.agendaposter < now:
		v.agendaposter = 0
		v.chudded_by = None
		notify_if_not_bot("Your chud status has expired!")
		badge = v.has_badge(28)
		if badge: g.db.delete(badge)
	if v.flairchanged and v.flairchanged < now:
		v.flairchanged = None
		notify_if_not_bot("Your flair lock has expired. You can now change your flair!")
		badge = v.has_badge(96)
		if badge: g.db.delete(badge)
	if v.marseyawarded and v.marseyawarded < now:
		v.marseyawarded = None
		notify_if_not_bot("Your marsey award has expired!")
		badge = v.has_badge(98)
		if badge: g.db.delete(badge)
	if v.longpost and v.longpost < now:
		v.longpost = None
		notify_if_not_bot("Your pizzashill award has expired!")
		badge = v.has_badge(97)
		if badge: g.db.delete(badge)
	if v.bird and v.bird < now:
		v.bird = None
		notify_if_not_bot("Your bird site award has expired!")
		badge = v.has_badge(95)
		if badge: g.db.delete(badge)
	if v.progressivestack and v.progressivestack != 1 and v.progressivestack < now:
		v.progressivestack = None
		notify_if_not_bot("Your progressive stack has expired!")
		badge = v.has_badge(94)
		if badge: g.db.delete(badge)
	if v.rehab and v.rehab < now:
		v.rehab = None
		notify_if_not_bot("Your rehab has finished!")
		badge = v.has_badge(109)
		if badge: g.db.delete(badge)
	if v.deflector and v.deflector < now:
		v.deflector = None
		notify_if_not_bot("Your deflector has expired!")
	if v.owoify and v.owoify < now:
		v.owoify = None
		notify_if_not_bot("Your OwOify status has expired!")
		badge = v.has_badge(167)
	if v.bite and v.bite < now:
		v.bite = None
		notify_if_not_bot("Your vampire status has ended!")
		v.house = v.old_house
		v.old_house = ''
		badge = v.has_badge(168)
		if badge: g.db.delete(badge)
	if v.earlylife and v.earlylife < now:
		v.earlylife = None
		notify_if_not_bot("Your earlylife status has expired!")
		badge = v.has_badge(169)
		if badge: g.db.delete(badge)
	if v.marsify and v.marsify != 1 and v.marsify < now:
		v.marsify = 0
		if SITE_NAME != 'rDrama': notify_if_not_bot("Your marsify status has expired!")
		badge = v.has_badge(170)
		if badge: g.db.delete(badge)
	if v.rainbow and v.rainbow < now:
		v.rainbow = None
		notify_if_not_bot("Your rainbow has expired!")
		badge = v.has_badge(171)
		if badge: g.db.delete(badge)
	if v.spider and v.spider != 1 and v.spider < now:
		v.spider = 0
		notify_if_not_bot("Your spider friend has left you!")
		badge = v.has_badge(179)
		if badge: g.db.delete(badge)

	g.db.add(v)


def award_timers_bots_task():
	accs = g.db.query(User).filter(User.id.in_(bots))
	for u in accs:
		award_timers(u, bot=True)
