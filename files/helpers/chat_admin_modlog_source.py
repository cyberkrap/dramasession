"""Patch the chat service so admin message actions are written to ModAction."""

import fcntl
import os
from pathlib import Path


_LOCK_PATH = "/tmp/obsession-chat-admin-modlog.lock"
_CHAT_ROUTE = Path("files/routes/chat.py")


def _atomic_write(path: Path, content: str) -> None:
    temp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temp.write_text(content, encoding="utf-8")
    os.replace(temp, path)


def patch_chat_admin_modlog_source() -> None:
    """Add durable modlog records before the chat module is imported."""
    with open(_LOCK_PATH, "w", encoding="utf-8") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        source = _CHAT_ROUTE.read_text(encoding="utf-8")
        patched = source

        distinguish_marker = "\tg.db.add(message)\n\tg.db.commit()\n\tif timeout_target:"
        distinguish_replacement = """\tg.db.add(message)\n\tg.db.commit()\n\tif distinguished:\n\t\tg.db.add(ModAction(\n\t\t\tkind='chat_distinguish',\n\t\t\tuser_id=v.id,\n\t\t\ttarget_user_id=message.user_id,\n\t\t\t_note=f'<a href=\"/chat#{message.id}\">chat message</a>',\n\t\t))\n\t\tg.db.commit()\n\tif timeout_target:"""
        if "kind='chat_distinguish'" not in patched:
            if distinguish_marker not in patched:
                raise RuntimeError("Could not locate chat message commit for distinguish logging")
            patched = patched.replace(distinguish_marker, distinguish_replacement, 1)

        remove_marker = """\tmessage.removed_by_id = v.id\n\tmessage.removed_by_username = v.username\n\tg.db.commit()\n\temit('delete', {"""
        remove_replacement = """\tmessage.removed_by_id = v.id\n\tmessage.removed_by_username = v.username\n\tg.db.add(ModAction(\n\t\tkind='chat_remove',\n\t\tuser_id=v.id,\n\t\ttarget_user_id=message.user_id,\n\t\t_note=f'<a href=\"/chat#{message.id}\">chat message</a>',\n\t))\n\tg.db.commit()\n\temit('delete', {"""
        if "kind='chat_remove'" not in patched:
            if remove_marker not in patched:
                raise RuntimeError("Could not locate chat removal commit for modlog logging")
            patched = patched.replace(remove_marker, remove_replacement, 1)

        if patched != source:
            _atomic_write(_CHAT_ROUTE, patched)
