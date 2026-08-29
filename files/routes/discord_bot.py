from flask import render_template, request

from files.__main__ import app, limiter
from files.helpers.config.const import DEFAULT_RATELIMIT
from files.helpers.discord_bot_api import (
    bot_api_configured,
    get_bot_health,
    get_command_catalog,
)
from files.routes.wrappers import auth_desired_with_logingate, get_ID


_CATEGORY_LABELS = {
    "configuration": "Configuration",
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


@app.get("/discordbot")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_desired_with_logingate
def discord_bot_hub(v):
    catalog = _catalog_view()
    health = get_bot_health() if bot_api_configured() else None

    return render_template(
        "discord_bot/index.html",
        v=v,
        catalog=catalog,
        health=health,
        api_configured=bot_api_configured(),
    )


@app.get("/discordbot/commands")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_desired_with_logingate
def discord_bot_commands(v):
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
