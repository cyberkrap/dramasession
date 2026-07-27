"""Profile connection accounts and live activity integrations."""

from __future__ import annotations

import base64
import hashlib
import json
import os
import secrets
import threading
import time
from urllib.parse import quote, urlencode, urlparse

import requests
from cryptography.fernet import Fernet, InvalidToken
from flask import abort, g, redirect, render_template, request, session
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from files.__main__ import app, engine, limiter
from files.classes import User
from files.helpers.config.const import DEFAULT_RATELIMIT, DEFAULT_RATELIMIT_SLOWER, SECRET_KEY
from files.helpers.get import get_user
from files.routes.wrappers import auth_desired_with_logingate, auth_required, get_ID


CONNECTIONS_BASE_URL = os.environ.get(
    "CONNECTIONS_BASE_URL", "https://theobsessionclub.com"
).strip().rstrip("/")

PROVIDER_CONFIG = {
    "spotify": {
        "label": "Spotify", "icon": "fab fa-spotify",
        "client_id_env": "SPOTIFY_CONNECTION_CLIENT_ID",
        "client_secret_env": "SPOTIFY_CONNECTION_CLIENT_SECRET",
        "authorize_url": "https://accounts.spotify.com/authorize",
        "token_url": "https://accounts.spotify.com/api/token",
        "scope": "user-read-currently-playing user-read-playback-state user-read-private",
        "activity": True,
    },
    "github": {
        "label": "GitHub", "icon": "fab fa-github",
        "client_id_env": "GITHUB_CONNECTION_CLIENT_ID",
        "client_secret_env": "GITHUB_CONNECTION_CLIENT_SECRET",
        "authorize_url": "https://github.com/login/oauth/authorize",
        "token_url": "https://github.com/login/oauth/access_token",
        "scope": "", "activity": False,
    },
    "discord": {
        "label": "Discord", "icon": "fab fa-discord",
        "client_id_env": "DISCORD_CONNECTION_CLIENT_ID",
        "client_secret_env": "DISCORD_CONNECTION_CLIENT_SECRET",
        "authorize_url": "https://discord.com/oauth2/authorize",
        "token_url": "https://discord.com/api/oauth2/token",
        "scope": "identify connections", "activity": False,
    },
    "steam": {"label": "Steam", "icon": "fab fa-steam", "activity": True},
}

MANUAL_PROVIDERS = {
    "bluesky": {"label": "Bluesky", "icon": "fas fa-cloud", "template": "https://bsky.app/profile/{handle}"},
    "reddit": {"label": "Reddit", "icon": "fab fa-reddit", "template": "https://www.reddit.com/user/{handle}"},
    "twitch": {"label": "Twitch", "icon": "fab fa-twitch", "template": "https://www.twitch.tv/{handle}"},
    "youtube": {"label": "YouTube", "icon": "fab fa-youtube", "template": "https://www.youtube.com/@{handle}"},
    "x": {"label": "X", "icon": "fab fa-x-twitter", "template": "https://x.com/{handle}"},
    "roblox": {"label": "Roblox", "icon": "fas fa-cube", "template": ""},
    "playstation": {"label": "PlayStation", "icon": "fab fa-playstation", "template": ""},
    "xbox": {"label": "Xbox", "icon": "fab fa-xbox", "template": ""},
    "epicgames": {"label": "Epic Games", "icon": "fas fa-shield", "template": ""},
    "battlenet": {"label": "Battle.net", "icon": "fas fa-gamepad", "template": ""},
}

DISCORD_PROVIDER_ALIASES = {"twitter": "x"}
_TABLE_LOCK = threading.Lock()
_TABLE_READY = False
_HTTP_TIMEOUT = (3.5, 6.0)


def _fernet():
    raw = os.environ.get("CONNECTIONS_ENCRYPTION_KEY", "").strip()
    if raw:
        try:
            return Fernet(raw.encode("ascii"))
        except (ValueError, TypeError):
            pass
    derived = hashlib.sha256(str(SECRET_KEY).encode("utf-8")).digest()
    return Fernet(base64.urlsafe_b64encode(derived))


_TOKEN_BOX = _fernet()


