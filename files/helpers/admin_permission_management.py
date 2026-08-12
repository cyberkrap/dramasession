import json
import os
import re
import time
from pathlib import Path

import fcntl
from flask import abort, g
from sqlalchemy import text

from files.__main__ import engine
from files.classes import ModAction
from files.helpers.config import const as const_module
from files.helpers.config.const import CURRENCY_ADMIN_PERMISSIONS, PERMS, SITE_NAME


OLD_HEAD_ADMIN_LEVEL = 5
HEAD_ADMIN_LEVEL_V2 = max(int(requirement) for requirement in PERMS.values()) + 1
_MIGRATION_KEY = f"admin_permissions:head_level_v2:{SITE_NAME}"
_TEMPLATE_PATH = Path("files/templates/admin/administrators.html")
_SOURCE_LOCK = "/tmp/obsession-admin-permission-management.lock"

_PERMISSION_PATTERN = re.compile(
    r"""(?:PERMS\s*\[\s*['\"]([A-Z0-9_]+)['\"]\s*\]|has_permission\(\s*['\"]([A-Z0-9_]+)['\"]\s*\))"""
)

_TOC_HIDDEN_PERMISSIONS = {
    "ADMIN_HOME_VISIBLE",
    "NOTIFICATIONS_REDDIT",
    "NOTIFICATIONS_SPECIFIC_WPD_COMMENTS",
    "NOTIFICATIONS_HOLE_INACTIVITY_DELETION",
    "POST_TO_CHANGELOG",
    "POST_TO_POLL_THREAD",
    "SITE_SETTINGS_SIDEBARS_BANNERS_BADGES",
    "SITE_SETTINGS_SNAPPY_QUOTES",
    "VIEW_CHUDRAMA",
    "VIEW_CLUB",
}

_SECTION_ORDER = (
    ("moderation", "Posts, comments & chat"),
    ("users", "Users & safety"),
    ("messages", "Messages & oversight"),
    ("boards", "Boards & community"),
    ("assets", "Assets & profiles"),
    ("site", "Site administration"),
    ("gambling", "Apps, lottery & gambling"),
    ("economy", "Economy"),
)

