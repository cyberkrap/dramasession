"""Runtime repairs for profile connection identity and presentation data."""

from __future__ import annotations

import html
import importlib
import os
import re
import time
from xml.etree import ElementTree

import requests
from flask import g
from sqlalchemy import text


_STEAM_RESOLVED_TTL = 6 * 60 * 60
_STEAM_UNRESOLVED_TTL = 5 * 60
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
                headers={"User-Agent": "Obsession-Connections/1.2"},
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
            headers={"User-Agent": "Obsession-Connections/1.2"},
            timeout=_HTTP_TIMEOUT,
        )
        if response.ok:
            root = ElementTree.fromstring(response.content)
            display_name = (root.findtext("steamID") or "").strip()
            avatar_url = (root.findtext("avatarFull") or root.findtext("avatarMedium") or "").strip()
            custom_url = (root.findtext("customURL") or "").strip()
            if custom_url:
                profile_url = f"https://steamcommunity.com/id/{custom_url}"
            if display_name:
                return {
                    "display_name": display_name,
                    "profile_url": profile_url,
                    "avatar_url": avatar_url or None,
                }
    except (requests.RequestException, ElementTree.ParseError, ValueError, TypeError):
        pass

    try:
        response = requests.get(
            profile_url,
            headers={"User-Agent": "Obsession-Connections/1.2"},
            timeout=_HTTP_TIMEOUT,
        )
        if not response.ok:
            return {}
        body = response.text
        match = re.search(r'<span[^>]+class="actual_persona_name"[^>]*>(.*?)</span>', body, re.I | re.S)
        if not match:
            match = re.search(r'<title>\s*Steam Community\s*::\s*(.*?)\s*</title>', body, re.I | re.S)
        display_name = html.unescape(re.sub(r"<[^>]+>", "", match.group(1))).strip() if match else ""
        avatar_match = re.search(r'<meta[^>]+property="og:image"[^>]+content="([^"]+)"', body, re.I)
        return {
            "display_name": display_name,
            "profile_url": profile_url,
            "avatar_url": html.unescape(avatar_match.group(1)).strip() if avatar_match else None,
        } if display_name else {}
    except (requests.RequestException, ValueError, TypeError):
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
    ttl = _STEAM_UNRESOLVED_TTL if unresolved else _STEAM_RESOLVED_TTL

    if not force and not unresolved:
        return hydrated
    if not force and last_checked > now - ttl:
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
    original_upsert = module._upsert_connection

    def upsert_connection(**kwargs):
        provider = str(kwargs.get("provider") or "").strip().lower()
        source = str(kwargs.get("source") or "direct").strip().lower()
        provider_user_id = str(kwargs.get("provider_user_id") or "").strip()
        display_name = str(kwargs.get("display_name") or "").strip()
        if provider == "steam" and source == "discord" and provider_user_id:
            direct = g.db.execute(
                text(
                    """
                    SELECT id, display_name FROM user_connections
                    WHERE user_id=:user_id AND provider='steam'
                      AND provider_user_id=:provider_user_id AND source='direct'
                    """
                ),
                {"user_id": int(kwargs["user_id"]), "provider_user_id": provider_user_id},
            ).mappings().first()
            if direct:
                current_name = str(direct.get("display_name") or "").strip()
                if display_name and not display_name.isdigit() and (not current_name or current_name.isdigit() or current_name == provider_user_id):
                    g.db.execute(
                        text(
                            """
                            UPDATE user_connections
                            SET display_name=:display_name,
                                profile_url=COALESCE(:profile_url, profile_url),
                                updated_utc=:updated_utc
                            WHERE id=:id
                            """
                        ),
                        {
                            "display_name": display_name[:255],
                            "profile_url": kwargs.get("profile_url"),
                            "updated_utc": int(time.time()),
                            "id": int(direct["id"]),
                        },
                    )
                return
        return original_upsert(**kwargs)

    def connection_rows(user_id, public_only=False):
        rows = original_rows(user_id, public_only=public_only)
        # Public profile requests must never wait on external Steam lookups.
        # Identity hydration still runs on the management page and callbacks.
        if public_only:
            return rows
        return [
            _hydrate_steam_row(module, row)
            if dict(row).get("provider") == "steam"
            else row
            for row in rows
        ]

    def public_connection(row):
        public = original_public(row)
        if public.get("provider") == "steam":
            name = str(public.get("display_name") or "").strip()
            provider_id = str(dict(row).get("provider_user_id") or "").strip()
            if not name or name == provider_id or name.isdigit():
                public["display_name"] = "Steam account"

        # Provider marks are stable and consistent; remote profile images may
        # expire or be blocked by provider CDNs.
        public["avatar_url"] = None
        return public

    def steam_callback(v):
        original_steam_callback(v)
        for row in original_rows(v.id):
            row_data = dict(row)
            if row_data.get("provider") == "steam" and row_data.get("source") == "direct":
                _hydrate_steam_row(module, row_data, force=True)

    module._upsert_connection = upsert_connection
    module._connection_rows = connection_rows
    module._public_connection = public_connection
    module._steam_callback = steam_callback
