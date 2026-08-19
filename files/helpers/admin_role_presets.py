import json
import os
import time
from pathlib import Path

from sqlalchemy import text

from files.__main__ import app, engine
from files.helpers.config.const import CURRENCY_ADMIN_PERMISSIONS, PERMS, SITE_NAME


_ADMIN_TEMPLATE = Path("files/templates/admin/administrators.html")
_MIGRATION_KEY = "admin_role_presets:v1"
_INSTALLED = False


# Explicit role capabilities. These are intentionally not generated from the
# inherited numeric permission levels: those levels bundled unrelated privacy,
# modmail, profile, and site-admin powers into low-level moderator accounts.
_TRIAL = {
    "CHAT",
    "HOLE_CREATE",
    "POST_COMMENT_MODERATION",
    "POST_COMMENT_DISTINGUISH",
}

_MODERATOR = _TRIAL | {
    "ADMIN_MOP_VISIBLE",
    "FLAGS_REMOVE",
    "NOTIFICATIONS_MODERATOR_ACTIONS",
    "POST_IN_GHOST_THREADS",
    "USER_AGENDAPOSTER",
    "USER_BAN",
    "USER_MODERATION_TOOLS_VISIBLE",
}

_ADMINISTRATOR = _MODERATOR | {
    "DOMAINS_BAN",
    "MESSAGE_BLOCKED_USERS",
    "NOTIFICATIONS_FROM_SHADOWBANNED_USERS",
    "NOTIFICATIONS_MODMAIL",
    "POST_BYPASS_REPOST_CHECKING",
    "POST_COMMENT_INFINITE_PINGS",
    "USER_BADGES",
    "USER_BLOCKS_VISIBLE",
    "USER_FOLLOWS_VISIBLE",
    "USER_LINK",
    "USER_PROFILE_IDENTITY",
    "USER_SHADOWBAN",
    "USER_TITLE_CHANGE",
    "USER_VOTERS_VISIBLE",
    "VIEW_ALTS",
    "VIEW_ALT_VOTES",
    "VIEW_LAST_ACTIVE",
    "VIEW_MODMAIL",
    "VIEW_PRIVATE_PROFILES",
    "VIEW_VOTE_BUTTONS_ON_USER_PAGE",
}

_SENIOR = _ADMINISTRATOR | {
    "ADMIN_ACTIONS_REVERT",
    "APPS_MODERATION",
    "BOT_CONTROLS",
    "IGNORE_BADGE_BLACKLIST",
    "LOTTERY_VIEW_PARTICIPANTS",
    "MODERATE_PENDING_SUBMITTED_ASSETS",
    "MODS_EVERY_HOLE",
    "NOTIFICATIONS_HOLE_CREATION",
    "POST_EDITING",
    "PROGSTACK",
    "SEE_GHOST_VOTES",
    "SITE_SETTINGS_SIDEBARS_BANNERS_BADGES",
    "UNDO_AWARD_PINS",
    "UPDATE_ASSETS",
    "USER_BLACKLIST",
    "USER_PROFILE_ASSETS",
    "USER_PROFILE_EDIT",
    "VIEW_ACTIVE_USERS",
    "VIEW_PENDING_SUBMITTED_HATS",
    "VIEW_PENDING_SUBMITTED_MARSEYS",
}

_ROLE_PERMISSIONS = {
    "trial": _TRIAL,
    "moderator": _MODERATOR,
    "administrator": _ADMINISTRATOR,
    "senior": _SENIOR,
}

_ROLE_DEFINITIONS = {
    "trial": {
        "label": "Trial Moderator",
        "tier": 1,
        "description": "Probationary content moderation only: remove/approve/pin/distinguish posts and comments, plus chat timeout controls.",
    },
    "moderator": {
        "label": "Moderator",
        "tier": 2,
        "description": "Day-to-day moderation: Trial tools plus bans, Chud/mute actions, report cleanup, and routine moderator notifications. No modmail, sessions, profile-admin, or site-admin access.",
    },
    "administrator": {
        "label": "Administrator",
        "tier": 3,
        "description": "Advanced moderation and investigations: shadowbans, modmail, alts/vote analysis, badges/flair, forced usernames, private-profile visibility, and domain safety tools.",
    },
    "senior": {
        "label": "Senior Administrator",
        "tier": 4,
        "description": "Operations role: Administrator tools plus session/activity visibility, profile/bot administration, action reverts, app moderation, and emote/hat/banner/sidebar asset management.",
    },
}


