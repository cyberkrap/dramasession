from flask import abort, g, render_template, request

from files.__main__ import app, limiter
from files.classes import User
from files.helpers.config.const import (
    DEFAULT_RATELIMIT,
    DEFAULT_RATELIMIT_SLOWER,
    FEATURES,
    PAGE_SIZE,
)
from files.helpers.config.username_effects import (
    USERNAME_EFFECTS,
    USERNAME_EFFECT_CATEGORIES,
)
from files.helpers.username_effects import (
    dump_username_effects,
    normalize_username_effects,
)
from files.routes.wrappers import auth_required, get_ID


def _effect_or_404(effect_key):
    key = str(effect_key or "").strip().lower()
    effect = USERNAME_EFFECTS.get(key)
    if not effect:
        abort(404, "Username effect not found.")
    return key, effect


def _owner_counts():
    counts = {key: 0 for key in USERNAME_EFFECTS}
    rows = g.db.query(User.username_effects).filter(
        User.username_effects.isnot(None),
        User.username_effects != "[]",
    ).all()
    for (raw_effects,) in rows:
        for key in normalize_username_effects(raw_effects):
            counts[key] += 1
    return counts


@app.get("/effects")
@app.get("/shop/effects")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def username_effect_shop(v):
    owned = set(v.owned_username_effects)
    active = set(v.active_username_effects)
    counts = _owner_counts()

    effects = []
    for effect in USERNAME_EFFECTS.values():
        item = dict(effect)
        item["owned"] = item["key"] in owned
        item["active"] = item["key"] in active
        item["owner_count"] = counts[item["key"]]
        effects.append(item)

    return render_template(
        "username_effects.html",
        v=v,
        effects=effects,
        categories=USERNAME_EFFECT_CATEGORIES,
        owned_effects=list(owned),
        active_effects=v.active_username_effects,
    )


@app.post("/shop/effects/<effect_key>/buy")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@auth_required
def buy_username_effect(v, effect_key):
    key, effect = _effect_or_404(effect_key)
    owned = normalize_username_effects(v.username_effects)
    if key in owned:
        abort(409, "You already own this username effect.")

    currency = "marseybux" if request.values.get("mb") else "coins"
    if currency == "marseybux" and not FEATURES["MARSEYBUX"]:
        abort(403, "Wishbux purchases are unavailable.")

    price = int(effect["price"])
    if not v.charge_account(currency, price):
        label = "Wishbux" if currency == "marseybux" else "Wishcoins"
        abort(400, f"Not enough {label}.")

    owned.append(key)
    active = normalize_username_effects(v.username_effects_active)
    if key not in active:
        active.append(key)

    v.username_effects = dump_username_effects(owned)
    v.username_effects_active = dump_username_effects(active)
    if currency == "coins":
        v.coins_spent += price
    g.db.add(v)

    return {
        "message": f"{effect['title']} bought and equipped.",
        "effect": key,
        "owned": True,
        "active": True,
    }


@app.post("/shop/effects/<effect_key>/toggle")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@auth_required
def toggle_username_effect(v, effect_key):
    key, effect = _effect_or_404(effect_key)
    owned = normalize_username_effects(v.username_effects)
    if key not in owned:
        abort(403, "You do not own this username effect.")

    active = normalize_username_effects(v.username_effects_active)
    if key in active:
        active.remove(key)
        enabled = False
    else:
        active.append(key)
        enabled = True

    v.username_effects_active = dump_username_effects(active)
    g.db.add(v)

    return {
        "message": f"{effect['title']} {'equipped' if enabled else 'unequipped'}.",
        "effect": key,
        "active": enabled,
    }


@app.post("/shop/effects/unequip-all")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@auth_required
def unequip_all_username_effects(v):
    v.username_effects_active = "[]"
    g.db.add(v)
    return {"message": "All username effects unequipped."}


@app.get("/shop/effects/<effect_key>/owners")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def username_effect_owners(v, effect_key):
    key, effect = _effect_or_404(effect_key)
    try:
        page = max(1, int(request.values.get("page", 1)))
    except (TypeError, ValueError):
        page = 1

    query = g.db.query(User).filter(
        User.username_effects.contains(f'"{key}"')
    ).order_by(User.truescore.desc(), User.id.asc())

    total = query.count()
    users = query.offset(PAGE_SIZE * (page - 1)).limit(PAGE_SIZE + 1).all()
    next_exists = len(users) > PAGE_SIZE
    users = users[:PAGE_SIZE]

    total_pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
    return render_template(
        "user_cards.html",
        v=v,
        users=users,
        next_exists=next_exists,
        page=page,
        total_pages=total_pages,
        user_cards_title=f"{effect['title']} Effect Owners",
    )
