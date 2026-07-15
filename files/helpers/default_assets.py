import json
import os

from files.helpers.config.const import SITE_NAME

DEFAULT_ASSETS_FILE = "files/assets/default_assets.json"
DEFAULT_ASSET_DIR = f"files/assets/images/{SITE_NAME}/defaults"
_DEFAULTS = {"profile": None, "banner": None}


def get_default_assets():
    try:
        with open(DEFAULT_ASSETS_FILE, "r", encoding="utf-8") as stream:
            values = json.load(stream)
    except (OSError, ValueError, TypeError):
        values = {}
    return {key: values.get(key) or None for key in _DEFAULTS}


def get_default_asset(kind):
    return get_default_assets().get(kind)


def set_default_asset(kind, path):
    if kind not in _DEFAULTS:
        raise ValueError("Unknown default asset kind")
    values = get_default_assets()
    values[kind] = path
    os.makedirs(os.path.dirname(DEFAULT_ASSETS_FILE), exist_ok=True)
    with open(DEFAULT_ASSETS_FILE, "w", encoding="utf-8") as stream:
        json.dump(values, stream, indent=2)
    return path