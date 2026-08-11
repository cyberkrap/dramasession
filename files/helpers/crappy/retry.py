from __future__ import annotations

import time

from files.classes import CrappyRequest


_TRANSIENT_RECOVERY_LOOKBACK_SECONDS = 6 * 60 * 60
_MAX_PROVIDER_BACKOFF_SECONDS = 24 * 60 * 60


def _retry_after_seconds(exc) -> int | None:
    value = getattr(exc, "retry_after_seconds", None)
    try:
        value = int(value) if value is not None else None
    except (TypeError, ValueError):
        return None
    if value is None:
        return None
    return max(1, min(value, _MAX_PROVIDER_BACKOFF_SECONDS))


def defer_transient_provider_failure(db, request_id: int, exc) -> bool:
    """Undo attempt consumption for provider failures that explicitly request a retry."""
    retry_after = _retry_after_seconds(exc)
    if retry_after is None:
        return False

    db.rollback()
    queued = db.get(CrappyRequest, request_id)
    if not queued:
        return False

    now = int(time.time())
    queued.status = "pending"
    queued.attempts = max(0, int(queued.attempts or 0) - 1)
    queued.available_utc = max(
        int(queued.available_utc or 0),
        now + retry_after,
    )
    queued.error = f"{type(exc).__name__}: {exc}"[:2000]
    queued.updated_utc = now
    db.add(queued)
    db.commit()
    return True


def recover_recent_rate_limited_requests(db) -> int:
    """Requeue recent requests that old worker code permanently failed on HTTP 429s."""
    now = int(time.time())
    queued_rows = (
        db.query(CrappyRequest)
        .filter(
            CrappyRequest.status == "failed",
            CrappyRequest.updated_utc >= now - _TRANSIENT_RECOVERY_LOOKBACK_SECONDS,
            CrappyRequest.error.ilike("%HTTP 429%"),
        )
        .order_by(CrappyRequest.id.asc())
        .all()
    )

    for queued in queued_rows:
        queued.status = "pending"
        queued.attempts = 0
        queued.available_utc = now
        queued.updated_utc = now
        db.add(queued)

    if queued_rows:
        db.commit()
    else:
        db.rollback()
    return len(queued_rows)
