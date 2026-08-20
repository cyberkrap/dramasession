from flask import g, redirect, render_template
from sqlalchemy import func

from files.__main__ import app, limiter
from files.classes import Badge, Comment, CommentVote, Marsey, Submission, User, UserBlock, Vote
from files.classes.leaderboard import Leaderboard
from files.helpers.config.const import DEFAULT_RATELIMIT
from files.routes.wrappers import auth_required, get_ID


def _counted_user_ids_lb(user_id_queries, v, db, users, limit):
    """Build a leaderboard from one or more queries that each emit a user id."""
    combined = user_id_queries[0]
    for query in user_id_queries[1:]:
        combined = combined.union_all(query)
    combined = combined.subquery()

    counts = (
        db.query(combined.c.uid.label("user_id"), func.count().label("count"))
        .group_by(combined.c.uid)
        .subquery()
    )
    allowed = users.with_entities(User.id.label("id")).subquery()
    leaderboard = (
        db.query(User, counts.c.count)
        .join(counts, User.id == counts.c.user_id)
        .join(allowed, allowed.c.id == User.id)
        .order_by(counts.c.count.desc(), User.id.asc())
    )

    ranked = (
        db.query(
            counts.c.user_id,
            counts.c.count,
            func.rank().over(order_by=counts.c.count.desc()).label("rank"),
        )
        .join(allowed, allowed.c.id == counts.c.user_id)
        .subquery()
    )
    position = db.query(ranked.c.rank, ranked.c.count).filter(ranked.c.user_id == v.id).one_or_none()
    if position:
        v_position, v_value = int(position[0]), int(position[1])
    else:
        v_position, v_value = leaderboard.count() + 1, 0

    return leaderboard.limit(limit).all(), v_position, v_value


def _upvotes_given(criteria, v, db, users, limit):
    post_votes = db.query(Vote.user_id.label("uid")).filter(Vote.vote_type == 1)
    comment_votes = db.query(CommentVote.user_id.label("uid")).filter(CommentVote.vote_type == 1)
    return _counted_user_ids_lb([post_votes, comment_votes], v, db, users, limit)


def _downvotes_received(criteria, v, db, users, limit):
    post_authors = (
        db.query(Submission.author_id.label("uid"))
        .join(Vote, Vote.submission_id == Submission.id)
        .filter(Vote.vote_type == -1, Submission.author_id != None)
    )
    comment_authors = (
        db.query(Comment.author_id.label("uid"))
        .join(CommentVote, CommentVote.comment_id == Comment.id)
        .filter(CommentVote.vote_type == -1, Comment.author_id != None)
    )
    return _counted_user_ids_lb([post_authors, comment_authors], v, db, users, limit)


def _emojis_made(criteria, v, db, users, limit):
    approved = db.query(Marsey.author_id.label("uid")).filter(
        Marsey.author_id != None,
        Marsey.submitter_id == None,
    )
    return _counted_user_ids_lb([approved], v, db, users, limit)


def _build_leaderboard(metric, v):
    users = g.db.query(User)
    if not v.can_see_shadowbanned:
        users = users.filter(User.shadowbanned == None)

    simple = {
        "coins": ("Coins", "coins", "Wishcoins", User.coins, lambda u: u.coins, None),
        "wishbux": ("Wishbux", "Wishbux", "Wishbux", User.marseybux, lambda u: u.marseybux, None),
        "spent": ("Spent in shop", "coins spent in shop", "Wishcoins", User.coins_spent, lambda u: u.coins_spent, None),
        "truescore": ("Truescore", "truescore", "Truescore", User.truescore, lambda u: u.truescore, None),
        "followers": ("Followers", "followers", "Followers", User.stored_subscriber_count, lambda u: u.stored_subscriber_count, "followers"),
        "posts": ("Posts", "post count", "Posts", User.post_count, lambda u: u.post_count, ""),
        "comments": ("Comments", "comment count", "Comments", User.comment_count, lambda u: u.comment_count, "comments"),
        "awards": ("Awards", "received awards", "Awards", User.received_award_count, lambda u: u.received_award_count, None),
    }
    if metric in simple:
        header, table_header, column, criterion, value_func, relative_url = simple[metric]
        return Leaderboard(
            header, table_header, metric, column, relative_url,
            Leaderboard.get_simple_lb, criterion, v, value_func, g.db, users,
        )

    if metric == "badges":
        return Leaderboard("Badges", "badges", "badges", "Badges", None, Leaderboard.get_badge_marsey_lb, Badge.user_id, v, None, g.db, None)
    if metric == "blocked":
        return Leaderboard("Blocked", "most blocked", "blocked", "Blocked By", "blockers", Leaderboard.get_blockers_lb, UserBlock.target_id, v, None, g.db, None)
    if metric == "owned-hats":
        return Leaderboard("Owned hats", "owned hats", "owned-hats", "Owned Hats", None, Leaderboard.get_hat_lb, User.owned_hats, v, None, g.db, None)
    if metric == "designed-hats":
        return Leaderboard("Designed hats", "designed hats", "designed-hats", "Designed Hats", None, Leaderboard.get_hat_lb, User.designed_hats, v, None, g.db, None)
    if metric == "emojis":
        return Leaderboard("Emojis made", "emojis made", "emojis", "Emojis", None, _emojis_made, None, v, None, g.db, users)
    if metric == "upvotes-given":
        return Leaderboard("Upvotes given", "upvotes given", "upvotes-given", "Upvotes", None, _upvotes_given, None, v, None, g.db, users)
    if metric == "downvotes-received":
        return Leaderboard("Downvotes received", "downvotes received", "downvotes-received", "Downvotes", None, _downvotes_received, None, v, None, g.db, users)
    return None


LEADERBOARD_NAV = (
    ("coins", "Coins"),
    ("wishbux", "Wishbux"),
    ("spent", "Spent in shop"),
    ("truescore", "Truescore"),
    ("followers", "Followers"),
    ("posts", "Posts"),
    ("comments", "Comments"),
    ("awards", "Received awards"),
    ("badges", "Badges"),
    ("blocked", "Most blocked"),
    ("owned-hats", "Owned hats"),
    ("designed-hats", "Designed hats"),
    ("emojis", "Emojis made"),
    ("upvotes-given", "Upvotes given"),
    ("downvotes-received", "Downvotes received"),
)


@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def _leaderboard_index(v):
    return redirect("/leaderboard/coins")


@app.get("/leaderboard/<metric>")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def leaderboard_metric(v, metric):
    # Keep the old rDrama spelling usable while TOC exposes the currency as Wishbux.
    if metric == "marseybux":
        return redirect("/leaderboard/wishbux")

    leaderboard = _build_leaderboard(metric, v)
    if leaderboard is None:
        return redirect("/leaderboard/coins")

    return render_template(
        "leaderboard.html",
        v=v,
        leaderboard=leaderboard,
        leaderboard_nav=LEADERBOARD_NAV,
        active_key=metric,
    )


# /leaderboard is registered by the legacy users route. Replace only its view
# function so old links redirect into the new one-leaderboard-per-page layout.
app.view_functions["leaderboard"] = _leaderboard_index
