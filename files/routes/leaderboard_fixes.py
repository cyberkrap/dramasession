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


def _leaderboards(v):
    users = g.db.query(User)
    if not v.can_see_shadowbanned:
        users = users.filter(User.shadowbanned == None)

    return {
        "coins": Leaderboard("Coins", "coins", "coins", "Wishcoins", None, Leaderboard.get_simple_lb, User.coins, v, lambda u: u.coins, g.db, users),
        "wishbux": Leaderboard("Wishbux", "Wishbux", "wishbux", "Wishbux", None, Leaderboard.get_simple_lb, User.marseybux, v, lambda u: u.marseybux, g.db, users),
        "spent": Leaderboard("Spent in shop", "coins spent in shop", "spent", "Wishcoins", None, Leaderboard.get_simple_lb, User.coins_spent, v, lambda u: u.coins_spent, g.db, users),
        "truescore": Leaderboard("Truescore", "truescore", "truescore", "Truescore", None, Leaderboard.get_simple_lb, User.truescore, v, lambda u: u.truescore, g.db, users),
        "followers": Leaderboard("Followers", "followers", "followers", "Followers", "followers", Leaderboard.get_simple_lb, User.stored_subscriber_count, v, lambda u: u.stored_subscriber_count, g.db, users),
        "posts": Leaderboard("Posts", "post count", "posts", "Posts", "", Leaderboard.get_simple_lb, User.post_count, v, lambda u: u.post_count, g.db, users),
        "comments": Leaderboard("Comments", "comment count", "comments", "Comments", "comments", Leaderboard.get_simple_lb, User.comment_count, v, lambda u: u.comment_count, g.db, users),
        "awards": Leaderboard("Awards", "received awards", "awards", "Awards", None, Leaderboard.get_simple_lb, User.received_award_count, v, lambda u: u.received_award_count, g.db, users),
        "badges": Leaderboard("Badges", "badges", "badges", "Badges", None, Leaderboard.get_badge_marsey_lb, Badge.user_id, v, None, g.db, None),
        "blocked": Leaderboard("Blocked", "most blocked", "blocked", "Blocked By", "blockers", Leaderboard.get_blockers_lb, UserBlock.target_id, v, None, g.db, None),
        "owned-hats": Leaderboard("Owned hats", "owned hats", "owned-hats", "Owned Hats", None, Leaderboard.get_hat_lb, User.owned_hats, v, None, g.db, None),
        "designed-hats": Leaderboard("Designed hats", "designed hats", "designed-hats", "Designed Hats", None, Leaderboard.get_hat_lb, User.designed_hats, v, None, g.db, None),
        "emojis": Leaderboard("Emojis made", "emojis made", "emojis", "Emojis", None, _emojis_made, None, v, None, g.db, users),
        "upvotes-given": Leaderboard("Upvotes given", "upvotes given", "upvotes-given", "Upvotes", None, _upvotes_given, None, v, None, g.db, users),
        "downvotes-received": Leaderboard("Downvotes received", "downvotes received", "downvotes-received", "Downvotes", None, _downvotes_received, None, v, None, g.db, users),
    }


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

    leaderboards = _leaderboards(v)
    if metric not in leaderboards:
        return redirect("/leaderboard/coins")

    return render_template(
        "leaderboard.html",
        v=v,
        leaderboard=leaderboards[metric],
        leaderboard_nav=LEADERBOARD_NAV,
        active_key=metric,
    )


# /leaderboard is registered by the legacy users route. Replace only its view
# function so old links redirect into the new one-leaderboard-per-page layout.
app.view_functions["leaderboard"] = _leaderboard_index
