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

# Timeout actions already keep their destination/duration inside `note` and
# interpolate that note directly into their configured action string. The
# generic ModAction formatter normally appends notes again in parentheses,
# which made untimeout entries render as `in Chat (Chat)`. Route both timeout
# kinds through the same one-pass formatter as the other public-chat actions.
CHAT_CUSTOM_STRING_KINDS = frozenset({
    *CHAT_ADMIN_MODACTION_TYPES,
    'chat_timeout',
    'chat_untimeout',
})

_installed = False


def install_chat_admin_modaction_types() -> None:
    """Teach ModAction and every modlog filter set about chat admin actions."""
    global _installed
    if _installed:
        return

    # There are two moderation-log filter dictionaries: the ordinary admin
    # filter and the higher-privilege filter. Register chat actions in both so
    # they appear no matter which administrator view is being rendered.
    MODACTION_TYPES.update(CHAT_ADMIN_MODACTION_TYPES)
    MODACTION_TYPES_FILTERED.update(CHAT_ADMIN_MODACTION_TYPES)
    MODACTION_TYPES__FILTERED.update(CHAT_ADMIN_MODACTION_TYPES)

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
