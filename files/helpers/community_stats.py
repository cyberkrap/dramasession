import datetime as dt
import time

from sqlalchemy import case, func

from files.__main__ import cache
from files.classes import (
    AwardRelationship,
    Badge,
    BadgeDef,
    CasinoGame,
    Comment,
    CommentVote,
    Follow,
    Hat,
    HatDef,
    Marsey,
    Submission,
    Sub,
    SubJoin,
    SubSubscription,
    Subscription,
    User,
    UserBlock,
    Vote,
)
from files.helpers.bank_statement_noise_fixes import (
    ECONOMY_RESET_UTC,
    get_economy_baseline,
)
from files.helpers.config.const import AUTOJANNY_ID, SITE
from files.helpers.house_system import base_house_names, special_award_for_house


_STATS_CACHE_VERSION = "v2-economy-reset-20260822"
_PERIODS = {
    "30d": {"buckets": 30, "seconds": 86400, "label": "Last 30 days", "date_format": "%b %d"},
    "26w": {"buckets": 26, "seconds": 604800, "label": "Last 26 weeks", "date_format": "%b %d"},
}


def _count(db, model, *criteria):
    query = db.query(func.count()).select_from(model)
    if criteria:
        query = query.filter(*criteria)
    return int(query.scalar() or 0)


def _sum(db, column, *criteria):
    query = db.query(func.coalesce(func.sum(column), 0))
    if criteria:
        query = query.filter(*criteria)
    return int(query.scalar() or 0)


def _distinct_count(db, column, *criteria):
    query = db.query(func.count(func.distinct(column)))
    if criteria:
        query = query.filter(*criteria)
    return int(query.scalar() or 0)


def _house_rows(db):
    rows = []
    for house in base_house_names():
        members = db.query(User).filter(User.house.in_((house, f"{house} Founder")))
        member_count = members.count()
        founder_count = members.filter(User.house == f"{house} Founder").count()
        total_truescore = (
            db.query(func.coalesce(func.sum(User.truescore), 0))
            .filter(User.house.in_((house, f"{house} Founder")))
            .scalar()
            or 0
        )
        special = special_award_for_house(house)
        rows.append({
            "name": house,
            "members": int(member_count),
            "founders": int(founder_count),
            "truescore": int(total_truescore),
            "award": special["title"] if special else None,
        })
    return rows


def _section(label, rows):
    return {"label": label, "rows": [{"label": name, "value": int(value or 0)} for name, value in rows]}


