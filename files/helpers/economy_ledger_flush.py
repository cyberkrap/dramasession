"""Keep ledger metadata alive until the balance UPDATE actually reaches PostgreSQL."""

from functools import wraps

from flask import g, has_request_context


def install_economy_ledger_flush_fix():
    from files.classes import User
    from files.helpers import economy_ledger as ledger

    if getattr(User, "_economy_flush_fix_installed", False):
        return

    for method_name in ("pay_account", "charge_account"):
        current = getattr(User, method_name)
        if getattr(current, "_economy_flush_stable", False):
            continue

        @wraps(current)
        def stable(self, *args, __current=current, **kwargs):
            db = getattr(g, "db", None) if has_request_context() else None
            if db is None:
                return __current(self, *args, **kwargs)

            # Capture the same caller context before the inner ledger wrapper clears
            # its transaction-local settings.  Then force the User UPDATE to flush
            # while that context is active.
            category, label, meta = ledger._caller_context(self)
            result = __current(self, *args, **kwargs)
            try:
                ledger.set_economy_context(db, category, label, meta)
                db.flush([self])
            finally:
                try:
                    ledger.set_economy_context(db)
                except Exception:
                    pass
            return result

        stable._economy_flush_stable = True
        setattr(User, method_name, stable)

    User._economy_flush_fix_installed = True
