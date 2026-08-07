import csv
import io
import json
import time
from urllib.parse import urlencode

from flask import Response, abort, g, render_template, request
from sqlalchemy import text

from files.__main__ import app, limiter
from files.classes import User
from files.helpers.config.const import DEFAULT_RATELIMIT
from files.helpers.get import get_user
from files.helpers.wishcoin_asset import WISHBUX_ASSET_URL, WISHCOIN_ASSET_URL
from files.routes.wrappers import auth_desired, get_ID


BANK_CATEGORIES = (
    ("all", "Everything"),
    ("casino", "Casino"),
    ("gifts", "Gifts"),
    ("awards", "Awards"),
    ("shop", "Shop"),
    ("lottery", "Lottery"),
    ("bets", "Bets"),
    ("exchange", "Exchange"),
    ("support", "Support"),
    ("admin", "Admin"),
    ("other", "Other"),
)
_VALID_CATEGORIES = {x[0] for x in BANK_CATEGORIES}
_VALID_DIRECTIONS = {"all", "in", "out"}
_VALID_RANGES = {"all", "24h", "7d", "30d", "90d"}
_RANGE_SECONDS = {"24h": 86400, "7d": 604800, "30d": 2592000, "90d": 7776000}


def _safe_json(raw):
    try:
        value = json.loads(raw or "{}")
        return value if isinstance(value, dict) else {}
    except (TypeError, ValueError):
        return {}


def _transaction_label(row):
    path = (row.get("origin_path") or "").lower()
    meta = _safe_json(row.get("context_json"))
    amount = int(row.get("amount") or 0)
    subsystem = (row.get("label") or "").strip()

    if subsystem == "Slots":
        return "Slots winnings" if amount > 0 else "Slots bet"
    if subsystem == "Blackjack":
        return "Blackjack winnings" if amount > 0 else "Blackjack bet"
    if subsystem == "Roulette":
        return "Roulette winnings" if amount > 0 else "Roulette bet"
    if subsystem == "Lottery":
        return "Lottery winnings" if amount > 0 else "Lottery purchase"
    if subsystem == "Awards":
        return "Award payout" if amount > 0 else "Award purchase"
    if subsystem == "Username effect":
        return "Username effect refund" if amount > 0 else "Username effect purchase"
    if subsystem == "Hat shop":
        return "Hat transaction" if amount > 0 else "Hat purchase"
    if subsystem == "Gift":
        target = meta.get("username") or meta.get("user") or meta.get("target") or meta.get("name")
        base = "Gift received" if amount > 0 else "Gift sent"
        return f"{base} involving @{target}" if target else base
    if subsystem == "Currency exchange":
        return "Currency exchange"
    if subsystem == "Support":
        return "Support reward" if amount > 0 else "Support transaction"
    if subsystem == "Admin adjustment":
        return "Admin balance adjustment"
    if subsystem == "Bet":
        return "Bet winnings" if amount > 0 else "Bet placed"
    if subsystem == "Casino":
        return "Casino winnings" if amount > 0 else "Casino bet"

    if "slot" in path:
        return "Slots winnings" if amount > 0 else "Slots bet"
    if "blackjack" in path or "twentyone" in path:
        return "Blackjack winnings" if amount > 0 else "Blackjack bet"
    if "roulette" in path:
        return "Roulette winnings" if amount > 0 else "Roulette bet"
    if "lottery" in path:
        return "Lottery winnings" if amount > 0 else "Lottery purchase"
    if "award" in path:
        return "Award payout" if amount > 0 else "Award purchase"
    if "username_effect" in path or "username-effect" in path or "effect" in path:
        return "Username effect refund" if amount > 0 else "Username effect purchase"
    if "hat" in path:
        return "Hat transaction" if amount > 0 else "Hat purchase"
    if "shop" in path:
        item = meta.get("item") or meta.get("name")
        return f"Shop purchase: {item}" if item and amount < 0 else "Shop transaction"
    if "gift" in path or "transfer" in path:
        target = meta.get("username") or meta.get("user") or meta.get("target") or meta.get("name")
        base = "Gift received" if amount > 0 else "Gift sent"
        return f"{base} involving @{target}" if target else base
    if "exchange" in path:
        return "Currency exchange"
    if "paypal" in path or "support" in path or "donat" in path:
        return "Support reward" if amount > 0 else "Support transaction"
    if "admin" in path or "mod" in path:
        return "Admin balance adjustment"
    if "bet" in path or "poll" in path:
        return "Bet winnings" if amount > 0 else "Bet placed"
    return "Balance credit" if amount > 0 else "Balance debit"