_META = {
    "CHAT": ("moderation", "Moderate public chat", "Use public-chat moderation controls, including timeouts and reversals."),
    "POST_COMMENT_MODERATION": ("moderation", "Moderate posts & comments", "Remove, approve, pin, inspect, and otherwise moderate site content."),
    "POST_COMMENT_DISTINGUISH": ("moderation", "Distinguish comments", "Mark comments as an official administrator response."),
    "POST_EDITING": ("moderation", "Edit any post", "Edit posts that were created by other users."),
    "POST_BYPASS_REPOST_CHECKING": ("moderation", "Bypass repost checks", "Create posts without the normal repost-detection restriction."),
    "POST_COMMENT_INFINITE_PINGS": ("moderation", "Bypass mention limits", "Use more mentions than normal post/comment ping limits allow."),
    "POST_IN_GHOST_THREADS": ("moderation", "Post in ghost threads", "Post or comment in ghost threads regardless of the normal gate."),
    "FLAGS_REMOVE": ("moderation", "Resolve reports", "Remove report flags after moderation review."),
    "BUY_GHOST_AWARD": ("moderation", "Use the Ghost award", "Purchase or use the privileged Ghost award."),
    "UNDO_AWARD_PINS": ("moderation", "Undo award-created pins", "Remove pins created by pin-style awards."),
    "SEE_GHOST_VOTES": ("moderation", "View ghost-content votes", "Inspect vote details on ghost content."),
    "BLACKJACK_NOTIFICATIONS": ("moderation", "Receive blackjack alerts", "Receive the site's blackjack moderation or automation notifications."),

    "USER_BAN": ("users", "Ban and unban users", "Use account ban and unban actions."),
    "USER_SHADOWBAN": ("users", "Shadowban users", "Apply and remove shadowbans and see shadowbanned-account moderation state."),
    "USER_AGENDAPOSTER": ("users", "Restrict users", "Apply and remove the site's restricted-user mode."),
    "PROGSTACK": ("users", "Apply progressive stack", "Apply progressive-stack moderation to posts, comments, and users."),
    "USER_BLACKLIST": ("users", "Manage restricted-board blacklist", "Blacklist or unblacklist members from restricted boards."),
    "USER_BADGES": ("users", "Grant or remove badges", "Manage normal profile badges on user accounts."),
    "IGNORE_BADGE_BLACKLIST": ("users", "Grant protected badges", "Bypass the badge blacklist when granting badges."),
    "USER_TITLE_CHANGE": ("users", "Change user titles", "Edit another user's profile title or flair."),
    "USER_LINK": ("users", "Link alternate accounts", "Link, delink, and relink known alternate accounts."),
    "VIEW_ALTS": ("users", "View alternate accounts", "See alt-account graphs and associated account data."),
    "VIEW_ALT_VOTES": ("users", "Analyze alt voting", "Compare voting overlap between accounts."),
    "VIEW_ACTIVE_USERS": ("users", "View active-session lists", "See currently logged-in and recently logged-out users."),
    "VIEW_LAST_ACTIVE": ("users", "View last-active times", "See private last-active timestamps on profiles."),
    "VIEW_PRIVATE_PROFILES": ("users", "View private profiles", "Open profiles that are private to normal members."),
    "USER_BLOCKS_VISIBLE": ("users", "View block relationships", "Inspect who a user blocks or is blocked by where supported."),
    "USER_FOLLOWS_VISIBLE": ("users", "View follow relationships", "Inspect follower and following lists regardless of normal visibility."),
    "USER_VOTERS_VISIBLE": ("users", "View user voting history", "Inspect supporter, critic, and voting-history views on profiles."),
    "VIEW_VOTE_BUTTONS_ON_USER_PAGE": ("users", "Use profile voting controls", "Keep voting controls available on user and profile views."),
    "USER_MODERATION_TOOLS_VISIBLE": ("users", "Use profile moderation tools", "Show and use profile moderation tools such as resetting profile media."),
    "ADMIN_MOP_VISIBLE": ("users", "Show administrator identity", "Display the administrator indicator where admin identity is exposed."),

    "VIEW_MODMAIL": ("messages", "View modmail", "Open and review member-to-staff modmail threads."),
    "NOTIFICATIONS_MODMAIL": ("messages", "Receive modmail notifications", "Receive notifications when new modmail activity needs staff attention."),
    "VIEW_DM_IMAGES": ("messages", "View DM image audit", "Open the administrator audit of images actually sent in DMs and modmail."),
    "MESSAGE_BLOCKED_USERS": ("messages", "Message through blocks", "Allow staff messaging when the normal user-block check would reject it."),
    "NOTIFICATIONS_FROM_SHADOWBANNED_USERS": ("messages", "Receive shadowbanned-user notifications", "Allow notifications originating from shadowbanned accounts."),
    "NOTIFICATIONS_MODERATOR_ACTIONS": ("messages", "Receive moderation-log notifications", "See new moderator actions in the notification stream."),
    "NOTIFICATIONS_HOLE_CREATION": ("messages", "Receive board-creation notifications", "Receive notifications when new boards are created."),

    "HOLE_CREATE": ("boards", "Create boards", "Create a new community board."),
    "MODS_EVERY_HOLE": ("boards", "Moderate every board", "Treat this administrator as a moderator of every board."),
    "DOMAINS_BAN": ("boards", "Ban domains", "Add or remove domains from the site-wide banned-domain list."),

    "VIEW_PENDING_SUBMITTED_MARSEYS": ("assets", "View pending emote previews", "View image previews for emotes that have not been approved yet."),
    "VIEW_PENDING_SUBMITTED_HATS": ("assets", "View pending hat submissions", "View pending hat submissions and their protected assets."),
    "MODERATE_PENDING_SUBMITTED_ASSETS": ("assets", "Manage submitted emotes & hats", "Approve, reject, edit, delete, and categorize submitted community emotes and hats."),
    "UPDATE_ASSETS": ("assets", "Manage approved hats & assets", "Edit or delete approved hats and other administrator-managed assets."),

    "ADMIN_ADD": ("site", "Manage administrators", "Open administrator management and add or change administrator access."),
    "ADMIN_REMOVE": ("site", "Remove administrators", "Remove administrator access from manageable accounts."),
    "ADMIN_ACTIONS_REVERT": ("site", "Revert moderator actions", "Use moderation-log rollback and revert tools."),
    "EDIT_RULES": ("site", "Edit site rules", "Edit the persistent rules and sidebar rules content."),
    "SITE_SETTINGS": ("site", "Manage site settings & community assets", "Change site settings, default signup assets, and review banner or sidebar submissions."),
    "SITE_SETTINGS_UNDER_ATTACK": ("site", "Control Under Attack mode", "Enable or disable the site's Cloudflare Under Attack protection."),
    "SITE_CACHE_PURGE_CDN": ("site", "Purge CDN cache", "Clear the site's Cloudflare or CDN cache."),
    "SITE_BYPASS_READ_ONLY_MODE": ("site", "Bypass read-only mode", "Keep write actions available while the site is read-only."),
    "SITE_BYPASS_UNDER_SIEGE_MODE": ("site", "Bypass under-siege restrictions", "Bypass restrictions applied while the site is in under-siege mode."),
    "SITE_WARN_ON_INVALID_AUTH": ("site", "Log failed administrator sign-ins", "Enable failed-login security logging for this administrator account."),
    "APPS_MODERATION": ("site", "Moderate API applications", "Approve, reject, revoke, and inspect registered API applications."),
    "VIEW_PATRONS": ("site", "View patron records", "Open administrator-only patron and member-support records."),

    "LOTTERY_VIEW_PARTICIPANTS": ("gambling", "View lottery participants", "See lottery participant and ticket details."),
    "LOTTERY_ADMIN": ("gambling", "Administer the lottery", "Use privileged lottery administration actions."),
    "POST_BETS": ("gambling", "Create post bets", "Create or manage betting actions attached to posts."),
    "POST_BETS_DISTRIBUTE": ("gambling", "Distribute post-bet winnings", "Resolve post bets and distribute winnings."),

    "ADMIN_UNLIMITED_SPENDING": ("economy", "Unlimited Spending", "Use purchases and wagers without deducting the administrator's displayed balance."),
    "ADMIN_GRANT_CURRENCY": ("economy", "Grant Wishcoins / Wishbux", "Add site currency to member accounts and record the action."),
    "ADMIN_REMOVE_CURRENCY": ("economy", "Remove Wishcoins / Wishbux", "Remove site currency from member accounts and record the action."),
}

