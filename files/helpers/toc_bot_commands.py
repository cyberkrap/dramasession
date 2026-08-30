import random
import re
import secrets
from dataclasses import dataclass
from typing import Callable, Optional

from sqlalchemy import func

from files.classes.user import User


TOC_BOT_PREFIX = ","
TOC_BOT_USERNAME = "OneWishBot"


@dataclass(frozen=True)
class TOCBotCommand:
    name: str
    category: str
    description: str
    syntax: str
    example: str
    aliases: tuple[str, ...] = ()
    permission: str = "Everyone"

    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "category": self.category,
            "description": self.description,
            "syntax": self.syntax,
            "example": self.example,
            "aliases": list(self.aliases),
            "permission": self.permission,
        }


@dataclass(frozen=True)
class TOCBotCommandResult:
    command: TOCBotCommand
    response: str


_COMMANDS = (
    TOCBotCommand(
        "commands",
        "information",
        "Show the TOC-native command directory.",
        ",commands",
        ",commands",
        aliases=("help",),
    ),
    TOCBotCommand(
        "ping",
        "information",
        "Check whether One Wish Bot is responding in TOC public chat.",
        ",ping",
        ",ping",
    ),
    TOCBotCommand(
        "userinfo",
        "information",
        "Show public TOC account information for a user.",
        ",userinfo [@username]",
        ",userinfo @cyberkrap",
        aliases=("user", "whois"),
    ),
    TOCBotCommand(
        "avatar",
        "information",
        "Get a user's current TOC profile picture.",
        ",avatar [@username]",
        ",avatar @cyberkrap",
        aliases=("pfp",),
    ),
    TOCBotCommand(
        "balance",
        "information",
        "Show a user's public Wishcoin and Wishbux balances.",
        ",balance [@username]",
        ",balance",
        aliases=("coins", "wallet"),
    ),
    TOCBotCommand(
        "stats",
        "information",
        "Open The Obsession Club's site statistics.",
        ",stats",
        ",stats",
    ),
    TOCBotCommand(
        "leaderboard",
        "information",
        "Open TOC's leaderboard directory.",
        ",leaderboard",
        ",leaderboard",
        aliases=("lb",),
    ),
    TOCBotCommand(
        "8ball",
        "fun",
        "Ask the magic 8-ball a question.",
        ",8ball <question>",
        ",8ball will the movie be good?",
        aliases=("eightball",),
    ),
    TOCBotCommand(
        "coinflip",
        "fun",
        "Flip a coin.",
        ",coinflip",
        ",coinflip",
        aliases=("flip",),
    ),
    TOCBotCommand(
        "roll",
        "fun",
        "Roll dice. Supports a side count or NdM notation.",
        ",roll [sides|NdM]",
        ",roll 2d20",
        aliases=("dice",),
    ),
    TOCBotCommand(
        "choose",
        "fun",
        "Choose randomly between two or more options separated with |.",
        ",choose <option> | <option> [| ...]",
        ",choose Obsession | The Backrooms",
        aliases=("pick",),
    ),
    TOCBotCommand(
        "rate",
        "fun",
        "Rate something from 0 to 100.",
        ",rate <thing>",
        ",rate my post",
    ),
)

_COMMAND_BY_NAME = {command.name: command for command in _COMMANDS}
for _command in _COMMANDS:
    for _alias in _command.aliases:
        _COMMAND_BY_NAME[_alias] = _command


_EIGHT_BALL = (
    "It is certain.",
    "Without a doubt.",
    "Most likely.",
    "Signs point to yes.",
    "Yes.",
    "Ask again later.",
    "Cannot predict now.",
    "Don't count on it.",
    "My reply is no.",
    "Very doubtful.",
)


def get_toc_bot_commands() -> list[dict]:
    """Return the public TOC command manifest used by both docs and execution."""
    return [command.as_dict() for command in _COMMANDS]


def parse_toc_bot_command(text: str) -> Optional[tuple[TOCBotCommand, str]]:
    """Parse only TOC-native comma commands; Discord command metadata is separate."""
    candidate = (text or "").strip()
    if not candidate.startswith(TOC_BOT_PREFIX):
        return None

    match = re.fullmatch(r",([a-z0-9][a-z0-9_-]*)(?:\s+(.*))?", candidate, re.IGNORECASE | re.DOTALL)
    if not match:
        return None

    command = _COMMAND_BY_NAME.get(match.group(1).lower())
    if not command:
        return None
    return command, (match.group(2) or "").strip()


def ensure_one_wish_bot_account(db) -> User:
    """Ensure TOC chat replies have a real, persistent first-party bot identity."""
    user = (
        db.query(User)
        .filter(func.lower(User.username) == TOC_BOT_USERNAME.lower())
        .order_by(User.id.asc())
        .first()
    )
    if user:
        return user

    user = User(
        username=TOC_BOT_USERNAME,
        original_username=TOC_BOT_USERNAME,
        password=secrets.token_urlsafe(64),
        is_activated=True,
        over_18=True,
        bio="Official utility bot for The Obsession Club.",
        bio_html="<p>Official utility bot for The Obsession Club.</p>",
    )
    db.add(user)
    db.flush()
    return user


