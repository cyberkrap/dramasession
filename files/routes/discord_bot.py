from flask import render_template, request

from files.__main__ import app, limiter
from files.helpers.config.const import DEFAULT_RATELIMIT
from files.helpers.discord_bot_api import (
    bot_api_configured,
    get_bot_health,
    get_command_catalog,
)
from files.helpers.toc_bot_commands import get_toc_bot_commands
from files.routes.wrappers import auth_desired_with_logingate, get_ID


_CATEGORY_LABELS = {
    "configuration": "Configuration",
    "fun": "Fun",
    "information": "Information",
    "levels": "Levels",
    "moderation": "Moderation",
    "roles": "Roles",
    "server": "Server",
    "slash": "Slash Commands",
    "utility": "Utility",
}


def _category_label(category):
    return _CATEGORY_LABELS.get(category, category.replace("_", " ").title())


def _catalog_view():
    """Discord-side command manifest supplied by the separate bot service."""
    catalog = get_command_catalog()
    if not catalog:
        return None

    category_counts = {}
    for command in catalog["commands"]:
        category = command["category"]
        category_counts[category] = category_counts.get(category, 0) + 1

    categories = [
        {
            "key": category,
            "label": _category_label(category),
            "count": category_counts.get(category, 0),
        }
        for category in catalog["categories"]
        if category_counts.get(category, 0)
    ]

    return {
        **catalog,
        "categories": categories,
        "command_count": len(catalog["commands"]),
    }


def _toc_catalog_view():
    """TOC public-chat command manifest owned by the TOC service itself."""
    commands = get_toc_bot_commands()
    category_counts = {}
    for command in commands:
        category = command["category"]
        category_counts[category] = category_counts.get(category, 0) + 1

    preferred_order = ("information", "fun")
    ordered_categories = [category for category in preferred_order if category in category_counts]
    ordered_categories.extend(
        sorted(category for category in category_counts if category not in preferred_order)
    )

    return {
        "commands": commands,
        "categories": [
            {
                "key": category,
                "label": _category_label(category),
                "count": category_counts[category],
            }
            for category in ordered_categories
        ],
    }


@app.get("/discordbot")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_desired_with_logingate
def discord_bot_hub(v):
    catalog = _catalog_view()
    toc_catalog = _toc_catalog_view()
    health = get_bot_health() if bot_api_configured() else None

    return render_template(
        "discord_bot/index.html",
        v=v,
        catalog=catalog,
        toc_command_count=len(toc_catalog["commands"]),
        health=health,
        api_configured=bot_api_configured(),
    )


@app.get("/discordbot/commands")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_desired_with_logingate
def discord_bot_commands(v):
    """Discord command docs. TOC public-chat commands live on their own surface."""
    catalog = _catalog_view()
    selected_category = request.args.get("category", "").strip().lower()
    query = request.args.get("q", "").strip()[:100]

    commands = []
    if catalog:
        known_categories = {category["key"] for category in catalog["categories"]}
        if selected_category not in known_categories:
            selected_category = catalog["categories"][0]["key"] if catalog["categories"] else ""

        commands = catalog["commands"]
        if selected_category:
            commands = [
                command for command in commands
                if command["category"] == selected_category
            ]

        if query:
            needle = query.casefold()
            commands = [
                command for command in commands
                if needle in " ".join([
                    command["name"],
                    command["description"],
                    " ".join(command["aliases"]),
                    command["usage"],
                ]).casefold()
            ]

    return render_template(
        "discord_bot/commands.html",
        v=v,
        catalog=catalog,
        commands=commands,
        selected_category=selected_category,
        selected_category_label=_category_label(selected_category) if selected_category else "Commands",
        query=query,
        api_configured=bot_api_configured(),
    )


@app.get("/discordbot/chat-commands")
@app.get("/discordbot/toc-commands")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_desired_with_logingate
def discord_bot_toc_commands(v):
    """Searchable documentation generated from the same registry TOC chat executes."""
    catalog = _toc_catalog_view()
    all_commands = catalog["commands"]
    selected_category = request.args.get("category", "").strip().lower()
    query = request.args.get("q", "").strip()[:100]

    known_categories = {category["key"] for category in catalog["categories"]}
    if selected_category not in known_categories:
        selected_category = ""

    commands = all_commands
    if selected_category:
        commands = [command for command in commands if command["category"] == selected_category]

    if query:
        needle = query.casefold()
        commands = [
            command for command in commands
            if needle in " ".join([
                command["name"],
                command["description"],
                command["syntax"],
                command["example"],
                " ".join(command["aliases"]),
            ]).casefold()
        ]

    return render_template(
        "discord_bot/toc_commands.html",
        v=v,
        all_commands=all_commands,
        categories=catalog["categories"],
        commands=commands,
        selected_category=selected_category,
        selected_category_label=_category_label(selected_category) if selected_category else "All TOC Chat Commands",
        query=query,
    )