def _encrypt(value):
    return _TOKEN_BOX.encrypt(str(value).encode()).decode("ascii") if value else None


def _decrypt(value):
    if not value:
        return None
    try:
        return _TOKEN_BOX.decrypt(str(value).encode("ascii")).decode("utf-8")
    except (InvalidToken, ValueError, TypeError):
        return None


def _ensure_table():
    global _TABLE_READY
    if _TABLE_READY:
        return
    with _TABLE_LOCK:
        if _TABLE_READY:
            return
        id_column = "BIGSERIAL PRIMARY KEY" if engine.dialect.name == "postgresql" else "INTEGER PRIMARY KEY AUTOINCREMENT"
        ddl = f"""
            CREATE TABLE IF NOT EXISTS user_connections (
                id {id_column},
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                provider VARCHAR(32) NOT NULL,
                provider_user_id VARCHAR(255) NOT NULL,
                display_name VARCHAR(255) NOT NULL,
                profile_url TEXT,
                avatar_url TEXT,
                source VARCHAR(32) NOT NULL DEFAULT 'direct',
                access_token TEXT,
                refresh_token TEXT,
                token_expires_utc BIGINT,
                scopes TEXT NOT NULL DEFAULT '',
                display_on_profile BOOLEAN NOT NULL DEFAULT TRUE,
                show_activity BOOLEAN NOT NULL DEFAULT TRUE,
                metadata_json TEXT NOT NULL DEFAULT '{{}}',
                activity_json TEXT NOT NULL DEFAULT '{{}}',
                activity_checked_utc BIGINT NOT NULL DEFAULT 0,
                created_utc BIGINT NOT NULL,
                updated_utc BIGINT NOT NULL,
                UNIQUE(user_id, provider, provider_user_id)
            )
        """
        try:
            with engine.begin() as connection:
                connection.execute(text(ddl))
                connection.execute(text("CREATE INDEX IF NOT EXISTS ix_user_connections_user ON user_connections (user_id)"))
                connection.execute(text("CREATE INDEX IF NOT EXISTS ix_user_connections_public ON user_connections (user_id, display_on_profile)"))
        except SQLAlchemyError:
            return
        _TABLE_READY = True


def _json_load(value):
    try:
        loaded = json.loads(value or "{}")
        return loaded if isinstance(loaded, dict) else {}
    except (TypeError, ValueError):
        return {}


def _json_dump(value):
    return json.dumps(value or {}, separators=(",", ":"), ensure_ascii=False)


def _provider_label(provider):
    config = PROVIDER_CONFIG.get(provider) or MANUAL_PROVIDERS.get(provider) or {}
    return config.get("label") or provider.replace("_", " ").title()


def _provider_icon(provider):
    config = PROVIDER_CONFIG.get(provider) or MANUAL_PROVIDERS.get(provider) or {}
    return config.get("icon") or "fas fa-link"


def _provider_credentials(provider):
    config = PROVIDER_CONFIG.get(provider, {})
    return (
        os.environ.get(config.get("client_id_env", ""), "").strip(),
        os.environ.get(config.get("client_secret_env", ""), "").strip(),
    )


def _provider_configured(provider):
    if provider == "steam":
        return True
    return all(_provider_credentials(provider))


def _callback_url(provider):
    return f"{CONNECTIONS_BASE_URL}/settings/connections/callback/{provider}"


def _connection_rows(user_id, public_only=False):
    _ensure_table()
    clause = " AND display_on_profile = TRUE" if public_only else ""
    return g.db.execute(text(f"""
        SELECT id, user_id, provider, provider_user_id, display_name,
               profile_url, avatar_url, source, access_token, refresh_token,
               token_expires_utc, scopes, display_on_profile, show_activity,
               metadata_json, activity_json, activity_checked_utc,
               created_utc, updated_utc
        FROM user_connections
        WHERE user_id = :user_id{clause}
        ORDER BY CASE source WHEN 'direct' THEN 0 WHEN 'manual' THEN 1 ELSE 2 END,
                 provider, display_name
    """), {"user_id": int(user_id)}).mappings().all()


