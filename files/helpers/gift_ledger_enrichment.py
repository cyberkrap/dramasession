"""Gift-specific bank statement enrichment and historical ledger repair.

A ledger row is only a gift when its HTTP origin is an actual currency-transfer
endpoint.  Earlier versions wrapped economy_ledger._caller_context from this
module; because this filename itself contains ``gift``, the stack-based fallback
could see the wrapper before the real caller and incorrectly classify unrelated
balance changes as gifts.  Do not wrap caller classification from this module.
"""

import html
import importlib
import re

from markupsafe import Markup, escape
from sqlalchemy import func, text

from files.classes import Comment, Notification, User


_TRANSFER_PATH_RE = re.compile(r"^/@([^/]+)/transfer[-_](?:bux|coins)$", re.I)
_AWARD_PATH_RE = re.compile(r"^/award/(post|comment)/(\d+)$", re.I)
_PROFILE_LINK_RE = re.compile(r'href=["\']/@([^"\']+)["\']', re.I)
_BLOCKQUOTE_RE = re.compile(r"<blockquote[^>]*>(.*?)</blockquote>", re.I | re.S)
_TAG_RE = re.compile(r"<[^>]+>")


def _plain_text(fragment):
    value = _TAG_RE.sub("", fragment or "")
    return html.unescape(value).strip()


def _notification_details(db, target_username, created_utc):
    """Recover an old gift sender/message from the recipient notification."""
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
    target = str(
        meta.get("target_username") or meta.get("username") or meta.get("target") or ""
    ).strip() or None
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
    """Repair historical rows polluted by the old gift-context wrapper."""
    from files.__main__ import engine

    if engine.dialect.name != "postgresql":
        return

    with engine.begin() as conn:
        # Vote rewards/reversals never belong in Bank Statement.
        conn.execute(text("""
            DELETE FROM economy_ledger
            WHERE LOWER(COALESCE(origin_path, '')) LIKE '/vote/%'
        """))

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

        conn.execute(text("""
            UPDATE economy_ledger
            SET category = 'lottery', label = 'Lottery'
            WHERE (category = 'gifts' OR label = 'Gift')
              AND (
                LOWER(COALESCE(origin_path, '')) LIKE '/lottery%'
                OR LOWER(COALESCE(origin_path, '')) LIKE '/lottershe%'
              )
        """))

        # Award inventory purchases and awards applied to content.
        conn.execute(text("""
            UPDATE economy_ledger
            SET category = 'awards', label = 'Awards'
            WHERE (category = 'gifts' OR label = 'Gift')
              AND (
                COALESCE(origin_path, '') ~ '^/award/(post|comment)/[0-9]+$'
                OR COALESCE(origin_path, '') ~ '^/buy/[^/]+$'
              )
        """))

        # Username-effect purchases were a major visible casualty of the old bug.
        conn.execute(text("""
            UPDATE economy_ledger
            SET category = 'shop', label = 'Username effect'
            WHERE (category = 'gifts' OR label = 'Gift')
              AND LOWER(COALESCE(origin_path, '')) ~ '^/shop/effects/[^/]+/buy$'
        """))

        conn.execute(text("""
            UPDATE economy_ledger
            SET category = 'shop', label = 'Hat shop'
            WHERE (category = 'gifts' OR label = 'Gift')
              AND LOWER(COALESCE(origin_path, '')) ~ '^/buy_hat/[0-9]+$'
        """))

        # Approving a submitted emote pays its author 250 Wishcoins.  These rows
        # were repeatedly appearing as "Gift received" because of the wrapper bug.
        conn.execute(text("""
            UPDATE economy_ledger
            SET category = 'other', label = 'Emote approval reward'
            WHERE (category = 'gifts' OR label = 'Gift')
              AND currency = 'coins'
              AND amount = 250
              AND LOWER(COALESCE(origin_path, '')) LIKE '/admin/approve/marsey/%'
        """))

        # A transaction is not a gift merely because stale Gift metadata leaked
        # into it.  For any remaining row with a known non-transfer HTTP origin,
        # clear the false gift classification.  Its normal path-based renderer can
        # then describe it, or safely fall back to Balance credit/deduction.
        conn.execute(text("""
            UPDATE economy_ledger
            SET category = 'other', label = NULL
            WHERE (category = 'gifts' OR label = 'Gift')
              AND COALESCE(origin_path, '') <> ''
              AND COALESCE(origin_path, '') !~* '^/@[^/]+/transfer[-_](bux|coins)$'
        """))


def install_gift_ledger_enrichment():
    """Repair false gifts and make gift rendering proof-based, not label-based."""
    bank = importlib.import_module("files.routes.bank_statement")

    _repair_misclassified_rows()

    if not getattr(bank, "_gift_description_enriched", False):
        original_description = bank._transaction_description

        def transaction_description(row, statement_user):
            path = str(row.get("origin_path") or "")
            label = str(row.get("label") or "")

            # Only the real transfer endpoint is allowed to render as a gift.
            if _TRANSFER_PATH_RE.match(path):
                return _gift_description(bank, row, statement_user)

            if label == "Emote approval reward":
                return bank._link("/submit/marseys", "Emote approval reward")

            # Historical corrupted rows can still exist with no trustworthy path.
            # Never call them gifts without proof; let the normal renderer infer
            # from the path or fall back to a neutral balance description.
            if row.get("category") == "gifts" or label == "Gift":
                cleaned = dict(row)
                cleaned["category"] = "other"
                cleaned["label"] = ""
                return original_description(cleaned, statement_user)

            return original_description(row, statement_user)

        bank._transaction_description = transaction_description
        bank._gift_description_enriched = True
