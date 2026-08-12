from __future__ import annotations

from sqlalchemy.orm import Session

from files.classes import Comment, Submission

from .config import CRAPPY_USERNAME


def contains_crappy_mention(text: str | None) -> bool:
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


def comment_invokes_crappy(
    session: Session,
    comment: Comment,
    crappy_id: int | None,
) -> bool:
    """Return whether a persisted/new human comment belongs to a Crappy conversation."""
    if not comment or not crappy_id:
        return False
    if comment.is_bot or comment.author_id == crappy_id:
        return False

    # Crappy's profile wall is a direct conversation.
    if comment.wall_user_id == crappy_id:
        return True

    # Direct replies to Crappy keep the conversation going anywhere on TOC.
    if comment.parent_comment_id:
        parent_author_id = (
            session.query(Comment.author_id)
            .filter(Comment.id == comment.parent_comment_id)
            .scalar()
        )
        if parent_author_id == crappy_id:
            return True

    # Posts authored by Crappy are conversational spaces (AMA/megathreads etc.).
    if comment.parent_submission:
        post_author_id = (
            session.query(Submission.author_id)
            .filter(Submission.id == comment.parent_submission)
            .scalar()
        )
        if post_author_id == crappy_id:
            return True

    # Everywhere else still requires an explicit mention.
    return contains_crappy_mention(comment.body)
