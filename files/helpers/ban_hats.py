import html
import re
import time

from flask import g

from files.classes import AwardRelationship, Comment, ModAction, Submission, User
from files.helpers.config.const import SITE_NAME
from files.helpers.lazy import lazy


BAN_HAT_PATHS = {
	"grass": "/i/Obsession/ban-hats/grass.svg",
	"award": "/i/Obsession/ban-hats/award.svg",
	"underage": "/i/Obsession/ban-hats/underage.svg",
	"temporary": "/i/Obsession/ban-hats/temporary.svg",
	"permanent": "/i/Obsession/ban-hats/permanent.svg",
}

_INSTALLED = False


def _plain_text(value):
	text = re.sub(r"<[^>]+>", "", value or "")
	return html.unescape(text).strip()


def _ban_kind(user):
	reason = _plain_text(user.ban_reason).lower()
	if reason.startswith("grass award used by"):
		return "grass"
	if reason.startswith("1-day ban award used by") or reason.startswith("ban award used by"):
		return "award"
	if "underage" in reason or "under age" in reason or re.search(r"\bminor\b", reason):
		return "underage"
	if user.unban_utc:
		return "temporary"
	return "permanent"


def _latest_award(user, kind):
	post_award = g.db.query(AwardRelationship).join(
		Submission,
		AwardRelationship.submission_id == Submission.id,
	).filter(
		AwardRelationship.kind == kind,
		Submission.author_id == user.id,
	).order_by(
		AwardRelationship.awarded_utc.desc(),
		AwardRelationship.created_utc.desc(),
	).first()

	comment_award = g.db.query(AwardRelationship).join(
		Comment,
		AwardRelationship.comment_id == Comment.id,
	).filter(
		AwardRelationship.kind == kind,
		Comment.author_id == user.id,
	).order_by(
		AwardRelationship.awarded_utc.desc(),
		AwardRelationship.created_utc.desc(),
	).first()

	candidates = [award for award in (post_award, comment_award) if award]
	if not candidates:
		return None
	return max(candidates, key=lambda award: (award.awarded_utc or award.created_utc or 0, award.id or 0))


def _latest_admin_ban(user):
	return g.db.query(ModAction).filter(
		ModAction.kind == "ban_user",
		ModAction.target_user_id == user.id,
	).order_by(ModAction.created_utc.desc(), ModAction.id.desc()).first()


def _display_date(timestamp):
	if not timestamp:
		return ""
	return time.strftime("%Y-%m-%d", time.gmtime(timestamp))


def _award_source(award):
	if not award:
		return ""
	if award.comment_id:
		return f"/comment/{award.comment_id}"
	if award.submission_id:
		return f"/post/{award.submission_id}"
	return ""


def _build_ban_display(user):
	if not user.is_suspended:
		return None

	kind = _ban_kind(user)
	actor = None
	timestamp = None
	reason = ""

	if kind in {"grass", "award"}:
		award_kind = "grass" if kind == "grass" else "ban"
		award = _latest_award(user, award_kind)
		actor = award.user if award else None
		timestamp = (award.awarded_utc or award.created_utc) if award else None
		label = "Grass award" if kind == "grass" else "Ban award"
		reason = label
		if actor:
			reason += f" used by @{actor.username}"
		source = _award_source(award)
		if source:
			reason += f" on {source}"
		prefix = "Banned for"
	else:
		action = _latest_admin_ban(user)
		actor = action.user if action and action.user else user.banned_by
		timestamp = action.created_utc if action else None
		reason = _plain_text(user.ban_reason) or "No reason provided"
		prefix = f"Banned by @{actor.username} for" if actor else "Banned by site administration for"

	details = reason
	date = _display_date(timestamp)
	if date:
		details += f" (@{user.username} - {date})"

	if user.unban_utc:
		duration = f" - {user.unban_string}"
	else:
		duration = " permanently"

	return {
		"kind": kind,
		"hat": BAN_HAT_PATHS[kind],
		"message": f'{prefix} "{details}"{duration}',
		"actor": actor,
		"timestamp": timestamp,
	}


def install_ban_hat_support():
	global _INSTALLED
	if _INSTALLED or SITE_NAME != "Obsession":
		return

	original_hat_active = User.hat_active
	original_ban = User.ban

	@lazy
	def ban_display(self):
		return _build_ban_display(self)

	@property
	def ban_notice(self):
		display = self.ban_display
		return display["message"] if display else ""

	@property
	def ban_display_actor(self):
		display = self.ban_display
		return display["actor"] if display else None

	@lazy
	def hat_active(self, viewer):
		if self.is_suspended:
			display = self.ban_display
			if display:
				return display["hat"], display["message"]
		return original_hat_active(self, viewer)

	def ban(self, admin=None, reason=None, days=0.0):
		if not days:
			self.unban_utc = 0
		result = original_ban(self, admin=admin, reason=reason, days=days)
		self.__dict__.pop("_lazy", None)
		return result

	User.ban_display = property(ban_display)
	User.ban_notice = ban_notice
	User.ban_display_actor = ban_display_actor
	User.hat_active = hat_active
	User.ban = ban
	_INSTALLED = True
