from sqlalchemy import event
from sqlalchemy.orm import Session

from files.classes import Comment, CrappyRequest
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


def _eligible_comment(comment: Comment) -> bool:
    return bool(
        crappy_enabled()
        and comment
        and not comment.is_bot
        and comment.parent_submission is not None
        and int(comment.level or 1) < COMMENT_MAX_DEPTH
        and _contains_crappy_mention(comment.body)
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
            if isinstance(item, Comment) and id(item) not in known and _eligible_comment(item):
                pending.append(item)
                known.add(id(item))

    @event.listens_for(Session, "after_flush_postexec")
    def _queue_new_comments(session, flush_context):
        pending = session.info.pop("crappy_comment_candidates", [])
        for comment in pending:
            if not comment.id or not _eligible_comment(comment):
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
