"""Runtime repairs for profile connection identity and presentation data."""

from __future__ import annotations

import importlib
import os
import time
from xml.etree import ElementTree

import requests
from flask import g
from sqlalchemy import text


_STEAM_IDENTITY_TTL = 6 * 60 * 60
_HTTP_TIMEOUT = (3.5, 6.0)


def _steam_identity(steam_id: str) -> dict:
    """Resolve a public Steam name/avatar, with or without a Web API key."""
    steam_id = str(steam_id or "").strip()
    if not steam_id.isdigit():
        return {}

    profile_url = f"https://steamcommunity.com/profiles/{steam_id}"
    api_key = os.environ.get("STEAM_WEB_API_KEY", "").strip()
    if api_key:
        try:
            response = requests.get(
                "https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/",
                params={"key": api_key, "steamids": steam_id},
                headers={"User-Agent": "Obsession-Connections/1.1"},
                timeout=_HTTP_TIMEOUT,
            )
            if response.ok:
                players = (response.json().get("response") or {}).get("players") or []
                if players:
                    player = players[0]
                    return {
                        "display_name": player.get("personaname") or "",
                        "profile_url": player.get("profileurl") or profile_url,
                        "avatar_url": player.get("avatarfull") or player.get("avatarmedium"),
                    }
        except (requests.RequestException, ValueError, TypeError):
            pass

    try:
        response = requests.get(
            profile_url,
            params={"xml": "1"},
            headers={"User-Agent": "Obsession-Connections/1.1"},
            timeout=_HTTP_TIMEOUT,
        )
        if not response.ok:
            return {}
        root = ElementTree.fromstring(response.content)
        display_name = (root.findtext("steamID") or "").strip()
        avatar_url = (root.findtext("avatarFull") or root.findtext("avatarMedium") or "").strip()
        custom_url = (root.findtext("customURL") or "").strip()
        if custom_url:
            profile_url = f"https://steamcommunity.com/id/{custom_url}"
        return {
            "display_name": display_name,
            "profile_url": profile_url,
            "avatar_url": avatar_url or None,
        }
    except (requests.RequestException, ElementTree.ParseError, ValueError, TypeError):
        return {}


def _needs_steam_identity(row: dict) -> bool:
    provider_id = str(row.get("provider_user_id") or "").strip()
    display_name = str(row.get("display_name") or "").strip()
    return not display_name or display_name == provider_id or display_name.isdigit()


def _hydrate_steam_row(module, row, *, force: bool = False):
    hydrated = dict(row)
    if hydrated.get("provider") != "steam":
        return hydrated

    metadata = module._json_load(hydrated.get("metadata_json"))
    now = int(time.time())
    last_checked = int(metadata.get("steam_identity_checked_utc") or 0)
    unresolved = _needs_steam_identity(hydrated)

    if not force and not unresolved:
        return hydrated
    if not force and last_checked > now - _STEAM_IDENTITY_TTL:
        return hydrated

    identity = _steam_identity(hydrated.get("provider_user_id"))
    metadata["steam_identity_checked_utc"] = now

    display_name = (identity.get("display_name") or "").strip()
    profile_url = identity.get("profile_url") or hydrated.get("profile_url")
    avatar_url = identity.get("avatar_url") or hydrated.get("avatar_url")

    g.db.execute(
        text(
            """
            UPDATE user_connections
            SET display_name=:display_name,
                profile_url=:profile_url,
                avatar_url=:avatar_url,
                metadata_json=:metadata_json,
                updated_utc=:updated_utc
            WHERE id=:id
            """
        ),
        {
            "display_name": display_name or hydrated.get("display_name"),
            "profile_url": profile_url,
            "avatar_url": avatar_url,
            "metadata_json": module._json_dump(metadata),
            "updated_utc": now,
            "id": int(hydrated["id"]),
        },
    )

    if display_name:
        hydrated["display_name"] = display_name
    hydrated["profile_url"] = profile_url
    hydrated["avatar_url"] = avatar_url
    hydrated["metadata_json"] = module._json_dump(metadata)
    hydrated["updated_utc"] = now
    return hydrated


def install_connection_repairs():
    """Patch the connection module after its routes have been registered."""
    module = importlib.import_module("files.routes.connections")
    if getattr(module, "_OBSESSION_CONNECTION_REPAIRS", False):
        return
    module._OBSESSION_CONNECTION_REPAIRS = True

    original_rows = module._connection_rows
    original_public = module._public_connection
    original_steam_callback = module._steam_callback

    def connection_rows(user_id, public_only=False):
        rows = original_rows(user_id, public_only=public_only)
        return [
            _hydrate_steam_row(module, row)
            if row.get("provider") == "steam"
            else row
            for row in rows
        ]

    def public_connection(row):
        public = original_public(row)
        if public.get("provider") == "steam":
            name = str(public.get("display_name") or "").strip()
            provider_id = str(row.get("provider_user_id") or "").strip()
            if not name or name == provider_id or name.isdigit():
                public["display_name"] = "Steam account"

        # Service marks are more reliable and visually consistent than remote
        # profile images, which may expire or be blocked by a provider CDN.
        public["avatar_url"] = None
        return public

    def steam_callback(v):
        original_steam_callback(v)
        for row in original_rows(v.id):
            if row.get("provider") == "steam" and row.get("source") == "direct":
                _hydrate_steam_row(module, row, force=True)

    module._connection_rows = connection_rows
    module._public_connection = public_connection
    module._steam_callback = steam_callback
