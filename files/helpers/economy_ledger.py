"""Immutable Wishcoin/Wishbux balance ledger.

The PostgreSQL trigger is authoritative: every users.coins/users.marseybux change
is recorded, including bulk SQL updates. Request and caller context only enrich
those immutable rows so the bank statement can describe what actually happened.
"""

import inspect
import json
from functools import wraps

from flask import g, has_request_context, request
from sqlalchemy import text

from files.helpers.config.const import SITE_NAME


_LEDGER_DDL = r"""
SELECT pg_advisory_xact_lock(hashtext('toc_economy_ledger_install'));

CREATE TABLE IF NOT EXISTS economy_ledger (
    id BIGSERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    currency VARCHAR(16) NOT NULL,
    amount BIGINT NOT NULL,
    balance_after BIGINT NOT NULL,
    category VARCHAR(24) NOT NULL DEFAULT 'other',
    label TEXT,
    origin_path TEXT,
    context_json TEXT,
    created_utc BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM NOW())::BIGINT)
);
ALTER TABLE economy_ledger ADD COLUMN IF NOT EXISTS label TEXT;

CREATE INDEX IF NOT EXISTS ix_economy_ledger_user_currency_created
    ON economy_ledger (user_id, currency, created_utc DESC, id DESC);
CREATE INDEX IF NOT EXISTS ix_economy_ledger_user_category_created
    ON economy_ledger (user_id, category, created_utc DESC, id DESC);

CREATE OR REPLACE FUNCTION toc_record_economy_change()
RETURNS TRIGGER AS $$
DECLARE
    req_path TEXT := COALESCE(current_setting('toc.request_path', true), '');
    req_meta TEXT := COALESCE(current_setting('toc.request_meta', true), '');
    category_override TEXT := COALESCE(current_setting('toc.economy_category', true), '');
    label_override TEXT := COALESCE(current_setting('toc.economy_label', true), '');
    meta_override TEXT := COALESCE(current_setting('toc.economy_meta', true), '');
    normalized TEXT := LOWER(req_path);
    tx_category TEXT;
    merged_meta TEXT;
BEGIN
    -- Some balance changes are intentionally not user-facing financial
    -- transactions. Vote rewards/reversals are one example: they affect the
    -- live Wishcoin balance but should not flood Bank Statement.
    IF category_override = '__skip__' THEN
        RETURN NEW;
    END IF;

    tx_category := COALESCE(NULLIF(category_override, ''), CASE
        WHEN normalized LIKE '%slot%' OR normalized LIKE '%roulette%'
          OR normalized LIKE '%blackjack%' OR normalized LIKE '%twentyone%'
          OR normalized LIKE '%casino%' THEN 'casino'
        WHEN normalized LIKE '%lottery%' THEN 'lottery'
        WHEN normalized LIKE '%award%' OR normalized LIKE '/buy/%' THEN 'awards'
        WHEN normalized LIKE '%gift%' OR normalized LIKE '%transfer%' THEN 'gifts'
        WHEN normalized LIKE '%exchange%' THEN 'exchange'
        WHEN normalized LIKE '%hat%' OR normalized LIKE '%shop%'
          OR normalized LIKE '%username_effect%' OR normalized LIKE '%username-effect%'
          OR normalized LIKE '%effect%' THEN 'shop'
        WHEN normalized LIKE '%paypal%' OR normalized LIKE '%donat%' THEN 'patron'
        WHEN normalized LIKE '%admin%' OR normalized LIKE '%mod%' THEN 'admin'
        WHEN normalized LIKE '%bet%' OR normalized LIKE '%poll%' THEN 'bets'
        ELSE 'other'
    END);

    merged_meta := (
        COALESCE(NULLIF(req_meta, ''), '{}')::jsonb
        || COALESCE(NULLIF(meta_override, ''), '{}')::jsonb
    )::text;

    IF NEW.coins IS DISTINCT FROM OLD.coins THEN
        INSERT INTO economy_ledger
            (user_id, currency, amount, balance_after, category, label, origin_path, context_json)
        VALUES
            (NEW.id, 'coins', COALESCE(NEW.coins, 0) - COALESCE(OLD.coins, 0),
             COALESCE(NEW.coins, 0), tx_category, NULLIF(label_override, ''),
             NULLIF(req_path, ''), NULLIF(merged_meta, '{}'));
    END IF;

    IF NEW.marseybux IS DISTINCT FROM OLD.marseybux THEN
        INSERT INTO economy_ledger
            (user_id, currency, amount, balance_after, category, label, origin_path, context_json)
        VALUES
            (NEW.id, 'wishbux', COALESCE(NEW.marseybux, 0) - COALESCE(OLD.marseybux, 0),
             COALESCE(NEW.marseybux, 0), tx_category, NULLIF(label_override, ''),
             NULLIF(req_path, ''), NULLIF(merged_meta, '{}'));
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS toc_economy_ledger_trigger ON users;
CREATE TRIGGER toc_economy_ledger_trigger
AFTER UPDATE OF coins, marseybux ON users
FOR EACH ROW
WHEN (OLD.coins IS DISTINCT FROM NEW.coins OR OLD.marseybux IS DISTINCT FROM NEW.marseybux)
EXECUTE FUNCTION toc_record_economy_change();

CREATE TABLE IF NOT EXISTS economy_ledger_data_migrations (
    migration_key TEXT PRIMARY KEY,
    applied_utc BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM NOW())::BIGINT)
);

-- Vote rewards are deliberately invisible in Bank Statement. Remove historical
-- vote-generated rows as well as suppressing future ones in _caller_context.
DELETE FROM economy_ledger
WHERE LOWER(COALESCE(origin_path, '')) LIKE '/vote/%';

DO $$
DECLARE
    target_user_id INTEGER;
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM economy_ledger_data_migrations
        WHERE migration_key = 'cybercrap_wishbux_tier5_seed_20260808'
    ) THEN
        SELECT id INTO target_user_id
        FROM users
        WHERE LOWER(username) = 'cybercrap' OR LOWER(COALESCE(original_username, '')) = 'cybercrap'
        ORDER BY CASE WHEN LOWER(username) = 'cybercrap' THEN 0 ELSE 1 END, id
        LIMIT 1;

        IF target_user_id IS NOT NULL THEN
            UPDATE users SET marseybux = 0 WHERE id = target_user_id;
            DELETE FROM economy_ledger
            WHERE user_id = target_user_id AND currency = 'wishbux';

            PERFORM set_config('toc.request_path', '/donate', true);
            PERFORM set_config('toc.request_meta', '{}', true);
            PERFORM set_config('toc.economy_category', 'patron', true);
            PERFORM set_config('toc.economy_label', 'Patron reward', true);
            PERFORM set_config(
                'toc.economy_meta',
                '{"tier_name":"Ian''s Bankroller","manual_seed":"cybercrap-tier5-reset-20260808"}',
                true
            );
            UPDATE users SET marseybux = 140000 WHERE id = target_user_id;

            INSERT INTO economy_ledger_data_migrations (migration_key)
            VALUES ('cybercrap_wishbux_tier5_seed_20260808');

            PERFORM set_config('toc.request_path', '', true);
            PERFORM set_config('toc.request_meta', '{}', true);
            PERFORM set_config('toc.economy_category', '', true);
            PERFORM set_config('toc.economy_label', '', true);
            PERFORM set_config('toc.economy_meta', '{}', true);
        END IF;
    END IF;
END;
$$;
"""

