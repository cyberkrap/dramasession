"""Keep ledger metadata alive until the balance UPDATE actually reaches PostgreSQL."""

from functools import wraps
import importlib

from flask import g, has_request_context, request
from markupsafe import Markup


def install_economy_ledger_flush_fix():
    from files.classes import User
    from files.helpers import economy_ledger as ledger

    # Routes whose economic meaning is unambiguous are authoritative.  This is
    # deliberately outside the stack-inspecting ledger helper so infrastructure
    # wrappers can never rename a transaction by accident.
    if not getattr(ledger, "_vote_path_suppression_installed", False):
        original_caller_context = ledger._caller_context

        def caller_context(account):
            if has_request_context():
                raw_path = str(request.path or "")
                path = raw_path.lower()

                # Vote-earned Wishcoins affect the live balance but are intentionally
                # invisible in Bank Statement.
                if path == "/vote" or path.startswith("/vote/"):
                    return "__skip__", "", {}

                # Buying a username effect is a Shop purchase, never a gift.
                if path.startswith("/shop/effects/") and path.endswith("/buy"):
                    bits = raw_path.strip("/").split("/")
                    effect_key = bits[2] if len(bits) >= 4 else ""
                    return "shop", "Username effect", {
                        "item_key": effect_key[:80],
                    }

                # Approving a submitted emote pays its author 250 Wishcoins.  Keep
                # that reward visible even when the author is also an administrator.
                if path.startswith("/admin/approve/marsey/") or path.startswith("/admin/approve/emote/"):
                    # The moderation form can rename an emote while approving it.
                    # Prefer that final name over the pending name embedded in the URL.
                    name = str(request.values.get("name") or raw_path.rsplit("/", 1)[-1]).lower().strip()
                    return "other", "Emote approval reward", {
                        "item_name": name[:120],
                    }

            return original_caller_context(account)

        ledger._caller_context = caller_context
        ledger._vote_path_suppression_installed = True

    if not getattr(User, "_economy_flush_fix_installed", False):
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
                # its transaction-local settings. Then force the User UPDATE to flush
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

    # Final presentation cleanup for ledger entries whose underlying accounting is
    # already correct.  This is installed after gift_ledger_enrichment, so these
    # precise descriptions win without disturbing its proof-based gift handling.
    bank = importlib.import_module("files.routes.bank_statement")
    if not getattr(bank, "_economy_entry_wording_fixed", False):
        original_description = bank._transaction_description

        def transaction_description(row, statement_user):
            path = str(row.get("origin_path") or "")
            lower_path = path.lower()
            label = str(row.get("label") or "")
            amount = int(row.get("amount") or 0)
            meta = bank._safe_json(row.get("context_json"))

            if label == "Username effect" or (
                lower_path.startswith("/shop/effects/") and lower_path.endswith("/buy")
            ):
                title = str(meta.get("item_name") or "").strip()
                if not title:
                    bits = path.strip("/").split("/")
                    effect_key = bits[2] if len(bits) >= 4 else str(meta.get("item_key") or "")
                    effect = bank.USERNAME_EFFECTS.get(effect_key)
                    title = str((effect or {}).get("title") or effect_key or "Username effect")
                effect_link = bank._link("/shop/effects", title)
                if amount < 0:
                    return Markup("{} username effect cost").format(effect_link)
                return Markup("{} username effect refund").format(effect_link)

            if label == "Emote approval reward":
                name = str(meta.get("item_name") or meta.get("name") or "").lower().strip()
                if not name and "/" in path:
                    name = path.rsplit("/", 1)[-1].lower().strip()
                if name:
                    emote_link = bank._link(f"/emote-preview/{name}.webp", f":{name}:")
                    return Markup("Emote approval reward for {}").format(emote_link)
                return Markup("Emote approval reward")

            return original_description(row, statement_user)

        bank._transaction_description = transaction_description
        bank._economy_entry_wording_fixed = True