def _connection_row(connection_id, user_id):
    _ensure_table()
    return g.db.execute(text("SELECT * FROM user_connections WHERE id=:id AND user_id=:user_id"), {
        "id": int(connection_id), "user_id": int(user_id)
    }).mappings().first()


def _upsert_connection(*, user_id, provider, provider_user_id, display_name,
                       profile_url=None, avatar_url=None, source="direct",
                       access_token=None, refresh_token=None, token_expires_utc=None,
                       scopes="", metadata=None, display_on_profile=True,
                       show_activity=True):
    _ensure_table()
    provider = str(provider).strip().lower()[:32]
    provider_user_id = str(provider_user_id).strip()[:255]
    display_name = str(display_name or provider_user_id).strip()[:255]
    now = int(time.time())
    existing = g.db.execute(text("""
        SELECT id, source FROM user_connections
        WHERE user_id=:user_id AND provider=:provider AND provider_user_id=:provider_user_id
    """), {"user_id": int(user_id), "provider": provider,
             "provider_user_id": provider_user_id}).mappings().first()
    if existing and existing["source"] == "direct" and source == "discord":
        return
    if source == "direct":
        g.db.execute(text("""
            DELETE FROM user_connections
            WHERE user_id=:user_id AND provider=:provider AND source='direct'
              AND provider_user_id != :provider_user_id
        """), {"user_id": int(user_id), "provider": provider,
                 "provider_user_id": provider_user_id})
    g.db.execute(text("""
        INSERT INTO user_connections (
            user_id, provider, provider_user_id, display_name, profile_url,
            avatar_url, source, access_token, refresh_token, token_expires_utc,
            scopes, display_on_profile, show_activity, metadata_json,
            activity_json, activity_checked_utc, created_utc, updated_utc
        ) VALUES (
            :user_id, :provider, :provider_user_id, :display_name, :profile_url,
            :avatar_url, :source, :access_token, :refresh_token, :token_expires_utc,
            :scopes, :display_on_profile, :show_activity, :metadata_json,
            '{}', 0, :now, :now
        )
        ON CONFLICT (user_id, provider, provider_user_id) DO UPDATE SET
            display_name=EXCLUDED.display_name,
            profile_url=EXCLUDED.profile_url,
            avatar_url=EXCLUDED.avatar_url,
            source=EXCLUDED.source,
            access_token=COALESCE(EXCLUDED.access_token,user_connections.access_token),
            refresh_token=COALESCE(EXCLUDED.refresh_token,user_connections.refresh_token),
            token_expires_utc=COALESCE(EXCLUDED.token_expires_utc,user_connections.token_expires_utc),
            scopes=EXCLUDED.scopes,
            metadata_json=EXCLUDED.metadata_json,
            updated_utc=EXCLUDED.updated_utc
    """), {
        "user_id": int(user_id), "provider": provider,
        "provider_user_id": provider_user_id, "display_name": display_name,
        "profile_url": profile_url, "avatar_url": avatar_url, "source": source,
        "access_token": _encrypt(access_token), "refresh_token": _encrypt(refresh_token),
        "token_expires_utc": token_expires_utc, "scopes": scopes or "",
        "display_on_profile": bool(display_on_profile), "show_activity": bool(show_activity),
        "metadata_json": _json_dump(metadata), "now": now,
    })


def _public_connection(row):
    metadata = _json_load(row["metadata_json"])
    return {
        "id": int(row["id"]), "provider": row["provider"],
        "provider_label": _provider_label(row["provider"]),
        "icon": _provider_icon(row["provider"]),
        "display_name": row["display_name"], "profile_url": row["profile_url"],
        "avatar_url": row["avatar_url"], "source": row["source"],
        "verified": bool(metadata.get("verified", row["source"] in {"direct", "discord"})),
        "display_on_profile": bool(row["display_on_profile"]),
        "show_activity": bool(row["show_activity"]),
        "activity": _json_load(row["activity_json"]),
    }


def _state_key(provider):
    return f"profile_connection_oauth:{provider}"


def _new_oauth_state(provider, user_id, verifier=None):
    state = secrets.token_urlsafe(32)
    session[_state_key(provider)] = {
        "state": state, "user_id": int(user_id),
        "created_utc": int(time.time()), "verifier": verifier,
    }
    session.modified = True
    return state


