import json
import re
import time
from urllib.parse import urlencode

from flask import abort, g, render_template, request
from markupsafe import Markup
from sqlalchemy import text

from files.__main__ import app, limiter
from files.classes import User
from files.classes.award import AwardRelationship
from files.classes.hats import HatDef
from files.helpers.config.awards import AWARDS_ENABLED, HOUSE_AWARDS
from files.helpers.config.const import DEFAULT_RATELIMIT
from files.helpers.config.username_effects import USERNAME_EFFECTS
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
    ("patron", "Patron rewards"),
)
_VALID_CATEGORIES = {x[0] for x in BANK_CATEGORIES}
_VALID_DIRECTIONS = {"all", "in", "out"}
_VALID_RANGES = {"all", "24h", "7d", "30d", "90d"}
_RANGE_SECONDS = {"24h": 86400, "7d": 604800, "30d": 2592000, "90d": 7776000}
_PROFILE_PATH_RE = re.compile(r"^/@([a-zA-Z0-9_-]+)$")
_AWARD_CONTENT_RE = re.compile(r"^/award/(post|comment)/(\d+)$")
_AWARD_BUY_RE = re.compile(r"^/buy/([^/]+)$")
_HAT_BUY_RE = re.compile(r"^/buy_hat/(\d+)$")
_EFFECT_BUY_RE = re.compile(r"^/shop/effects/([^/]+)/buy$")
_TRANSFER_RE = re.compile(r"^/@([^/]+)/transfer-(?:bux|coins)$", re.I)

_TIER_BY_WISHBUX = {
    5000: "Nikki's Supporter",
    11000: "Bear's Insider",
    24000: "Sandy's Devoted",
    65000: "Curry's Obsession",
    140000: "Ian's Bankroller",
}


def _safe_json(raw):
    try:
        value = json.loads(raw or "{}")
        return value if isinstance(value, dict) else {}
    except (TypeError, ValueError):
        return {}


def _link(href, text_value):
    return Markup('<a class="bank-inline-link" href="{}">{}</a>').format(href, text_value)


def _award_title(kind):
    kind = str(kind or "").strip()
    if not kind:
        return "Award"
    award = AWARDS_ENABLED.get(kind) or HOUSE_AWARDS.get(kind)
    if award:
        return award.get("title") or kind
    return kind.replace("-", " ").replace("_", " ").title()


def _award_quantity(meta, path):
    raw = meta.get("batch_quantity")
    if raw is None and _AWARD_CONTENT_RE.match(path):
        raw = meta.get("amount")
    try:
        quantity = int(raw or 1)
    except (TypeError, ValueError):
        quantity = 1
    return max(1, min(quantity, 30))


def _award_context_from_history(row, user_id):
    path = row.get("origin_path") or ""
    match = _AWARD_CONTENT_RE.match(path)
    if not match:
        return None, None, None

    thing_type, raw_id = match.groups()
    thing_id = int(raw_id)
    query = g.db.query(AwardRelationship).filter(AwardRelationship.user_id == user_id)
    if thing_type == "post":
        query = query.filter(AwardRelationship.submission_id == thing_id)
    else:
        query = query.filter(AwardRelationship.comment_id == thing_id)

    created = int(row.get("created_utc") or 0)
    award = query.filter(
        AwardRelationship.awarded_utc >= created - 120,
        AwardRelationship.awarded_utc <= created + 120,
    ).order_by(AwardRelationship.awarded_utc.desc()).first()
    return (award.kind if award else None), thing_type, thing_id