def _atomic_write(path: Path, content: str) -> None:
    temp_path = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temp_path.write_text(content, encoding="utf-8")
    os.replace(temp_path, path)


def _filtered_permissions(permission_management, preset):
    active = permission_management.active_permission_names()
    if preset == "head":
        return sorted(active - CURRENCY_ADMIN_PERMISSIONS)
    if preset == "head_economy":
        return sorted(active)
    return sorted(_ROLE_PERMISSIONS[preset] & active)


def _configure_presets(permission_management, admin_routes):
    head_level = permission_management.HEAD_ADMIN_LEVEL_V2
    presets = {}
    for key in ("trial", "moderator", "administrator", "senior"):
        definition = dict(_ROLE_DEFINITIONS[key])
        definition["level"] = definition["tier"]
        presets[key] = definition
    presets["head"] = {
        "label": "Head Administrator",
        "level": head_level,
        "tier": 5,
        "description": "Full TOC administration and every active non-economy permission, including site settings, security controls, age-verification administration, DM audits, and all Admin Home controls.",
    }
    presets["head_economy"] = {
        "label": "Head Administrator + Economy",
        "level": head_level,
        "tier": 6,
        "description": "Owner-level access: everything Head Administrator has, plus unlimited-spending and Wishcoin/Wishbux economy authority.",
    }
    admin_routes.ADMIN_PRESETS.clear()
    admin_routes.ADMIN_PRESETS.update(presets)
    admin_routes._preset_permissions = lambda preset: _filtered_permissions(permission_management, preset)


def _patch_admin_management_template():
    source = _ADMIN_TEMPLATE.read_text(encoding="utf-8")
    original = source

    source = source.replace(
        '<span class="admin-role-level">Level {{preset.level}}</span>',
        '<span class="admin-role-level">Tier {{preset.tier}}</span>',
    )

    old_summary = '<div class="admin-role-summary">{% if admin.has_all_admin_permissions %}EVERYTHING{% else %}Level {{admin.admin_level}} - {{admin.admin_permission_count or 0}} permissions{% endif %}</div>'
    new_summary = '<div class="admin-role-summary">{% set detected_preset = admin_preset_key(admin) %}{% if detected_preset %}{{admin_presets[detected_preset].label}}{% if not admin.has_all_admin_permissions %} · {{admin.admin_permission_count or 0}} permissions{% endif %}{% else %}Custom access · {{admin.admin_permission_count or 0}} permissions{% endif %}</div>'
    if old_summary in source:
        source = source.replace(old_summary, new_summary, 1)

    old_current = '{% set current_preset = "moderator" %}\n\t\t\t\t\t{% if admin.has_all_admin_permissions %}{% set current_preset = "head_economy" if (admin.has_permission("ADMIN_UNLIMITED_SPENDING") and admin.has_permission("ADMIN_GRANT_CURRENCY") and admin.has_permission("ADMIN_REMOVE_CURRENCY")) else "head" %}{% elif admin.admin_level >= 4 %}{% set current_preset = "senior" %}{% elif admin.admin_level >= 3 %}{% set current_preset = "administrator" %}{% endif %}'
    new_current = '{% set current_preset = admin_preset_key(admin) %}'
    if old_current in source:
        source = source.replace(old_current, new_current, 1)

    if source != original:
        _atomic_write(_ADMIN_TEMPLATE, source)


