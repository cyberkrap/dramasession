"""Shared patron capabilities and PayPal support-page configuration."""

import hashlib
import hmac
import os
import time

from files.helpers.config.const import (
    COMMENT_BODY_HTML_LENGTH_LIMIT,
    COMMENT_BODY_LENGTH_LIMIT,
    MAX_IMAGE_AUDIO_SIZE_MB,
    MAX_IMAGE_AUDIO_SIZE_MB_PATRON,
    MAX_VIDEO_SIZE_MB,
    MAX_VIDEO_SIZE_MB_PATRON,
    POST_BODY_HTML_LENGTH_LIMIT,
    POST_BODY_LENGTH_LIMIT,
    SECRET_KEY,
)


PATRON_CAPABILITIES = {
    "signature": 3,
    "gifting_tax_exempt": 1,
    "custom_background": 2,
    "benefactor": 2,
}

PATRON_LIMITS = {
    "image_audio_mb": (MAX_IMAGE_AUDIO_SIZE_MB, MAX_IMAGE_AUDIO_SIZE_MB_PATRON),
    "video_mb": (MAX_VIDEO_SIZE_MB, MAX_VIDEO_SIZE_MB_PATRON),
    "attachment_count": (4, 4),
    "post_body_length": (POST_BODY_LENGTH_LIMIT, POST_BODY_LENGTH_LIMIT),
    "post_body_html_length": (POST_BODY_HTML_LENGTH_LIMIT, POST_BODY_HTML_LENGTH_LIMIT),
    "comment_body_length": (COMMENT_BODY_LENGTH_LIMIT, COMMENT_BODY_LENGTH_LIMIT),
    "comment_body_html_length": (COMMENT_BODY_HTML_LENGTH_LIMIT, COMMENT_BODY_HTML_LENGTH_LIMIT),
}


def patron_level(user):
    level = int(getattr(user, "patron", 0) or 0)
    expires = int(getattr(user, "patron_utc", 0) or 0)
    if level <= 0 or (expires and expires <= int(time.time())):
        return 0
    return level


def patron_has(user, capability):
    required_level = PATRON_CAPABILITIES.get(capability)
    return required_level is not None and patron_level(user) >= required_level


def patron_limit(user, limit_name):
    limits = PATRON_LIMITS[limit_name]
    return limits[1] if patron_level(user) >= 1 else limits[0]


SUPPORT_BASE_BENEFITS = (
    "Supporter badge and nameplate",
    "5,000 Wishbux monthly",
    "10% shop and award discount",
    "16 MB image and audio limit",
    "64 MB video limit",
    "No transfer tax when gifting Wishcoins or Wishbux",
)

SUPPORT_TIERS = (
    {
        "level": 1, "slug": "supporter", "name": "Supporter", "price": 5,
        "wishbux": 5000, "discount": 10, "badge": 21, "popular": False,
        "new_perks": SUPPORT_BASE_BENEFITS,
    },
    {
        "level": 2, "slug": "insider", "name": "Insider", "price": 10,
        "wishbux": 11000, "discount": 15, "badge": 22, "popular": False,
        "new_perks": ("Insider badge and nameplate", "11,000 Wishbux monthly",
                       "15% shop and award discount", "Custom site background",
                       "Benefactor award access"),
    },
    {
        "level": 3, "slug": "devoted", "name": "Devoted", "price": 20,
        "wishbux": 24000, "discount": 20, "badge": 23, "popular": True,
        "new_perks": ("Devoted badge and nameplate", "24,000 Wishbux monthly",
                       "20% shop and award discount", "Profile signature"),
    },
    {
        "level": 4, "slug": "obsessed", "name": "Obsessed", "price": 50,
        "wishbux": 65000, "discount": 25, "badge": 24, "popular": False,
        "new_perks": ("Obsessed badge and nameplate", "65,000 Wishbux monthly",
                       "25% shop and award discount"),
    },
    {
        "level": 5, "slug": "inner_circle", "name": "Inner Circle", "price": 100,
        "wishbux": 140000, "discount": 30, "badge": 25, "popular": False,
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


PAYPAL_MODE = os.environ.get("PAYPAL_MODE", "sandbox").strip().lower()
if PAYPAL_MODE not in {"sandbox", "live"}:
    PAYPAL_MODE = "sandbox"

PAYPAL_CLIENT_ID = os.environ.get("PAYPAL_CLIENT_ID", "").strip()
PAYPAL_CLIENT_SECRET = os.environ.get("PAYPAL_CLIENT_SECRET", "").strip()
PAYPAL_WEBHOOK_ID = os.environ.get("PAYPAL_WEBHOOK_ID", "").strip()
PAYPAL_CURRENCY = os.environ.get("PAYPAL_CURRENCY", "USD").strip().upper() or "USD"
PAYPAL_API_BASE = (
    "https://api-m.sandbox.paypal.com"
    if PAYPAL_MODE == "sandbox"
    else "https://api-m.paypal.com"
)

_PAYPAL_PLAN_ENV = {
    "supporter": "PAYPAL_PLAN_SUPPORTER",
    "insider": "PAYPAL_PLAN_INSIDER",
    "devoted": "PAYPAL_PLAN_DEVOTED",
    "obsessed": "PAYPAL_PLAN_OBSESSED",
    "inner_circle": "PAYPAL_PLAN_INNER_CIRCLE",
}
PAYPAL_PLAN_IDS = {
    slug: os.environ.get(variable, "").strip()
    for slug, variable in _PAYPAL_PLAN_ENV.items()
}

SUPPORT_TIERS = tuple(
    {**tier, "plan_id": PAYPAL_PLAN_IDS.get(tier["slug"], "")}
    for tier in _with_benefits(SUPPORT_TIERS)
)
SUPPORT_TIER_BY_PLAN_ID = {
    tier["plan_id"]: tier for tier in SUPPORT_TIERS if tier["plan_id"]
}
SUPPORT_TIER_BY_LEVEL = {tier["level"]: tier for tier in SUPPORT_TIERS}

PAYPAL_CHECKOUT_CONFIGURED = bool(
    PAYPAL_CLIENT_ID
    and PAYPAL_CLIENT_SECRET
    and all(PAYPAL_PLAN_IDS.values())
)
PAYPAL_READY = bool(PAYPAL_CHECKOUT_CONFIGURED and PAYPAL_WEBHOOK_ID)


def paypal_custom_id(user_id):
    user_id = int(user_id)
    message = f"paypal-subscription:{user_id}".encode("utf-8")
    digest = hmac.new(SECRET_KEY.encode("utf-8"), message, hashlib.sha256).hexdigest()[:24]
    return f"obsession:{user_id}:{digest}"


def paypal_user_id_from_custom_id(value):
    try:
        prefix, raw_user_id, supplied_digest = str(value or "").split(":", 2)
        if prefix != "obsession":
            return None
        user_id = int(raw_user_id)
    except (TypeError, ValueError):
        return None

    expected = paypal_custom_id(user_id).rsplit(":", 1)[1]
    if not hmac.compare_digest(supplied_digest, expected):
        return None
    return user_id


SUPPORT_PAYMENT_CONFIGURED = PAYPAL_READY
SUPPORT_PAYMENT_URL = None
