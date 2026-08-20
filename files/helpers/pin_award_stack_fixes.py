import os
from pathlib import Path

import fcntl

from files.helpers.chud_repairs import patch_chud_source


# This helper is imported during the pre-route source-repair phase, before
# files.routes.admin is imported. Apply Chud repairs here so the legacy admin
# handler and moderation templates are corrected before Flask registers them.
patch_chud_source()


_LOCK_PATH = "/tmp/obsession-pin-award-stack.lock"
_AWARDS_ROUTE_PATH = Path("files/routes/awards.py")
_MARKER = "# toc-stackable-pin-awards-v2"


def _atomic_write(path: Path, content: str) -> None:
    temp_path = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temp_path.write_text(content, encoding="utf-8")
    os.replace(temp_path, path)


def _stackable_block(kind: str, hours_post: int, hours_comment: int, credit: str) -> str:
    return f'''\telif kind == "{kind}":\n\t\tif not FEATURES['PINS']: abort(403)\n\t\tif thing.is_banned: abort(403)\n\n\t\t# {_MARKER}\n\t\t# Lock the exact target row so simultaneous or batched pin awards cannot\n\t\t# overwrite each other's expiry. Every award extends the active expiry; if\n\t\t# the stored timed pin already expired, start from now instead.\n\t\tpin_thing = (\n\t\t\tg.db.query(thing.__class__)\n\t\t\t.filter(thing.__class__.id == thing.id)\n\t\t\t.with_for_update()\n\t\t\t.one()\n\t\t)\n\t\tif thing_type == 'comment': add = 3600 * {hours_comment}\n\t\telse: add = 3600 * {hours_post}\n\n\t\tnow = int(time.time())\n\t\tbase_expiry = max(int(pin_thing.stickied_utc or 0), now)\n\t\tpin_thing.stickied_utc = base_expiry + add\n\t\tpin_thing.stickied = f'{{v.username}}{credit}'\n\t\tg.db.add(pin_thing)\n\t\tg.db.flush()\n\t\tthing = pin_thing\n\t\tcache.delete_memoized(frontlist)\n'''


def patch_stackable_pin_award_source() -> None:
    """Make Pin and Giga Pin durations additive and concurrency-safe.

    Pin adds 1 hour to posts / 6 hours to comments per award.
    Giga Pin adds 12 hours to posts / 12 days to comments per award.
    """
    with open(_LOCK_PATH, "w", encoding="utf-8") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        source = _AWARDS_ROUTE_PATH.read_text(encoding="utf-8")
        if _MARKER in source:
            return

        pin_start = source.find('\telif kind == "pin":\n')
        pin_end = source.find('\telif kind == "unpin":\n', pin_start)
        if pin_start == -1 or pin_end == -1:
            raise RuntimeError("Could not locate Pin award mechanics")
        source = source[:pin_start] + _stackable_block("pin", 1, 6, "{PIN_AWARD_TEXT}") + source[pin_end:]

        giga_start = source.find('\telif kind == "gigapin":\n')
        giga_end = source.find('\telif kind == "gigaunpin":\n', giga_start)
        if giga_start == -1 or giga_end == -1:
            raise RuntimeError("Could not locate Giga Pin award mechanics")
        source = source[:giga_start] + _stackable_block("gigapin", 12, 24 * 12, " (Giga pin award)") + source[giga_end:]

        _atomic_write(_AWARDS_ROUTE_PATH, source)