def _consume_oauth_state(provider, supplied, user_id):
    stored = session.pop(_state_key(provider), None)
    session.modified = True
    if not isinstance(stored, dict):
        abort(400, "Connection authorization expired. Start again.")
    if not secrets.compare_digest(str(stored.get("state", "")), str(supplied or "")):
        abort(400, "Connection authorization state did not match.")
    if int(stored.get("user_id", 0)) != int(user_id):
        abort(403)
    if int(stored.get("created_utc", 0)) < int(time.time()) - 900:
        abort(400, "Connection authorization expired. Start again.")
    return stored


def _pkce_pair():
    verifier = secrets.token_urlsafe(48)
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
    return verifier, challenge


def _oauth_authorize(provider, v):
    if provider not in PROVIDER_CONFIG:
        abort(404)
    if provider == "steam":
        state = _new_oauth_state(provider, v.id)
        return_to = f"{_callback_url(provider)}?state={quote(state)}"
        params = {
            "openid.ns": "http://specs.openid.net/auth/2.0",
            "openid.mode": "checkid_setup", "openid.return_to": return_to,
            "openid.realm": CONNECTIONS_BASE_URL,
            "openid.identity": "http://specs.openid.net/auth/2.0/identifier_select",
            "openid.claimed_id": "http://specs.openid.net/auth/2.0/identifier_select",
        }
        return redirect("https://steamcommunity.com/openid/login?" + urlencode(params))
    if not _provider_configured(provider):
        return redirect("/settings/connections?error=" + quote(
            f"{_provider_label(provider)} connections are not configured yet."))
    config = PROVIDER_CONFIG[provider]
    client_id, _ = _provider_credentials(provider)
    verifier = challenge = None
    if provider == "github":
        verifier, challenge = _pkce_pair()
    state = _new_oauth_state(provider, v.id, verifier)
    params = {"client_id": client_id, "redirect_uri": _callback_url(provider),
              "response_type": "code", "state": state}
    if config.get("scope"):
        params["scope"] = config["scope"]
    if challenge:
        params.update({"code_challenge": challenge, "code_challenge_method": "S256"})
    return redirect(config["authorize_url"] + "?" + urlencode(params))


def _exchange_oauth_code(provider, code, state_data):
    config = PROVIDER_CONFIG[provider]
    client_id, client_secret = _provider_credentials(provider)
    data = {"grant_type": "authorization_code", "code": code,
            "redirect_uri": _callback_url(provider), "client_id": client_id,
            "client_secret": client_secret}
    if state_data.get("verifier"):
        data["code_verifier"] = state_data["verifier"]
    headers = {"Accept": "application/json"}
    if provider == "spotify":
        auth = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
        headers["Authorization"] = f"Basic {auth}"
        data.pop("client_id", None); data.pop("client_secret", None)
    response = requests.post(config["token_url"], data=data, headers=headers,
                             timeout=_HTTP_TIMEOUT)
    if response.status_code >= 400:
        raise RuntimeError(f"{_provider_label(provider)} rejected the authorization code.")
    payload = response.json()
    if not payload.get("access_token"):
        raise RuntimeError(f"{_provider_label(provider)} did not return an access token.")
    return payload


def _api_get(url, token, accept="application/json"):
    return requests.get(url, headers={"Authorization": f"Bearer {token}",
        "Accept": accept, "User-Agent": "Obsession-Connections/1.0"},
        timeout=_HTTP_TIMEOUT)


def _spotify_identity(token):
    response = _api_get("https://api.spotify.com/v1/me", token)
    response.raise_for_status(); data = response.json(); images = data.get("images") or []
    return {"provider_user_id": data["id"],
            "display_name": data.get("display_name") or data["id"],
            "profile_url": (data.get("external_urls") or {}).get("spotify"),
            "avatar_url": images[0].get("url") if images else None,
            "metadata": {"verified": True, "product": data.get("product")}}


