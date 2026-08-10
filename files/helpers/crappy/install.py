import os
import secrets

from sqlalchemy import func
from werkzeug.security import check_password_hash

from files.classes import CrappyRequest, User
from files.helpers.security import hash_password

from .config import CRAPPY_USERNAME


def ensure_crappy_account(db) -> User:
    user = (
        db.query(User)
        .filter(func.lower(User.username) == CRAPPY_USERNAME.lower())
        .order_by(User.id.asc())
        .first()
    )
    if user:
        return user

    user = User(
        username=CRAPPY_USERNAME,
        original_username=CRAPPY_USERNAME,
        password=secrets.token_urlsafe(64),
        is_activated=True,
        over_18=True,
        bio="AI assistant for The Obsession Club.",
        bio_html="<p>AI assistant for The Obsession Club.</p>",
    )
    db.add(user)
    db.flush()
    return user


def _apply_configured_login_password(user: User) -> bool:
    """Optionally bootstrap/reset Crappy's interactive login password from Railway."""
    password = (os.environ.get("CRAPPY_LOGIN_PASSWORD") or "").strip()
    if not password:
        return False

    if not 8 <= len(password) <= 100:
        print(
            "CRAPPY_LOGIN_PASSWORD ignored: password must be between 8 and 100 characters",
            flush=True,
        )
        return False

    if user.passhash and check_password_hash(user.passhash, password):
        return False

    user.passhash = hash_password(password)
    return True


def install_crappy(engine, db_session_factory=None, enabled: bool = False) -> None:
    CrappyRequest.__table__.create(bind=engine, checkfirst=True)
    if not enabled or db_session_factory is None:
        return

    db = db_session_factory()
    try:
        user = ensure_crappy_account(db)
        if _apply_configured_login_password(user):
            db.add(user)
        db.commit()
    finally:
        db.close()
