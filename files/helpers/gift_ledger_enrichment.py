"""Gift-specific enrichment for the economy ledger and bank statement.

Keeps transfer behavior untouched while preserving the useful human context:
who sent/received the gift and the optional gift message. Older ledger rows can
recover that context from the existing AutoJanny transfer notification.

Request paths with unambiguous meaning (casino, lottery, awards) are classified
before any stack-based inference. A balance mutation made by one of those routes
must never inherit stale Gift context.
"""

import html
import importlib
import inspect
import re

from flask import has_request_context, request
from markupsafe import Markup, escape
from sqlalchemy import func, text

from files.classes import Comment, Notification, User


_TRANSFER_PATH_RE = re.compile(r"^/@([^/]+)/transfer[-_](?:bux|coins)$", re.I)
_AWARD_PATH_RE = re.compile(r"^/award/(post|comment)/(\d+)$", re.I)
_PROFILE_LINK_RE = re.compile(r'href=["\']/@([^"\']+)["\']', re.I)
_BLOCKQUOTE_RE = re.compile(r"<blockquote[^>]*>(.*?)</blockquote>", re.I | re.S)
_TAG_RE = re.compile(r"<[^>]+>")


def _username(value):
    return str(getattr(value, "username", "") or "")[:80]


def _request_classification():
    """Return authoritative classification for routes with unambiguous meaning."""
    if not has_request_context():
        return None

    raw_path = str(request.path or "")
    path = raw_path.lower()
    if path.startswith("/casino/slots"):
        return "casino", "Slots", {}
    if path.startswith("/casino/twentyone") or path.startswith("/casino/blackjack"):
        return "casino", "Blackjack", {}
    if path.startswith("/casino/roulette"):
        return "casino", "Roulette", {}
    if path.startswith("/casino/"):
        return "casino", "Casino", {}
    if path.startswith("/lottery") or path.startswith("/lottershe"):
        return "lottery", "Lottery", {}

    award_match = _AWARD_PATH_RE.match(raw_path)
    if award_match:
        thing_type, thing_id = award_match.groups()
        meta = {
            "thing_type": thing_type.lower(),
            "thing_id": str(thing_id)[:24],
        }
        kind = str(request.values.get("kind") or request.values.get("award") or "").strip()
        if kind:
            meta["award_kind"] = kind[:80]
            meta["kind"] = kind[:80]
        raw_quantity = request.values.get("amount") or request.values.get("quantity")
        try:
            quantity = max(1, min(30, int(raw_quantity or 1)))
        except (TypeError, ValueError):
            quantity = 1
        meta["batch_quantity"] = quantity
        meta["amount"] = str(quantity)
        return "awards", "Awards", meta

    return None


def _gift_frame_context(account):
    """Read the real transfer_currency locals without changing that function."""
    frame = inspect.currentframe()
    try:
        frame = frame.f_back if frame else None
        for _ in range(18):
            if frame is None:
                break
            if frame.f_code.co_name == "transfer_currency":
                local = frame.f_locals
                actor = local.get("v")
                receiver = local.get("receiver")
                reason = str(local.get("reason") or "").strip()
                meta = {}
                if _username(actor):
                    meta["actor_username"] = _username(actor)
                if _username(receiver):
                    meta["target_username"] = _username(receiver)
                if reason:
                    meta["gift_message"] = reason[:500]
                if getattr(account, "id", None) == getattr(actor, "id", None):
                    meta["account_role"] = "sender"
                elif getattr(account, "id", None) == getattr(receiver, "id", None):
                    meta["account_role"] = "recipient"
                return meta
            frame = frame.f_back
    finally:
        del frame
    return None


def _plain_text(fragment):
    value = _TAG_RE.sub("", fragment or "")
    return html.unescape(value).strip()


def _notification_details(db, target_username, created_utc):
    """Recover old gift sender/message from the recipient's transfer notification."""
    if not target_username or not created_utc:
        return None, None

    target = db.query(User).filter(func.lower(User.username) == target_username.lower()).first()
    if target is None:
        return None, None

    rows = db.query(Comment.body_html, Notification.created_utc).join(
        Notification,
        Notification.comment_id == Comment.id,
    ).filter(
        Notification.user_id == target.id,
        Notification.created_utc >= int(created_utc) - 180,
        Notification.created_utc <= int(created_utc) + 180,
        Comment.body_html.ilike("%has gifted you%"),
    ).order_by(
        func.abs(Notification.created_utc - int(created_utc)),
        Notification.created_utc.desc(),
    ).limit(8).all()

    for body_html, _notification_utc in rows:
        body_html = str(body_html or "")
        actor_match = _PROFILE_LINK_RE.search(body_html)
        actor = actor_match.group(1) if actor_match else None
        quote_match = _BLOCKQUOTE_RE.search(body_html)
        message = _plain_text(quote_match.group(1)) if quote_match else None
        if actor or message:
            return actor, message
    return None, None


