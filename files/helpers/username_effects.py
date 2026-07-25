import json
import re
from pathlib import Path
from typing import Iterable

from sqlalchemy import Column, String, Text, inspect, text

from files.helpers.config.username_effects import USERNAME_EFFECT_KEYS


_EMPTY_EFFECTS = '[]'
_DEFAULT_EFFECT_TEXT_COLOR = 'ffffff'
_EFFECT_ASSET_DIR = Path('files/assets/images/username_effects')
_COLOR_RE = re.compile(r'^[0-9a-f]{6}$')


def ensure_username_effect_assets():
    required = set(USERNAME_EFFECT_KEYS)
    required.add('siren_patron')
    missing = sorted(
        f'{key}.webp'
        for key in required
        if not (_EFFECT_ASSET_DIR / f'{key}.webp').is_file()
    )
    if missing:
        raise RuntimeError(
            'Direct username effect assets are missing: ' + ', '.join(missing)
        )


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
                items = [item.strip() for item in raw.split(',')]
    elif isinstance(value, (list, tuple, set)):
        items = list(value)
    else:
        items = []

    if not isinstance(items, list):
        return []

    clean = []
    seen = set()
    for item in items:
        key = str(item or '').strip().lower()
        if key not in USERNAME_EFFECT_KEYS or key in seen:
            continue
        seen.add(key)
        clean.append(key)
    return clean


def dump_username_effects(values: Iterable[str]) -> str:
    return json.dumps(normalize_username_effects(list(values)), separators=(',', ':'))


def normalize_username_effect_color(value) -> str:
    color = str(value or '').strip().lower().lstrip('#')
    return color if _COLOR_RE.fullmatch(color) else _DEFAULT_EFFECT_TEXT_COLOR


def _install_columns(User):
    if not hasattr(User, 'username_effects'):
        User.username_effects = Column(
            Text,
            nullable=False,
            default=_EMPTY_EFFECTS,
            server_default=text("'[]'"),
        )
    if not hasattr(User, 'username_effects_active'):
        User.username_effects_active = Column(
            Text,
            nullable=False,
            default=_EMPTY_EFFECTS,
            server_default=text("'[]'"),
        )
    if not hasattr(User, 'username_effect_color'):
        User.username_effect_color = Column(
            String(6),
            nullable=False,
            default=_DEFAULT_EFFECT_TEXT_COLOR,
            server_default=text("'ffffff'"),
        )


def _ensure_database_columns(engine):
    inspector = inspect(engine)
    if not inspector.has_table('users'):
        return

    existing = {column['name'] for column in inspector.get_columns('users')}
    required = {
        'username_effects': "TEXT NOT NULL DEFAULT '[]'",
        'username_effects_active': "TEXT NOT NULL DEFAULT '[]'",
        'username_effect_color': "VARCHAR(6) NOT NULL DEFAULT 'ffffff'",
    }

    with engine.begin() as connection:
        for column_name, definition in required.items():
            if column_name in existing:
                continue
            if engine.dialect.name == 'postgresql':
                connection.exec_driver_sql(
                    f'ALTER TABLE users ADD COLUMN IF NOT EXISTS {column_name} {definition}'
                )
            else:
                connection.exec_driver_sql(
                    f'ALTER TABLE users ADD COLUMN {column_name} {definition}'
                )


def install_username_effects(engine, User):
    if getattr(User, '_username_effects_installed', False):
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

    def effect_text_color(self):
        return normalize_username_effect_color(self.username_effect_color)

    User.owned_username_effects = property(owned_effects)
    User.active_username_effects = property(active_effects)
    User.username_effect_text_color = property(effect_text_color)

    original_json_popover = User.json_popover
    original_json_property = User.json

    def json_popover_with_effects(self, v):
        data = dict(original_json_popover(self, v))
        data['username_effects'] = active_effects(self)
        data['username_effect_color'] = effect_text_color(self)
        return data

    def json_with_effects(self):
        data = dict(original_json_property.fget(self))
        data['username_effects'] = active_effects(self)
        data['username_effect_color'] = effect_text_color(self)
        return data

    User.json_popover = json_popover_with_effects
    User.json = property(json_with_effects)
    User._username_effects_installed = True
