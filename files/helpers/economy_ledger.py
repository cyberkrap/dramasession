"""Immutable Wishcoin/Wishbux balance ledger.

A PostgreSQL trigger records every change to users.coins/users.marseybux, including
bulk UPDATEs that bypass User.pay_account()/charge_account(). Request context is
attached transaction-locally so the bank-statement UI can classify activity
without changing existing economy code paths.
"""

import json

from flask import g, request
from sqlalchemy import text

from files.helpers.config.const import SITE_NAME


_LEDGER_DDL = r"""
-- Multiple Gunicorn workers import routes at the same time. Serialize this
-- installer inside PostgreSQL so trigger creation cannot race at boot.
SELECT pg_advisory_xact_lock(hashtext('toc_economy_ledger_install'));

CREATE TABLE IF NOT EXISTS economy_ledger (
    id BIGSERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    currency VARCHAR(16) NOT NULL,
    amount BIGINT NOT NULL,
    balance_after BIGINT NOT NULL,
    category VARCHAR(24) NOT NULL DEFAULT 'other',
    origin_path TEXT,
    context_json TEXT,
    created_utc BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM NOW())::BIGINT)
);

CREATE INDEX IF NOT EXISTS ix_economy_ledger_user_currency_created
    ON economy_ledger (user_id, currency, created_utc DESC, id DESC);
CREATE INDEX IF NOT EXISTS ix_economy_ledger_user_category_created
    ON economy_ledger (user_id, category, created_utc DESC, id DESC);

CREATE OR REPLACE FUNCTION toc_record_economy_change()
RETURNS TRIGGER AS $$
DECLARE
    req_path TEXT := COALESCE(current_setting('toc.request_path', true), '');
    req_meta TEXT := COALESCE(current_setting('toc.request_meta', true), '');
    normalized TEXT := LOWER(COALESCE(current_setting('toc.request_path', true), ''));
    tx_category TEXT;
BEGIN
    tx_category := CASE
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
    END;

    IF NEW.coins IS DISTINCT FROM OLD.coins THEN
        INSERT INTO economy_ledger
            (user_id, currency, amount, balance_after, category, origin_path, context_json)
        VALUES
            (NEW.id, 'coins', COALESCE(NEW.coins, 0) - COALESCE(OLD.coins, 0),
             COALESCE(NEW.coins, 0), tx_category, NULLIF(req_path, ''), NULLIF(req_meta, ''));
    END IF;

    IF NEW.marseybux IS DISTINCT FROM OLD.marseybux THEN
        INSERT INTO economy_ledger
            (user_id, currency, amount, balance_after, category, origin_path, context_json)
        VALUES
            (NEW.id, 'wishbux', COALESCE(NEW.marseybux, 0) - COALESCE(OLD.marseybux, 0),
             COALESCE(NEW.marseybux, 0), tx_category, NULLIF(req_path, ''), NULLIF(req_meta, ''));
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


def install_economy_ledger(app, engine):
    """Create the ledger/trigger and attach safe request context."""
    if SITE_NAME != "Obsession" or getattr(app, "_economy_ledger_installed", False):
        return
    app._economy_ledger_installed = True

    # Production is PostgreSQL. Do not crash local/alternate dialects that do
    # not understand PL/pgSQL; the feature simply remains unavailable there.
    if engine.dialect.name != "postgresql":
        return

    with engine.begin() as conn:
        conn.execute(text(_LEDGER_DDL))

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
                    "set_config('toc.request_meta', :meta, true)"
                ),
                {
                    "path": request.path[:500],
                    "meta": json.dumps(safe, separators=(",", ":"))[:1800],
                },
            )
        except Exception:
            # Ledger context is descriptive metadata only; an inability to set
            # it must never block the actual user action.
            pass
        return None
