import secrets

from sqlalchemy import func

from files.classes import CrappyRequest, User

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


def install_crappy(engine, db_session_factory=None, enabled: bool = False) -> None:
    CrappyRequest.__table__.create(bind=engine, checkfirst=True)
    if not enabled or db_session_factory is None:
        return

    db = db_session_factory()
    try:
        ensure_crappy_account(db)
        db.commit()
    finally:
        db.close()
