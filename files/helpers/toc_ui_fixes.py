import os
from pathlib import Path

import fcntl

from files.__main__ import app
from files.helpers.config.awards import AWARDS, AWARDS_ENABLED
from files.helpers.config.const import FEATURES


_LOCK_PATH = "/tmp/obsession-toc-ui-fixes.lock"
_MACROS_TEMPLATE = Path("files/templates/util/macros.html")
_COMMENTS_TEMPLATE = Path("files/templates/comments.html")
_PROFILE_BANNER_TEMPLATE = Path("files/templates/userpage/banner.html")

# One visual treatment for house identity everywhere it appears beside a user.
_HOUSE_ICON_STYLE = (
    "width:20px;height:20px;display:inline-block!important;"
    "object-fit:contain;vertical-align:middle;margin-right:-2px"
)


def _atomic_write(path: Path, content: str) -> None:
    temp_path = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temp_path.write_text(content, encoding="utf-8")
    os.replace(temp_path, path)


def _write_if_changed(path: Path, original: str, updated: str) -> None:
    if updated != original:
        _atomic_write(path, updated)


def _insert_after_line(source: str, marker: str, block: str, label: str) -> str:
    start = source.find(marker)
    if start < 0:
        raise RuntimeError(f"Could not locate {label}")
    line_end = source.find("\n", start)
    if line_end < 0:
        raise RuntimeError(f"Could not locate end of {label}")
    line_end += 1
    return source[:line_end] + block + source[line_end:]


def _patch_post_identity() -> None:
    """Make the house badge part of one canonical post-author inline.

    The homepage, board feeds, profile feeds and full threads all call the same
    post_meta macro. Do not create a listing-only house path. The house and
    Verified badges live *inside the same author link as the avatar/username*, so
    compact listing overflow cannot clip the house while leaving the username.
    """
    source = _MACROS_TEMPLATE.read_text(encoding="utf-8")
    original = source

    # A second web worker can run this installer after the first one patched the
    # shared filesystem. The marker makes the operation strictly idempotent.
    if 'data-toc-user-identity="post"' in source:
        return

    # Normalize any previously committed experimental macro signature. There is
    # exactly one post identity path now.
    source = source.replace(
        "{% macro post_meta(p, house_inline=false) %}",
        "{% macro post_meta(p) %}",
        1,
    )

    native_house = (
        "\t\t{% if FEATURES['HOUSES'] and p.author.house %}\n"
        "\t\t\t<img loading=\"lazy\" src=\"{{p.author.house | house_icon}}\" height=\"20\" "
        "data-bs-toggle=\"tooltip\" data-bs-placement=\"bottom\" title=\"House {{p.author.house}}\" "
        "alt=\"House {{p.author.house}}\">\n"
        "\t\t{% endif %}\n\n"
    )
    native_verified = (
        "\t\t{% if p.author.verified %}<i class=\"fas fa-badge-check align-middle ml-1 "
        "{% if p.author.verified=='Glowiefied' %}glow{% endif %}\" "
        "style=\"color:{% if p.author.verifiedcolor %}#{{p.author.verifiedcolor}}{% else %}#1DA1F2{% endif %}\" "
        "data-bs-toggle=\"tooltip\" data-bs-placement=\"bottom\" title=\"{{p.author.verified}}\"></i>\n"
        "\t\t{% endif %}\n"
    )

    if native_house not in source:
        raise RuntimeError("Could not locate native post house badge block")
    if native_verified not in source:
        raise RuntimeError("Could not locate native post Verified badge block")

    # Remove the detached badges. They are reinserted inside the author link.
    source = source.replace(native_house, "", 1)
    source = source.replace(native_verified, "", 1)

    anchor_marker = '\t\t<a class="user-name text-decoration-none" href="{{p.author.url}}"'
    anchor_start = source.find(anchor_marker)
    if anchor_start < 0:
        raise RuntimeError("Could not locate post author identity link")
    anchor_end = source.find("\n", anchor_start)
    if anchor_end < 0:
        raise RuntimeError("Could not locate end of post author identity link")
    anchor_end += 1

    anchor_line = source[anchor_start:anchor_end].replace(
        "<a ", '<a data-toc-user-identity="post" ', 1
    )
    source = source[:anchor_start] + anchor_line + source[anchor_end:]
    anchor_end = anchor_start + len(anchor_line)

    identity_badges = (
        "\t\t\t{% if p.author.house %}\n"
        "\t\t\t\t<img loading=\"lazy\" class=\"house-user-icon\" "
        "src=\"{{p.author.house | house_icon}}\" width=\"20\" height=\"20\" "
        f"style=\"{_HOUSE_ICON_STYLE}\" data-bs-toggle=\"tooltip\" data-bs-placement=\"bottom\" "
        "title=\"House {{p.author.house}}\" alt=\"House {{p.author.house}}\">\n"
        "\t\t\t{% endif %}\n"
        "\t\t\t{% if p.author.verified %}<i class=\"fas fa-badge-check align-middle "
        "{% if not p.author.house %}ml-1 {% endif %}{% if p.author.verified=='Glowiefied' %}glow{% endif %}\" "
        "style=\"color:{% if p.author.verifiedcolor %}#{{p.author.verifiedcolor}}{% else %}#1DA1F2{% endif %}\" "
        "data-bs-toggle=\"tooltip\" data-bs-placement=\"bottom\" title=\"{{p.author.verified}}\"></i>\n"
        "\t\t\t{% endif %}\n"
    )
    source = source[:anchor_end] + identity_badges + source[anchor_end:]

    # Keep the compact avatar visually centered with the badges/username.
    source = source.replace(
        '<div class="profile-pic-30-wrapper" style="margin-top:9px">',
        '<div class="profile-pic-30-wrapper" style="margin-top:2px">',
        1,
    )
    source = source.replace(
        '<div class="profile-pic-30-wrapper" style="margin-top:4px">',
        '<div class="profile-pic-30-wrapper" style="margin-top:2px">',
        1,
    )

    if 'data-toc-user-identity="post"' not in source:
        raise RuntimeError("Post identity marker was not installed")
    if source.find('class="house-user-icon"', anchor_start) < anchor_start:
        raise RuntimeError("Post house badge was not moved inside the author identity")

    _write_if_changed(_MACROS_TEMPLATE, original, source)


