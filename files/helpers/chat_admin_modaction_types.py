"""Register readable moderation-log entries for public-chat admin actions."""

from files.classes.mod_logs import ModAction
from files.helpers.config.modaction_types import (
    MODACTION_TYPES,
    MODACTION_TYPES_FILTERED,
    MODACTION_TYPES__FILTERED,
)
from files.helpers.lazy import lazy


CHAT_ADMIN_MODACTION_TYPES = {
    'chat_distinguish': {
        'str': 'distinguished a {self.note}',
        'icon': 'fa-crown',
        'color': 'bg-success',
    },
    'chat_remove': {
        'str': 'removed a {self.note}',
        # fa-comment-slash is not present in the site's current icon bundle.
        # Use the same proven comment glyph as comment-removal actions; the
        # danger background communicates the destructive action.
        'icon': 'fa-comment',
        'color': 'bg-danger',
    },
}

# Use one coherent timeout metaphor everywhere. These are standard Font
# Awesome icons and avoid the misleading green checkmark / verified look.
# Color belongs to the modlog action tile, not the filter dropdown itself.
CHAT_TIMEOUT_MODACTION_TYPES = {
    'chat_timeout': {
        'str': 'timed out {self.target_link} from speaking in {self.note}',
        'icon': 'fa-hourglass-half',
        'color': 'bg-danger',
    },
    'chat_untimeout': {
        'str': 'removed the chat timeout from {self.target_link} in {self.note}',
        'icon': 'fa-hourglass-end',
        'color': 'bg-success',
    },
}

ALL_CHAT_MODACTION_TYPES = {
    **CHAT_ADMIN_MODACTION_TYPES,
    **CHAT_TIMEOUT_MODACTION_TYPES,
}

# Timeout actions already keep their destination/duration inside `note` and
# interpolate that note directly into their configured action string. The
# generic ModAction formatter normally appends notes again in parentheses,
# which made untimeout entries render as `in Chat (Chat)`. Route all public
# chat actions through a one-pass formatter.
CHAT_CUSTOM_STRING_KINDS = frozenset(ALL_CHAT_MODACTION_TYPES)

_installed = False


def install_chat_admin_modaction_types() -> None:
    """Teach ModAction and every modlog filter set about public-chat actions."""
    global _installed
    if _installed:
        return

    # There are two moderation-log filter dictionaries: the ordinary admin
    # filter and the higher-privilege filter. Register/update chat actions in
    # all of them so labels, icons and filtering stay consistent everywhere.
    MODACTION_TYPES.update(ALL_CHAT_MODACTION_TYPES)
    MODACTION_TYPES_FILTERED.update(ALL_CHAT_MODACTION_TYPES)
    MODACTION_TYPES__FILTERED.update(ALL_CHAT_MODACTION_TYPES)

    original_getter = ModAction.string.fget
    if not getattr(original_getter, '_chat_admin_modaction_string', False):
        @lazy
        def string_with_chat_actions(self):
            if self.kind in CHAT_CUSTOM_STRING_KINDS:
                return self.action_type['str'].format(self=self)
            return original_getter(self)

        string_with_chat_actions._chat_admin_modaction_string = True
        ModAction.string = property(string_with_chat_actions)

    _installed = True
