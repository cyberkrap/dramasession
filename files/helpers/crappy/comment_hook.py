from sqlalchemy import event, func
from sqlalchemy.orm import Session

from files.classes import Comment, CrappyRequest, User
from files.helpers.config.const import COMMENT_MAX_DEPTH

from .config import CRAPPY_USERNAME, crappy_enabled
from .conversation import comment_invokes_crappy


_installed = False


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
    return bool(
        crappy_id
        and comment_invokes_crappy(session, comment, crappy_id)
    )


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
