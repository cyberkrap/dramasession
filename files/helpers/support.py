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
    "signature": 3,