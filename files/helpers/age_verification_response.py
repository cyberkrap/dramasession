"""Preserve useful Didit startup errors behind Cloudflare."""

from flask import request

from files.__main__ import app


_installed = False


def install_age_verification_response_fix() -> None:
    """Keep the branded diagnostic page instead of triggering a proxy 502 page."""
    global _installed
    if _installed:
        return

    @app.after_request
    def preserve_age_verification_error_page(response):
        if request.endpoint == "age_verification_start" and response.status_code == 502:
            response.status_code = 200
            response.headers["X-Age-Verification-Upstream-Error"] = "didit"
            response.headers["Cache-Control"] = "no-store"
        return response

    _installed = True
