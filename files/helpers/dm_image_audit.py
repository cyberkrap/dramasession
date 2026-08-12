import html
import os
import re
import time
from functools import wraps
from pathlib import Path
from urllib.parse import urlparse

import fcntl
from flask import g, render_template, request
from sqlalchemy import or_

from files.__main__ import app, limiter
from files.classes import Comment, User
from files.classes.media import Media
from files.helpers.config.const import DEFAULT_RATELIMIT, LOG_DIRECTORY, MODMAIL_ID, PERMS, SITE_FULL
from files.routes.wrappers import admin_level_required, get_ID

_LOG_PATH = Path(LOG_DIRECTORY) / "dm_images.log"
_LOCK_PATH = "/tmp/obsession-dm-image-audit.lock"
_SITE_NETLOC = urlparse(SITE_FULL).netloc.lower()
_IMAGE_URL_RE = re.compile(r"""(?P<url>https?://[^\s\"'<>]+/(?:images|dm_images)/[A-Za-z0-9._-]+\.webp(?:\?[^\s\"'<>]*)?|/(?:images|dm_images)/[A-Za-z0-9._-]+\.webp(?:\?[^\s\"'<>]*)?)""", re.I)


def _format_utc(ts):
    try: ts = int(float(ts))
    except (TypeError, ValueError): return "Unknown"
    return time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime(ts)) if ts > 0 else "Unknown"


def _display_timestamp(value):
    try:
        calendar = __import__("calendar")
        return calendar.timegm(time.strptime(str(value), "%Y-%m-%d %H:%M:%S UTC"))
    except (TypeError, ValueError, OverflowError):
        return 0


def _normalize_image_url(value):
    value = html.unescape(str(value or "")).strip()
    if not value: return None
    try: parsed = urlparse(value)
    except ValueError: return None
    if parsed.scheme:
        if parsed.scheme not in {"http", "https"} or (parsed.netloc and parsed.netloc.lower() != _SITE_NETLOC):
            return None
        path = parsed.path
    else:
        path = value.split("?", 1)[0]
    if not path.startswith(("/images/", "/dm_images/")) or not path.lower().endswith(".webp"):
        return None
    return f"{SITE_FULL.rstrip('/')}{path}"


def _infer_timestamp(url):
    normalized = _normalize_image_url(url)
    if not normalized: return 0
    stem = os.path.basename(urlparse(normalized).path).rsplit(".", 1)[0]
    digits = "".join(c for c in stem if c.isdigit())
    if len(digits) < 10: return 0
    try: ts = int(digits[:10])
    except ValueError: return 0
    return ts if 1_400_000_000 <= ts <= int(time.time()) + 86400 else 0


def _entry(url, sender, sender_id, recipient, recipient_id, sent=None):
    normalized = _normalize_image_url(url)
    if not normalized: return None
    explicit = bool(sent)
    ts = _display_timestamp(sent) if sent else 0
    if not ts: ts = _infer_timestamp(normalized)
    return {"url": normalized, "sender": str(sender or "Unknown"), "sender_id": str(sender_id or ""),
            "recipient": str(recipient or "Unknown"), "recipient_id": str(recipient_id or ""),
            "sent_utc": _format_utc(ts), "sent_epoch": ts, "explicit_date": bool(explicit and ts)}


def _dedupe(entries):
    kept = []
    for item in sorted(entries, key=lambda x: (x["sent_epoch"], x["explicit_date"]), reverse=True):
        duplicate = False
        for old in kept:
            same = item["url"] == old["url"] and item["sender_id"] == old["sender_id"] and item["recipient_id"] == old["recipient_id"]
            if not same: continue
            if item["sent_epoch"] and old["sent_epoch"] and abs(item["sent_epoch"] - old["sent_epoch"]) <= 30:
                duplicate = True; break
            if not item["sent_epoch"] and not old["sent_epoch"]:
                duplicate = True; break
        if not duplicate: kept.append(item)
    return kept


def read_dm_image_log():
    if not _LOG_PATH.exists(): return []
    try: lines = _LOG_PATH.read_text(encoding="utf-8").splitlines()
    except OSError: return []
    entries, pending = [], []
    for raw in lines:
        line = raw.strip()
        if not line: continue
        parts = line.split(", ")
        if len(parts) >= 5 and _normalize_image_url(parts[0]):
            urls = pending + [parts[0]]; pending = []
            sent = ", ".join(parts[5:]).strip() if len(parts) > 5 else None
            for url in urls:
                item = _entry(url, parts[1], parts[2], parts[3], parts[4], sent)
                if item: entries.append(item)
        elif _normalize_image_url(line):
            pending.append(line)
    for url in pending:
        item = _entry(url, "Unknown", "", "Unknown", "")
        if item: entries.append(item)
    return _dedupe(entries)