def _migrate_legacy_presets(permission_management):
    """Rebalance accounts that still exactly match the old level-generated presets."""
    active = permission_management.active_permission_names()
    # This permission was intentionally hidden when the old presets were built.
    legacy_active = active - {"SITE_SETTINGS_SIDEBARS_BANNERS_BADGES"}
    legacy_sets = {
        1: {name for name in legacy_active if name not in CURRENCY_ADMIN_PERMISSIONS and int(PERMS[name]) <= 1},
        3: {name for name in legacy_active if name not in CURRENCY_ADMIN_PERMISSIONS and int(PERMS[name]) <= 3},
        4: {name for name in legacy_active if name not in CURRENCY_ADMIN_PERMISSIONS and int(PERMS[name]) <= 4},
    }
    level_to_role = {1: "moderator", 3: "administrator", 4: "senior"}

    with engine.begin() as connection:
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS persistent_site_content (
                content_key VARCHAR(255) PRIMARY KEY,
                content TEXT NOT NULL,
                updated_utc BIGINT NOT NULL,
                updated_by VARCHAR(255)
            )
        """))
        if connection.execute(
            text("SELECT 1 FROM persistent_site_content WHERE content_key = :key"),
            {"key": _MIGRATION_KEY},
        ).scalar():
            return

        rows = connection.execute(text("""
            SELECT id, admin_level, admin_permissions
            FROM users
            WHERE admin_level > 0 AND admin_level < :head_level
        """), {"head_level": permission_management.HEAD_ADMIN_LEVEL_V2}).mappings().all()

        migrated = 0
        for row in rows:
            try:
                stored = json.loads(row["admin_permissions"] or "[]")
                current = set(stored) if isinstance(stored, list) else set()
            except (TypeError, ValueError):
                current = set()

            role = None
            level = int(row["admin_level"] or 0)
            if current:
                for old_level, old_permissions in legacy_sets.items():
                    if current == old_permissions:
                        role = level_to_role[old_level]
                        break
            elif level in level_to_role:
                # Old Make Admin created a numeric-only role; treat level 1 as a
                # normal Moderator rather than silently keeping the broad L1 bundle.
                role = level_to_role[level]

            if not role:
                continue

            permissions = _filtered_permissions(permission_management, role)
            new_level = max((int(PERMS[name]) for name in permissions), default=1)
            connection.execute(text("""
                UPDATE users
                SET admin_permissions = :permissions, admin_level = :admin_level
                WHERE id = :user_id
            """), {
                "permissions": json.dumps(permissions),
                "admin_level": new_level,
                "user_id": row["id"],
            })
            migrated += 1

        connection.execute(text("""
            INSERT INTO persistent_site_content (content_key, content, updated_utc, updated_by)
            VALUES (:key, :content, :updated_utc, :updated_by)
            ON CONFLICT (content_key) DO NOTHING
        """), {
            "key": _MIGRATION_KEY,
            "content": json.dumps({"migrated": migrated, "roles": list(_ROLE_PERMISSIONS)}),
            "updated_utc": int(time.time()),
            "updated_by": "automatic role preset rebalance",
        })


def _preset_key_for_user(permission_management, user):
    if user.has_all_admin_permissions:
        return "head_economy" if all(user.has_permission(name) for name in CURRENCY_ADMIN_PERMISSIONS) else "head"
    current = set(user.admin_permission_names)
    for key in ("trial", "moderator", "administrator", "senior"):
        if current == set(_filtered_permissions(permission_management, key)):
            return key
    return None


def install_admin_role_presets():
    global _INSTALLED
    if _INSTALLED or SITE_NAME != "Obsession":
        return

    from files.helpers import admin_permission_management as permission_management
    import files.routes.admin as admin_routes

    # Banner/sidebar management is a live TOC capability and belongs to Senior,
    # so expose it as a real grantable permission instead of hiding it as legacy.
    permission_management._TOC_HIDDEN_PERMISSIONS.discard("SITE_SETTINGS_SIDEBARS_BANNERS_BADGES")
    permission_management._META["SITE_SETTINGS_SIDEBARS_BANNERS_BADGES"] = (
        "assets",
        "Manage banners & sidebar art",
        "Approve, remove, and manage site banner/sidebar community assets without granting general site-setting toggles.",
    )
    permission_management._CATALOG = None

    _configure_presets(permission_management, admin_routes)
    app.jinja_env.globals["admin_preset_key"] = lambda user: _preset_key_for_user(permission_management, user)
    _patch_admin_management_template()
    _migrate_legacy_presets(permission_management)
    _INSTALLED = True


@app.before_request
def install_admin_role_presets_before_first_request():
    # admin_permission_management is installed near the end of route startup.
    # Waiting until the first request guarantees its wrappers are already in
    # place, while still applying these presets before any admin page is served.
    install_admin_role_presets()
