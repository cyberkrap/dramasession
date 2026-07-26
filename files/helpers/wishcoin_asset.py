"""Serve the uploaded Obsession Wishcoin artwork everywhere the legacy icon appears."""

import re

from flask import redirect, request

from files.helpers.config.const import SITE_NAME


WISHCOIN_ASSET_PATH = "/i/Obsession/wishcoin2-optimize.webp"
WISHCOIN_ASSET_URL = f"{WISHCOIN_ASSET_PATH}?v=20260726-webp"

_LEGACY_REQUEST_PATHS = {
	"/i/Obsession/coins.webp",
	"/i/Obsession/wishcoin.webp",
	"/i/coins.webp",
	"/i/wishcoin.webp",
}

_LEGACY_RENDERED_ASSET = re.compile(
	r"(?:/i/(?:Obsession/)?|/assets/images/Obsession/|assets/images/Obsession/)"
	r"(?:coins|wishcoin)\.webp(?:\?v=[^\"'\s)<>,]+)?",
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
	"""Redirect legacy requests and rewrite rendered references to the uploaded WebP."""
	if SITE_NAME != "Obsession" or getattr(app, "_obsession_wishcoin_asset_installed", False):
		return

	app._obsession_wishcoin_asset_installed = True

	@app.before_request
	def obsession_redirect_legacy_wishcoin_asset():
		if request.path in _LEGACY_REQUEST_PATHS:
			return redirect(WISHCOIN_ASSET_URL, code=302)
		return None

	@app.after_request
	def obsession_rewrite_wishcoin_asset_references(response):
		if response.direct_passthrough or response.mimetype not in _TEXT_MIMETYPES:
			return response

		body = response.get_data(as_text=True)
		updated = _LEGACY_RENDERED_ASSET.sub(WISHCOIN_ASSET_URL, body)
		if updated != body:
			response.set_data(updated)
			response.headers.pop("Content-Length", None)
		return response