_CATALOG = None


def _discover_active_permission_names():
    roots = (Path("files/routes"), Path("files/helpers"), Path("files/classes"), Path("files/templates"))
    active = set(CURRENCY_ADMIN_PERMISSIONS)
    skip_paths = {
        Path("files/helpers/config/const.py"),
        Path("files/helpers/admin_permission_management.py"),
        Path("files/templates/admin/administrators.html"),
    }
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if path.suffix not in {".py", ".html"} or path in skip_paths:
                continue
            try:
                source = path.read_text(encoding="utf-8")
            except OSError:
                continue
            for match in _PERMISSION_PATTERN.finditer(source):
                name = match.group(1) or match.group(2)
                if name in PERMS:
                    active.add(name)
    active.difference_update(_TOC_HIDDEN_PERMISSIONS)
    return active


def _fallback_label(name):
    return name.replace("HOLE", "BOARD").replace("MARSEYS", "EMOTES").replace("_", " ").title()


def _build_catalog():
    active = _discover_active_permission_names()
    rank = {key: index for index, (key, _) in enumerate(_SECTION_ORDER)}
    catalog = []
    for name in active:
        section, label, description = _META.get(
            name,
            ("site", _fallback_label(name), "This capability is checked by current TOC code."),
        )
        catalog.append({
            "name": name,
            "label": label,
            "description": description,
            "level": int(PERMS[name]),
            "section": section,
            "currency": name in CURRENCY_ADMIN_PERMISSIONS,
        })
    catalog.sort(key=lambda item: (rank.get(item["section"], 999), item["label"].lower(), item["name"]))
    return catalog