def _patch_comment_identity() -> None:
    """Use the same house/checkmark/avatar/username inline for comments/replies."""
    source = _COMMENTS_TEMPLATE.read_text(encoding="utf-8")
    original = source

    if 'data-toc-user-identity="comment"' in source:
        return

    native_house = (
        "\t\t\t\t\t{% if FEATURES['HOUSES'] and c.author.house %}\n"
        "\t\t\t\t\t\t<img loading=\"lazy\" src=\"{{c.author.house | house_icon}}\" height=\"20\" "
        "data-bs-toggle=\"tooltip\" data-bs-placement=\"bottom\" title=\"House {{c.author.house}}\" "
        "alt=\"House {{c.author.house}}\">\n"
        "\t\t\t\t\t{% endif %}\n\n"
    )
    native_verified = (
        "\t\t\t\t\t{% if c.author.verified %}<i class=\"fas fa-badge-check align-middle ml-1 "
        "{% if c.author.verified=='Glowiefied' %}glow{% endif %}\" "
        "style=\"color:{% if c.author.verifiedcolor %}#{{c.author.verifiedcolor}}{% else %}#1DA1F2{% endif %}\" "
        "data-bs-toggle=\"tooltip\" data-bs-placement=\"bottom\" title=\"{{c.author.verified}}\"></i>\n"
        "\t\t\t\t\t{% endif %}\n\n"
    )

    if native_house not in source:
        raise RuntimeError("Could not locate native comment house badge block")
    if native_verified not in source:
        raise RuntimeError("Could not locate native comment Verified badge block")

    source = source.replace(native_house, "", 1)
    source = source.replace(native_verified, "", 1)

    anchor_marker = '\t\t\t\t\t<a class="user-name text-decoration-none" href="{{c.author.url}}"'
    anchor_start = source.find(anchor_marker)
    if anchor_start < 0:
        raise RuntimeError("Could not locate comment author identity link")
    anchor_end = source.find("\n", anchor_start)
    if anchor_end < 0:
        raise RuntimeError("Could not locate end of comment author identity link")
    anchor_end += 1

    anchor_line = source[anchor_start:anchor_end].replace(
        "<a ", '<a data-toc-user-identity="comment" ', 1
    )
    source = source[:anchor_start] + anchor_line + source[anchor_end:]
    anchor_end = anchor_start + len(anchor_line)

    identity_badges = (
        "\t\t\t\t\t\t{% if c.author.house %}\n"
        "\t\t\t\t\t\t\t<img loading=\"lazy\" class=\"house-user-icon\" "
        "src=\"{{c.author.house | house_icon}}\" width=\"20\" height=\"20\" "
        f"style=\"{_HOUSE_ICON_STYLE}\" data-bs-toggle=\"tooltip\" data-bs-placement=\"bottom\" "
        "title=\"House {{c.author.house}}\" alt=\"House {{c.author.house}}\">\n"
        "\t\t\t\t\t\t{% endif %}\n"
        "\t\t\t\t\t\t{% if c.author.verified %}<i class=\"fas fa-badge-check align-middle "
        "{% if not c.author.house %}ml-1 {% endif %}{% if c.author.verified=='Glowiefied' %}glow{% endif %}\" "
        "style=\"color:{% if c.author.verifiedcolor %}#{{c.author.verifiedcolor}}{% else %}#1DA1F2{% endif %}\" "
        "data-bs-toggle=\"tooltip\" data-bs-placement=\"bottom\" title=\"{{c.author.verified}}\"></i>\n"
        "\t\t\t\t\t\t{% endif %}\n"
    )
    source = source[:anchor_end] + identity_badges + source[anchor_end:]

    if 'data-toc-user-identity="comment"' not in source:
        raise RuntimeError("Comment identity marker was not installed")

    _write_if_changed(_COMMENTS_TEMPLATE, original, source)


