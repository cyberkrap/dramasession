import importlib

from sqlalchemy import text


_AUTO_CREDIT_SQL = "amount = 1 AND category = 'other' AND COALESCE(label, '') = ''"


def install_bank_statement_noise_fixes(engine) -> None:
    """Remove generic automatic +1 Wishcoin credits from Bank Statement.

    The balance change itself is preserved. These unlabeled one-coin credits are
    contribution/vote bookkeeping noise, not meaningful user-facing banking
    transactions, so old rows are purged and future statement queries hide them.
    """
    if engine.dialect.name == "postgresql":
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