def _transaction_description(row, statement_user):
    path = str(row.get("origin_path") or "")
    meta = _safe_json(row.get("context_json"))
    amount = int(row.get("amount") or 0)
    label = str(row.get("label") or "")

    if row.get("category") == "awards" or label == "Awards" or _AWARD_BUY_RE.match(path) or _AWARD_CONTENT_RE.match(path):
        kind = meta.get("award_kind") or meta.get("kind") or meta.get("award")
        thing_type = meta.get("thing_type")
        quantity = _award_quantity(meta, path)
        try:
            thing_id = int(meta.get("thing_id") or 0) or None
        except (TypeError, ValueError):
            thing_id = None

        direct = _AWARD_BUY_RE.match(path)
        if direct and not kind:
            kind = direct.group(1)
        content = _AWARD_CONTENT_RE.match(path)
        if content:
            thing_type = thing_type or content.group(1)
            thing_id = thing_id or int(content.group(2))
        if content and not kind:
            kind, thing_type, thing_id = _award_context_from_history(row, statement_user.id)

        title = meta.get("award_title") or _award_title(kind)
        award_link = _link("/shop", title)
        award_word = "Award" if quantity == 1 else "Awards"
        if thing_type in {"post", "comment"} and thing_id:
            href = f"/{thing_type}/{thing_id}" + ("#context" if thing_type == "comment" else "")
            content_link = _link(href, f"this {thing_type}")
            if amount < 0:
                return Markup("Cost of {} {} {} on {}").format(quantity, award_link, award_word, content_link)
            return Markup("Payout from {} {} {} on {}").format(quantity, award_link, award_word, content_link)
        if amount < 0:
            return Markup("Cost of {} {} {}").format(quantity, award_link, award_word)
        return Markup("Payout from {} {} {}").format(quantity, award_link, award_word)

    if label == "Hat shop" or _HAT_BUY_RE.match(path):
        name = meta.get("item_name")
        if not name:
            match = _HAT_BUY_RE.match(path)
            if match:
                hat = g.db.get(HatDef, int(match.group(1)))
                name = hat.name if hat else None
        hat_link = _link("/hats", name or "Hat")
        if amount < 0:
            return Markup("{} hat purchase cost").format(hat_link)
        return Markup("Creator share from {} hat purchase").format(hat_link)

    if label == "Username effect" or _EFFECT_BUY_RE.match(path):
        title = meta.get("item_name")
        if not title:
            match = _EFFECT_BUY_RE.match(path)
            if match:
                effect = USERNAME_EFFECTS.get(match.group(1))
                title = (effect or {}).get("title") or match.group(1)
        effect_link = _link("/shop/effects", title or "Username effect")
        return Markup("{} purchase cost").format(effect_link) if amount < 0 else Markup("{} refund").format(effect_link)

    if row.get("category") == "gifts" or label == "Gift" or _TRANSFER_RE.match(path):
        role = meta.get("account_role")
        actor = meta.get("actor_username")
        target = meta.get("target_username") or meta.get("username") or meta.get("target")
        match = _TRANSFER_RE.match(path)
        if match and not target:
            target = match.group(1)
        if amount < 0 or role == "sender":
            return Markup("Gift sent to {}").format(_link(f"/@{target}", f"@{target}")) if target else Markup("Gift sent")
        if actor:
            return Markup("Gift from {}").format(_link(f"/@{actor}", f"@{actor}"))
        return Markup("Gift received")

    if row.get("category") in {"patron", "support"} or label in {"Patron reward", "Support"}:
        tier_name = meta.get("tier_name") or _TIER_BY_WISHBUX.get(abs(amount))
        if amount < 0:
            return Markup("{} patron reward reversal").format(_link("/donate", tier_name or "Patron"))
        return Markup("{} patron reward").format(_link("/donate", tier_name or "Patron"))

    lower_path = path.lower()
    if label == "Slots" or "slot" in lower_path:
        return _link("/casino", "Slots winnings" if amount > 0 else "Slots bet")
    if label == "Blackjack" or "blackjack" in lower_path or "twentyone" in lower_path:
        return _link("/casino", "Blackjack winnings" if amount > 0 else "Blackjack bet")
    if label == "Roulette" or "roulette" in lower_path:
        return _link("/casino", "Roulette winnings" if amount > 0 else "Roulette bet")
    if row.get("category") == "casino" or label == "Casino":
        return _link("/casino", "Casino winnings" if amount > 0 else "Casino bet")
    if row.get("category") == "lottery" or label == "Lottery":
        return _link("/lottery", "Lottery winnings" if amount > 0 else "Lottery ticket purchase")
    if row.get("category") == "bets" or label == "Bet":
        return Markup("Bet winnings" if amount > 0 else "Bet placed")
    if row.get("category") == "exchange" or label == "Currency exchange":
        return Markup("Currency exchange")
    if row.get("category") == "admin" or label == "Admin adjustment":
        return Markup("Admin balance adjustment")
    return Markup("Balance credit" if amount > 0 else "Balance deduction")


def _display_group(category):
    return {
        "casino": "Casino",
        "gifts": "Gifts",
        "awards": "Awards",
        "shop": "Shop",
        "lottery": "Lottery",
        "bets": "Bets",
        "patron": "Patron reward",
        "support": "Patron reward",
        "exchange": "Currency",
        "admin": "Balance adjustment",
        "other": "Balance",
    }.get(category, "Balance")


def _build_statement_query(user_id, currency, category, direction, period, q, hide_casino, hide_admin):
    clauses = ["user_id = :user_id", "currency = :currency"]
    params = {"user_id": user_id, "currency": currency}

    if category == "patron":
        clauses.append("category IN ('patron', 'support')")
    elif category != "all":
        clauses.append("category = :category")
        params["category"] = category
    if hide_casino:
        clauses.append("category <> 'casino'")
    if hide_admin:
        clauses.append("category <> 'admin'")
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
            "(LOWER(COALESCE(label,'')) LIKE :q OR LOWER(COALESCE(context_json,'')) LIKE :q OR "
            " CAST(id AS TEXT) LIKE :q OR CAST(amount AS TEXT) LIKE :q)"
        )
    return " AND ".join(clauses), params


