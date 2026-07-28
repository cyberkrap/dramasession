"""Keep Obsession badge names and descriptions free of legacy branding."""

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from files.helpers.support import (
    CONTRIBUTION_BADGE_DESCRIPTIONS,
    CONTRIBUTION_BADGE_NAMES,
)


# These are recurring support badges, not lifetime donation milestones. Mutating
# the shared dictionary also keeps the PayPal fulfilment helper consistent.
CONTRIBUTION_BADGE_DESCRIPTIONS.update({
    21: "Donates $5/month",
    22: "Donates $10/month",
    23: "Donates $20/month",
    24: "Donates $50/month",
    25: "Donates $100/month",
    26: "Retired legacy support badge",
    27: "Retired legacy support badge",
})


BADGE_BRANDING = {
    1: (
        "Alpha User",
        "Joined during The Obsession Club launch promotion.",
    ),
    16: (
        "Emoji Master",
        "Made major contributions to the site's emoji collection.",
    ),
    17: (
        "Emoji Artisan",
        "Created an approved emoji for the site.",
    ),
    99: (
        "Sidebar Artist",
        "Created approved artwork for the site sidebar.",
    ),
}
BADGE_BRANDING.update({
    badge_id: (
        CONTRIBUTION_BADGE_NAMES[badge_id],
        CONTRIBUTION_BADGE_DESCRIPTIONS[badge_id],
    )
    for badge_id in CONTRIBUTION_BADGE_NAMES
})


def install_badge_branding(engine):
    """Update existing badge definitions at startup without touching ownership."""
    try:
        with engine.begin() as connection:
            for badge_id, (name, description) in BADGE_BRANDING.items():
                connection.execute(
                    text(
                        "UPDATE badge_defs "
                        "SET name = :name, description = :description "
                        "WHERE id = :badge_id "
                        "AND (name IS DISTINCT FROM :name "
                        "OR description IS DISTINCT FROM :description)"
                    ),
                    {
                        "badge_id": badge_id,
                        "name": name,
                        "description": description,
                    },
                )
    except SQLAlchemyError:
        # Database initialization may run before badge_defs exists on a fresh install.
        return False
    return True
