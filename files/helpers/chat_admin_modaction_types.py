"""Register readable moderation-log entries for public-chat admin actions."""

from files.classes.mod_logs import ModAction
from files.helpers.config.modaction_types import MODACTION_TYPES, MODACTION_TYPES_FILTERED
from files.helpers.lazy import lazy


CHAT_ADMIN_MODACTION_TYPES = {
    'chat_distinguish': {
        'str': 'distinguished a {self.note}',
        'icon': 'fa-crown',
        'color': 'bg-success',
    },
    'chat_remove': {
        'str': 'removed a {self.note}',
        'icon': 'fa-comment-slash',
        'color': 'bg-danger',
    },
}

_installed = False


def install_chat_admin_modaction_types() -> None:
    """Teach ModAction how to display chat-message links without duplicating notes."""
    global _installed
    if _installed:
        return

    MODACTION_TYPES.update(CHAT_ADMIN_MODACTION_TYPES)
    MODACTION_TYPES_FILTERED.update(CHAT_ADMIN_MODACTION_TYPES)

    original_getter = ModAction.string.fget
    if not getattr(original_getter, '_chat_admin_modaction_string', False):
        @lazy
        def string_with_chat_actions(self):
            if self.kind in CHAT_ADMIN_MODACTION_TYPES:
                return self.action_type['str'].format(self=self)
            return original_getter(self)

        string_with_chat_actions._chat_admin_modaction_string = True
        ModAction.string = property(string_with_chat_actions)

    _installed = True
