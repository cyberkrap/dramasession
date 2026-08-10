from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Any

from sqlalchemy import func, or_

from files.classes import (
    AwardRelationship,
    Comment,
    Sub,
    SubJoin,
    Submission,
    User,
)
from files.helpers.config.awards import AWARDS, HOUSE_AWARDS
from files.helpers.config.const import (
    PERMS,
    TRUESCORE_CHUDRAMA_MINIMUM,
    TRUESCORE_CLUB_MINIMUM,
    TRUESCORE_MASTERBAITERS_MINIMUM,
)

from .config import CRAPPY_USERNAME
from .provider import CrappyToolDefinition


TOOL_TEXT_LIMIT = 4000
THREAD_ITEM_BODY_LIMIT = 1400
THREAD_ITEM_LIMIT = 30
AWARD_ITEM_LIMIT = 60


SITE_GUIDE = {
    "overview": (
        "The Obsession Club (TOC) is a multi-purpose forum/social platform. Its name and visual "
        "identity do not limit boards to Obsession-related topics. Users can create and discuss "
        "posts on boards, use profile walls, public chat, awards/economy features, and social/profile customizations."
    ),
    "boards": (
        "TOC communities are called boards in the UI. Board URLs use /h/<name> because the codebase "
        "historically calls them holes/subs. Boards can have their own sidebar, banners, icon/marsey art, "
        "custom CSS, memberships, followers, blocks, moderators, and exiles. Use get_board for live board details."
    ),
    "profiles": (
        "TOC profiles have public activity and profile-wall discussions and can display profile styling, "
        "badges, hats, signatures, titles, houses, patron status, and linked external accounts where configured. "
        "Use get_profile for live public profile data."
    ),
    "connections": (
        "Users manage linked accounts from Settings > Connections (/settings/connections). TOC supports verified "
        "provider connections for Spotify, GitHub, Discord, and Steam when the corresponding site integration is "
        "configured, plus manual public profile links for services including Bluesky, Reddit, Twitch, YouTube, X, "
        "Roblox, PlayStation, Xbox, Epic Games, and Battle.net. Each connection can be hidden from the public profile; "
        "supported direct Spotify/Steam connections can also expose live activity when enabled by the user."
    ),
    "awards": (
        "Awards are real objects attached to posts or comments and retain their award kind, giver, and time. "
        "Some are cosmetic while others apply site effects such as temporary bans, unbans, pins, posting "
        "constraints, or profile/account effects. Awards can be purchased directly or consumed from owned stock. "
        "Use get_comment/get_post for the live awards on specific content instead of guessing."
    ),
    "currencies": (
        "The user-facing TOC economy uses Wishcoins and Wishbux. In the inherited backend these are still "
        "named coins and marseybux in several models/routes. They are used across awards and other economy/game systems."
    ),
    "casino": (
        "TOC has native casino/game systems tied to the site economy. The exact live game state and balances "
        "should be treated as site data rather than invented by the model."
    ),
    "lottery": (
        "TOC has a native lottery with tickets, active lottery sessions, participant rankings, winner selection, "
        "and tracked user lottery statistics. The worker should not invent current draw/ticket state without a live tool."
    ),
    "chat": (
        "TOC has persistent public chat in addition to posts/comments. Chat is a separate live service/process "
        "with stored messages, quotes, mentions, moderation metadata, and permalink-style message anchors."
    ),
    "apps_api": (
        "TOC Apps/API uses OAuth applications and access tokens associated with user accounts. Authenticated app "
        "requests use the site's normal routes, with API-authored post/comment content marked as bot content unless privileged."
    ),
}


def _trim(value: str | None, limit: int) -> str:
    text = (value or "").strip()
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 20)].rstrip() + "\n[…truncated…]"


def _award_definition(kind: str) -> dict:
    if kind in AWARDS:
        return AWARDS[kind]
    if kind in HOUSE_AWARDS:
        return HOUSE_AWARDS[kind]
    return {"kind": kind, "title": kind, "description": ""}


