"""Runtime helpers for award batches.

Award effects are intentionally applied once per award so existing duration and
stacking semantics remain unchanged.  Economy rows, however, should describe the
user action (one quantity-N award action), not each internal iteration.
"""

from __future__ import annotations

import json
import re
from collections import defaultdict

from sqlalchemy import text


_AWARD_PATH_RE = re.compile(r"^/award/(post|comment)/(\d+)$", re.I)
_MIGRATION_KEY = "award_batch_ledger_cleanup_20260809_v1"


def _safe_json(raw):
    try:
        value = json.loads(raw or "{}")
        return value if isinstance(value, dict) else {}
    except (TypeError, ValueError):
        return {}


def _username(value):
    return str(getattr(value, "username", "") or "")[:80]


def award_batch_ledger_start(db) -> int:
    """Return a request-local ledger watermark before an award batch mutates balances."""
    try:
        return int(db.execute(text("SELECT COALESCE(MAX(id), 0) FROM economy_ledger")).scalar() or 0)
    except Exception:
        return 0


def _merged_award_meta(raw, *, kind, quantity, thing_type, thing_id, actor=None, recipient=None):
    meta = _safe_json(raw)
    meta["award_kind"] = str(kind or "")[:80]
    meta["kind"] = str(kind or "")[:80]
    meta["thing_type"] = str(thing_type or "")[:16]
    meta["thing_id"] = str(thing_id or "")[:24]
    meta["batch_quantity"] = int(quantity or 1)
    meta["amount"] = str(int(quantity or 1))
    if _username(actor):
        meta["actor_username"] = _username(actor)
    if _username(recipient):
        meta["recipient_username"] = _username(recipient)
    return json.dumps(meta, separators=(",", ":"), ensure_ascii=False)[:1800]


def collapse_award_batch_ledger(
    db,
    start_id: int,
    origin_path: str,
    *,
    kind: str,
    quantity: int,
    thing_type: str,
    thing_id: int,
    actor=None,
    recipient=None,
):
    """Collapse balance mutations produced by one award request into user-facing rows.

    We keep separate rows by account, currency, and direction.  This means a
    cosmetic batch can still show one buyer cost and one recipient payout while a
    self-award cannot incorrectly net the purchase and payout together.
    """
    if int(quantity or 1) <= 1:
        return

    try:
        db.flush()
        rows = db.execute(
            text(
                "SELECT id, user_id, currency, amount, balance_after, context_json "
                "FROM economy_ledger "
                "WHERE id > :start_id AND origin_path = :origin_path "
                "ORDER BY id ASC"
            ),
            {"start_id": int(start_id or 0), "origin_path": str(origin_path or "")[:500]},
        ).mappings().all()
    except Exception:
        return

    groups = defaultdict(list)
    for row in rows:
        amount = int(row.get("amount") or 0)
        direction = 1 if amount > 0 else -1 if amount < 0 else 0
        groups[(int(row["user_id"]), str(row["currency"]), direction)].append(dict(row))

    for group in groups.values():
        if not group:
            continue
        keep = group[-1]
        total = sum(int(item.get("amount") or 0) for item in group)
        meta = _merged_award_meta(
            keep.get("context_json"),
            kind=kind,
            quantity=quantity,
            thing_type=thing_type,
            thing_id=thing_id,
            actor=actor,
            recipient=recipient,
        )
        db.execute(
            text(
                "UPDATE economy_ledger SET amount = :amount, balance_after = :balance_after, "
                "category = 'awards', label = 'Awards', context_json = :meta "
                "WHERE id = :id"
            ),
            {
                "amount": total,
                "balance_after": int(keep.get("balance_after") or 0),
                "meta": meta,
                "id": int(keep["id"]),
            },
        )
        stale_ids = [int(item["id"]) for item in group[:-1]]
        if stale_ids:
            db.execute(
                text("DELETE FROM economy_ledger WHERE id = ANY(:ids)"),
                {"ids": stale_ids},
            )


