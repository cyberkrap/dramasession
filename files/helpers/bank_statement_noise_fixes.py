import importlib

from sqlalchemy import text


_AUTO_CREDIT_SQL = "amount = 1 AND category = 'other' AND COALESCE(label, '') = ''"

# The 2026-08-22 reset is a presentation/history reset, not a balance wipe.
# Current user balances remain authoritative. Historical shop/hat counters use a
# stored baseline and casino history starts fresh from this UTC cutoff.
ECONOMY_RESET_UTC = 1787360340
ECONOMY_RESET_KEY = "20260822"


def _install_economy_history_reset(engine) -> None:
    """Apply the requested one-time TOC economy-history reset.

    - Snapshot cumulative shop/hat spend so site stats can show post-reset spend.
    - Clear @banman's pre-reset Bank Statement rows without changing balances.
    - Leave the immutable ledger trigger and all future rows intact.
    """
    if engine.dialect.name != "postgresql":
        return

    with engine.begin() as conn:
        conn.execute(text(f"""
            SELECT pg_advisory_xact_lock(hashtext('toc_economy_history_reset_20260822'));

            CREATE TABLE IF NOT EXISTS toc_economy_stats_baselines (
                reset_key TEXT NOT NULL,
                metric TEXT NOT NULL,
                value BIGINT NOT NULL,
                created_utc BIGINT NOT NULL,
                PRIMARY KEY (reset_key, metric)
            );

            INSERT INTO toc_economy_stats_baselines (reset_key, metric, value, created_utc)
            SELECT '{ECONOMY_RESET_KEY}', 'coins_spent', COALESCE(SUM(coins_spent), 0), {ECONOMY_RESET_UTC}
            FROM users
            ON CONFLICT (reset_key, metric) DO NOTHING;

            INSERT INTO toc_economy_stats_baselines (reset_key, metric, value, created_utc)
            SELECT '{ECONOMY_RESET_KEY}', 'coins_spent_on_hats', COALESCE(SUM(coins_spent_on_hats), 0), {ECONOMY_RESET_UTC}
            FROM users
            ON CONFLICT (reset_key, metric) DO NOTHING;

            CREATE TABLE IF NOT EXISTS economy_ledger_data_migrations (
                migration_key TEXT PRIMARY KEY,
                applied_utc BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM NOW())::BIGINT)
            );

            DO $$
            DECLARE
                target_user_id INTEGER;
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM economy_ledger_data_migrations
                    WHERE migration_key = 'banman_bank_statement_reset_20260822'
                ) THEN
                    SELECT id INTO target_user_id
                    FROM users
                    WHERE LOWER(username) = 'banman'
                       OR LOWER(COALESCE(original_username, '')) = 'banman'
                    ORDER BY CASE WHEN LOWER(username) = 'banman' THEN 0 ELSE 1 END, id
                    LIMIT 1;

                    IF target_user_id IS NOT NULL THEN
                        DELETE FROM economy_ledger
                        WHERE user_id = target_user_id
                          AND created_utc < {ECONOMY_RESET_UTC};
                    END IF;

                    INSERT INTO economy_ledger_data_migrations (migration_key)
                    VALUES ('banman_bank_statement_reset_20260822')
                    ON CONFLICT (migration_key) DO NOTHING;
                END IF;
            END;
            $$;
        """))


def get_economy_baseline(db, metric: str) -> int:
    """Return the stored cumulative baseline for a resettable economy metric."""
    if db.get_bind().dialect.name != "postgresql":
        return 0
    value = db.execute(
        text(
            "SELECT value FROM toc_economy_stats_baselines "
            "WHERE reset_key = :reset_key AND metric = :metric"
        ),
        {"reset_key": ECONOMY_RESET_KEY, "metric": metric},
    ).scalar()
    return int(value or 0)


def install_bank_statement_noise_fixes(engine) -> None:
    """Keep Bank Statement useful and apply the current TOC economy reset."""
    if engine.dialect.name == "postgresql":
        _install_economy_history_reset(engine)
        with engine.begin() as conn:
            conn.execute(text(f"""
                DELETE FROM economy_ledger
                WHERE currency = 'coins'
                  AND {_AUTO_CREDIT_SQL}
            """))

    module = importlib.import_module("files.routes.bank_statement")
    original = module._build_statement_query
    if getattr(original, "_toc_contribution_credit_filter", False):
        return

    def filtered_build_statement_query(user_id, currency, category, direction, period, q, hide_casino, hide_admin):
        where_sql, params = original(user_id, currency, category, direction, period, q, hide_casino, hide_admin)
        if currency == "coins":
            where_sql += " AND NOT (" + _AUTO_CREDIT_SQL + ")"
        return where_sql, params

    filtered_build_statement_query._toc_contribution_credit_filter = True
    module._build_statement_query = filtered_build_statement_query