def permission_catalog():
    global _CATALOG
    if _CATALOG is None:
        _CATALOG = _build_catalog()
    return _CATALOG


def active_permission_names():
    return {item["name"] for item in permission_catalog()}


def permission_groups():
    catalog = permission_catalog()
    groups = []
    for key, label in _SECTION_ORDER:
        permissions = [item for item in catalog if item["section"] == key]
        if permissions:
            groups.append({"key": key, "label": label, "permissions": permissions})
    return groups


def _migrate_existing_heads():
    with engine.begin() as connection:
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS persistent_site_content (
                content_key VARCHAR(255) PRIMARY KEY,
                content TEXT NOT NULL,
                updated_utc BIGINT NOT NULL,
                updated_by VARCHAR(255)
            )
        """))
        exists = connection.execute(
            text("SELECT 1 FROM persistent_site_content WHERE content_key = :key"),
            {"key": _MIGRATION_KEY},
        ).scalar()
        if exists:
            return
        result = connection.execute(
            text("""
                UPDATE users
                SET admin_level = :new_level
                WHERE admin_level >= :old_level
                  AND admin_level < :new_level
            """),
            {"old_level": OLD_HEAD_ADMIN_LEVEL, "new_level": HEAD_ADMIN_LEVEL_V2},
        )
        connection.execute(
            text("""
                INSERT INTO persistent_site_content
                    (content_key, content, updated_utc, updated_by)
                VALUES (:key, :content, :updated_utc, :updated_by)
                ON CONFLICT (content_key) DO NOTHING
            """),
            {
                "key": _MIGRATION_KEY,
                "content": json.dumps({"migrated": int(result.rowcount or 0), "head_level": HEAD_ADMIN_LEVEL_V2}),
                "updated_utc": int(time.time()),
                "updated_by": "automatic admin permission migration",
            },
        )


def _set_head_level_globals(admin_routes):
    from files.classes import user as user_module
    from files.helpers import production_bootstrap as bootstrap_module

    const_module.HEAD_ADMIN_LEVEL = HEAD_ADMIN_LEVEL_V2
    user_module.HEAD_ADMIN_LEVEL = HEAD_ADMIN_LEVEL_V2
    admin_routes.HEAD_ADMIN_LEVEL = HEAD_ADMIN_LEVEL_V2
    bootstrap_module.HEAD_ADMIN_LEVEL = HEAD_ADMIN_LEVEL_V2
    admin_routes.ADMIN_PRESETS["head"]["level"] = HEAD_ADMIN_LEVEL_V2
    admin_routes.ADMIN_PRESETS["head_economy"]["level"] = HEAD_ADMIN_LEVEL_V2
    admin_routes.ADMIN_PRESETS["head"]["description"] = "Every active TOC admin permission except delegated economy access."
    admin_routes.ADMIN_PRESETS["head_economy"]["description"] = "Full TOC administrator access plus economy permissions and economy delegation."


def _preset_permissions(admin_routes, preset):
    config = admin_routes.ADMIN_PRESETS[preset]
    active = active_permission_names()
    if preset in {"head", "head_economy"}:
        permissions = sorted(active - CURRENCY_ADMIN_PERMISSIONS)
    else:
        permissions = sorted(
            name for name in active
            if name not in CURRENCY_ADMIN_PERMISSIONS and int(PERMS[name]) <= int(config["level"])
        )
    if preset == "head_economy":
        permissions.extend(sorted(CURRENCY_ADMIN_PERMISSIONS))
    return sorted(set(permissions))


def _save_admin_permissions(admin_routes, actor, user, permissions):
    admin_routes._require_head_administrator(actor)
    if user.id == actor.id or not actor.can_manage_admin(user):
        abort(403)

    active = active_permission_names()
    permissions = sorted({name for name in permissions if name in active})
    selected = set(permissions)

    if selected & CURRENCY_ADMIN_PERMISSIONS and not actor.has_admin_economy_permissions:
        abort(403, "Only a Head Administrator + Economy account can delegate economy permissions.")

    for permission in permissions:
        if not actor.has_permission(permission):
            abort(403, "You cannot grant a permission you do not have.")

    head_permissions = set(_preset_permissions(admin_routes, "head"))
    is_head_role = bool(head_permissions) and head_permissions.issubset(selected)
    if is_head_role and not actor.has_admin_economy_permissions:
        abort(403, "Head Administrator roles can only be granted by Head Administrator + Economy.")

    user.admin_permissions = json.dumps(permissions)
    user.admin_level = HEAD_ADMIN_LEVEL_V2 if is_head_role else max((int(PERMS[name]) for name in permissions), default=1)
    g.db.add(user)
    g.db.add(ModAction(kind="admin_permissions", user_id=actor.id, target_user_id=user.id))


def _atomic_write(path, content):
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_text(content, encoding="utf-8")
    os.replace(temporary, path)


def _patch_admin_template():
    if not _TEMPLATE_PATH.exists():
        return
    with open(_SOURCE_LOCK, "w", encoding="utf-8") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        source = _TEMPLATE_PATH.read_text(encoding="utf-8")
        original = source

        old_gate = "{% if preset_key not in ('head', 'head_economy') or (preset_key == 'head' and v.has_admin_economy_permissions) %}"
        new_gate = "{% if preset_key not in ('head', 'head_economy') or v.has_admin_economy_permissions %}"
        source = source.replace(old_gate, new_gate)

        start_marker = '\t\t\t\t\t\t\t\t\t<p class="text-muted small">Only permissions you already hold can be granted. Economy permissions are restricted to the head administrator.</p>'
        end_marker = '\t\t\t\t\t\t\t\t\t<button type="submit" class="btn btn-primary">Save custom access</button>'
        start = source.find(start_marker)
        end = source.find(end_marker, start + 1) if start >= 0 else -1
        if start < 0 or end < 0:
            raise RuntimeError("Could not locate administrator custom-permission controls")

        replacement = """\t\t\t\t\t\t\t\t\t<p class="text-muted small">Only permissions you already hold can be granted. This list comes from permissions used by current TOC code; retired rDrama/WPD-only controls are omitted.</p>
