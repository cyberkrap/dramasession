from sqlalchemy import event, func
from sqlalchemy.orm import Session

from files.classes import Comment, CrappyRequest, Submission, User
from files.helpers.config.const import COMMENT_MAX_DEPTH

from .config import CRAPPY_USERNAME, crappy_enabled


_installed = False


def _contains_crappy_mention(text: str | None) -> bool:
    if not text:
        return False
    lowered = text.lower()
    marker = f"@{CRAPPY_USERNAME.lower()}"
    start = 0
    while True:
        index = lowered.find(marker, start)
        if index < 0:
            return False
        before = lowered[index - 1] if index else ""
        after_index = index + len(marker)
        after = lowered[after_index] if after_index < len(lowered) else ""
        if (not before or not (before.isalnum() or before == "_")) and (
            not after or not (after.isalnum() or after == "_")
        ):
            return True
        start = index + len(marker)


def _crappy_account_id(session: Session) -> int | None:
    cache_key = "crappy_account_id"
    if cache_key in session.info:
        cached = int(session.info.get(cache_key) or 0)
        return cached or None

    row = (
        session.query(User.id)
        .filter(func.lower(User.username) == CRAPPY_USERNAME.lower())
        .order_by(User.id.asc())
        .first()
    )
    crappy_id = int(row[0]) if row else 0
    session.info[cache_key] = crappy_id
    return crappy_id or None


def _is_implicit_crappy_conversation(
    session: Session,
    comment: Comment,
    crappy_id: int,
) -> bool:
    # Crappy's own profile wall is always conversational.
    if comment.wall_user_id == crappy_id:
        return True

    # A direct reply to one of Crappy's comments is conversational regardless
    # of which post/profile wall contains the thread.
    if comment.parent_comment_id:
        parent_author_id = (
            session.query(Comment.author_id)
            .filter(Comment.id == comment.parent_comment_id)
            .scalar()
        )
        if parent_author_id == crappy_id:
            return True

    # Every human comment anywhere under a post authored by Crappy is an
    # invocation. This is what makes AMA/megathread posts work naturally.
    if comment.parent_submission:
        post_author_id = (
            session.query(Submission.author_id)
            .filter(Submission.id == comment.parent_submission)
            .scalar()
        )
        if post_author_id == crappy_id:
            return True

    return False


def _eligible_comment(session: Session, comment: Comment) -> bool:
    if not (
        crappy_enabled()
        and comment
        and not comment.is_bot
        and (comment.parent_submission is not None or comment.wall_user_id is not None)
        and int(comment.level or 1) < COMMENT_MAX_DEPTH
    ):
        return False

    crappy_id = _crappy_account_id(session)
    if crappy_id and comment.author_id == crappy_id:
        return False

    if crappy_id and _is_implicit_crappy_conversation(session, comment, crappy_id):
        return True

    # Everywhere outside a Crappy-owned conversation still requires an
    # explicit mention.
    return _contains_crappy_mention(comment.body)


def install_crappy_comment_hook() -> None:
    global _installed
    if _installed:
        return

    @event.listens_for(Session, "before_flush")
    def _capture_new_comments(session, flush_context, instances):
        pending = session.info.setdefault("crappy_comment_candidates", [])
        known = {id(item) for item in pending}
        for item in session.new:
            if (
                isinstance(item, Comment)
                and id(item) not in known
                and _eligible_comment(session, item)
            ):
                pending.append(item)
                known.add(id(item))

    @event.listens_for(Session, "after_flush_postexec")
    def _queue_new_comments(session, flush_context):
        pending = session.info.pop("crappy_comment_candidates", [])
        for comment in pending:
            if not comment.id or not _eligible_comment(session, comment):
                continue
            session.add(
                CrappyRequest(
                    source_type="comment",
                    source_id=comment.id,
                    requester_id=comment.author_id,
                    status="pending",
                    available_utc=0,
                )
            )

    _installed = True
