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
	limit = 48
	try:
		limit = int(request.values.get("limit", 48))
	except:
		pass
	if searchTerm and limit:
		url = f"https://api.giphy.com/v1/gifs/search?q={searchTerm}&api_key={GIPHY_KEY}&limit={limit}"
	elif searchTerm and not limit:
		url = f"https://api.giphy.com/v1/gifs/search?q={searchTerm}&api_key={GIPHY_KEY}&limit=48"
	else:
		url = f"https://api.giphy.com/v1/gifs?api_key={GIPHY_KEY}&limit=48"
	return requests.get(url, timeout=5).json()