def _append(item):
    _LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    line = ", ".join((item["url"], item["sender"], item["sender_id"], item["recipient"], item["recipient_id"], item["sent_utc"]))
    with open(_LOCK_PATH, "w", encoding="utf-8") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        with open(_LOG_PATH, "a", encoding="utf-8") as stream:
            stream.write(line + "\n")


def _local_images(comment, actor_id):
    body = html.unescape(str(comment.body_html or ""))
    found = []
    for match in _IMAGE_URL_RE.finditer(body):
        url = _normalize_image_url(match.group("url"))
        if not url or url in found: continue
        path = urlparse(url).path
        exists = g.db.query(Media.filename).filter(Media.kind == "image", Media.filename == path, Media.user_id == actor_id).first()
        if exists: found.append(url)
    return found


def _recipient(comment):
    if comment.sentto == MODMAIL_ID: return "Modmail", "Modmail"
    if comment.sentto:
        user = g.db.get(User, comment.sentto)
        if user: return user.username, str(user.id)
    if comment.top_comment_id:
        top = g.db.get(Comment, comment.top_comment_id)
        if top and top.sentto == MODMAIL_ID: return "Modmail", "Modmail"
        if top and top.sentto:
            # A reply remains part of the same DM thread. If the current author
            # is the root recipient, the audit recipient is the root sender;
            # otherwise it is still the root recipient.
            if comment.author_id == top.sentto:
                sender = g.db.get(User, top.author_id)
                if sender: return sender.username, str(sender.id)
            recipient = g.db.get(User, top.sentto)
            if recipient: return recipient.username, str(recipient.id)
    return "Unknown", ""


def _audit_item(comment, actor, url):
    recipient, recipient_id = _recipient(comment)
    if recipient == "Unknown": return None
    sent_epoch = int(comment.created_utc or time.time())
    return {"url": url, "sender": actor.username, "sender_id": str(actor.id), "recipient": recipient,
            "recipient_id": str(recipient_id), "sent_utc": _format_utc(sent_epoch),
            "sent_epoch": sent_epoch, "explicit_date": True}


def _historical_entries():
    comments = g.db.query(Comment).filter(
        Comment.parent_submission.is_(None),
        Comment.wall_user_id.is_(None),
        or_(Comment.body_html.ilike("%/images/%"), Comment.body_html.ilike("%/dm_images/%")),
    ).order_by(Comment.created_utc.desc()).all()
    entries = []
    for comment in comments:
        actor = g.db.get(User, comment.author_id)
        if not actor: continue
        for url in _local_images(comment, actor.id):
            item = _audit_item(comment, actor, url)
            if item: entries.append(item)
    return entries


def _audit(comment, actor):
    urls = _local_images(comment, actor.id)
    if not urls: return
    current = read_dm_image_log()
    for url in urls:
        item = _audit_item(comment, actor, url)
        if not item: continue
        if any(x["url"] == item["url"] and x["sender_id"] == item["sender_id"] and x["recipient_id"] == item["recipient_id"]
               and x["sent_epoch"] and abs(x["sent_epoch"] - item["sent_epoch"]) <= 30 for x in current):
            continue
        _append(item); current.append(item)


def _latest(endpoint, actor, started_at):
    q = g.db.query(Comment).filter(Comment.author_id == actor.id, Comment.parent_submission.is_(None), Comment.created_utc >= started_at - 2)
    if endpoint == "message2":
        q = q.filter(Comment.level == 1, Comment.sentto.isnot(None))
    elif endpoint == "messagereply":
        try: parent_id = int(request.values.get("parent_id"))
        except (TypeError, ValueError): parent_id = None
        q = q.filter(Comment.parent_comment_id == parent_id) if parent_id else q.filter(Comment.parent_comment_id.isnot(None))
    elif endpoint == "submit_contact":
        q = q.filter(Comment.level == 1, Comment.sentto == MODMAIL_ID, Comment.parent_comment_id.is_(None))
    return q.order_by(Comment.id.desc()).first()


def _wrap(endpoint):
    original = app.view_functions.get(endpoint)
    if not original or getattr(original, "_dm_image_audit", False): return
    @wraps(original)
    def wrapped(*args, **kwargs):
        started_at = int(time.time())
        response = original(*args, **kwargs)
        actor = getattr(g, "v", None)
        if actor and getattr(g, "db", None):
            try:
                comment = _latest(endpoint, actor, started_at)
                if comment: _audit(comment, actor)
            except Exception as error:
                print(f"DM image audit failed ({type(error).__name__})", flush=True)
        return response
    wrapped._dm_image_audit = True
    app.view_functions[endpoint] = wrapped


@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@admin_level_required(PERMS["VIEW_DM_IMAGES"])
def dm_images_audit(v):
    items = _dedupe(read_dm_image_log() + _historical_entries())
    return render_template("admin/dm_images.html", v=v, items=items)


def install_dm_image_audit():
    for endpoint in ("message2", "messagereply", "submit_contact"): _wrap(endpoint)
    app.view_functions["dm_images"] = dm_images_audit