def _collapse_existing_cluster(conn, cluster, quantity):
    if not cluster:
        return
    keep = cluster[-1]
    total = sum(int(row.get("amount") or 0) for row in cluster)
    meta = _safe_json(keep.get("context_json"))
    path_match = _AWARD_PATH_RE.match(str(keep.get("origin_path") or ""))
    if path_match:
        meta.setdefault("thing_type", path_match.group(1).lower())
        meta.setdefault("thing_id", path_match.group(2))
    kind = str(meta.get("award_kind") or meta.get("kind") or meta.get("award") or "").strip()
    if kind:
        meta["award_kind"] = kind[:80]
        meta["kind"] = kind[:80]
    meta["batch_quantity"] = int(quantity)
    meta["amount"] = str(int(quantity))
    payload = json.dumps(meta, separators=(",", ":"), ensure_ascii=False)[:1800]

    conn.execute(
        text(
            "UPDATE economy_ledger SET amount = :amount, balance_after = :balance_after, "
            "category = 'awards', label = 'Awards', context_json = :meta WHERE id = :id"
        ),
        {
            "amount": total,
            "balance_after": int(keep.get("balance_after") or 0),
            "meta": payload,
            "id": int(keep["id"]),
        },
    )
    stale = [int(row["id"]) for row in cluster[:-1]]
    if stale:
        conn.execute(text("DELETE FROM economy_ledger WHERE id = ANY(:ids)"), {"ids": stale})


def repair_existing_award_batches(engine):
    """One-time cleanup for award rows created before proper batch aggregation.

    Old batch requests already carry their requested `amount` in request metadata,
    which gives us a reliable signal that the repeated rows belong to a batch.
    Rows are clustered by account/currency/content/kind/direction and timestamp so
    unrelated award actions are not merged.
    """
    if engine.dialect.name != "postgresql":
        return

    with engine.begin() as conn:
        exists = conn.execute(text("SELECT to_regclass('public.economy_ledger')")).scalar()
        if not exists:
            return
        conn.execute(text("SELECT pg_advisory_xact_lock(hashtext('toc_award_batch_ledger_repair'))"))
        conn.execute(
            text(
                "CREATE TABLE IF NOT EXISTS economy_ledger_data_migrations ("
                "migration_key TEXT PRIMARY KEY, "
                "applied_utc BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM NOW())::BIGINT))"
            )
        )
        if conn.execute(
            text("SELECT 1 FROM economy_ledger_data_migrations WHERE migration_key = :key"),
            {"key": _MIGRATION_KEY},
        ).first():
            return

        rows = conn.execute(
            text(
                "SELECT id, user_id, currency, amount, balance_after, category, label, "
                "origin_path, context_json, created_utc FROM economy_ledger "
                "WHERE origin_path ~ '^/award/(post|comment)/[0-9]+$' "
                "ORDER BY user_id, currency, origin_path, created_utc, id"
            )
        ).mappings().all()

        # Every award-route row is an award regardless of whatever stale caller
        # metadata was accidentally active when the trigger fired.
        conn.execute(
            text(
                "UPDATE economy_ledger SET category = 'awards', label = 'Awards' "
                "WHERE origin_path ~ '^/award/(post|comment)/[0-9]+$'"
            )
        )

        buckets = defaultdict(list)
        for raw in rows:
            row = dict(raw)
            meta = _safe_json(row.get("context_json"))
            try:
                quantity = int(meta.get("batch_quantity") or meta.get("amount") or 1)
            except (TypeError, ValueError):
                quantity = 1
            if quantity <= 1:
                continue
            kind = str(meta.get("award_kind") or meta.get("kind") or meta.get("award") or "").strip().lower()
            amount = int(row.get("amount") or 0)
            direction = 1 if amount > 0 else -1 if amount < 0 else 0
            key = (
                int(row["user_id"]),
                str(row["currency"]),
                str(row.get("origin_path") or ""),
                kind,
                quantity,
                direction,
            )
            buckets[key].append(row)

        for key, group in buckets.items():
            quantity = int(key[4])
            group.sort(key=lambda row: (int(row.get("created_utc") or 0), int(row["id"])))
            cluster = []
            previous_time = None
            for row in group:
                current_time = int(row.get("created_utc") or 0)
                # A single HTTP award batch runs in a very tight interval. Split
                # separate user actions rather than merging an entire history.
                if cluster and previous_time is not None and current_time - previous_time > 3:
                    _collapse_existing_cluster(conn, cluster, quantity)
                    cluster = []
                cluster.append(row)
                previous_time = current_time
            if cluster:
                _collapse_existing_cluster(conn, cluster, quantity)

        conn.execute(
            text("INSERT INTO economy_ledger_data_migrations (migration_key) VALUES (:key)"),
            {"key": _MIGRATION_KEY},
        )