def build_snapshot(db):
    now = int(time.time())
    day = now - 86400
    week = now - 604800

    applied_award = (
        AwardRelationship.submission_id.isnot(None)
        | AwardRelationship.comment_id.isnot(None)
    )

    casino_by_kind = {
        kind: {
            "wagered": int(wagered or 0),
            # CasinoGame.winnings is net result, so only positive rows represent
            # money won by players. Summing negative losses made the old "paid
            # out" statistic nonsensically negative.
            "paid_out": int(paid_out or 0),
        }
        for kind, wagered, paid_out in (
            db.query(
                CasinoGame.kind,
                func.coalesce(func.sum(CasinoGame.wager), 0),
                func.coalesce(
                    func.sum(case((CasinoGame.winnings > 0, CasinoGame.winnings), else_=0)),
                    0,
                ),
            )
            .filter(
                CasinoGame.active.is_(False),
                CasinoGame.created_utc >= ECONOMY_RESET_UTC,
            )
            .group_by(CasinoGame.kind)
            .all()
        )
    }

    coins_spent_since_reset = max(
        0,
        _sum(db, User.coins_spent) - get_economy_baseline(db, "coins_spent"),
    )
    hats_spent_since_reset = max(
        0,
        _sum(db, User.coins_spent_on_hats) - get_economy_baseline(db, "coins_spent_on_hats"),
    )

    houses = _house_rows(db)

    sections = [
        _section("Community", [
            ("Registered users", _count(db, User)),
            ("Signups in the last 24 hours", _count(db, User, User.created_utc > day)),
            ("Active users in the last 7 days", _count(db, User, User.last_active > week)),
            ("Banned users", _count(db, User, User.is_banned.isnot(None))),
            ("Muted users", _count(db, User, User.is_muted.is_(True))),
            ("Private profiles", _count(db, User, User.is_private.is_(True))),
            ("Verified-email users", _count(db, User, User.is_activated.is_(True))),
            ("Users in a house", _count(db, User, User.house != "")),
            ("User follows", _count(db, Follow)),
            ("User blocks", _count(db, UserBlock)),
        ]),
        _section("Content", [
            ("Total posts", _count(db, Submission)),
            ("Listed posts", _count(db, Submission, Submission.is_banned.is_(False), Submission.deleted_utc == 0)),
            ("Posts removed by admins", _count(db, Submission, Submission.is_banned.is_(True))),
            ("Posts deleted by authors", _count(db, Submission, Submission.deleted_utc > 0)),
            ("Posts in the last 24 hours", _count(db, Submission, Submission.created_utc > day)),
            ("Users who have posted", _distinct_count(db, Submission.author_id, Submission.author_id.isnot(None))),
            ("Total comments", _count(db, Comment, Comment.author_id != AUTOJANNY_ID)),
            ("Comments removed by admins", _count(db, Comment, Comment.is_banned.is_(True), Comment.author_id != AUTOJANNY_ID)),
            ("Comments deleted by authors", _count(db, Comment, Comment.deleted_utc > 0, Comment.author_id != AUTOJANNY_ID)),
            ("Comments in the last 24 hours", _count(db, Comment, Comment.created_utc > day, Comment.author_id != AUTOJANNY_ID)),
            ("Users who have commented", _distinct_count(db, Comment.author_id, Comment.author_id != AUTOJANNY_ID)),
            ("Thread subscriptions", _count(db, Subscription)),
        ]),
        _section("Engagement", [
            ("Post votes", _count(db, Vote)),
            ("Comment votes", _count(db, CommentVote)),
            ("Total upvotes", _count(db, Vote, Vote.vote_type == 1) + _count(db, CommentVote, CommentVote.vote_type == 1)),
            ("Total downvotes", _count(db, Vote, Vote.vote_type == -1) + _count(db, CommentVote, CommentVote.vote_type == -1)),
            ("Awards given", _count(db, AwardRelationship, applied_award)),
            ("Award inventory items", _count(db, AwardRelationship, AwardRelationship.submission_id.is_(None), AwardRelationship.comment_id.is_(None))),
            ("Wishcoins spent on applied awards", _sum(db, AwardRelationship.price_paid, applied_award)),
        ]),
        _section("Economy", [
            # Circulation is intentionally current-state data, not a historical
            # counter. Resetting it would mean changing real user balances.
            ("Wishcoins in circulation now", _sum(db, User.coins)),
            ("Wishbux in circulation now", _sum(db, User.marseybux)),
            ("Wishcoins spent in shop since reset", coins_spent_since_reset),
            ("Wishcoins spent on hats since reset", hats_spent_since_reset),
            ("Casino wagered since reset", sum(item["wagered"] for item in casino_by_kind.values())),
            ("Casino paid out since reset", sum(item["paid_out"] for item in casino_by_kind.values())),
            ("Blackjack wagered since reset", casino_by_kind.get("blackjack", {}).get("wagered", 0)),
            ("Blackjack paid out since reset", casino_by_kind.get("blackjack", {}).get("paid_out", 0)),
            ("Slots wagered since reset", casino_by_kind.get("slots", {}).get("wagered", 0)),
            ("Slots paid out since reset", casino_by_kind.get("slots", {}).get("paid_out", 0)),
            ("Roulette wagered since reset", casino_by_kind.get("roulette", {}).get("wagered", 0)),
            ("Roulette paid out since reset", casino_by_kind.get("roulette", {}).get("paid_out", 0)),
        ]),
        _section("Boards & customization", [
            ("Boards", _count(db, Sub)),
            ("Board memberships", _count(db, SubJoin)),
            ("Board subscriptions", _count(db, SubSubscription)),
            ("Approved emotes", _count(db, Marsey, Marsey.submitter_id.is_(None))),
            ("Total emote uses", _sum(db, Marsey.count, Marsey.submitter_id.is_(None))),
            ("Approved hats", _count(db, HatDef, HatDef.submitter_id.is_(None))),
            ("Hat ownerships", _count(db, Hat)),
            ("Badge types", _count(db, BadgeDef)),
            ("Badges earned", _count(db, Badge)),
        ]),
    ]

    return {
        "generated_utc": now,
        "economy_reset_utc": ECONOMY_RESET_UTC,
        "sections": sections,
        "houses": houses,
        "headline": {
            "users": _count(db, User),
            "active_7d": _count(db, User, User.last_active > week),
            "posts": _count(db, Submission),
            "comments": _count(db, Comment, Comment.author_id != AUTOJANNY_ID),
        },
    }


