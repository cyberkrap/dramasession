import os
from copy import deepcopy
from pathlib import Path

import fcntl

from files.helpers.config.awards import AWARDS, AWARDS_ENABLED, HOUSE_AWARDS
from files.helpers.config.const import HOUSES


_LOCK_PATH = "/tmp/obsession-house-system.lock"
_AWARDS_ROUTE = Path("files/routes/awards.py")
_FOUNDER_DISCOUNT = 0.75


def base_house_names():
    """Return configured houses without the sentinel, preserving config order."""
    return tuple(house for house in HOUSES if house and house != "None" and not house.endswith(" Founder"))


def normalize_house_name(house):
    value = str(house or "").strip()
    return value[:-8] if value.endswith(" Founder") else value


def is_house_founder(house):
    return str(house or "").strip().endswith(" Founder")


def special_award_for_house(house):
    return HOUSE_AWARDS.get(str(house or "").strip())


def _atomic_write(path: Path, content: str) -> None:
    temp_path = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temp_path.write_text(content, encoding="utf-8")
    os.replace(temp_path, path)


def _build_house_award(base_house):
    if base_house == "Furry":
        award = deepcopy(AWARDS["owoify"])
        award.update({
            "kind": "Furry",
            "title": "OwOify",
            "description": "OwOifies the recipient's comments for 6 hours.",
            "enabled": True,
        })
        return award

    if base_house == "Femboy":
        award = deepcopy(AWARDS["rainbow"])
        award.update({
            "kind": "Femboy",
            "title": "Rainbow",
            "description": "Makes the recipient's comments and posts rainbow text for 24 hours.",
            "enabled": True,
        })
        return award

    if base_house == "Racist":
        legacy = deepcopy(HOUSE_AWARDS.get("Racist") or {})
        legacy.update({
            "kind": "Racist",
            "title": "Early Life",
            "description": "Gives the recipient the Early Life effect for 24 hours.",
            "icon": "fas fa-star-of-david",
            "color": "text-yellow",
            "price": int(legacy.get("price") or 400),
            "deflectable": True,
            "cosmetic": False,
            "ghost": False,
            "enabled": True,
        })
        return legacy

    # Vampire intentionally has no house-only award at the moment. Keeping this
    # as an explicit no-award case means adding one later is a single config edit.
    return None


def _configure_house_awards():
    # OwOify and Rainbow are house privileges on TOC, not globally available
    # awards. Keep their base definitions for mechanics/history, but remove them
    # from the public global catalog.
    for kind in ("owoify", "rainbow"):
        if kind in AWARDS:
            AWARDS[kind]["enabled"] = False
        AWARDS_ENABLED.pop(kind, None)

    HOUSE_AWARDS.clear()
    for house in base_house_names():
        award = _build_house_award(house)
        if not award:
            continue

        HOUSE_AWARDS[house] = award

        founder_name = f"{house} Founder"
        founder_award = deepcopy(award)
        founder_award["kind"] = founder_name
        founder_award["price"] = int(founder_award["price"] * _FOUNDER_DISCOUNT)
        HOUSE_AWARDS[founder_name] = founder_award


def _patch_award_catalog_lookups():
    """Make no-award houses valid without assuming every house owns an award."""
    with open(_LOCK_PATH, "w", encoding="utf-8") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        source = _AWARDS_ROUTE.read_text(encoding="utf-8")
        original = source

        # Three catalog-building sites exist in shop(), buy(), and award_thing().
        source = source.replace(
            "\tif v.house:\n\t\tAWARDS[v.house] = deepcopy(HOUSE_AWARDS[v.house])",
            "\tif v.house in HOUSE_AWARDS:\n\t\tAWARDS[v.house] = deepcopy(HOUSE_AWARDS[v.house])",
        )
        source = source.replace(
            "\tif v.house:\n\t\tAWARDS[v.house] = HOUSE_AWARDS[v.house]",
            "\tif v.house in HOUSE_AWARDS:\n\t\tAWARDS[v.house] = HOUSE_AWARDS[v.house]",
        )

        if source == original:
            if source.count("if v.house in HOUSE_AWARDS:") < 3:
                raise RuntimeError("Could not locate all house award catalog lookups")
            return

        if source.count("if v.house in HOUSE_AWARDS:") < 3:
            raise RuntimeError("House award lookup repair was incomplete")
        _atomic_write(_AWARDS_ROUTE, source)


def install_house_system():
    _configure_house_awards()
    _patch_award_catalog_lookups()
