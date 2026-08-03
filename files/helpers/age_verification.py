"""Didit-backed age verification state, persistence, and gating helpers."""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import time
from functools import wraps
from urllib.parse import urlsplit

import requests
from flask import g, redirect, request
from sqlalchemy import Column, Integer, String, inspect, text

from files.classes.badges import Badge, BadgeDef, _OBSESSION_BADGE_ASSETS
from files.helpers.config import const


MINOR_STRIKE_BADGE_NAME = "Minor Strike"
MINOR_STRIKE_BADGE_DESCRIPTION = (
    "This user has verified their age. Thanks for keeping this community minor-free!"
)
MINOR_STRIKE_BADGE_ASSET = "minor-strike.webp"
DIDIT_API_BASE = "https://verification.didit.me/v3"
FINISHED_FAILURE_STATUSES = {
    "declined",
    "expired",
    "abandoned",
    "kyc expired",
}

_installed = False
_chat_gate_installed = False


def didit_enabled() -> bool:
    return os.environ.get("DIDIT_ENABLED", "false").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def didit_configured(include_webhook: bool = False) -> bool:
    required = [
        os.environ.get("DIDIT_API_KEY"),
        os.environ.get("DIDIT_WORKFLOW_ID"),
        os.environ.get("DIDIT_CALLBACK_URL"),
    ]
    if include_webhook:
        required.append(os.environ.get("DIDIT_WEBHOOK_SECRET"))
    return all(str(value or "").strip() for value in required)


def _bot_ids() -> set[int]:
    result = set()
    for name in ("AUTOJANNY_ID", "SNAPPY_ID"):
        try:
            value = int(getattr(const, name, 0) or 0)
        except (TypeError, ValueError):
            value = 0
        if value:
            result.add(value)
    for value in getattr(const, "PRIVILEGED_USER_BOTS", ()) or ():
        try:
            result.add(int(value))
        except (TypeError, ValueError):
            continue
    return result


def is_age_verification_exempt(user) -> bool:
    return bool(user and int(getattr(user, "id", 0) or 0) in _bot_ids())


def is_age_verified(user) -> bool:
    if not user:
        return False
    if is_age_verification_exempt(user):
        return True
    status = str(getattr(user, "age_verification_status", "") or "").strip().lower()
    verified_utc = int(getattr(user, "age_verified_utc", 0) or 0)
    return status == "approved" and verified_utc > 0


def needs_age_verification(user) -> bool:
    return didit_enabled() and bool(user) and not is_age_verified(user)


def vendor_data_for_user(user_id: int) -> str:
    return f"obsession:user:{int(user_id)}"


def user_id_from_vendor_data(value) -> int | None:
    text_value = str(value or "").strip()
    prefix = "obsession:user:"
    if not text_value.startswith(prefix):
        return None
    try:
        user_id = int(text_value[len(prefix):])
    except (TypeError, ValueError):
        return None
    return user_id if user_id > 0 else None


def safe_internal_path(value, fallback: str = "/") -> str:
    candidate = str(value or "").strip()
    if not candidate:
        return fallback
    parsed = urlsplit(candidate)
    if parsed.scheme or parsed.netloc or not parsed.path.startswith("/"):
        return fallback
    if parsed.path.startswith("//"):
        return fallback
    output = parsed.path
    if parsed.query:
        output += "?" + parsed.query
    return output


def _install_user_columns(User) -> None:
    if not hasattr(User, "age_verified_utc"):
        User.age_verified_utc = Column(
            Integer,
            nullable=False,
            default=0,
            server_default=text("0"),
        )
    if not hasattr(User, "age_verification_status"):
        User.age_verification_status = Column(
            String(32),
            nullable=False,
            default="unverified",
            server_default=text("'unverified'"),
        )
    if not hasattr(User, "age_verification_provider"):
        User.age_verification_provider = Column(String(32), nullable=True)
    if not hasattr(User, "age_verification_session_id"):
        User.age_verification_session_id = Column(String(64), nullable=True)
    if not hasattr(User, "age_verification_consent_utc"):
        User.age_verification_consent_utc = Column(
            Integer,
            nullable=False,
            default=0,
            server_default=text("0"),
        )


