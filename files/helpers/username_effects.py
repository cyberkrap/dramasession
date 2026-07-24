import base64
import io
import json
import os
from pathlib import Path
from typing import Iterable
from zipfile import ZipFile

from sqlalchemy import Column, Text, inspect, text

from files.helpers.config.username_effects import USERNAME_EFFECT_KEYS


_EMPTY_EFFECTS = "[]"


_EFFECT_BUNDLE_PARTS = Path("files/username_effects_bundle")
_EFFECT_ASSET_DIR = Path("files/assets/images/username_effects")


def ensure_username_effect_assets():
    expected = {f"{key}.webp" for key in USERNAME_EFFECT_KEYS}
    if expected and all((_EFFECT_ASSET_DIR / filename).is_file() for filename in expected):
        return

    parts = sorted(_EFFECT_BUNDLE_PARTS.glob("chunk*.b64"))
    if not parts:
        raise RuntimeError("Username effect asset bundle is missing.")

    try:
        encoded = "".join(part.read_text(encoding="ascii").strip() for part in parts)
        bundle = base64.b64decode(encoded, validate=True)
    except (OSError, ValueError) as exc:
        raise RuntimeError("Username effect asset bundle is corrupt.") from exc

    _EFFECT_ASSET_DIR.mkdir(parents=True, exist_ok=True)
    with ZipFile(io.BytesIO(bundle)) as archive:
        available = set(archive.namelist())
        missing = expected - available
        if missing:
            raise RuntimeError(
                "Username effect bundle is incomplete: " + ", ".join(sorted(missing))
            )

        for filename in sorted(expected):
            target = _EFFECT_ASSET_DIR / filename
            temporary = target.with_suffix(".webp.tmp")
            with archive.open(filename) as source, temporary.open("wb") as destination:
                while True:
                    chunk = source.read(1024 * 256)
                    if not chunk:
                        break
                    destination.write(chunk)
            os.replace(temporary, target)


def normalize_username_effects(value) -> list[str]:
    if value is None:
        return []

    if isinstance(value, str):
        raw = value.strip()
        if not raw:
            items = []
        else:
            try:
                items = json.loads(raw)
            except (TypeError, ValueError):
                items = [item.strip() for item in raw.split(",")]
    elif isinstance(value, (list, tuple, set)):
        items = list(value)
    else:
        items = []

    if not isinstance(items, list):
        return []

    clean = []
    seen = set()
    for item in items:
        key = str(item or "").strip().lower()
        if key not in USERNAME_EFFECT_KEYS or key in seen:
            continue
        seen.add(key)
        clean.append(key)
    return clean


def dump_username_effects(values: Iterable[str]) -> str:
    return json.dumps(normalize_username_effects(list(values)), separators=(",", ":"))


def _install_columns(User):
    if not hasattr(User, "username_effects"):
        User.username_effects = Column(
            Text,
            nullable=False,
            default=_EMPTY_EFFECTS,
            server_default=text("'[]'"),
        )
    if not hasattr(User, "username_effects_active"):
        User.username_effects_active = Column(
            Text,
            nullable=False,
            default=_EMPTY_EFFECTS,
            server_default=text("'[]'"),
        )


def _ensure_database_columns(engine):
    inspector = inspect(engine)
    if not inspector.has_table("users"):
        return

    existing = {column["name"] for column in inspector.get_columns("users")}
    required = {
        "username_effects": "TEXT NOT NULL DEFAULT '[]'",
        "username_effects_active": "TEXT NOT NULL DEFAULT '[]'",
    }

    with engine.begin() as connection:
        for column_name, definition in required.items():
            if column_name in existing:
                continue
            if engine.dialect.name == "postgresql":
                connection.exec_driver_sql(
                    f"ALTER TABLE users ADD COLUMN IF NOT EXISTS {column_name} {definition}"
                )
            else:
                connection.exec_driver_sql(
                    f"ALTER TABLE users ADD COLUMN {column_name} {definition}"
                )


def install_username_effects(engine, User):
    if getattr(User, "_username_effects_installed", False):
        return

    ensure_username_effect_assets()
    _install_columns(User)
    _ensure_database_columns(engine)

    def owned_effects(self):
        return normalize_username_effects(self.username_effects)

    def active_effects(self):
        owned = set(owned_effects(self))
        return [
            key
            for key in normalize_username_effects(self.username_effects_active)
            if key in owned
        ]

    User.owned_username_effects = property(owned_effects)
    User.active_username_effects = property(active_effects)

    original_json_popover = User.json_popover
    original_json_property = User.json

    def json_popover_with_effects(self, v):
        data = dict(original_json_popover(self, v))
        data["username_effects"] = active_effects(self)
        return data

    def json_with_effects(self):
        data = dict(original_json_property.fget(self))
        data["username_effects"] = active_effects(self)
        return data

    User.json_popover = json_popover_with_effects
    User.json = property(json_with_effects)
    User._username_effects_installed = True