_SAFE_CONTEXT_KEYS = {
    "username", "user", "target", "name", "amount", "currency", "coins",
    "marseybux", "wishbux", "award", "award_id", "kind", "bet", "wager",
    "game", "quantity", "item", "item_id", "post_id", "comment_id",
    "submission_id", "note",
}


def _username(value):
    return str(getattr(value, "username", "") or "")[:80]


def _caller_context(account):
    """Infer subsystem and useful object metadata from the economy caller."""
    frame = inspect.currentframe()
    try:
        frame = frame.f_back if frame else None
        for _ in range(14):
            if frame is None:
                break
            filename = frame.f_code.co_filename.replace('\\', '/').lower()
            func = frame.f_code.co_name.lower()
            haystack = f"{filename} {func}"
            local = frame.f_locals
            meta = {}

            # Upvote/downvote Wishcoin deltas are intentionally not part of the
            # bank ledger. Their balances still change normally; only the
            # user-facing transaction record is suppressed.
            if filename.endswith('/routes/votes.py') or func == 'vote_post_comment':
                return "__skip__", "", meta

            if "slots.py" in filename or "slot" in func:
                return "casino", "Slots", meta
            if "twentyone.py" in filename or "blackjack" in haystack or "twentyone" in haystack:
                return "casino", "Blackjack", meta
            if "roulette" in haystack:
                return "casino", "Roulette", meta
            if "lottery" in haystack:
                return "lottery", "Lottery", meta

            if "award" in haystack:
                kind = local.get("kind") or local.get("award")
                if isinstance(kind, str):
                    meta["award_kind"] = kind[:80]
                title = local.get("award_title")
                if title:
                    meta["award_title"] = str(title)[:120]
                thing_type = local.get("thing_type")
                if thing_type in {"post", "comment"}:
                    meta["thing_type"] = thing_type
                    thing = local.get("thing")
                    thing_id = getattr(thing, "id", None) or local.get("id")
                    if thing_id is not None:
                        meta["thing_id"] = str(thing_id)[:24]
                actor = local.get("v")
                author = local.get("author")
                if _username(actor):
                    meta["actor_username"] = _username(actor)
                if _username(author):
                    meta["recipient_username"] = _username(author)
                if getattr(account, "id", None) == getattr(actor, "id", None):
                    meta["account_role"] = "buyer"
                elif getattr(account, "id", None) == getattr(author, "id", None):
                    meta["account_role"] = "recipient"
                return "awards", "Awards", meta

            if "username_effect" in haystack:
                effect = local.get("effect")
                if isinstance(effect, dict):
                    meta["item_name"] = str(effect.get("title") or effect.get("key") or "")[:120]
                    meta["item_key"] = str(effect.get("key") or "")[:80]
                return "shop", "Username effect", meta

            if "/hats.py" in filename or "hat_" in func or func.startswith("buy_hat"):
                hat = local.get("hat")
                if hat is not None:
                    meta["item_name"] = str(getattr(hat, "name", "") or "")[:120]
                    meta["item_id"] = str(getattr(hat, "id", "") or "")[:24]
                    author = getattr(hat, "author", None)
                    buyer = local.get("v")
                    if _username(buyer):
                        meta["actor_username"] = _username(buyer)
                    if getattr(account, "id", None) == getattr(buyer, "id", None):
                        meta["account_role"] = "buyer"
                    elif getattr(account, "id", None) == getattr(author, "id", None):
                        meta["account_role"] = "creator"
                return "shop", "Hat shop", meta

            if "exchange" in haystack:
                return "exchange", "Currency exchange", meta

            if "gift" in haystack or "transfer" in haystack:
                actor = local.get("v") or local.get("sender")
                recipient = local.get("recipient") or local.get("user") or local.get("target")
                if _username(actor):
                    meta["actor_username"] = _username(actor)
                if _username(recipient):
                    meta["target_username"] = _username(recipient)
                if getattr(account, "id", None) == getattr(actor, "id", None):
                    meta["account_role"] = "sender"
                elif getattr(account, "id", None) == getattr(recipient, "id", None):
                    meta["account_role"] = "recipient"
                return "gifts", "Gift", meta

            if "paypal" in haystack or "donat" in haystack:
                return "patron", "Patron reward", meta
            if "admin.py" in filename or "profile_moderation" in filename:
                return "admin", "Admin adjustment", meta
            if "casino" in haystack:
                return "casino", "Casino", meta
            if "bet" in func or "poll" in filename:
                return "bets", "Bet", meta

            frame = frame.f_back
    finally:
        del frame
    return "", "", {}