def _ensure_database_schema(engine) -> None:
    inspector = inspect(engine)
    if not inspector.has_table("users"):
        return

    existing = {column["name"] for column in inspector.get_columns("users")}
    required = {
        "age_verified_utc": "BIGINT NOT NULL DEFAULT 0",
        "age_verification_status": "VARCHAR(32) NOT NULL DEFAULT 'unverified'",
        "age_verification_provider": "VARCHAR(32)",
        "age_verification_session_id": "VARCHAR(64)",
        "age_verification_consent_utc": "BIGINT NOT NULL DEFAULT 0",
    }

    with engine.begin() as connection:
        for column_name, definition in required.items():
            if column_name in existing:
                continue
            if engine.dialect.name == "postgresql":
                connection.exec_driver_sql(
                    f"ALTER TABLE users ADD COLUMN IF NOT EXISTS {column_name} {definition}"
                )
            else:
                connection.exec_driver_sql(
                    f"ALTER TABLE users ADD COLUMN {column_name} {definition}"
                )

        connection.exec_driver_sql(
            """
            CREATE TABLE IF NOT EXISTS age_verification_events (
                event_id VARCHAR(128) PRIMARY KEY,
                session_id VARCHAR(64) NOT NULL,
                user_id INTEGER,
                status VARCHAR(32),
                webhook_type VARCHAR(32),
                created_utc BIGINT NOT NULL
            )
            """
        )
        connection.exec_driver_sql(
            "CREATE INDEX IF NOT EXISTS ix_age_verification_events_session_id "
            "ON age_verification_events (session_id)"
        )
        connection.exec_driver_sql(
            "CREATE INDEX IF NOT EXISTS ix_users_age_verification_session_id "
            "ON users (age_verification_session_id)"
        )


def _ensure_minor_strike_badge(db_session_factory) -> int:
    db = db_session_factory()
    try:
        badge_def = (
            db.query(BadgeDef)
            .filter(BadgeDef.name == MINOR_STRIKE_BADGE_NAME)
            .order_by(BadgeDef.id.asc())
            .first()
        )
        if not badge_def:
            badge_def = BadgeDef(
                name=MINOR_STRIKE_BADGE_NAME,
                description=MINOR_STRIKE_BADGE_DESCRIPTION,
            )
            db.add(badge_def)
            db.flush()
        elif badge_def.description != MINOR_STRIKE_BADGE_DESCRIPTION:
            badge_def.description = MINOR_STRIKE_BADGE_DESCRIPTION
            db.add(badge_def)
        badge_id = int(badge_def.id)
        _OBSESSION_BADGE_ASSETS[badge_id] = MINOR_STRIKE_BADGE_ASSET
        db.commit()
        return badge_id
    finally:
        db.close()


def grant_minor_strike_badge(db, user) -> None:
    badge_def = (
        db.query(BadgeDef)
        .filter(BadgeDef.name == MINOR_STRIKE_BADGE_NAME)
        .order_by(BadgeDef.id.asc())
        .first()
    )
    if not badge_def:
        badge_def = BadgeDef(
            name=MINOR_STRIKE_BADGE_NAME,
            description=MINOR_STRIKE_BADGE_DESCRIPTION,
        )
        db.add(badge_def)
        db.flush()
    _OBSESSION_BADGE_ASSETS[int(badge_def.id)] = MINOR_STRIKE_BADGE_ASSET
    exists = (
        db.query(Badge)
        .filter(Badge.user_id == user.id, Badge.badge_id == badge_def.id)
        .one_or_none()
    )
    if not exists:
        db.add(Badge(user_id=user.id, badge_id=badge_def.id))


def install_age_verification(engine, User, db_session_factory, ensure_badge: bool = True) -> None:
    global _installed
    if _installed:
        return
    _install_user_columns(User)
    _ensure_database_schema(engine)
    if ensure_badge:
        _ensure_minor_strike_badge(db_session_factory)
    User.is_age_verified = property(is_age_verified)
    User.needs_age_verification = property(needs_age_verification)
    _installed = True


def _didit_headers() -> dict[str, str]:
    api_key = str(os.environ.get("DIDIT_API_KEY") or "").strip()
    if not api_key:
        raise RuntimeError("DIDIT_API_KEY is not configured")
    return {
        "accept": "application/json",
        "content-type": "application/json",
        "x-api-key": api_key,
    }


def create_didit_session(user) -> dict:
    workflow_id = str(os.environ.get("DIDIT_WORKFLOW_ID") or "").strip()
    callback_url = str(os.environ.get("DIDIT_CALLBACK_URL") or "").strip()
    if not workflow_id or not callback_url:
        raise RuntimeError("Didit workflow or callback URL is not configured")

    response = requests.post(
        f"{DIDIT_API_BASE}/session/",
        headers=_didit_headers(),
        json={
            "workflow_id": workflow_id,
            "vendor_data": vendor_data_for_user(user.id),
            "callback": callback_url,
            "callback_method": "both",
            "metadata": {
                "purpose": "obsession_age_verification",
                "obsession_user_id": str(user.id),
            },
        },
        timeout=(5, 25),
    )
    if response.status_code not in (200, 201):
        detail = ""
        try:
            body = response.json()
            detail = str(body.get("detail") or body.get("message") or "")[:240]
        except (ValueError, AttributeError):
            detail = response.text[:240]
        raise RuntimeError(
            f"Didit returned HTTP {response.status_code}"
            + (f": {detail}" if detail else "")
        )
    data = response.json()
    if not data.get("session_id") or not data.get("url"):
        raise RuntimeError("Didit did not return a session ID and verification URL")
    return data


