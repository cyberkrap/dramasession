"""Create or reuse the live PayPal webhook from Railway environment variables.

Run from the Railway service console:
    python scripts/create_paypal_webhook.py

The script never prints the PayPal client secret. It is safe to run more than once.
"""

from __future__ import annotations

import os
import sys
from typing import Any

import requests


WEBHOOK_URL = os.environ.get(
    "PAYPAL_WEBHOOK_URL",
    "https://theobsessionclub.com/api/paypal/webhook",
).strip()

EVENT_NAMES = (
    "BILLING.SUBSCRIPTION.CREATED",
    "BILLING.SUBSCRIPTION.ACTIVATED",
    "BILLING.SUBSCRIPTION.UPDATED",
    "BILLING.SUBSCRIPTION.CANCELLED",
    "BILLING.SUBSCRIPTION.EXPIRED",
    "BILLING.SUBSCRIPTION.SUSPENDED",
    "BILLING.SUBSCRIPTION.PAYMENT.FAILED",
    "PAYMENT.SALE.COMPLETED",
    "PAYMENT.SALE.REFUNDED",
    "PAYMENT.SALE.REVERSED",
)


class SetupError(RuntimeError):
    pass


def _required_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise SetupError(f"Missing Railway variable: {name}")
    return value


def _response_error(response: requests.Response) -> str:
    try:
        payload: Any = response.json()
    except ValueError:
        payload = response.text

    if isinstance(payload, dict):
        message = payload.get("message") or payload.get("name") or str(payload)
        debug_id = payload.get("debug_id")
        details = payload.get("details")
        parts = [str(message)]
        if details:
            parts.append(str(details))
        if debug_id:
            parts.append(f"debug_id={debug_id}")
        return " | ".join(parts)
    return str(payload)


def _expect(response: requests.Response, *statuses: int) -> requests.Response:
    if response.status_code not in statuses:
        raise SetupError(
            f"PayPal API returned HTTP {response.status_code}: {_response_error(response)}"
        )
    return response


def _access_token(client_id: str, client_secret: str) -> str:
    response = requests.post(
        "https://api-m.paypal.com/v1/oauth2/token",
        auth=(client_id, client_secret),
        data={"grant_type": "client_credentials"},
        headers={"Accept": "application/json", "Accept-Language": "en_US"},
        timeout=30,
    )
    payload = _expect(response, 200).json()
    token = str(payload.get("access_token") or "")
    if not token:
        raise SetupError("PayPal returned no access token")
    return token


def _headers(token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }


def _list_webhooks(token: str) -> list[dict[str, Any]]:
    response = requests.get(
        "https://api-m.paypal.com/v1/notifications/webhooks",
        headers=_headers(token),
        timeout=30,
    )
    payload = _expect(response, 200).json()
    webhooks = payload.get("webhooks") or []
    return [item for item in webhooks if isinstance(item, dict)]


def _event_payload() -> list[dict[str, str]]:
    return [{"name": name} for name in EVENT_NAMES]


def _update_webhook(token: str, webhook_id: str) -> None:
    response = requests.patch(
        f"https://api-m.paypal.com/v1/notifications/webhooks/{webhook_id}",
        headers=_headers(token),
        json=[
            {"op": "replace", "path": "/url", "value": WEBHOOK_URL},
            {"op": "replace", "path": "/event_types", "value": _event_payload()},
        ],
        timeout=30,
    )
    _expect(response, 200, 204)


def _create_webhook(token: str) -> dict[str, Any]:
    response = requests.post(
        "https://api-m.paypal.com/v1/notifications/webhooks",
        headers=_headers(token),
        json={"url": WEBHOOK_URL, "event_types": _event_payload()},
        timeout=30,
    )
    return _expect(response, 200, 201).json()


def main() -> int:
    try:
        mode = os.environ.get("PAYPAL_MODE", "live").strip().lower()
        if mode != "live":
            raise SetupError(
                f"PAYPAL_MODE is {mode!r}. Refusing to create a production webhook."
            )

        client_id = _required_env("PAYPAL_LIVE_CLIENT_ID")
        client_secret = _required_env("PAYPAL_LIVE_CLIENT_SECRET")
        token = _access_token(client_id, client_secret)

        matching = next(
            (item for item in _list_webhooks(token) if item.get("url") == WEBHOOK_URL),
            None,
        )

        if matching:
            webhook_id = str(matching.get("id") or "")
            if not webhook_id:
                raise SetupError("Existing webhook is missing its PayPal webhook ID")
            _update_webhook(token, webhook_id)
            action = "Updated existing live webhook"
        else:
            created = _create_webhook(token)
            webhook_id = str(created.get("id") or "")
            if not webhook_id:
                raise SetupError("PayPal created the webhook but returned no webhook ID")
            action = "Created live webhook"

        print(action)
        print(f"URL: {WEBHOOK_URL}")
        print(f"Events: {len(EVENT_NAMES)}")
        print()
        print("Add this exact Railway variable:")
        print(f"PAYPAL_LIVE_WEBHOOK_ID={webhook_id}")
        return 0
    except requests.RequestException as exc:
        print(f"Network error while contacting PayPal: {exc}", file=sys.stderr)
    except SetupError as exc:
        print(f"PayPal webhook setup failed: {exc}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
