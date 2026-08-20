import os
import re
from pathlib import Path

import fcntl
from flask import request


_LOCK_PATH = "/tmp/obsession-transfer-currency-format.lock"
_USERS_ROUTE_PATH = Path("files/routes/users.py")
_TRANSFER_AMOUNT_RE = re.compile(
    r"(has transferred\s+)(\d+)(\s+(?:Wishbux|Wishcoins)\b)"
)


def _atomic_write(path: Path, content: str) -> None:
    temp_path = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temp_path.write_text(content, encoding="utf-8")
    os.replace(temp_path, path)


def patch_transfer_currency_source() -> None:
    """Store newly-created transfer messages with readable thousands separators."""
    with open(_LOCK_PATH, "w", encoding="utf-8") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)

        source = _USERS_ROUTE_PATH.read_text(encoding="utf-8")
        original = source
        source = source.replace(
            'log_message = f"@{v.username} has transferred {amount} {currency_label} to @{receiver.username}"',
            'log_message = f"@{v.username} has transferred {amount:,} {currency_label} to @{receiver.username}"',
        )
        source = source.replace(
            'notif_text = f"@{v.username} has gifted you {amount-tax} {currency_label}!"',
            'notif_text = f"@{v.username} has gifted you {amount - tax:,} {currency_label}!"',
        )

        if source != original:
            _atomic_write(_USERS_ROUTE_PATH, source)


def _format_transfer_html(html: str) -> str:
    return _TRANSFER_AMOUNT_RE.sub(
        lambda match: f"{match.group(1)}{int(match.group(2)):,}{match.group(3)}",
        html,
    )


def install_transfer_currency_format_fix(app) -> None:
    """Format historical transfer rows on /transfers without rewriting old records."""
    if getattr(app, "_toc_transfer_currency_format_fix", False):
        return

    @app.after_request
    def toc_format_transfer_currency(response):
        path = request.path
        if (
            (path == "/transfers" or path.startswith("/transfers/"))
            and response.mimetype == "text/html"
            and response.status_code < 400
        ):
            response.set_data(_format_transfer_html(response.get_data(as_text=True)))
        return response

    app._toc_transfer_currency_format_fix = True
