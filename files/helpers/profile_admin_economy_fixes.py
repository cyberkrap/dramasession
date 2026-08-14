import os
import tempfile
from pathlib import Path

from files.helpers.config.const import PERMS, PermissionRequirement


_PROFILE_ADMIN_PERMISSIONS = {
    "USER_PROFILE_IDENTITY": 1,
    "USER_PROFILE_EDIT": 1,
    "USER_PROFILE_ASSETS": 1,
    "BOT_CONTROLS": 1,
}

_PROFILE_ADMIN_PERMISSION_META = {
    "USER_PROFILE_IDENTITY": (
        "users",
        "Manage usernames & reserved names",
        "Force-change usernames and release a user's reserved previous username.",
    ),
    "USER_PROFILE_EDIT": (
        "assets",
        "Edit profile bio & CSS",
        "Edit or wipe another user's biography and manage their profile CSS.",
    ),
    "USER_PROFILE_ASSETS": (
        "assets",
        "Manage profile media & anthem",
        "Upload or reset profile pictures, banners, backgrounds, and remove profile anthems.",
    ),
    "BOT_CONTROLS": (
        "users",
        "Manage bot controls",
        "Enable or disable bot accounts and set their daily post/comment limits.",
    ),
}


def install_profile_admin_permissions() -> None:
    for name, level in _PROFILE_ADMIN_PERMISSIONS.items():
        if name not in PERMS:
            PERMS[name] = PermissionRequirement(name, level)


def install_profile_admin_permission_metadata(permission_management) -> None:
    permission_management._META.update(_PROFILE_ADMIN_PERMISSION_META)
    permission_management._CATALOG = None


def _atomic_write(path: Path, content: str) -> None:
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(content)
        os.replace(temporary, path)
    finally:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass


def _replace_once(source: str, old: str, new: str, label: str) -> str:
    if new in source:
        return source
    if old not in source:
        raise RuntimeError(f"Could not locate {label}")
    return source.replace(old, new, 1)


def _patch(path_string: str, replacements) -> None:
    path = Path(path_string)
    source = path.read_text(encoding="utf-8")
    original = source
    for old, new, label in replacements:
        source = _replace_once(source, old, new, label)
    if source != original:
        _atomic_write(path, source)


