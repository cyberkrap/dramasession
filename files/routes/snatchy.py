import hashlib
import hmac
import os
import time
from urllib.parse import quote

from flask import abort, g, request
from sqlalchemy import text

from files.__main__ import app, cache, db_session, engine, limiter
from files.classes import Submission, Sub, Vote
from files.helpers.sanitize import filter_emojis_only, sanitize, sanitize_raw_body, sanitize_raw_title
from files.helpers.snatchy import (
    SNATCHY_SOURCE_SUBREDDIT,
    ensure_snatchy_account,
    install_snatchy,
    snatchy_board_name,
)


SNATCHY_WEBHOOK_PATH = "/api/integrations/reddit/snatchy"
SNATCHY_REPLAY_WINDOW_SECONDS = 300
SNATCHY_MAX_PAYLOAD_BYTES = 2_000_000


install_snatchy(engine, db_session)


def _normalized_reddit_post_id(value) -> str:
    post_id = str(value or "").strip()
    if post_id.lower().startswith("t3_"):
        post_id = post_id[3:]
    if not post_id or len(post_id) > 61:
        abort(400, "Invalid Reddit post id")
    if not all(character.isalnum() or character in {"_", "-"} for character in post_id):
        abort(400, "Invalid Reddit post id")
    return post_id


def _normalized_subreddit(value) -> str:
    subreddit = str(value or "").strip().lower()
    if subreddit.startswith("r/"):
        subreddit = subreddit[2:]
    return subreddit


def _canonical_reddit_url(post_id: str) -> str:
    return f"https://www.reddit.com/comments/{quote(post_id, safe='')}"


def _source_created_utc(value) -> int:
    now = int(time.time())
    try:
        timestamp = int(float(value))
    except (TypeError, ValueError):
        return now
    if timestamp > 10_000_000_000:
        timestamp //= 1000
    if timestamp < 946684800 or timestamp > now + 300:
        return now
    return timestamp


def _invalidate_snatchy_caches() -> None:
    from files.routes.front import frontlist
    from files.routes.users import userpagelisting

    cache.delete_memoized(frontlist)
    cache.delete_memoized(userpagelisting)


def _verify_snatchy_webhook() -> bytes:
    secret = (os.environ.get("SNATCHY_WEBHOOK_SECRET") or "").strip()
    if not secret:
        abort(503, "Snatchy webhook secret is not configured")

    raw = request.get_data(cache=True)
    if len(raw) > SNATCHY_MAX_PAYLOAD_BYTES:
        abort(413)

    timestamp_header = (request.headers.get("X-Snatchy-Timestamp") or "").strip()
    signature_header = (request.headers.get("X-Snatchy-Signature") or "").strip().lower()
    if signature_header.startswith("sha256="):
        signature_header = signature_header[7:]

    try:
        timestamp = int(timestamp_header)
    except ValueError:
        abort(401)

    if abs(int(time.time()) - timestamp) > SNATCHY_REPLAY_WINDOW_SECONDS:
        abort(401)

    signed = timestamp_header.encode("ascii") + b"." + raw
    expected = hmac.new(secret.encode("utf-8"), signed, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, signature_header):
        abort(401)

    return raw


def _snatchy_render(title, body, snatchy):
    g.v = snatchy
    snatchy.client = None

    title = sanitize_raw_title(title)
    if not title:
        abort(400, "Reddit post has no title")
    title_html = filter_emojis_only(title, golden=False, graceful=True)

    body = sanitize_raw_body(body, True)
    body_html = sanitize(
        body,
        golden=False,
        limit_pings=0,
        showmore=False,
        count_marseys=False,
    )
    return title, title_html, body, body_html


def _existing_import(post_id: str):
    return g.db.execute(text("""
        SELECT reddit_post_id, toc_submission_id, source_deleted_utc
        FROM snatchy_imports
        WHERE reddit_post_id = :post_id
    """), {"post_id": post_id}).mappings().first()


def _reserve_import(post_id: str, author_name: str, permalink: str, source_created_utc: int) -> bool:
    result = g.db.execute(text("""
        INSERT INTO snatchy_imports (
            reddit_post_id, toc_submission_id, source_author_name,
            source_permalink, source_created_utc, created_utc, source_deleted_utc
        ) VALUES (
            :post_id, NULL, :author_name, :permalink,
            :source_created_utc, :created_utc, 0
        )
        ON CONFLICT (reddit_post_id) DO NOTHING
    """), {
        "post_id": post_id,
        "author_name": author_name,
        "permalink": permalink,
        "source_created_utc": source_created_utc,
        "created_utc": int(time.time()),
    })
    return bool(result.rowcount)