def _qs(**overrides):
    args = request.args.to_dict(flat=True)
    args.update({k: v for k, v in overrides.items() if v is not None})
    for key in [k for k, v in args.items() if v in (None, "", "all") and k not in {"currency"}]:
        args.pop(key, None)
    args.pop("page", None)
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
    hide_admin = bool(int(getattr(u, "admin_level", 0) or 0) > 0)

    try:
        page = max(1, int(request.args.get("page", 1)))
    except (TypeError, ValueError):
        page = 1
    try:
        per_page = max(25, min(100, int(request.args.get("per_page", 50) or 50)))
    except (TypeError, ValueError):
        per_page = 50

    where_sql, params = _build_statement_query(
        u.id, currency, category, direction, period, q, hide_casino, hide_admin
    )
    stats = g.db.execute(
        text(
            f"SELECT COUNT(*) AS total, "
            f"COALESCE(SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END), 0) AS money_in, "
            f"COALESCE(SUM(CASE WHEN amount < 0 THEN -amount ELSE 0 END), 0) AS money_out, "
            f"COALESCE(SUM(amount), 0) AS net FROM economy_ledger WHERE {where_sql}"
        ), params,
    ).mappings().one()

    select_columns = "id, created_utc, amount, balance_after, category, label, origin_path, context_json"
    rows = g.db.execute(
        text(
            f"SELECT {select_columns} FROM economy_ledger WHERE {where_sql} "
            f"ORDER BY created_utc DESC, id DESC OFFSET :offset LIMIT :limit"
        ),
        {**params, "offset": (page - 1) * per_page, "limit": per_page + 1},
    ).mappings().all()

    next_exists = len(rows) > per_page
    rows = rows[:per_page]
    current_balance = int(u.coins if currency == "coins" else u.marseybux)

    transactions = []
    for row in rows:
        item = dict(row)
        item["description"] = _transaction_description(item, u)
        item["group_label"] = _display_group(item.get("category"))
        transactions.append(item)

    asset_url = WISHCOIN_ASSET_URL if currency == "coins" else WISHBUX_ASSET_URL
    currency_name = "Wishcoins" if currency == "coins" else "Wishbux"
    return render_template(
        "userpage/bank_statement.html",
        v=v, u=u, currency=currency, currency_name=currency_name,
        currency_asset=asset_url, transactions=transactions, stats=dict(stats),
        current_balance=current_balance, categories=BANK_CATEGORIES,
        category=category, direction=direction, period=period, q=q,
        hide_casino=hide_casino, page=page, per_page=per_page,
        next_exists=next_exists, query_string=_qs(),
    )


@app.after_request
def link_profile_balances_to_bank_statement(response):
    """Expose bank/history entry points directly from a profile."""
    match = _PROFILE_PATH_RE.fullmatch(request.path)
    if not match or response.direct_passthrough or response.mimetype != "text/html" or response.status_code >= 400:
        return response

    body = response.get_data(as_text=True)
    username = match.group(1)
    body = re.sub(
        r'<div class="profile-stat"><strong id="profile-bux-amount">(.*?)</strong><span>Wishbux</span></div>',
        rf'<a class="profile-stat" href="/@{username}/bank?currency=wishbux" title="View Wishbux bank statement"><strong id="profile-bux-amount">\1</strong><span>Wishbux</span></a>',
        body, count=1,
    )
    body = re.sub(
        r'<div class="profile-stat"><strong id="profile-coins-amount">(.*?)</strong><span>Wishcoins</span></div>',
        rf'<a class="profile-stat" href="/@{username}/bank?currency=coins" title="View Wishcoin bank statement"><strong id="profile-coins-amount">\1</strong><span>Wishcoins</span></a>',
        body, count=1,
    )

    views_link = f'<a href="/@{username}/views">Profile Views</a>'
    viewed_link = f'<a href="/@{username}/viewed">Profiles Viewed</a>'
    voting_link = f'<a href="/@{username}/voted/posts">Voting history</a>'
    bank_link = f'<a href="/@{username}/bank">Bank Statement</a>'
    if views_link in body and viewed_link not in body:
        body = body.replace(views_link, views_link + "\
\t\t\t\t\t" + viewed_link, 1)
    if voting_link in body and bank_link not in body:
        body = body.replace(voting_link, voting_link + "\
\t\t\t\t\t" + bank_link, 1)

    response.set_data(body)
    response.headers.pop("Content-Length", None)
    return response
