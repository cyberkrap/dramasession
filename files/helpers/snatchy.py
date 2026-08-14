import os
import secrets

from sqlalchemy import func, text

from files.classes import User


SNATCHY_USERNAME = "Snatchy"
SNATCHY_SOURCE_SUBREDDIT = "obsessionmovie"
SNATCHY_DEFAULT_BOARD = "obsession"


def snatchy_board_name() -> str:
    value = (os.environ.get("SNATCHY_BOARD") or SNATCHY_DEFAULT_BOARD).strip().lower()
    for prefix in ("/b/", "/h/"):
        if value.startswith(prefix):
            value = value[len(prefix):]
            break
    return value or SNATCHY_DEFAULT_BOARD


def ensure_snatchy_account(db) -> User:
    user = (
        db.query(User)
        .filter(func.lower(User.username) == SNATCHY_USERNAME.lower())
        .order_by(User.id.asc())
        .first()
    )
    if user:
        return user

    user = User(
        username=SNATCHY_USERNAME,
        original_username=SNATCHY_USERNAME,
        password=secrets.token_urlsafe(64),
        is_activated=True,
        over_18=True,
        bio="Reddit courier for The Obsession Club.",
        bio_html="<p>Reddit courier for The Obsession Club.</p>",
    )
    db.add(user)
    db.flush()
    return user


def install_snatchy(engine, db_session_factory) -> None:
    with engine.begin() as connection:
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS snatchy_imports (
                reddit_post_id VARCHAR(64) PRIMARY KEY,
                toc_submission_id INTEGER REFERENCES submissions(id) ON DELETE CASCADE,
                source_author_name VARCHAR(255),
                source_permalink TEXT,
                source_created_utc BIGINT,
                created_utc BIGINT NOT NULL,
                source_deleted_utc BIGINT NOT NULL DEFAULT 0
            )
        """))
        connection.execute(text("""
            CREATE UNIQUE INDEX IF NOT EXISTS ux_snatchy_imports_submission
            ON snatchy_imports (toc_submission_id)
        """))

    db = db_session_factory()
    try:
        ensure_snatchy_account(db)
        db.commit()
    finally:
        db.close()