def retrieve_didit_decision(session_id: str) -> dict:
    clean_session_id = str(session_id or "").strip()
    if not clean_session_id or len(clean_session_id) > 64:
        raise RuntimeError("Invalid Didit session ID")
    response = requests.get(
        f"{DIDIT_API_BASE}/session/{clean_session_id}/decision/",
        headers=_didit_headers(),
        timeout=(5, 25),
    )
    if response.status_code != 200:
        raise RuntimeError(f"Didit decision lookup returned HTTP {response.status_code}")
    return response.json()


def validate_didit_decision(decision: dict, expected_session_id: str | None = None) -> int:
    workflow_id = str(os.environ.get("DIDIT_WORKFLOW_ID") or "").strip()
    if workflow_id and str(decision.get("workflow_id") or "") != workflow_id:
        raise RuntimeError("Didit decision belongs to a different workflow")
    if expected_session_id and str(decision.get("session_id") or "") != str(expected_session_id):
        raise RuntimeError("Didit returned a mismatched session")
    user_id = user_id_from_vendor_data(decision.get("vendor_data"))
    if not user_id:
        raise RuntimeError("Didit decision has invalid vendor data")
    return user_id


def apply_didit_status(db, user, session_id: str, status) -> str:
    clean_status = str(status or "").strip()
    normalized = clean_status.lower()
    user.age_verification_session_id = str(session_id)
    user.age_verification_provider = "didit"

    if normalized == "approved":
        user.age_verification_status = "approved"
        if not int(getattr(user, "age_verified_utc", 0) or 0):
            user.age_verified_utc = int(time.time())
        # Keep compatibility with the site's existing NSFW checks, but all new
        # contribution gates rely on age_verified_utc + approved status.
        user.over_18 = True
        grant_minor_strike_badge(db, user)
    elif not is_age_verified(user):
        user.age_verification_status = normalized or "unknown"
        if normalized in FINISHED_FAILURE_STATUSES:
            user.age_verified_utc = 0

    db.add(user)
    return normalized


def _shorten_floats(value):
    if isinstance(value, dict):
        return {key: _shorten_floats(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_shorten_floats(item) for item in value]
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return value


def verify_didit_webhook(payload: dict, signature: str, timestamp_header: str) -> bool:
    secret = str(os.environ.get("DIDIT_WEBHOOK_SECRET") or "").strip()
    if not secret or not signature or not timestamp_header:
        return False
    try:
        timestamp = int(timestamp_header)
    except (TypeError, ValueError):
        return False
    if abs(int(time.time()) - timestamp) > 300:
        return False
    payload_timestamp = payload.get("timestamp")
    if payload_timestamp is not None and str(payload_timestamp) != str(timestamp):
        return False
    canonical = json.dumps(
        _shorten_floats(payload),
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    )
    expected = hmac.new(
        secret.encode("utf-8"),
        canonical.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, str(signature))


def webhook_event_seen(db, event_id: str) -> bool:
    return bool(
        db.execute(
            text("SELECT 1 FROM age_verification_events WHERE event_id = :event_id"),
            {"event_id": event_id},
        ).first()
    )


def record_webhook_event(
    db,
    event_id: str,
    session_id: str,
    user_id: int,
    status: str,
    webhook_type: str,
) -> None:
    db.execute(
        text(
            """
            INSERT INTO age_verification_events
                (event_id, session_id, user_id, status, webhook_type, created_utc)
            VALUES
                (:event_id, :session_id, :user_id, :status, :webhook_type, :created_utc)
            """
        ),
        {
            "event_id": event_id,
            "session_id": session_id,
            "user_id": user_id,
            "status": status[:32],
            "webhook_type": webhook_type[:32],
            "created_utc": int(time.time()),
        },
    )


def install_chat_age_verification_gate(chat_module) -> None:
    """Enforce the same age gate in the independently served chat process."""
    global _chat_gate_installed
    if _chat_gate_installed:
        return

    app = chat_module.app
    original_view = app.view_functions.get("chat")
    if original_view:
        @wraps(original_view)
        def gated_chat_view(*args, **kwargs):
            if didit_enabled():
                user = chat_module.get_logged_in_user()
                if user and not is_age_verified(user):
                    return redirect("/age-verification?next=/chat&reason=chat")
            return original_view(*args, **kwargs)
        app.view_functions["chat"] = gated_chat_view

    handlers = chat_module.socketio.server.handlers.get("/", {})
    for event_name in ("connect", "speak"):
        original_handler = handlers.get(event_name)
        if not original_handler:
            continue

        def make_handler(original, current_event):
            @wraps(original)
            def gated_handler(*args, **kwargs):
                if didit_enabled():
                    user = chat_module.get_logged_in_user()
                    if user and not is_age_verified(user):
                        if current_event == "speak":
                            chat_module.emit(
                                "chat_error",
                                "Age verification is required before using public chat.",
                            )
                            return "", 403
                        return False
                return original(*args, **kwargs)
            return gated_handler

        handlers[event_name] = make_handler(original_handler, event_name)

    _chat_gate_installed = True