def patch_profile_admin_economy_sources() -> None:
    # Make the administrator-management catalog describe these permissions before
    # that module is imported and freezes its catalog.
    _patch("files/helpers/admin_permission_management.py", (
        (
            "_META = {\n",
            "_META = {\n"
            "    \"USER_PROFILE_IDENTITY\": (\"users\", \"Manage usernames & reserved names\", \"Force-change usernames and release a user's reserved previous username.\"),\n"
            "    \"USER_PROFILE_EDIT\": (\"assets\", \"Edit profile bio & CSS\", \"Edit or wipe another user's biography and manage their profile CSS.\"),\n"
            "    \"USER_PROFILE_ASSETS\": (\"assets\", \"Manage profile media & anthem\", \"Upload or reset profile pictures, banners, backgrounds, and remove profile anthems.\"),\n"
            "    \"BOT_CONTROLS\": (\"users\", \"Manage bot controls\", \"Enable or disable bot accounts and set their daily post/comment limits.\"),\n",
            "profile admin permission metadata",
        ),
    ))

    # Profile actions get real granular permissions and forced renames reserve
    # the name that was actually primary immediately before the admin change.
    _patch("files/routes/profile_admin_tools.py", (
        (
            '@app.post("/admin/profile/<int:user_id>/bot-controls")\n@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)\n@admin_level_required(PERMS["USER_MODERATION_TOOLS_VISIBLE"])',
            '@app.post("/admin/profile/<int:user_id>/bot-controls")\n@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)\n@admin_level_required(PERMS["BOT_CONTROLS"])',
            "bot controls permission",
        ),
        (
            '@app.post("/admin/profile/<int:user_id>/username")\n@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)\n@admin_level_required(PERMS["USER_MODERATION_TOOLS_VISIBLE"])',
            '@app.post("/admin/profile/<int:user_id>/username")\n@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)\n@admin_level_required(PERMS["USER_PROFILE_IDENTITY"])',
            "forced username permission",
        ),
        (
            '    old_name = user.username\n    user.username = new_name\n    g.db.add(user)\n    for identifier in (user.id, old_name, user.original_username, new_name):',
            '    old_name = user.username\n    old_reserved = user.original_username\n    user.original_username = old_name\n    user.username = new_name\n    user.name_changed_utc = int(time.time())\n    g.db.add(user)\n    for identifier in (user.id, old_name, old_reserved, new_name):',
            "forced username reservation semantics",
        ),
        (
            '@app.post("/admin/profile/<int:user_id>/wipe-reserved-username")\n@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)\n@admin_level_required(PERMS["USER_MODERATION_TOOLS_VISIBLE"])',
            '@app.post("/admin/profile/<int:user_id>/wipe-reserved-username")\n@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)\n@admin_level_required(PERMS["USER_PROFILE_IDENTITY"])',
            "reserved username wipe permission",
        ),
        (
            '@app.post("/admin/profile/<int:user_id>/bio")\n@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)\n@admin_level_required(PERMS["USER_MODERATION_TOOLS_VISIBLE"])',
            '@app.post("/admin/profile/<int:user_id>/bio")\n@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)\n@admin_level_required(PERMS["USER_PROFILE_EDIT"])',
            "profile bio permission",
        ),
        (
            '@app.post("/admin/profile/<int:user_id>/profile-css")\n@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)\n@admin_level_required(PERMS["USER_MODERATION_TOOLS_VISIBLE"])',
            '@app.post("/admin/profile/<int:user_id>/profile-css")\n@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)\n@admin_level_required(PERMS["USER_PROFILE_EDIT"])',
            "profile CSS permission",
        ),
        (
            '@app.post("/admin/profile/<int:user_id>/image/<kind>")\n@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)\n@admin_level_required(PERMS["USER_MODERATION_TOOLS_VISIBLE"])',
            '@app.post("/admin/profile/<int:user_id>/image/<kind>")\n@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)\n@admin_level_required(PERMS["USER_PROFILE_ASSETS"])',
            "profile image permission",
        ),
    ))

    _patch("files/routes/admin.py", tuple(
        (
            f'@app.post("/admin/{endpoint}/<int:user_id>")\n@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)\n@admin_level_required(PERMS[\'USER_MODERATION_TOOLS_VISIBLE\'])',
            f'@app.post("/admin/{endpoint}/<int:user_id>")\n@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)\n@admin_level_required(PERMS[\'USER_PROFILE_ASSETS\'])',
            f"{endpoint} permission",
        )
        for endpoint in ("wipe_profile_picture", "wipe_profile_banner", "wipe_profile_background")
    ))

    _patch("files/routes/profile_moderation_fixes.py", (
        (
            '@app.post("/admin/wipe_profile_anthem/<int:user_id>")\n@admin_level_required(PERMS["USER_MODERATION_TOOLS_VISIBLE"])',
            '@app.post("/admin/wipe_profile_anthem/<int:user_id>")\n@admin_level_required(PERMS["USER_PROFILE_ASSETS"])',
            "profile anthem permission",
        ),
    ))

    _patch("files/templates/userpage/banner.html", (
        (
            "{% if v and v.id != u.id and v.admin_level >= PERMS['USER_MODERATION_TOOLS_VISIBLE'] %}\n\t\t<details class=\"profile-moderation\">",
            "{% if v and v.id != u.id and (v.admin_level >= PERMS['USER_MODERATION_TOOLS_VISIBLE'] or v.has_permission('USER_PROFILE_IDENTITY') or v.has_permission('USER_PROFILE_EDIT') or v.has_permission('USER_PROFILE_ASSETS') or v.has_permission('BOT_CONTROLS')) %}\n\t\t<details class=\"profile-moderation\">",
            "profile moderation panel permission visibility",
        ),
    ))

    _patch("files/templates/userpage/admintools.html", (
        (
            "\t\t\t{% if v.admin_level >= PERMS['USER_MODERATION_TOOLS_VISIBLE'] %}\n\t\t\t\t<div class=\"moderation-asset-actions",
            "\t\t\t{% if v.has_permission('USER_PROFILE_ASSETS') %}\n\t\t\t\t<div class=\"moderation-asset-actions",
            "profile asset moderation UI permission",
        ),
    ))

    _patch("files/templates/settings/personal.html", (
        (
            '\t\t\t\t\t\t\t<p>Your original username will always stay reserved for you: <code>{{v.original_username}}</code></p>',
            '\t\t\t\t\t\t\t{% if v.original_username %}<p>Your original username will always stay reserved for you: <code>{{v.original_username}}</code></p>{% endif %}',
            "reserved username settings copy",
        ),
    ))

    _patch("files/routes/users.py", (
        (
            "v.charge_account(currency_name, amount, allow_unlimited=False)",
            "v.charge_account(currency_name, amount)",
            "unlimited gift transfer charge",
        ),
    ))

    _patch("files/helpers/economy_ledger.py", (
        (
            'recipient = local.get("recipient") or local.get("user") or local.get("target")',
            'recipient = local.get("recipient") or local.get("receiver") or local.get("user") or local.get("target")',
            "gift ledger receiver metadata",
        ),
    ))

    _patch("files/helpers/slots.py", (
        (
            "\t\tgambler.pay_account(currency, reward, skip_if_unlimited=True)",
            "\t\tcredited_reward = max(0, reward - wager_value) if gambler.has_unlimited_spending else reward\n\t\tgambler.pay_account(currency, credited_reward)",
            "unlimited slots net payout",
        ),
    ))

    _patch("files/helpers/twentyone.py", (
        (
            "\tgambler.pay_account(game.currency, payout, skip_if_unlimited=True)",
            "\tcredited_payout = max(0, game.winnings) if gambler.has_unlimited_spending else payout\n\tgambler.pay_account(game.currency, credited_payout)",
            "unlimited blackjack net payout",
        ),
    ))

    _patch("files/helpers/roulette.py", (
        (
            "\t# Pay each winner the returned stake plus the reward earned by winning bets.\n\tfor user_id in winners:\n\t\tgambler = get_account(user_id)\n\t\tgambler_payout = payouts[user_id]\n\t\tgambler.pay_account(\n\t\t\t'coins',\n\t\t\tgambler_payout['coins'],\n\t\t\tskip_if_unlimited=True,\n\t\t)\n\t\tgambler.pay_account(\n\t\t\t'marseybux',\n\t\t\tgambler_payout['marseybux'],\n\t\t\tskip_if_unlimited=True,\n\t\t)",
            "\t# Normal accounts receive returned stake + winnings. Unlimited accounts\n\t# were never debited, so credit only the actual reward earned by winning bets.\n\tfor user_id in winners:\n\t\tgambler = get_account(user_id)\n\t\tgambler_payout = payouts[user_id]\n\t\tif gambler.has_unlimited_spending:\n\t\t\tgambler_payout = {'coins': 0, 'marseybux': 0}\n\t\t\tfor game in active_games:\n\t\t\t\tif game.user_id != user_id or game.id not in rewards_by_game_id:\n\t\t\t\t\tcontinue\n\t\t\t\tgambler_payout[game.currency] += int(rewards_by_game_id[game.id])\n\t\tgambler.pay_account('coins', gambler_payout['coins'])\n\t\tgambler.pay_account('marseybux', gambler_payout['marseybux'])",
            "unlimited roulette net payout",
        ),
    ))