def set_economy_context(db, category="", label="", meta=None):
    """Set transaction-local ledger metadata for direct balance mutations."""
    payload = json.dumps(meta or {}, separators=(",", ":"), ensure_ascii=False)[:1800]
    db.execute(
        text(
            "SELECT set_config('toc.economy_category', :category, true), "
            "set_config('toc.economy_label', :label, true), "
            "set_config('toc.economy_meta', :meta, true)"
        ),
        {"category": category or "", "label": label or "", "meta": payload},
    )


def _wrap_balance_method(User, method_name):
    original = getattr(User, method_name)
    if getattr(original, "_economy_ledger_wrapped", False):
        return

    @wraps(original)
    def wrapped(self, *args, **kwargs):
        db = getattr(g, "db", None) if has_request_context() else None
        if db is None:
            return original(self, *args, **kwargs)

        category, label, meta = _caller_context(self)
        try:
            set_economy_context(db, category, label, meta)
            result = original(self, *args, **kwargs)
            # The DB trigger must fire while this exact context is still active.
            # Clearing the transaction-local config before SQLAlchemy flushes is
            # what previously allowed Awards/Votes to inherit stale Gift context.
            db.flush()
            return result
        finally:
            try:
                set_economy_context(db)
            except Exception:
                pass

    wrapped._economy_ledger_wrapped = True
    setattr(User, method_name, wrapped)


def install_economy_ledger(app, engine):
    """Create the ledger/trigger and attach safe request/caller context."""
    if SITE_NAME != "Obsession" or getattr(app, "_economy_ledger_installed", False):
        return
    app._economy_ledger_installed = True

    if engine.dialect.name != "postgresql":
        return

    with engine.begin() as conn:
        conn.execute(text(_LEDGER_DDL))

    from files.classes import User
    _wrap_balance_method(User, "pay_account")
    _wrap_balance_method(User, "charge_account")

    @app.before_request
    def attach_economy_request_context():
        db = getattr(g, "db", None)
        if db is None:
            return None

        safe = {}
        for key in _SAFE_CONTEXT_KEYS:
            value = request.values.get(key)
            if value is not None:
                safe[key] = str(value)[:160]

        try:
            db.execute(
                text(
                    "SELECT set_config('toc.request_path', :path, true), "
                    "set_config('toc.request_meta', :meta, true), "
                    "set_config('toc.economy_category', '', true), "
                    "set_config('toc.economy_label', '', true), "
                    "set_config('toc.economy_meta', '{}', true)"
                ),
                {
                    "path": request.path[:500],
                    "meta": json.dumps(safe, separators=(",", ":"), ensure_ascii=False)[:1800],
                },
            )
        except Exception:
            pass
        return None
