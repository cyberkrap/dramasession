"""PayPal subscription checkout confirmation and webhook routes."""

import time

from flask import abort, g, jsonify, redirect, request

from files.__main__ import app, limiter
from files.classes import PaypalSubscription, PaypalWebhookEvent
from files.helpers.config.const import DEFAULT_RATELIMIT_SLOWER
from files.helpers.paypal import (
    PayPalError,
    cancel_paypal_subscription,
    get