def _restore_profile_house_identity() -> None:
    """Keep the house badge on the profile identity row beside other badges."""
    source = _PROFILE_BANNER_TEMPLATE.read_text(encoding="utf-8")
    original = source

    if 'id="profile--house"' not in source:
        verified_marker = "\t\t\t\t\t\t{% if u.verified %}\n"
        if verified_marker not in source:
            raise RuntimeError("Could not locate profile verified badge block")
        house_block = (
            "\t\t\t\t\t\t{% if FEATURES['HOUSES'] and u.house %}\n"
            "\t\t\t\t\t\t\t<img loading=\"lazy\" id=\"profile--house\" src=\"{{u.house | house_icon}}\" "
            "height=\"20\" data-bs-toggle=\"tooltip\" data-bs-placement=\"bottom\" "
            "title=\"House {{u.house}}\" alt=\"House {{u.house}}\">\n"
            "\t\t\t\t\t\t{% endif %}\n"
        )
        source = source.replace(verified_marker, house_block + verified_marker, 1)

    _write_if_changed(_PROFILE_BANNER_TEMPLATE, original, source)


def _clear_template_cache() -> None:
    app.jinja_env.cache.clear()
    bytecode_cache = app.jinja_env.bytecode_cache
    if bytecode_cache and hasattr(bytecode_cache, "clear"):
        bytecode_cache.clear()


def install_toc_ui_fixes() -> None:
    """Install the small set of TOC identity/display normalizations."""
    FEATURES["HOUSES"] = True

    for catalog in (AWARDS, AWARDS_ENABLED):
        if "ban" in catalog:
            catalog["ban"]["title"] = "Ban"
        if "unban" in catalog:
            catalog["unban"]["title"] = "Unban"

    with open(_LOCK_PATH, "w", encoding="utf-8") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        _patch_post_identity()
        _patch_comment_identity()
        _restore_profile_house_identity()
        _clear_template_cache()