\t\t\t\t\t\t\t\t\t{% for group in permission_groups if group.key != 'economy' %}
\t\t\t\t\t\t\t\t\t\t<h4 class="mt-3 mb-1">{{group.label}}</h4>
\t\t\t\t\t\t\t\t\t\t<div class="admin-permission-grid">
\t\t\t\t\t\t\t\t\t\t\t{% for permission in group.permissions %}
\t\t\t\t\t\t\t\t\t\t\t\t<label class="admin-permission-option" title="{{permission.description}}">
\t\t\t\t\t\t\t\t\t\t\t\t\t<input type="checkbox" name="permissions" value="{{permission.name}}" {% if admin.has_permission(permission.name) %}checked{% endif %}>
\t\t\t\t\t\t\t\t\t\t\t\t\t<span><strong>{{permission.label}}</strong><br><span class="text-muted">{{permission.description}}</span></span>
\t\t\t\t\t\t\t\t\t\t\t\t\t<small>L{{permission.level}}</small>
\t\t\t\t\t\t\t\t\t\t\t\t</label>
\t\t\t\t\t\t\t\t\t\t\t{% endfor %}
\t\t\t\t\t\t\t\t\t\t</div>
\t\t\t\t\t\t\t\t\t{% endfor %}
\t\t\t\t\t\t\t\t\t{% if v.has_admin_economy_permissions %}
\t\t\t\t\t\t\t\t\t\t{% for group in permission_groups if group.key == 'economy' %}
\t\t\t\t\t\t\t\t\t\t\t<div class="admin-economy-permissions">
\t\t\t\t\t\t\t\t\t\t\t\t<h4>{{group.label}}</h4>
\t\t\t\t\t\t\t\t\t\t\t\t<p class="text-muted small">You have full Economy authority, so you can delegate or revoke these permissions on other administrator accounts.</p>
\t\t\t\t\t\t\t\t\t\t\t\t<div class="admin-permission-grid">
\t\t\t\t\t\t\t\t\t\t\t\t\t{% for permission in group.permissions %}
\t\t\t\t\t\t\t\t\t\t\t\t\t\t<label class="admin-permission-option" title="{{permission.description}}">
\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t<input type="checkbox" name="permissions" value="{{permission.name}}" {% if admin.has_permission(permission.name) %}checked{% endif %}>
\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t<span><strong>{{permission.label}}</strong><br><span class="text-muted">{{permission.description}}</span></span>
\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t<small>Economy</small>
\t\t\t\t\t\t\t\t\t\t\t\t\t\t</label>
\t\t\t\t\t\t\t\t\t\t\t\t\t{% endfor %}
\t\t\t\t\t\t\t\t\t\t\t\t</div>
\t\t\t\t\t\t\t\t\t\t\t</div>
\t\t\t\t\t\t\t\t\t\t{% endfor %}
\t\t\t\t\t\t\t\t\t{% endif %}
"""
        source = source[:start] + replacement + source[end:]

        old_reference = """\t\t\t{% for group in permission_groups %}