def _gift_details(bank_module, row, statement_user):
    meta = bank_module._safe_json(row.get("context_json"))
    path = str(row.get("origin_path") or "")
    amount = int(row.get("amount") or 0)
    role = meta.get("account_role")
    actor = str(meta.get("actor_username") or "").strip() or None
    target = str(meta.get("target_username") or meta.get("username") or meta.get("target") or "").strip() or None
    message = str(meta.get("gift_message") or meta.get("reason") or "").strip() or None

    path_match = _TRANSFER_PATH_RE.match(path)
    if path_match and not target:
        target = path_match.group(1)

    if target and (not actor or not message):
        recovered_actor, recovered_message = _notification_details(
            bank_module.g.db,
            target,
            int(row.get("created_utc") or 0),
        )
        actor = actor or recovered_actor
        message = message or recovered_message

    if not role:
        if amount < 0:
            role = "sender"
        elif target and statement_user.username.lower() == target.lower():
            role = "recipient"

    return role, actor, target, message


def _gift_description(bank_module, row, statement_user):
    role, actor, target, message = _gift_details(bank_module, row, statement_user)
    amount = int(row.get("amount") or 0)

    if amount < 0 or role == "sender":
        if target:
            headline = Markup("Gift sent to {}").format(
                bank_module._link(f"/@{target}", f"@{target}")
            )
        else:
            headline = Markup("Gift sent")
    else:
        if actor:
            headline = Markup("Gift from {}").format(
                bank_module._link(f"/@{actor}", f"@{actor}")
            )
        else:
            headline = Markup("Gift received")

    if not message:
        return headline

    note = Markup(
        '<div class="mt-2 px-3 py-2 border-left border-light font-weight-normal">{}</div>'
    ).format(escape(message))
    return headline + note


def _repair_misclassified_rows():
    """Repair rows produced before authoritative request classification existed."""
    from files.__main__ import engine

    if engine.dialect.name != "postgresql":
        return

    with engine.begin() as conn:
        conn.execute(text("""
            UPDATE economy_ledger
            SET category = 'casino',
                label = CASE
                    WHEN LOWER(COALESCE(origin_path, '')) LIKE '/casino/slots%' THEN 'Slots'
                    WHEN LOWER(COALESCE(origin_path, '')) LIKE '/casino/twentyone%'
                      OR LOWER(COALESCE(origin_path, '')) LIKE '/casino/blackjack%' THEN 'Blackjack'
                    WHEN LOWER(COALESCE(origin_path, '')) LIKE '/casino/roulette%' THEN 'Roulette'
                    ELSE 'Casino'
                END
            WHERE (category = 'gifts' OR label = 'Gift')
              AND LOWER(COALESCE(origin_path, '')) LIKE '/casino/%'
        """))
        # Any balance mutation whose HTTP origin is the award endpoint is an
        # award purchase/payout, even if an older stale context labeled it Gift.
        conn.execute(text("""
            UPDATE economy_ledger
            SET category = 'awards', label = 'Awards'
            WHERE COALESCE(origin_path, '') ~ '^/award/(post|comment)/[0-9]+$'
              AND (category <> 'awards' OR COALESCE(label, '') <> 'Awards')
        """))


def install_gift_ledger_enrichment():
    """Patch the already-installed ledger wrapper and bank renderer in-place."""
    ledger = importlib.import_module("files.helpers.economy_ledger")
    bank = importlib.import_module("files.routes.bank_statement")

    _repair_misclassified_rows()

    if not getattr(ledger, "_gift_context_enriched", False):
        original_caller_context = ledger._caller_context

        def caller_context(account):
            route_context = _request_classification()
            if route_context is not None:
                return route_context

            # Gift enrichment activates only on a real transfer endpoint.
            if has_request_context():
                path_match = _TRANSFER_PATH_RE.match(str(request.path or ""))
                if path_match:
                    gift_meta = _gift_frame_context(account) or {}
                    gift_meta.setdefault("target_username", path_match.group(1))
                    return "gifts", "Gift", gift_meta

            return original_caller_context(account)

        ledger._caller_context = caller_context
        ledger._gift_context_enriched = True

    if not getattr(bank, "_gift_description_enriched", False):
        original_description = bank._transaction_description

        def transaction_description(row, statement_user):
            path = str(row.get("origin_path") or "")
            label = str(row.get("label") or "")
            # Only actual transfer rows are gifts. A stale `Gift` label on an
            # authoritative award/casino route must never override its route.
            if _TRANSFER_PATH_RE.match(path) or (
                row.get("category") == "gifts" and not _AWARD_PATH_RE.match(path)
            ):
                return _gift_description(bank, row, statement_user)
            return original_description(row, statement_user)

        bank._transaction_description = transaction_description
        bank._gift_description_enriched = True