def _github_identity(token):
    response = _api_get("https://api.github.com/user", token,
                        "application/vnd.github+json")
    response.raise_for_status(); data = response.json()
    return {"provider_user_id": str(data["id"]),
            "display_name": data.get("login") or str(data["id"]),
            "profile_url": data.get("html_url"), "avatar_url": data.get("avatar_url"),
            "metadata": {"verified": True}}


def _discord_identity(token):
    response = _api_get("https://discord.com/api/v10/users/@me", token)
    response.raise_for_status(); data = response.json(); avatar = data.get("avatar")
    avatar_url = f"https://cdn.discordapp.com/avatars/{data['id']}/{avatar}.png?size=128" if avatar else None
    return {"provider_user_id": data["id"],
            "display_name": data.get("global_name") or data.get("username") or data["id"],
            "profile_url": f"https://discord.com/users/{data['id']}",
            "avatar_url": avatar_url,
            "metadata": {"verified": True, "username": data.get("username")}}


def _discord_profile_url(provider, account_id, name):
    safe_name = quote(str(name or "").strip(), safe="@._-")
    safe_id = quote(str(account_id or "").strip(), safe="")
    return {
        "github": f"https://github.com/{safe_name}",
        "spotify": f"https://open.spotify.com/user/{safe_id}",
        "steam": f"https://steamcommunity.com/profiles/{safe_id}",
        "reddit": f"https://www.reddit.com/user/{safe_name}",
        "twitch": f"https://www.twitch.tv/{safe_name}",
        "youtube": f"https://www.youtube.com/channel/{safe_id}",
        "x": f"https://x.com/{safe_name}",
        "bluesky": f"https://bsky.app/profile/{safe_name}",
        "roblox": f"https://www.roblox.com/users/{safe_id}/profile",
    }.get(provider)


def _import_discord_connections(user_id, token):
    response = _api_get("https://discord.com/api/v10/users/@me/connections", token)
    response.raise_for_status(); count = 0
    for item in response.json():
        if int(item.get("visibility", 0) or 0) != 1:
            continue
        provider = DISCORD_PROVIDER_ALIASES.get(item.get("type"), item.get("type"))
        if provider not in set(PROVIDER_CONFIG) | set(MANUAL_PROVIDERS):
            continue
        account_id = str(item.get("id") or item.get("name") or "").strip()
        name = str(item.get("name") or account_id).strip()
        if not account_id or not name:
            continue
        _upsert_connection(user_id=user_id, provider=provider,
            provider_user_id=account_id, display_name=name,
            profile_url=_discord_profile_url(provider, account_id, name),
            source="discord", metadata={"verified": bool(item.get("verified")),
            "show_activity_on_discord": bool(item.get("show_activity"))},
            show_activity=bool(item.get("show_activity")))
        count += 1
    return count


def _steam_callback(v):
    validation = dict(request.args); validation["openid.mode"] = "check_authentication"
    response = requests.post("https://steamcommunity.com/openid/login",
                             data=validation, timeout=_HTTP_TIMEOUT)
    if "is_valid:true" not in response.text:
        raise RuntimeError("Steam could not verify this account.")
    claimed = request.args.get("openid.claimed_id", "")
    steam_id = claimed.rstrip("/").rsplit("/", 1)[-1]
    if not steam_id.isdigit():
        raise RuntimeError("Steam returned an invalid account identifier.")
    display_name = steam_id; profile_url = f"https://steamcommunity.com/profiles/{steam_id}"
    avatar_url = None; metadata = {"verified": True}
    api_key = os.environ.get("STEAM_WEB_API_KEY", "").strip()
    if api_key:
        result = requests.get("https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/",
            params={"key": api_key, "steamids": steam_id}, timeout=_HTTP_TIMEOUT)
        if result.ok:
            players = (result.json().get("response") or {}).get("players") or []
            if players:
                player = players[0]; display_name = player.get("personaname") or display_name
                profile_url = player.get("profileurl") or profile_url
                avatar_url = player.get("avatarfull") or player.get("avatarmedium")
    _upsert_connection(user_id=v.id, provider="steam", provider_user_id=steam_id,
        display_name=display_name, profile_url=profile_url, avatar_url=avatar_url,
        source="direct", metadata=metadata, show_activity=True)