def _import_reddit_post(payload):
    post_id = _normalized_reddit_post_id(payload.get("redditPostId"))
    existing = _existing_import(post_id)
    if existing and existing["toc_submission_id"]:
        return {
            "status": "duplicate",
            "post_id": int(existing["toc_submission_id"]),
        }

    author_name = str(payload.get("redditAuthor") or "").strip()[:255]
    if not author_name:
        abort(400, "Reddit post has no author")

    source_created_utc = _source_created_utc(payload.get("createdUtc"))
    permalink = str(payload.get("sourcePermalink") or _canonical_reddit_url(post_id)).strip()[:2048]

    if not existing and not _reserve_import(post_id, author_name, permalink, source_created_utc):
        existing = _existing_import(post_id)
        if existing and existing["toc_submission_id"]:
            return {
                "status": "duplicate",
                "post_id": int(existing["toc_submission_id"]),
            }
        abort(409, "Reddit post import is already in progress")

    board_name = snatchy_board_name()
    board = g.db.query(Sub).filter(Sub.name == board_name).one_or_none()
    if not board:
        abort(503, f"Snatchy destination board /b/{board_name} does not exist")

    snatchy = ensure_snatchy_account(g.db)
    title, title_html, body, body_html = _snatchy_render(
        payload.get("title"),
        payload.get("body"),
        snatchy,
    )

    post = Submission(
        private=False,
        notify=False,
        author_id=snatchy.id,
        over_18=bool(payload.get("over18")),
        new=False,
        app_id=None,
        is_bot=True,
        url=_canonical_reddit_url(post_id),
        body=body,
        body_html=body_html,
        embed_url=None,
        title=title,
        title_html=title_html,
        sub=board.name,
        ghost=False,
        created_utc=source_created_utc,
    )
    g.db.add(post)
    g.db.flush()

    g.db.add(Vote(user_id=snatchy.id, vote_type=1, submission_id=post.id))
    g.db.execute(text("""
        UPDATE snatchy_imports
        SET toc_submission_id = :toc_submission_id,
            source_author_name = :author_name,
            source_permalink = :permalink,
            source_created_utc = :source_created_utc
        WHERE reddit_post_id = :post_id
    """), {
        "toc_submission_id": post.id,
        "author_name": author_name,
        "permalink": permalink,
        "source_created_utc": source_created_utc,
        "post_id": post_id,
    })

    snatchy.post_count = g.db.query(Submission).filter_by(
        author_id=snatchy.id,
        deleted_utc=0,
    ).count()
    g.db.add(snatchy)

    _invalidate_snatchy_caches()
    return {
        "status": "created",
        "post_id": post.id,
        "permalink": post.permalink,
    }


def _scrub_deleted_reddit_post(payload):
    post_id = _normalized_reddit_post_id(payload.get("redditPostId"))
    mapping = _existing_import(post_id)
    if not mapping or not mapping["toc_submission_id"]:
        return {"status": "ignored"}

    toc_post_id = int(mapping["toc_submission_id"])
    if mapping["source_deleted_utc"]:
        return {"status": "already_scrubbed", "post_id": toc_post_id}

    snatchy = ensure_snatchy_account(g.db)
    post = g.db.query(Submission).filter(Submission.id == toc_post_id).one_or_none()
    now = int(time.time())

    if post:
        title, title_html, body, body_html = _snatchy_render(
            "[Deleted Reddit post]",
            "The original Reddit post was deleted. The TOC discussion is preserved here.",
            snatchy,
        )
        post.title = title
        post.title_html = title_html
        post.body = body
        post.body_html = body_html
        post.url = ""
        post.thumburl = None
        post.embed_url = None
        post.flair = None
        post.over_18 = False
        post.edited_utc = now
        g.db.add(post)

    g.db.execute(text("""
        UPDATE snatchy_imports
        SET source_author_name = NULL,
            source_permalink = NULL,
            source_deleted_utc = :deleted_utc
        WHERE reddit_post_id = :post_id
    """), {"deleted_utc": now, "post_id": post_id})

    _invalidate_snatchy_caches()
    return {"status": "scrubbed", "post_id": toc_post_id}


@app.post(SNATCHY_WEBHOOK_PATH)
@limiter.limit("60/minute")
def snatchy_reddit_webhook():
    _verify_snatchy_webhook()
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        abort(400)

    if payload.get("source") != "reddit":
        abort(400, "Unsupported Snatchy source")
    if _normalized_subreddit(payload.get("subreddit")) != SNATCHY_SOURCE_SUBREDDIT:
        abort(403)

    action = payload.get("action")
    if action == "import":
        result = _import_reddit_post(payload)
    elif action == "source_deleted":
        result = _scrub_deleted_reddit_post(payload)
    else:
        abort(400, "Unsupported Snatchy action")

    return result, 200
