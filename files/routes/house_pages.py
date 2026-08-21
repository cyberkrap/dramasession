from flask import g, redirect, render_template
from sqlalchemy import case, func

from files.__main__ import app, limiter
from files.classes import User
from files.helpers.config.const import DEFAULT_RATELIMIT
from files.helpers.house_system import base_house_names, special_award_for_house
from files.routes.wrappers import auth_required, get_ID


def _resolve_house(value):
    requested = str(value or "").strip().lower()
    return next((house for house in base_house_names() if house.lower() == requested), None)


def _visible_members(v):
    query = g.db.query(User)
    if not v.can_see_shadowbanned:
        query = query.filter(User.shadowbanned.is_(None))
    return query


def _house_summary(house, v):
    members = _visible_members(v).filter(User.house.in_((house, f"{house} Founder")))
    special = special_award_for_house(house)
    return {
        "name": house,
        "members": members.count(),
        "founders": members.filter(User.house == f"{house} Founder").count(),
        "truescore": int(
            g.db.query(func.coalesce(func.sum(User.truescore), 0))
            .filter(User.house.in_((house, f"{house} Founder")))
            .scalar()
            or 0
        ),
        "award": special["title"] if special else None,
    }


@app.get("/houses")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def houses(v):
    houses = [_house_summary(house, v) for house in base_house_names()]
    houses.sort(key=lambda row: (-row["truescore"], row["name"].lower()))
    return render_template("houses/index.html", v=v, houses=houses)


@app.get("/house/<house_name>")
@app.get("/houses/<house_name>")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def house_members(v, house_name):
    house = _resolve_house(house_name)
    if not house:
        return redirect("/houses")

    founder_value = f"{house} Founder"
    founder_first = case((User.house == founder_value, 0), else_=1)
    members = (
        _visible_members(v)
        .filter(User.house.in_((house, founder_value)))
        .order_by(founder_first.asc(), User.truescore.desc(), func.lower(User.username).asc())
        .all()
    )

    return render_template(
        "houses/detail.html",
        v=v,
        house=house,
        summary=_house_summary(house, v),
        members=members,
    )
