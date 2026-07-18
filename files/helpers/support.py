"""Shared support page configuration.

These capabilities describe the patron behavior that is currently enforced by
the application. Payment processing remains intentionally separate.
"""

from files.helpers.config.const import DEFAULT_CONFIG_VALUE, DONATE_LINK


SUPPORT_VERIFIED_PERKS = (
    "16 MB image and audio upload limits",
    "64 MB video upload limit",
    "Custom profile background",
    "Profile signature",
    "No transfer tax when gifting Wishcoins or Wishbux",
)


SUPPORT_TIERS = (
    {
        "name": "Supporter",
        "price": 5,
        "wishbux": 5000,
        "badge": "21",
        "popular": False,
        "perks": SUPPORT_VERIFIED_PERKS,
    },
    {
        "name": "Insider",
        "price": 10,
        "wishbux": 11000,
        "badge": "22",
        "popular": False,
        "perks": ("Everything in the previous tier",),
    },
    {
        "name": "Devoted",
        "price": 20,
        "wishbux": 24000,
        "badge": "23",
        "popular": True,
        "perks": ("Everything in the previous tier",),
    },
    {
        "name": "Obsessed",
        "price": 50,
        "wishbux": 65000,
        "badge": "24",
        "popular": False,
        "perks": ("Everything in the previous tier",),
    },
    {
        "name": "Inner Circle",
        "price": 100,
        "wishbux": 140000,
        "badge": "25",
        "popular": False,
        "perks": ("Everything in the previous tier",),
    },
)


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