def _bucket_rows(db, column, start, seconds, *criteria):
    bucket = func.floor((column - start) / seconds)
    query = db.query(bucket.label("bucket"), func.count()).filter(column >= start)
    if criteria:
        query = query.filter(*criteria)
    return {int(index): int(count) for index, count in query.group_by(bucket).all()}


def _combine_buckets(*maps):
    combined = {}
    for mapping in maps:
        for key, value in mapping.items():
            combined[key] = combined.get(key, 0) + value
    return combined


def _chart_points(values, width=1000, height=190, pad=12):
    if not values:
        return ""
    peak = max(values) or 1
    usable_w = width - (pad * 2)
    usable_h = height - (pad * 2)
    step = usable_w / max(len(values) - 1, 1)
    points = []
    for index, value in enumerate(values):
        x = pad + (index * step)
        y = height - pad - ((value / peak) * usable_h)
        points.append(f"{x:.1f},{y:.1f}")
    return " ".join(points)


def build_trends(db, period):
    config = _PERIODS.get(period) or _PERIODS["30d"]
    period = period if period in _PERIODS else "30d"
    now = int(time.time())
    seconds = config["seconds"]
    current_bucket = (now // seconds) * seconds
    start = current_bucket - ((config["buckets"] - 1) * seconds)

    signups = _bucket_rows(db, User.created_utc, start, seconds)
    posts = _bucket_rows(db, Submission.created_utc, start, seconds)
    comments = _bucket_rows(db, Comment.created_utc, start, seconds, Comment.author_id != AUTOJANNY_ID)
    votes = _combine_buckets(
        _bucket_rows(db, Vote.created_utc, start, seconds),
        _bucket_rows(db, CommentVote.created_utc, start, seconds),
    )

    labels = [
        dt.datetime.fromtimestamp(start + (index * seconds), tz=dt.timezone.utc).strftime(config["date_format"])
        for index in range(config["buckets"])
    ]

    charts = []
    for key, label, mapping in (
        ("signups", "Signups", signups),
        ("posts", "Posts", posts),
        ("comments", "Comments", comments),
        ("votes", "Votes", votes),
    ):
        values = [mapping.get(index, 0) for index in range(config["buckets"])]
        charts.append({
            "key": key,
            "label": label,
            "values": values,
            "points": _chart_points(values),
            "total": sum(values),
            "latest": values[-1] if values else 0,
            "peak": max(values) if values else 0,
        })

    return {
        "key": period,
        "label": config["label"],
        "labels": labels,
        "start_label": labels[0],
        "end_label": labels[-1],
        "charts": charts,
    }


def get_community_stats(db, period="30d"):
    period = period if period in _PERIODS else "30d"
    snapshot_key = f"{SITE}:community-stats:{_STATS_CACHE_VERSION}:snapshot"
    trends_key = f"{SITE}:community-stats:{_STATS_CACHE_VERSION}:trends:{period}"

    snapshot = cache.get(snapshot_key)
    if snapshot is None:
        snapshot = build_snapshot(db)
        cache.set(snapshot_key, snapshot, timeout=300)

    trends = cache.get(trends_key)
    if trends is None:
        trends = build_trends(db, period)
        cache.set(trends_key, trends, timeout=300)

    return snapshot, trends
