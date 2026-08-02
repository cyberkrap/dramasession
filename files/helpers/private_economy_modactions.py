"""Keep direct economy administration out of public moderator logs."""

from sqlalchemy import event, text
from sqlalchemy.orm import Session

from files.classes.mod_logs import ModAction


PRIVATE_ECONOMY_MODACTION_KINDS = frozenset({
    "grant_currency",
    "remove_currency",
    "enable_unlimited_spending",
    "disable_unlimited_spending",
})

_installed = False


def install_private_economy_modactions(engine):
    """Delete legacy entries and prevent new private economy logs being stored."""
    global _installed
    if _installed:
        return

    kinds = tuple(sorted(PRIVATE_ECONOMY_MODACTION_KINDS))
    placeholders = ", ".join(f":kind_{index}" for index in range(len(kinds)))
    parameters = {f"kind_{index}": kind for index, kind in enumerate(kinds)}

    # These records were previously displayed in the Modactions notification
    # feed. Remove them from the database so no role or alternate log view can
    # expose the historical entries.
    with engine.begin() as connection:
        connection.execute(
            text(f"DELETE FROM modactions WHERE kind IN ({placeholders})"),
            parameters,
        )

    @event.listens_for(Session, "before_flush")
    def _discard_private_economy_modactions(session, flush_context, instances):
        for item in tuple(session.new):
            if (
                isinstance(item, ModAction)
                and item.kind in PRIVATE_ECONOMY_MODACTION_KINDS
            ):
                session.expunge(item)

    _installed = True
