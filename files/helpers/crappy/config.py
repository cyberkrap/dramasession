import os


CRAPPY_USERNAME = "Crappy"


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def crappy_enabled() -> bool:
    return _env_bool("CRAPPY_ENABLED", False)


def crappy_provider_name() -> str:
    return (os.environ.get("CRAPPY_PROVIDER") or "gemini").strip().lower()