def can_user_view_board(db, user: User, board: Sub | None) -> bool:
    if board is None:
        return True
    if user is None or user.shadowbanned:
        return False

    name = (board.name or "").lower()
    if name == "chudrama":
        if user.blacklisted_by or user.is_suspended_permanently:
            return False
        if user.admin_level >= PERMS["VIEW_CHUDRAMA"]:
            return True
        if int(user.truescore or 0) >= TRUESCORE_CHUDRAMA_MINIMUM:
            return True
        if user.agendaposter or user.patron:
            return True
        return False
    if name in {"countryclub", "splash_mountain"}:
        if user.blacklisted_by or user.is_suspended_permanently or user.agendaposter == 1:
            return False
        if user.admin_level >= PERMS["VIEW_CLUB"]:
            return True
        return int(user.truescore or 0) >= TRUESCORE_CLUB_MINIMUM
    if name == "masterbaiters":
        if user.blacklisted_by or user.is_suspended_permanently:
            return False
        return int(user.truescore or 0) >= TRUESCORE_MASTERBAITERS_MINIMUM

    if board.stealth:
        return bool(
            db.query(SubJoin.user_id)
            .filter(SubJoin.user_id == user.id, SubJoin.sub == board.name)
            .first()
        )
    return True


@dataclass
class CrappyToolbox:
    db: Any
    requester_id: int
    trigger_comment_id: int

    @property
    def definitions(self) -> tuple[CrappyToolDefinition, ...]:
        return (
            CrappyToolDefinition(
                name="get_current_toc_context",
                description=(
                    "Returns the current TOC comment, its post or profile-wall location, "
                    "the requester, IDs needed for follow-up lookups, and Crappy's own account state."
                ),
                parameters={"type": "object", "properties": {}},
            ),
            CrappyToolDefinition(
                name="get_comment",
                description=(
                    "Reads one requester-visible TOC comment by ID, including its author, body, "
                    "thread IDs, score, and the real awards attached to that comment. Use this "
                    "instead of guessing about awards or nearby comment state."
                ),
                parameters={
                    "type": "object",
                    "properties": {
                        "comment_id": {
                            "type": "integer",
                            "description": "Numeric TOC comment ID.",
                        }
                    },
                    "required": ["comment_id"],
                },
            ),
            CrappyToolDefinition(
                name="get_thread_context",
                description=(
                    "Returns up to 30 requester-visible comments from the same TOC thread as a "
                    "comment, with comment IDs, parent IDs, authors, bodies, and award summaries. "
                    "Use this for references like 'the comment above', earlier replies, or thread history."
                ),
                parameters={
                    "type": "object",
                    "properties": {
                        "comment_id": {
                            "type": "integer",
                            "description": "Any comment ID in the thread.",
                        }
                    },
                    "required": ["comment_id"],
                },
            ),
            CrappyToolDefinition(
                name="get_post",
                description=(
                    "Reads one requester-visible public TOC post by ID, including title, body, "
                    "author, board, score, comment count, and awards."
                ),
                parameters={
                    "type": "object",
                    "properties": {
                        "post_id": {"type": "integer", "description": "Numeric TOC post ID."}
                    },
                    "required": ["post_id"],
                },
            ),
            CrappyToolDefinition(
                name="get_profile",
                description=(
                    "Reads public TOC profile information for a username: bio, title, pronouns, "
                    "house, patron level, badges, counts, and suspension state. Private or hidden "
                    "profiles are not exposed."
                ),
                parameters={
                    "type": "object",
                    "properties": {
                        "username": {"type": "string", "description": "TOC username without @."}
                    },
                    "required": ["username"],
                },
            ),
            CrappyToolDefinition(
                name="get_board",
                description=(
                    "Reads one requester-visible TOC board by name, including its sidebar text and "
                    "member/follower counts. TOC calls these boards in the UI; legacy code may call them holes/subs."
                ),
                parameters={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Board name without /h/."}
                    },
                    "required": ["name"],
                },
            ),
            CrappyToolDefinition(
                name="get_toc_site_guide",
                description=(
                    "Returns TOC-native guidance for common site concepts. Use this when the user asks what "
                    "The Obsession Club is, what a feature is for, or how boards/profiles/awards/currencies/"
                    "casino/lottery/chat/Apps work at a high level. For live object state, use the object tools instead."
                ),
                parameters={
                    "type": "object",
                    "properties": {
                        "topic": {
                            "type": "string",
                            "enum": [
                                "overview", "boards", "profiles", "connections", "awards",
                                "currencies", "casino", "lottery", "chat", "apps_api"
                            ],
                            "description": "TOC feature area to explain."
                        }
                    },
                    "required": ["topic"],
                },
            ),
            CrappyToolDefinition(
                name="get_account_state",
                description=(
                    "Returns posting-relevant account state only for @Crappy or the requesting user, "
                    "including suspension, shadowban, and unban timing. Use this before making claims "
                    "about whether Crappy itself is banned or allowed to post."
                ),
                parameters={
                    "type": "object",
                    "properties": {
                        "username": {"type": "string", "description": "Either Crappy or the requester username."}
                    },
                    "required": ["username"],
                },
            ),
        )

    @property
    def requester(self) -> User:
        user = self.db.get(User, self.requester_id)
        if not user:
            raise ValueError("requesting user no longer exists")
        return user

    def _find_user(self, username: str) -> User | None:
        value = str(username or "").strip().lstrip("@").strip()
        if not value:
            return None
        return (
            self.db.query(User)
            .filter(func.lower(User.username) == value.lower())
            .order_by(User.id.asc())
            .first()
        )

    def _refresh_user(self, target: User) -> User:
        self.db.refresh(target)
        target.__dict__.pop("_lazy", None)
        return target

    def _public_profile(self, target: User) -> bool:
        requester = self.requester
        if target.shadowbanned and target.id != requester.id:
            return False
        if target.is_private and target.id != requester.id:
            return False
        return True

    def _public_post(self, post: Submission | None) -> bool:
        if not post or post.deleted_utc or post.is_banned or post.private:
            return False
        if not post.author or post.author.shadowbanned:
            return False
        if post.sub and not can_user_view_board(self.db, self.requester, post.subr):
            return False
        return True

    def _public_comment(self, comment: Comment | None) -> bool:
        if not comment or comment.deleted_utc or comment.is_banned:
            return False
        if not comment.author or comment.author.shadowbanned:
            return False
        if comment.parent_submission is not None:
            return self._public_post(comment.post)
        if comment.wall_user_id is not None:
            wall_owner = self.db.get(User, comment.wall_user_id)
            return bool(wall_owner and self._public_profile(wall_owner))
        return False

    def _awards(self, *, comment_id: int | None = None, post_id: int | None = None) -> dict:
        query = self.db.query(AwardRelationship)
        if comment_id is not None:
            query = query.filter(AwardRelationship.comment_id == comment_id)
        elif post_id is not None:
            query = query.filter(AwardRelationship.submission_id == post_id)
        else:
            return {"total": 0, "counts": {}, "given_by_requester": [], "items": []}

        rows = query.order_by(AwardRelationship.awarded_utc.asc(), AwardRelationship.id.asc()).all()
        items = []
        titles = []
        requester_titles = []
        for award in rows:
            definition = _award_definition(award.kind)
            title = str(definition.get("title") or award.kind)
            titles.append(title)
            if award.user_id == self.requester_id:
                requester_titles.append(title)

        for award in rows[:AWARD_ITEM_LIMIT]:
            definition = _award_definition(award.kind)
            title = str(definition.get("title") or award.kind)
            giver = self.db.get(User, award.user_id) if award.user_id else None
            giver_username = None
            if giver and (not giver.shadowbanned or giver.id == self.requester_id):
                giver_username = giver.username
            items.append(
                {
                    "kind": award.kind,
                    "title": title,
                    "description": str(definition.get("description") or ""),
                    "giver": giver_username,
                    "given_by_requester": award.user_id == self.requester_id,
                    "awarded_utc": award.awarded_utc,
                }
            )

        return {
            "total": len(rows),
            "counts": dict(Counter(titles)),
            "given_by_requester": requester_titles,
            "items": items,
            "truncated": len(rows) > AWARD_ITEM_LIMIT,
        }

    def _comment_payload(self, comment: Comment, compact: bool = False) -> dict:
        body_limit = THREAD_ITEM_BODY_LIMIT if compact else TOOL_TEXT_LIMIT
        return {
            "id": comment.id,
            "author": "👻" if comment.ghost else (comment.author.username if comment.author else None),
            "body": _trim(comment.body, body_limit),
            "created_utc": comment.created_utc,
            "parent_comment_id": comment.parent_comment_id,
            "parent_submission_id": comment.parent_submission,
            "wall_user_id": comment.wall_user_id,
            "top_comment_id": comment.top_comment_id,
            "level": int(comment.level or 1),
            "score": int(comment.upvotes or 0) - int(comment.downvotes or 0),
            "awards": self._awards(comment_id=comment.id),
        }

    def _post_payload(self, post: Submission) -> dict:
        return {
            "id": post.id,
            "title": _trim(post.title, 1000),
            "body": _trim(post.body, TOOL_TEXT_LIMIT),
            "author": "👻" if post.ghost else (post.author.username if post.author else None),
            "board": post.sub,
            "created_utc": post.created_utc,
            "score": int(post.upvotes or 0) - int(post.downvotes or 0),
            "comment_count": int(post.comment_count or 0),
            "over_18": bool(post.over_18),
            "permalink": post.shortlink,
            "awards": self._awards(post_id=post.id),
        }

    def execute(self, name: str, arguments: dict[str, Any]) -> Any:
        handlers = {
            "get_current_toc_context": self._get_current_context,
            "get_comment": self._get_comment,
            "get_thread_context": self._get_thread_context,
            "get_post": self._get_post,
            "get_profile": self._get_profile,
            "get_board": self._get_board,
            "get_toc_site_guide": self._get_toc_site_guide,
            "get_account_state": self._get_account_state,
        }
        handler = handlers.get(str(name or ""))
        if handler is None:
            raise ValueError(f"unknown Crappy tool: {name}")
        return handler(arguments or {})

    def _get_current_context(self, arguments: dict) -> dict:
        trigger = self.db.get(Comment, self.trigger_comment_id)
        if not self._public_comment(trigger):
            raise ValueError("current comment is no longer publicly visible")
        requester = self.requester
        crappy = self._find_user(CRAPPY_USERNAME)
        payload = {
            "requester": {"id": requester.id, "username": requester.username},
            "trigger_comment": self._comment_payload(trigger),
            "crappy_account": self._account_state_payload(crappy) if crappy else None,
        }
        if trigger.parent_submission is not None and self._public_post(trigger.post):
            payload["post"] = self._post_payload(trigger.post)
        elif trigger.wall_user_id is not None:
            owner = self.db.get(User, trigger.wall_user_id)
            payload["profile_wall"] = {
                "user_id": owner.id if owner else trigger.wall_user_id,
                "username": owner.username if owner else None,
            }
        return payload

    def _get_comment(self, arguments: dict) -> dict:
        comment_id = int(arguments.get("comment_id"))
        comment = self.db.get(Comment, comment_id)
        if not self._public_comment(comment):
            raise ValueError("comment is not available to this requester")
        return self._comment_payload(comment)

    def _get_thread_context(self, arguments: dict) -> dict:
        comment_id = int(arguments.get("comment_id"))
        anchor = self.db.get(Comment, comment_id)
        if not self._public_comment(anchor):
            raise ValueError("comment is not available to this requester")

        root_id = int(anchor.top_comment_id or anchor.id)
        query = (
            self.db.query(Comment)
            .filter(or_(Comment.id == root_id, Comment.top_comment_id == root_id))
            .order_by(Comment.created_utc.desc(), Comment.id.desc())
            .limit(THREAD_ITEM_LIMIT)
        )
        comments = [item for item in query.all() if self._public_comment(item)]
        comments.reverse()
        return {
            "anchor_comment_id": anchor.id,
            "root_comment_id": root_id,
            "comments": [self._comment_payload(item, compact=True) for item in comments],
            "returned": len(comments),
            "limit": THREAD_ITEM_LIMIT,
        }

    def _get_post(self, arguments: dict) -> dict:
        post_id = int(arguments.get("post_id"))
        post = self.db.get(Submission, post_id)
        if not self._public_post(post):
            raise ValueError("post is not available to this requester")
        return self._post_payload(post)

    def _get_profile(self, arguments: dict) -> dict:
        target = self._find_user(str(arguments.get("username") or ""))
        if target:
            target = self._refresh_user(target)
        if not target or not self._public_profile(target):
            raise ValueError("profile is not available to this requester")

        badges = []
        for badge in target.badges[:50]:
            badges.append({"id": badge.badge_id, "name": badge.name})

        return {
            "id": target.id,
            "username": target.username,
            "original_username": target.original_username,
            "bio": _trim(target.bio, TOOL_TEXT_LIMIT),
            "title": target.customtitleplain or target.customtitle,
            "pronouns": target.pronouns,
            "house": target.house,
            "patron_level": int(target.patron or 0),
            "created_utc": target.created_utc,
            "post_count": int(target.post_count or 0),
            "comment_count": int(target.comment_count or 0),
            "received_award_count": int(target.received_award_count or 0),
            "is_suspended": bool(target.is_suspended),
            "is_private": bool(target.is_private),
            "badges": badges,
            "profile_path": f"/@{target.username}",
        }

    def _get_board(self, arguments: dict) -> dict:
        name = str(arguments.get("name") or "").strip().replace("/h/", "").strip("/").lower()
        if not name:
            raise ValueError("board name is required")
        board = self.db.get(Sub, name)
        if not board or not can_user_view_board(self.db, self.requester, board):
            raise ValueError("board is not available to this requester")
        return {
            "name": board.name,
            "path": f"/h/{board.name}",
            "sidebar": _trim(board.sidebar, 8000),
            "member_count": int(board.join_num or 0),
            "follower_count": int(board.follow_num or 0),
            "is_stealth": bool(board.stealth),
        }

    def _get_toc_site_guide(self, arguments: dict) -> dict:
        topic = str(arguments.get("topic") or "").strip().lower()
        if topic not in SITE_GUIDE:
            raise ValueError("unknown TOC site-guide topic")
        return {"topic": topic, "guidance": SITE_GUIDE[topic]}

    def _account_state_payload(self, target: User) -> dict:
        target = self._refresh_user(target)
        return {
            "id": target.id,
            "username": target.username,
            "is_suspended": bool(target.is_suspended),
            "is_permanently_suspended": bool(target.is_suspended_permanently),
            "unban_utc": int(target.unban_utc or 0),
            "ban_reason": _trim(target.ban_reason, 1000) if target.is_suspended else None,
            "shadowbanned": bool(target.shadowbanned),
            "is_private": bool(target.is_private),
        }

    def _get_account_state(self, arguments: dict) -> dict:
        target = self._find_user(str(arguments.get("username") or ""))
        if not target:
            raise ValueError("account does not exist")
        requester = self.requester
        if target.id != requester.id and target.username.lower() != CRAPPY_USERNAME.lower():
            raise ValueError("account-state lookup is limited to Crappy and the requester")
        return self._account_state_payload(target)
