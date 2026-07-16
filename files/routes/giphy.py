import requests
from files.helpers.config.const import *
from files.routes.wrappers import *
from files.__main__ import app


@app.get("/giphy")
@app.get("/giphy<path>")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def giphy(v=None, path=None):
	searchTerm = request.values.get("searchTerm", "").strip()
	try:
		limit = int(request.values.get("limit", 48))
	except (TypeError, ValueError):
		limit = 48
	limit = max(1, min(48, limit))

	placeholder_keys = {"", DEFAULT_CONFIG_VALUE, "replace-with-giphy-key", "your-giphy-key"}
	if not GIPHY_KEY or GIPHY_KEY.lower() in placeholder_keys:
		return {"error": "not_configured", "message": "GIF integration is not configured."}, 503

	try:
		endpoint = "https://api.giphy.com/v1/gifs/search" if searchTerm else "https://api.giphy.com/v1/gifs/trending"
		params = {"api_key": GIPHY_KEY, "limit": limit}
		if searchTerm:
			params["q"] = searchTerm
		response = requests.get(endpoint, params=params, timeout=5)
		response.raise_for_status()
		return response.json()
	except requests.Timeout:
		return {"error": "unavailable", "message": "GIF service is temporarily unavailable."}, 503
	except (requests.RequestException, ValueError):
		return {"error": "unavailable", "message": "GIF service is temporarily unavailable."}, 503