def patch_username_patron_markers() -> None:
    _patch("files/templates/comments.html", (
        (
            'data-username-effect-color="{{c.author.username_effect_text_color}}"',
            'data-username-effect-color="{{c.author.username_effect_text_color}}" data-username-effect-patron="{{1 if c.author.active_patron else 0}}"',
            "comment username patron marker",
        ),
    ))
    _patch("files/templates/user_in_table.html", (
        (
            'data-username-effect-color="{{user.username_effect_text_color}}"',
            'data-username-effect-color="{{user.username_effect_text_color}}" data-username-effect-patron="{{1 if user.active_patron else 0}}"',
            "table username patron marker",
        ),
    ))
    _patch("files/templates/user_listing.html", (
        (
            'data-username-effects="{{u.active_username_effects|join(\',\')}}"',
            'data-username-effects="{{u.active_username_effects|join(\',\')}}" data-username-effect-color="{{u.username_effect_text_color}}" data-username-effect-patron="{{1 if u.active_patron else 0}}"',
            "user listing patron marker",
        ),
    ))
    _patch("files/assets/js/username_effects.js", (
        (
            "\tfunction prepareTarget(element, color) {\n\t\tif (!(element instanceof HTMLElement)) return;\n\t\telement.classList.add('username-effect-host');",
            "\tfunction prepareTarget(element, color) {\n\t\tif (!(element instanceof HTMLElement)) return;\n\t\tif (element.dataset.usernameEffectPatron === '0') {\n\t\t\telement.classList.remove('patron', 'username-effect-plate');\n\t\t\telement.style.removeProperty('background-color');\n\t\t\telement.style.removeProperty('--username-effect-text-color');\n\t\t}\n\t\telement.classList.add('username-effect-host');",
            "username renderer patron normalization",
        ),
    ))