def _target_user(db, viewer: User, argument: str) -> Optional[User]:
    token = (argument or "").strip().split(maxsplit=1)[0] if argument.strip() else ""
    username = token.lstrip("@").strip()
    if not username:
        return viewer
    if not re.fullmatch(r"[A-Za-z0-9_-]{3,30}", username):
        return None
    return (
        db.query(User)
        .filter(func.lower(User.username) == username.lower())
        .order_by(User.id.asc())
        .first()
    )


def _cmd_commands(_args: str, _viewer: User, _db) -> str:
    names = ", ".join(f",{command.name}" for command in _COMMANDS)
    return f"TOC-native commands: {names}. Full directory: /discordbot/toc-commands"


def _cmd_ping(_args: str, _viewer: User, _db) -> str:
    return "Pong. One Wish Bot is online in TOC chat."


def _cmd_userinfo(args: str, viewer: User, db) -> str:
    target = _target_user(db, viewer, args)
    if not target:
        return "User not found. Usage: ,userinfo [@username]"

    bits = [f"@{target.username}", f"truescore {int(target.truescore):,}"]
    house = str(getattr(target, "house", "") or "").strip()
    if house:
        bits.append(f"house {house}")
    bits.append(f"/@{target.username}")
    return " · ".join(bits)


def _cmd_avatar(args: str, viewer: User, db) -> str:
    target = _target_user(db, viewer, args)
    if not target:
        return "User not found. Usage: ,avatar [@username]"
    return f"@{target.username}'s avatar: {target.profile_url}"


def _cmd_balance(args: str, viewer: User, db) -> str:
    target = _target_user(db, viewer, args)
    if not target:
        return "User not found. Usage: ,balance [@username]"
    coins = int(getattr(target, "coins", 0) or 0)
    wishbux = int(getattr(target, "marseybux", 0) or 0)
    return f"@{target.username} · {coins:,} Wishcoins · {wishbux:,} Wishbux"


def _cmd_stats(_args: str, _viewer: User, _db) -> str:
    return "TOC site statistics: /stats"


def _cmd_leaderboard(_args: str, _viewer: User, _db) -> str:
    return "TOC leaderboards: /leaderboard"


def _cmd_8ball(args: str, _viewer: User, _db) -> str:
    if not args:
        return "Ask me something. Usage: ,8ball <question>"
    return random.choice(_EIGHT_BALL)


def _cmd_coinflip(_args: str, _viewer: User, _db) -> str:
    return random.choice(("Heads.", "Tails."))


def _cmd_roll(args: str, _viewer: User, _db) -> str:
    spec = (args or "").strip().lower()
    if not spec:
        return f"Rolled 1d100: {random.randint(1, 100)}"

    if spec.isdigit():
        sides = int(spec)
        if not 2 <= sides <= 1_000_000:
            return "Sides must be between 2 and 1,000,000."
        return f"Rolled 1d{sides}: {random.randint(1, sides)}"

    match = re.fullmatch(r"(\d{1,2})d(\d{1,7})", spec)
    if not match:
        return "Usage: ,roll [sides|NdM] — for example ,roll 2d20"

    count, sides = int(match.group(1)), int(match.group(2))
    if not 1 <= count <= 20 or not 2 <= sides <= 1_000_000:
        return "Dice limits: 1-20 dice, 2-1,000,000 sides each."

    rolls = [random.randint(1, sides) for _ in range(count)]
    rendered = ", ".join(str(value) for value in rolls)
    return f"Rolled {count}d{sides}: {rendered} · total {sum(rolls):,}"


def _cmd_choose(args: str, _viewer: User, _db) -> str:
    options = [part.strip() for part in (args or "").split("|") if part.strip()]
    if len(options) < 2:
        return "Give me at least two options separated by |. Example: ,choose A | B"
    if len(options) > 20 or any(len(option) > 120 for option in options):
        return "Keep it to 20 options with at most 120 characters each."
    return f"I choose: {random.choice(options)}"


def _cmd_rate(args: str, _viewer: User, _db) -> str:
    subject = (args or "").strip()
    if not subject:
        return "Usage: ,rate <thing>"
    if len(subject) > 180:
        subject = subject[:177] + "..."
    return f"{subject}: {random.randint(0, 100)}/100"


_HANDLERS: dict[str, Callable[[str, User, object], str]] = {
    "commands": _cmd_commands,
    "ping": _cmd_ping,
    "userinfo": _cmd_userinfo,
    "avatar": _cmd_avatar,
    "balance": _cmd_balance,
    "stats": _cmd_stats,
    "leaderboard": _cmd_leaderboard,
    "8ball": _cmd_8ball,
    "coinflip": _cmd_coinflip,
    "roll": _cmd_roll,
    "choose": _cmd_choose,
    "rate": _cmd_rate,
}


def execute_toc_bot_command(text: str, viewer: User, db) -> Optional[TOCBotCommandResult]:
    parsed = parse_toc_bot_command(text)
    if not parsed:
        return None
    command, args = parsed
    handler = _HANDLERS[command.name]
    return TOCBotCommandResult(command=command, response=handler(args, viewer, db))
