import importlib

from sqlalchemy import text


_CONTRIBUTION_PATH_SQL = "(origin_path = '/comment' OR origin_path = '/submit' OR origin_path LIKE '/h/%/submit')"


def install_bank_statement_noise_fixes(engine) -> None:
    """Remove automatic +1 content credits from the user-facing bank ledger.

    Posting/commenting still grants the same Wishcoin balance. These tiny
    contribution credits are bookkeeping noise rather than meaningful bank
    transactions, so historical rows are purged and future rows are excluded
    from Bank Statement queries.
    """
    if engine.dialect.name == "postgresql":
        with engine.begin() as conn:
            conn.execute(text(f"""
                DELETE FROM economy_ledger
                WHERE currency = 'coins'
                  AND amount = 1
                  AND category = 'other'
                  AND COALESCE(label, '') = ''
                  AND {_CONTRIBUTION_PATH_SQL}
            """))

    module = importlib.import_module("files.routes.bank_statement")
    original = module._build_statement_query
    if getattr(original, "_toc_contribution_credit_filter", False):
        return

    def filtered_build_statement_query(user_id, currency, category, direction, period, q, hide_casino, hide_admin):
        where_sql, params = original(user_id, currency, category, direction, period, q, hide_casino, hide_admin)
        if currency == "coins":
            where_sql += (
                " AND NOT (amount = 1 AND category = 'other' AND COALESCE(label, '') = '' AND "
                + _CONTRIBUTION_PATH_SQL
                + ")"
            )
        return where_sql, params

    filtered_build_statement_query._toc_contribution_credit_filter = True
    module._build_statement_query = filtered_build_statement_query
