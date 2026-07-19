"""Shared patron capabilities and support-page configuration."""

import time

from files.helpers.config.const import (
    COMMENT_BODY_HTML_LENGTH_LIMIT,
    COMMENT_BODY_LENGTH_LIMIT,
    DEFAULT_CONFIG_VALUE,
    DONATE_LINK,
    MAX_IMAGE_AUDIO_SIZE_MB,
    MAX_IMAGE_AUDIO_SIZE_MB_PATRON,
    MAX_VIDEO_SIZE_MB,
    MAX_VIDEO_SIZE_MB_PATRON,
    POST_BODY_HTML_LENGTH_LIMIT,
    POST_BODY_LENGTH_LIMIT,
)


# These are the only patron-gated capabilities currently enforced by the app.
PATRON_CAPABILITIES = {
    "signature": 1,
    "gifting_tax_exempt": 1,
    "custom_background": 2,
    "benefactor": 2,
}

PATRON_LIMITS = {
    "image_audio_mb": (MAX_IMAGE_AUDIO_SIZE_MB, MAX_IMAGE_AUDIO_SIZE_MB_PATRON),
    "video_mb": (MAX_VIDEO_SIZE_MB, MAX_VIDEO_SIZE_MB_PATRON),
    # The current application enforces four files and these text limits for
    # every user. Keep the values centralized without inventing higher caps.
    "attachment_count": (4, 4),
    "post_body_length": (POST_BODY_LENGTH_LIMIT, POST_BODY_LENGTH_LIMIT),
    "post_body_html_length": (POST_BODY_HTML_LENGTH_LIMIT, POST_BODY_HTML_LENGTH_LIMIT),
    "comment_body_length": (COMMENT_BODY_LENGTH_LIMIT, COMMENT_BODY_LENGTH_LIMIT),
    "comment_body_html_length": (COMMENT_BODY_HTML_LENGTH_LIMIT, COMMENT_BODY_HTML_LENGTH_LIMIT),
}


def patron_level(user):
    """Return the currently active patron level, honoring expiry."""
    level = int(getattr(user, "patron", 0) or 0)
    expires = int(getattr(user, "patron_utc", 0) or 0)
    if level <= 0 or (expires and expires <= int(time.time())):
        return 0
    return level


def patron_has(user, capability):
    required_level = PATRON_CAPABILITIES.get(capability)
    return required_level is not None and patron_level(user) >= required_level


def patron_limit(user, limit_name):
    """Return the server-side limit for a user and known limit name."""
    limits = PATRON_LIMITS[limit_name]
    return limits[1] if patron_level(user) >= 1 else limits[0]


SUPPORT_BASE_BENEFITS = (
    "Supporter badge and nameplate",
    "5,000 Wishbux monthly",
    "10% shop and award discount",
    "Profile signature",
    "16 MB image and audio limit",
    "64 MB video limit",
    "No transfer tax when gifting Wishcoins or Wishbux",
)

SUPPORT_TIERS = (
    {
        "name": "Supporter", "price": 5, "wishbux": 5000, "discount": 10,
        "badge": "21", "popular": False, "new_perks": SUPPORT_BASE_BENEFITS,
    },
    {
        "name": "Insider", "price": 10, "wishbux": 11000, "discount": 15,
        "badge": "22", "popular": False,
        "new_perks": ("Insider badge and nameplate", "11,000 Wishbux monthly",
                       "15% shop and award discount", "Custom site background",
                       "Benefactor award access"),
    },
    {
        "name": "Devoted", "price": 20, "wishbux": 24000, "discount": 20,
        "badge": "23", "popular": True,
        "new_perks": ("Devoted badge and nameplate", "24,000 Wishbux monthly",
                       "20% shop and award discount"),
    },
    {
        "name": "Obsessed", "price": 50, "wishbux": 65000, "discount": 25,
        "badge": "24", "popular": False,
        "new_perks": ("Obsessed badge and nameplate", "65,000 Wishbux monthly",
                       "25% shop and award discount"),
    },
    {
        "name": "Inner Circle", "price": 100, "wishbux": 140000, "discount": 30,
        "badge": "25", "popular": False,
        "new_perks": ("Inner Circle badge and nameplate", "140,000 Wishbux monthly",
                       "30% shop and award discount"),
    },
)


def _with_benefits(tiers):
    inherited = []
    result = []
    for tier in tiers:
        inherited.extend(tier["new_perks"])
        item = dict(tier)
        item["perks"] = tier["new_perks"]
        item["all_benefits"] = tuple(inherited)
        item["benefit_count"] = len(item["all_benefits"])
        result.append(item)
    return tuple(result)


SUPPORT_TIERS = _with_benefits(SUPPORT_TIERS)


def _configured_payment_url():
    if not DONATE_LINK or DONATE_LINK == DEFAULT_CONFIG_VALUE:
        return None
    if DEFAULT_CONFIG_VALUE.lower() in DONATE_LINK.lower():
        return None
    if not DONATE_LINK.startswith(("https://", "http://")):
        return None
    return DONATE_LINK


SUPPORT_PAYMENT_URL = _configured_payment_url()
SUPPORT_PAYMENT_CONFIGURED = SUPPORT_PAYMENT_URL is not None