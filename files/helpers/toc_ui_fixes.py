from files.helpers.config.awards import AWARDS, AWARDS_ENABLED
from files.helpers.config.const import FEATURES


def install_toc_ui_fixes() -> None:
    """Keep only non-invasive TOC display configuration.

    House identity rendering belongs to the repository's native templates. Do not
    rewrite post/comment/profile templates at runtime: the recent homepage house
    icon experiments were unverified and created unnecessary rendering risk.
    """
    FEATURES["HOUSES"] = True

    # Public display names only; internal award keys/mechanics stay unchanged.
    for catalog in (AWARDS, AWARDS_ENABLED):
        if "ban" in catalog:
            catalog["ban"]["title"] = "Ban"
        if "unban" in catalog:
            catalog["unban"]["title"] = "Unban"
