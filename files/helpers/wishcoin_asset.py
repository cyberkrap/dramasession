"""Serve the uploaded Obsession currency artwork in place of legacy icons."""

import re

from flask import redirect, request

from files.helpers.config.const import SITE_NAME


WISHCOIN_ASSET_PATH = "/i/Obsession/wishcoin2-optimize.webp"
WISHCOIN_ASSET_URL = f"{WISHCOIN_ASSET_PATH}?v=20260726-webp"
WISHBUX_ASSET_PATH = "/i/Obsession/wishbux.webp"
WISHBUX_ASSET_URL = f"{WISHBUX_ASSET_PATH}?v=20260726"

_LEGACY_REQUEST_REDIRECTS = {
	"/i/Obsession/coins.webp": WISHCOIN_ASSET_URL,
	"/i/Obsession/wishcoin.webp": WISHCOIN_ASSET_URL,
	"/i/coins.webp": WISHCOIN_ASSET_URL,
	"/i/wishcoin.webp": WISHCOIN_ASSET_URL,
	"/i/Obsession/marseybux.webp": WISHBUX_ASSET_URL,
	"/i/Obsession/marseybux.png": WISHBUX_ASSET_URL,
	"/i/marseybux.webp": WISHBUX_ASSET_URL,
	"/i/marseybux.png": WISHBUX_ASSET_URL,
}

_LEGACY_WISHCOIN_ASSET = re.compile(
	r"(?:/i/(?:Obsession/)?|/assets/images/Obsession/|assets/images/Obsession/)"
	r"(?:coins|wishcoin)\.webp(?:\?v=[^\"'\s)<>,]+)?",
	re.IGNORECASE,
)

_LEGACY_WISHBUX_ASSET = re.compile(
	r"(?:/i/(?:Obsession/)?|/assets/images/Obsession/|assets/images/Obsession/)"
	r"marseybux\.(?:webp|png|gif)(?:\?v=[^\"'\s)<>,]+)?",
	re.IGNORECASE,
)

_TEXT_MIMETYPES = {
	"text/html",
	"text/css",
	"text/javascript",
	"application/javascript",
	"application/json",
}


def install_wishcoin_asset(app):
	"""Redirect legacy requests and rewrite rendered references to uploaded WebPs."""
	if SITE_NAME != "Obsession" or getattr(app, "_obsession_wishcoin_asset_installed", False):
		return

	app._obsession_wishcoin_asset_installed = True

	@app.before_request
	def obsession_redirect_legacy_currency_assets():
		target = _LEGACY_REQUEST_REDIRECTS.get(request.path)
		if target:
			return redirect(target, code=302)
		return None

	@app.after_request
	def obsession_rewrite_currency_asset_references(response):
		if response.direct_passthrough or response.mimetype not in _TEXT_MIMETYPES:
			return response

		body = response.get_data(as_text=True)
		updated = _LEGACY_WISHCOIN_ASSET.sub(WISHCOIN_ASSET_URL, body)
		updated = _LEGACY_WISHBUX_ASSET.sub(WISHBUX_ASSET_URL, updated)
		if updated != body:
			response.set_data(updated)
			response.headers.pop("Content-Length", None)
		return response
