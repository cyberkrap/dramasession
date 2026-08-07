"""Immutable Wishcoin/Wishbux balance ledger.

A PostgreSQL trigger records every change to users.coins/users.marseybux, including
bulk UPDATEs that bypass User.pay_account()/charge_account(). Request and caller
context are attached transaction-locally so bank statements remain useful even
when an economy action originates from chat or a background helper.
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
    normalized TEXT := LOWER(COALESCE(current_setting('toc.request_path', true), ''));
    tx_category TEXT;
BEGIN
    tx_category := COALESCE(NULLIF(category_override, ''), CASE
        WHEN normalized LIKE '%slot%' OR normalized LIKE '%roulette%'
          OR normalized LIKE '%blackjack%' OR normalized LIKE '%twentyone%'
          OR normalized LIKE '%casino%' THEN 'casino'
        WHEN normalized LIKE '%lottery%' THEN 'lottery'
        WHEN normalized LIKE '%award%' THEN 'awards'
        WHEN normalized LIKE '%gift%' OR normalized LIKE '%transfer%' THEN 'gifts'
        WHEN normalized LIKE '%exchange%' THEN 'exchange'
        WHEN normalized LIKE '%hat%' OR normalized LIKE '%shop%'
          OR normalized LIKE '%username_effect%' OR normalized LIKE '%username-effect%'
          OR normalized LIKE '%effect%' THEN 'shop'
        WHEN normalized LIKE '%paypal%' OR normalized LIKE '%support%'
          OR normalized LIKE '%donat%' THEN 'support'
        WHEN normalized LIKE '%admin%' OR normalized LIKE '%mod%' THEN 'admin'
        WHEN normalized LIKE '%bet%' OR normalized LIKE '%poll%' THEN 'bets'
        ELSE 'other'
    END);

    IF NEW.coins IS DISTINCT FROM OLD.coins THEN
        INSERT INTO economy_ledger
            (user_id, currency, amount, balance_after, category, label, origin_path, context_json)
        VALUES
            (NEW.id, 'coins', COALESCE(NEW.coins, 0) - COALESCE(OLD.coins, 0),
             COALESCE(NEW.coins, 0), tx_category, NULLIF(label_override, ''),
             NULLIF(req_path, ''), NULLIF(req_meta, ''));
    END IF;

    IF NEW.marseybux IS DISTINCT FROM OLD.marseybux THEN
        INSERT INTO economy_ledger
            (user_id, currency, amount, balance_after, category, label, origin_path, context_json)
        VALUES
            (NEW.id, 'wishbux', COALESCE(NEW.marseybux, 0) - COALESCE(OLD.marseybux, 0),
             COALESCE(NEW.marseybux, 0), tx_category, NULLIF(label_override, ''),
             NULLIF(req_path, ''), NULLIF(req_meta, ''));
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
"""

_SAFE_CONTEXT_KEYS = {
    "username", "user", "target", "name", "amount", "currency", "coins",
    "marseybux", "wishbux", "award", "award_id", "bet", "wager", "game",
    "quantity", "item", "item_id", "post_id", "comment_id", "submission_id",
}


def _caller_context():
    """Infer a useful ledger category from the economy subsystem on the stack."""
    frame = inspect.currentframe()
    try:
        frame = frame.f_back if frame else None
        for _ in range(12):
            if frame is None:
                break
            filename = frame.f_code.co_filename.replace('\\', '/').lower()
            func = frame.f_code.co_name.lower()
            haystack = f"{filename} {func}"

            if "slots.py" in filename or "slot" in func:
                return "casino", "Slots"
            if "twentyone.py" in filename or "blackjack" in haystack or "twentyone" in haystack:
                return "casino", "Blackjack"
            if "roulette" in haystack:
                return "casino", "Roulette"
            if "lottery" in haystack:
                return "lottery", "Lottery"
            if "award" in haystack:
                return "awards", "Awards"
            if "username_effect" in haystack:
                return "shop", "Username effect"
            if "/hats.py" in filename or "hat_" in func or func.startswith("buy_hat"):
                return "shop", "Hat shop"
            if "exchange" in haystack:
                return "exchange", "Currency exchange"
            if "gift" in haystack or "transfer" in haystack:
                return "gifts", "Gift"
            if "paypal" in haystack or "support" in haystack or "donat" in haystack:
                return "support", "Support"
            if "admin.py" in filename or "profile_moderation" in filename:
                return "admin", "Admin adjustment"
            if "casino" in haystack:
                return "casino", "Casino"
            if "bet" in func or "poll" in filename:
                return "bets", "Bet"

            frame = frame.f_back
    finally:
        del frame
    return "", ""


def _set_local_context(db, category, label):
    db.execute(
        text(
            "SELECT set_config('toc.economy_category', :category, true), "
            "set_config('toc.economy_label', :label, true)"
        ),
        {"category": category or "", "label": label or ""},
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

        category, label = _caller_context()
        try:
            _set_local_context(db, category, label)
            return original(self, *args, **kwargs)
        finally:
            try:
                _set_local_context(db, "", "")
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

    # Import lazily to avoid creating a classes/helpers circular import during
    # initial module loading.
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
                    "set_config('toc.economy_label', '', true)"
                ),
                {
                    "path": request.path[:500],
                    "meta": json.dumps(safe, separators=(",", ":"))[:1800],
                },
            )
        except Exception:
            pass
        return None