def _refresh_token(row):
    provider = row["provider"]; refresh_token = _decrypt(row["refresh_token"])
    if not refresh_token or provider not in {"spotify", "discord"}:
        return _decrypt(row["access_token"])
    client_id, client_secret = _provider_credentials(provider); config = PROVIDER_CONFIG[provider]
    data = {"grant_type": "refresh_token", "refresh_token": refresh_token,
            "client_id": client_id, "client_secret": client_secret}
    headers = {"Accept": "application/json"}
    if provider == "spotify":
        auth = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
        headers["Authorization"] = f"Basic {auth}"; data.pop("client_id"); data.pop("client_secret")
    response = requests.post(config["token_url"], data=data, headers=headers,
                             timeout=_HTTP_TIMEOUT)
    if not response.ok:
        return None
    payload = response.json(); access_token = payload.get("access_token")
    if not access_token:
        return None
    new_refresh = payload.get("refresh_token") or refresh_token
    expires = int(time.time()) + int(payload.get("expires_in", 3600))
    g.db.execute(text("""
        UPDATE user_connections SET access_token=:access_token,
        refresh_token=:refresh_token,token_expires_utc=:expires,updated_utc=:now
        WHERE id=:id
    """), {"access_token": _encrypt(access_token), "refresh_token": _encrypt(new_refresh),
             "expires": expires, "now": int(time.time()), "id": int(row["id"])})
    return access_token


def _valid_access_token(row):
    token = _decrypt(row["access_token"]); expires = int(row["token_expires_utc"] or 0)
    if token and (not expires or expires > int(time.time()) + 60):
        return token
    return _refresh_token(row)


def _save_activity(connection_id, activity, checked_utc=None):
    checked = int(checked_utc or time.time())
    g.db.execute(text("""
        UPDATE user_connections SET activity_json=:activity,
        activity_checked_utc=:checked,updated_utc=:checked WHERE id=:id
    """), {"activity": _json_dump(activity), "checked": checked,
             "id": int(connection_id)})


def _spotify_activity(row):
    cached = _json_load(row["activity_json"]); now = int(time.time())
    if now - int(row["activity_checked_utc"] or 0) < 30:
        return cached
    token = _valid_access_token(row)
    if not token:
        _save_activity(row["id"], {}); return {}
    url = "https://api.spotify.com/v1/me/player/currently-playing?additional_types=track,episode"
    response = _api_get(url, token)
    if response.status_code == 401:
        token = _refresh_token(row)
        if token: response = _api_get(url, token)
    if response.status_code == 429:
        return cached
    if response.status_code == 204 or not response.ok:
        _save_activity(row["id"], {}); return {}
    data = response.json(); item = data.get("item") or {}
    if not item or not data.get("is_playing"):
        _save_activity(row["id"], {}); return {}
    if item.get("type") == "episode":
        subtitle = (item.get("show") or {}).get("name") or "Podcast"
        images = item.get("images") or (item.get("show") or {}).get("images") or []
    else:
        subtitle = ", ".join(a.get("name", "") for a in item.get("artists") or [] if a.get("name"))
        images = (item.get("album") or {}).get("images") or []
    activity = {"type": "listening", "provider": "spotify",
        "label": "Listening on Spotify", "title": item.get("name") or "Unknown track",
        "subtitle": subtitle, "image_url": images[0].get("url") if images else None,
        "external_url": (item.get("external_urls") or {}).get("spotify"),
        "progress_ms": int(data.get("progress_ms") or 0),
        "duration_ms": int(item.get("duration_ms") or 0), "checked_utc": now}
    _save_activity(row["id"], activity, now); return activity


