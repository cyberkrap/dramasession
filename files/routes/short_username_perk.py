import re
from importlib import import_module

from flask import g, request

from files.__main__ import app
from files.helpers.support import patron_has


_settings = import_module("files.routes.settings")
_standard_username_regex = _settings.valid_username_regex
_short_username_regex = re.compile(r"^[a-zA-Z0-9_\-]{1,25}$", flags=re.A)


class _PatronAwareUsernameRegex:
    """Keep the normal signup/name rules, but allow active level-3+ patrons to go shorter."""

    def fullmatch(self, value, *args, **kwargs):
        user = getattr(g, "v", None)
        if user is not None and patron_has(user, "short_username"):
            return _short_username_regex.fullmatch(value, *args, **kwargs)
        return _standard_username_regex.fullmatch(value, *args, **kwargs)

    def __getattr__(self, name):
        return getattr(_standard_username_regex, name)


# settings_name_change resolves this module global at request time. Replacing it
# here preserves its existing form-key validation, rate limits, uniqueness check,
# original-username reservation, cooldown data, and all other route behavior.
_settings.valid_username_regex = _PatronAwareUsernameRegex()


@app.after_request
def render_short_username_setting(response):
    """Make the Personal Settings copy and browser validation match the server rule."""
    if response.status_code >= 400 and response.status_code not in {400, 403, 409}:
        return response
    if not request.path.startswith("/settings/"):
        return response
    if not response.content_type or "text/html" not in response.content_type:
        return response

    body = response.get_data(as_text=True)
    if 'action="/settings/name_change"' not in body:
        return response

    user = getattr(g, "v", None)
    short_allowed = bool(user and patron_has(user, "short_username"))
    minimum = 1 if short_allowed else 3

    body = re.sub(
        r'(<input autocomplete="off" type="text" name="name" class="form-control" value="[^"]*")([^>]*)>',
        lambda match: (
            match.group(1)
            + re.sub(r'\s+(?:minlength|maxlength)="[^"]*"', '', match.group(2))
            + f' minlength="{minimum}" maxlength="25">'
        ),
        body,
        count=1,
    )

    normal_help = '<small>3-25 characters, including letters, numbers, _ , and -</small>'
    if short_allowed:
        help_text = (
            '<small>1-25 characters, including letters, numbers, _ , and -. '
            '<span class="text-primary">Sandy\'s Devoted perk active: 1- and 2-character usernames are available.</span>'
            '</small>'
        )
    else:
        help_text = normal_help
    body = body.replace(normal_help, help_text, 1)

    response.set_data(body)
    return response
