import os
from pathlib import Path

import fcntl


_LOCK_PATH = "/tmp/obsession-pin-ui-repairs.lock"
_COMMENTS_TEMPLATE_PATH = Path("files/templates/comments.html")
_MACROS_TEMPLATE_PATH = Path("files/templates/util/macros.html")
_POST_ACTIONS_PATH = Path("files/templates/post_actions.html")
_POST_ADMIN_MOBILE_PATH = Path("files/templates/post_admin_actions_mobile.html")
_AWARD_EFFECTS_REQUESTED_PATH = Path("files/assets/js/award_effects_requested.js")


def _atomic_write(path, content):
    temp_path = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temp_path.write_text(content, encoding="utf-8")
    os.replace(temp_path, path)


def _patch_pin_metadata(path, target):
    source = path.read_text(encoding="utf-8")
    original = source

    old_raw = f'title="Pinned by @{{{{{target}.stickied}}}}"'
    normalized = f'title="Pinned by {{{{pin_credit({target}.stickied)}}}}"'
    durable = normalized + f' data-pin-credit="{{{{pin_credit({target}.stickied)}}}}"'

    if durable not in source:
        if normalized in source:
            source = source.replace(normalized, durable, 1)
        elif old_raw in source:
            source = source.replace(old_raw, durable, 1)

    if source != original:
        _atomic_write(path, source)


def _patch_pin_tooltip_js():
    source = _AWARD_EFFECTS_REQUESTED_PATH.read_text(encoding="utf-8")
    original = source

    source_line = "\t\tconst source=latestPinAward(pinOwner(pin));\n"
    source_with_credit = source_line + "\t\tconst serverCredit=(pin.dataset.pinCredit||'').trim();\n"
    if source_with_credit not in source and source_line in source:
        source = source.replace(source_line, source_with_credit, 1)

    old_base = "\t\tlet base=source ? `Pinned by @${source.giver} (${source.kind==='gigapin'?'Giga pin award':'Pin award'})` :\n\t\t\t(/^Pinned by\\s+/i.test(existing)?existing:'Pinned by (a site admin)');\n"
    new_base = "\t\tlet base=serverCredit ? `Pinned by ${serverCredit}` : source ? `Pinned by @${source.giver} (${source.kind==='gigapin'?'Giga pin award':'Pin award'})` :\n\t\t\t(/^Pinned by\\s+/i.test(existing)?existing:'Pinned by (a site admin)');\n"
    if new_base not in source and old_base in source:
        source = source.replace(old_base, new_base, 1)

    if source != original:
        _atomic_write(_AWARD_EFFECTS_REQUESTED_PATH, source)


def _patch_desktop_pin_controls():
    source = _POST_ACTIONS_PATH.read_text(encoding="utf-8")
    original = source

    old = "\t\t\t<button type=\"button\" id=\"pin-{{p.id}}\" class=\"dropdown-item {% if p.stickied and not p.stickied_utc %}d-none{% endif %} list-inline-item text-info\" data-nonce=\"{{g.nonce}}\" data-onclick=\"pinPost(this, '{{p.id}}')\"><i class=\"fas fa-thumbtack fa-rotate--45\"></i>Pin {% if p.stickied_utc %}permanently{% else %}for 1 hour{% endif %}</button>\n"
    new = "\t\t\t<button type=\"button\" id=\"pin-hour-{{p.id}}\" class=\"dropdown-item list-inline-item text-info\" data-nonce=\"{{g.nonce}}\" data-onclick=\"postToastReload(this,'/admin/pin-post/{{p.id}}/hour')\"><i class=\"fas fa-clock fa-fw\"></i>Pin for 1 hour</button>\n\t\t\t<button type=\"button\" id=\"pin-permanent-{{p.id}}\" class=\"dropdown-item list-inline-item text-info\" data-nonce=\"{{g.nonce}}\" data-onclick=\"postToastReload(this,'/admin/pin-post/{{p.id}}/permanent')\"><i class=\"fas fa-thumbtack fa-rotate--45 fa-fw\"></i>Pin permanently</button>\n"
    if new not in source and old in source:
        source = source.replace(old, new, 1)

    if source != original:
        _atomic_write(_POST_ACTIONS_PATH, source)


def _patch_mobile_pin_controls():
    source = _POST_ADMIN_MOBILE_PATH.read_text(encoding="utf-8")
    original = source

    old = "\t\t\t\t\t\t<button type=\"button\" id=\"pin2-{{p.id}}\" class=\"{% if p.stickied and not p.stickied_utc %}d-none{% endif %} nobackground btn btn-link btn-block btn-lg text-left text-primary\" data-nonce=\"{{g.nonce}}\" data-onclick=\"pinPost(this,'{{p.id}}')\" data-bs-dismiss=\"modal\"><i class=\"fas fa-thumbtack fa-rotate--45 text-center text-primary mr-2\"></i>Pin {% if p.stickied_utc %}permanently{% else %}for 1 hour{% endif %}</button>\n"
    new = "\t\t\t\t\t\t<button type=\"button\" id=\"pin-hour2-{{p.id}}\" class=\"nobackground btn btn-link btn-block btn-lg text-left text-primary\" data-nonce=\"{{g.nonce}}\" data-onclick=\"postToastReload(this,'/admin/pin-post/{{p.id}}/hour')\" data-bs-dismiss=\"modal\"><i class=\"fas fa-clock text-center text-primary mr-2\"></i>Pin for 1 hour</button>\n\t\t\t\t\t\t<button type=\"button\" id=\"pin-permanent2-{{p.id}}\" class=\"nobackground btn btn-link btn-block btn-lg text-left text-primary\" data-nonce=\"{{g.nonce}}\" data-onclick=\"postToastReload(this,'/admin/pin-post/{{p.id}}/permanent')\" data-bs-dismiss=\"modal\"><i class=\"fas fa-thumbtack fa-rotate--45 text-center text-primary mr-2\"></i>Pin permanently</button>\n"
    if new not in source and old in source:
        source = source.replace(old, new, 1)

    if source != original:
        _atomic_write(_POST_ADMIN_MOBILE_PATH, source)


def install_pin_ui_repairs():
    """Make pin source attribution durable and expose explicit admin pin durations."""
    with open(_LOCK_PATH, "w", encoding="utf-8") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        _patch_pin_metadata(_COMMENTS_TEMPLATE_PATH, "c")
        _patch_pin_metadata(_MACROS_TEMPLATE_PATH, "p")
        _patch_pin_tooltip_js()
        _patch_desktop_pin_controls()
        _patch_mobile_pin_controls()