def _steam_activity(row):
    cached = _json_load(row["activity_json"]); now = int(time.time())
    if now - int(row["activity_checked_utc"] or 0) < 60:
        return cached
    api_key = os.environ.get("STEAM_WEB_API_KEY", "").strip()
    if not api_key:
        return cached
    response = requests.get("https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/",
        params={"key": api_key, "steamids": row["provider_user_id"]}, timeout=_HTTP_TIMEOUT)
    if not response.ok:
        return cached
    players = (response.json().get("response") or {}).get("players") or []
    if not players:
        _save_activity(row["id"], {}); return {}
    player = players[0]
    g.db.execute(text("""
        UPDATE user_connections SET display_name=:display_name,profile_url=:profile_url,
        avatar_url=:avatar_url,updated_utc=:now WHERE id=:id
    """), {"display_name": player.get("personaname") or row["display_name"],
        "profile_url": player.get("profileurl") or row["profile_url"],
        "avatar_url": player.get("avatarfull") or row["avatar_url"],
        "now": now, "id": int(row["id"])})
    game = player.get("gameextrainfo")
    if not game:
        _save_activity(row["id"], {}); return {}
    game_id = str(player.get("gameid") or "")
    activity = {"type": "playing", "provider": "steam", "label": "Playing on Steam",
        "title": game, "subtitle": "In game now",
        "image_url": f"https://cdn.cloudflare.steamstatic.com/steam/apps/{quote(game_id)}/header.jpg" if game_id else None,
        "external_url": f"https://store.steampowered.com/app/{quote(game_id)}" if game_id else row["profile_url"],
        "checked_utc": now}
    _save_activity(row["id"], activity, now); return activity


def _activity_for(row):
    if not bool(row["show_activity"]):
        return {}
    if row["provider"] == "spotify" and row["source"] == "direct":
        return _spotify_activity(row)
    if row["provider"] == "steam":
        return _steam_activity(row)
    return _json_load(row["activity_json"])


@app.before_request
def ensure_connection_storage():
    if request.path.startswith("/settings/connections") or request.path.startswith("/api/profile/"):
        _ensure_table()


@app.get("/settings/connections")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def connections_settings(v):
    rows = [_public_connection(row) for row in _connection_rows(v.id)]
    providers = []
    for key, config in PROVIDER_CONFIG.items():
        configured = _provider_configured(key)
        providers.append({"key": key, "label": config["label"], "icon": config["icon"],
            "configured": configured, "activity": bool(config.get("activity")),
            "needs": "Ready" if configured else f"Add {config.get('client_id_env')} and {config.get('client_secret_env')}"})
    return render_template("settings/connections.html", v=v, connections=rows,
        connection_providers=providers,
        manual_connection_providers=[{"key": key, **value} for key, value in MANUAL_PROVIDERS.items()],
        steam_activity_configured=bool(os.environ.get("STEAM_WEB_API_KEY", "").strip()),
        error=request.args.get("error"), msg=request.args.get("msg"))


@app.get("/settings/connections/connect/<provider>")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@auth_required
def connection_authorize(v, provider):
    return _oauth_authorize(provider.strip().lower(), v)


@app.get("/settings/connections/callback/<provider>")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@auth_required
def connection_callback(v, provider):
    provider = provider.strip().lower()
    if provider not in PROVIDER_CONFIG: abort(404)
    state_data = _consume_oauth_state(provider, request.args.get("state", ""), v.id)
    try:
        if provider == "steam":
            _steam_callback(v)
            return redirect("/settings/connections?msg=" + quote("Steam account connected."))
        if request.args.get("error"):
            raise RuntimeError(f"{_provider_label(provider)} authorization was cancelled.")
        code = request.args.get("code", "").strip()
        if not code: raise RuntimeError("The provider did not return an authorization code.")
        token_data = _exchange_oauth_code(provider, code, state_data)
        access_token = token_data["access_token"]
        identity = {"spotify": _spotify_identity, "github": _github_identity,
                    "discord": _discord_identity}[provider](access_token)
        expires = int(time.time()) + int(token_data["expires_in"]) if token_data.get("expires_in") else None
        keep_token = provider in {"spotify", "discord"}
        _upsert_connection(user_id=v.id, provider=provider,
            provider_user_id=identity["provider_user_id"], display_name=identity["display_name"],
            profile_url=identity.get("profile_url"), avatar_url=identity.get("avatar_url"),
            source="direct", access_token=access_token if keep_token else None,
            refresh_token=token_data.get("refresh_token") if keep_token else None,
            token_expires_utc=expires if keep_token else None,
            scopes=token_data.get("scope", ""), metadata=identity.get("metadata"),
            show_activity=provider == "spotify")
        imported = _import_discord_connections(v.id, access_token) if provider == "discord" else 0
        message = f"{_provider_label(provider)} account connected."
        if imported: message += f" Imported {imported} public Discord connection(s)."
        return redirect("/settings/connections?msg=" + quote(message))
    except (requests.RequestException, RuntimeError, ValueError) as exc:
        return redirect("/settings/connections?error=" + quote(str(exc)))