def _build_statement_query(user_id, currency, category, direction, period, q, hide_casino):
    clauses = ["user_id = :user_id", "currency = :currency"]
    params = {"user_id": user_id, "currency": currency}

    if category != "all":
        clauses.append("category = :category")
        params["category"] = category
    if hide_casino:
        clauses.append("category <> 'casino'")
    if direction == "in":
        clauses.append("amount > 0")
    elif direction == "out":
        clauses.append("amount < 0")
    if period != "all":
        params["since"] = int(time.time()) - _RANGE_SECONDS[period]
        clauses.append("created_utc >= :since")
    if q:
        params["q"] = f"%{q.lower()}%"
        clauses.append(
            "(LOWER(COALESCE(label,'')) LIKE :q OR LOWER(COALESCE(origin_path,'')) LIKE :q OR "
            " LOWER(COALESCE(context_json,'')) LIKE :q OR "
            " CAST(id AS TEXT) LIKE :q OR CAST(amount AS TEXT) LIKE :q)"
        )

    return " AND ".join(clauses), params


def _qs(**overrides):
    args = request.args.to_dict(flat=True)
    args.update({k: v for k, v in overrides.items() if v is not None})
    for key in [k for k, v in args.items() if v in (None, "", "all") and k not in {"currency"}]:
        args.pop(key, None)
    args.pop("page", None)
    args.pop("format", None)
    return urlencode(args)


@app.get("/@<username>/bank")
@app.get("/@<username>/bank-statement")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_desired
def bank_statement(v: User, username: str):
    u = get_user(username, v=v, include_shadowbanned=bool(v and v.can_see_shadowbanned))

    currency = request.args.get("currency", "coins").lower()
    if currency not in {"coins", "wishbux"}:
        abort(400, "Invalid currency")

    category = request.args.get("category", "all").lower()
    if category not in _VALID_CATEGORIES:
        category = "all"
    direction = request.args.get("direction", "all").lower()
    if direction not in _VALID_DIRECTIONS:
        direction = "all"
    period = request.args.get("range", "all").lower()
    if period not in _VALID_RANGES:
        period = "all"
    q = request.args.get("q", "").strip()[:80]
    hide_casino = request.args.get("hide_casino") == "1"

    try:
        page = max(1, int(request.args.get("page", 1)))
    except (TypeError, ValueError):
        page = 1
    try:
        per_page = max(25, min(100, int(request.args.get("per_page", 50) or 50)))
    except (TypeError, ValueError):
        per_page = 50

    where_sql, params = _build_statement_query(
        u.id, currency, category, direction, period, q, hide_casino
    )

    stats = g.db.execute(
        text(
            f"SELECT COUNT(*) AS total, "
            f"COALESCE(SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END), 0) AS money_in, "
            f"COALESCE(SUM(CASE WHEN amount < 0 THEN -amount ELSE 0 END), 0) AS money_out, "
            f"COALESCE(SUM(amount), 0) AS net "
            f"FROM economy_ledger WHERE {where_sql}"
        ),
        params,
    ).mappings().one()

    select_columns = "id, created_utc, amount, balance_after, category, label, origin_path, context_json"

    if request.args.get("format") == "csv":
        export_rows = g.db.execute(
            text(
                f"SELECT {select_columns} FROM economy_ledger WHERE {where_sql} "
                f"ORDER BY created_utc DESC, id DESC LIMIT 10000"
            ),
            params,
        ).mappings().all()
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["transaction_id", "timestamp_utc", "currency", "amount", "balance_after", "category", "description", "source"])
        for row in export_rows:
            writer.writerow([
                row["id"], row["created_utc"], currency, row["amount"], row["balance_after"],
                row["category"], _transaction_label(row), row["origin_path"] or "system",
            ])
        filename = f"{u.username}-{currency}-bank-statement.csv"
        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )

    rows = g.db.execute(
        text(
            f"SELECT {select_columns} FROM economy_ledger WHERE {where_sql} "
            f"ORDER BY created_utc DESC, id DESC OFFSET :offset LIMIT :limit"
        ),
        {**params, "offset": (page - 1) * per_page, "limit": per_page + 1},
    ).mappings().all()

    next_exists = len(rows) > per_page
    rows = rows[:per_page]
    transactions = []
    for row in rows:
        item = dict(row)
        item["description"] = _transaction_label(item)
        item["meta"] = _safe_json(item.get("context_json"))
        transactions.append(item)

    current_balance = int(u.coins if currency == "coins" else u.marseybux)
    asset_url = WISHCOIN_ASSET_URL if currency == "coins" else WISHBUX_ASSET_URL
    currency_name = "Wishcoins" if currency == "coins" else "Wishbux"

    return render_template(
        "userpage/bank_statement.html",
        v=v,
        u=u,
        currency=currency,
        currency_name=currency_name,
        currency_asset=asset_url,
        transactions=transactions,
        stats=dict(stats),
        current_balance=current_balance,
        categories=BANK_CATEGORIES,
        category=category,
        direction=direction,
        period=period,
        q=q,
        hide_casino=hide_casino,
        page=page,
        per_page=per_page,
        next_exists=next_exists,
        query_string=_qs(),
    )
