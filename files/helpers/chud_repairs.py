import os
from pathlib import Path

import fcntl


_LOCK_PATH = "/tmp/obsession-chud-repairs.lock"
_ADMIN_ROUTE_PATH = Path("files/routes/admin.py")

_TEMPLATE_REPLACEMENTS = {
    Path("files/templates/post_actions.html"): (
        (">Restrict user</button>", ">Chud user</button>"),
        (">Remove restriction</button>", ">Remove Chud</button>"),
    ),
    Path("files/templates/post_admin_actions_mobile.html"): (
        (">Restrict user</button>", ">Chud user</button>"),
        (">Remove restriction</button>", ">Remove Chud</button>"),
    ),
    Path("files/templates/comments.html"): (
        (">Restrict user</button>", ">Chud user</button>"),
        (">Remove restriction</button>", ">Remove Chud</button>"),
        ("User was restricted for this comment", "User was chudded for this comment"),
    ),
    Path("files/templates/userpage/admintools.html"): (
        ('value="Restrict user"', 'value="Chud user"'),
        ("Remove restriction", "Remove Chud"),
    ),
    Path("files/templates/chuds.html"): (
        ("Restricted Users", "Chudded Users"),
        ("Restriction ends", "Chud ends"),
    ),
    Path("files/templates/admin/admin_home.html"): (
        ("Restricted Users", "Chudded Users"),
    ),
    Path("files/templates/util/macros.html"): (
        ("User was restricted for this post", "User was chudded for this post"),
    ),
}


def _atomic_write(path: Path, content: str) -> None:
    temp_path = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temp_path.write_text(content, encoding="utf-8")
    os.replace(temp_path, path)


def patch_chud_source() -> None:
    """Keep TOC's Chud terminology canonical and support profile-wall comments.

    The legacy admin agendaposter handler assumed every comment belongs to a
    submission and dereferenced ``comment.post.sub``. Profile-wall comments have
    no parent submission, so that raised AttributeError and returned a 500.
    """
    with open(_LOCK_PATH, "w", encoding="utf-8") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)

        source = _ADMIN_ROUTE_PATH.read_text(encoding="utf-8")
        original = source
        source = source.replace(
            "\t\t\tif comment.post.sub == 'chudrama':\n",
            "\t\t\tif comment.post and comment.post.sub == 'chudrama':\n",
        )
        if source != original:
            _atomic_write(_ADMIN_ROUTE_PATH, source)

        for path, replacements in _TEMPLATE_REPLACEMENTS.items():
            if not path.exists():
                continue
            source = path.read_text(encoding="utf-8")
            original = source
            for old, new in replacements:
                source = source.replace(old, new)
            if source != original:
                _atomic_write(path, source)