@app.post("/settings/connections/manual")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@auth_required
def connection_manual(v):
    provider = (request.form.get("provider") or "").strip().lower()
    handle = (request.form.get("handle") or "").strip()
    profile_url = (request.form.get("profile_url") or "").strip()
    if provider not in MANUAL_PROVIDERS: abort(400, "Unknown connection provider.")
    if not 1 <= len(handle) <= 100: abort(400, "Enter a valid account name.")
    config = MANUAL_PROVIDERS[provider]
    if config.get("template"):
        profile_url = config["template"].format(handle=quote(handle.lstrip("@"), safe="@._-"))
    elif profile_url:
        parsed = urlparse(profile_url)
        if parsed.scheme not in {"https", "http"} or not parsed.netloc:
            abort(400, "Enter a valid profile URL.")
    else: profile_url = None
    _upsert_connection(user_id=v.id, provider=provider,
        provider_user_id=handle.lower(), display_name=handle, profile_url=profile_url,
        source="manual", metadata={"verified": False}, show_activity=False)
    return redirect("/settings/connections?msg=" + quote(f"{_provider_label(provider)} added."))


@app.post("/settings/connections/<int:connection_id>/update")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@auth_required
def connection_update(v, connection_id):
    row = _connection_row(connection_id, v.id)
    if not row: abort(404)
    g.db.execute(text("""
        UPDATE user_connections SET display_on_profile=:display,
        show_activity=:show_activity,activity_checked_utc=0,updated_utc=:now
        WHERE id=:id AND user_id=:user_id
    """), {"display": request.form.get("display_on_profile") == "on",
        "show_activity": request.form.get("show_activity") == "on",
        "now": int(time.time()), "id": connection_id, "user_id": v.id})
    return redirect("/settings/connections?msg=" + quote("Connection preferences updated."))


@app.post("/settings/connections/<int:connection_id>/disconnect")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@auth_required
def connection_disconnect(v, connection_id):
    row = _connection_row(connection_id, v.id)
    if not row: abort(404)
    if row["provider"] == "discord" and row["source"] == "direct":
        g.db.execute(text("DELETE FROM user_connections WHERE user_id=:user_id AND source='discord'"), {"user_id": v.id})
    g.db.execute(text("DELETE FROM user_connections WHERE id=:id AND user_id=:user_id"),
                 {"id": connection_id, "user_id": v.id})
    return redirect("/settings/connections?msg=" + quote("Connection removed."))


@app.post("/settings/connections/discord/sync")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@auth_required
def connection_discord_sync(v):
    row = next((item for item in _connection_rows(v.id)
                if item["provider"] == "discord" and item["source"] == "direct"), None)
    if not row: return redirect("/settings/connections?error=" + quote("Connect Discord first."))
    token = _valid_access_token(row)
    if not token: return redirect("/settings/connections?error=" + quote("Discord authorization expired. Reconnect Discord."))
    try: imported = _import_discord_connections(v.id, token)
    except requests.RequestException:
        return redirect("/settings/connections?error=" + quote("Discord sync failed."))
    return redirect("/settings/connections?msg=" + quote(f"Synced {imported} public Discord connection(s)."))


@app.get("/api/profile/<username>/connections")
@limiter.limit("30 per minute", key_func=get_ID)
@auth_desired_with_logingate
def profile_connections(v, username):
    user = get_user(username, v=v, include_shadowbanned=False)
    if not user.is_visible_to(v): abort(403)
    result = []
    for row in _connection_rows(user.id, public_only=True):
        public = _public_connection(row)
        try: public["activity"] = _activity_for(row)
        except requests.RequestException: pass
        result.append(public)
    return {"data": result, "username": user.username,
            "can_manage": bool(v and v.id == user.id), "refresh_seconds": 40}