\t\t\t\t<div class="admin-reference-level"><h3>Level {{group.level}}</h3><div class="admin-chip-list">{% for permission_name in group.permissions %}<span class="admin-permission-chip{% if permission_name in currency_permissions %} admin-permission-chip-economy{% endif %}">{{permission_name.replace('_', ' ').title()}}</span>{% endfor %}</div></div>
\t\t\t{% endfor %}"""
        new_reference = """\t\t\t{% for group in permission_groups %}
\t\t\t\t<div class="admin-reference-level"><h3>{{group.label}}</h3><div class="admin-chip-list">{% for permission in group.permissions %}<span class="admin-permission-chip{% if permission.currency %} admin-permission-chip-economy{% endif %}" title="{{permission.description}}">{{permission.label}} · L{{permission.level}}</span>{% endfor %}</div></div>
\t\t\t{% endfor %}"""
        if old_reference not in source:
            raise RuntimeError("Could not locate administrator permission reference")
        source = source.replace(old_reference, new_reference, 1)
        source = source.replace(
            "Higher levels include the permissions listed at lower levels. Economy access is always explicit.",
            "Permissions are grouped by the current TOC capability they control. Economy access is always explicit and delegatable only by Head Administrator + Economy.",
        )

        if old_gate in source:
            raise RuntimeError("Administrator preset gate repair was incomplete")
        if source != original:
            _atomic_write(_TEMPLATE_PATH, source)


def install_admin_permission_management():
    if SITE_NAME != "Obsession":
        return
    import files.routes.admin as admin_routes

    _migrate_existing_heads()
    _set_head_level_globals(admin_routes)
    admin_routes._permission_groups = permission_groups
    admin_routes._preset_permissions = lambda preset: _preset_permissions(admin_routes, preset)
    admin_routes._save_admin_permissions = lambda actor, user, permissions: _save_admin_permissions(admin_routes, actor, user, permissions)
    _patch_admin_template()
