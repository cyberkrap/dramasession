from flask import redirect

from files.__main__ import app, limiter
from files.helpers.community_assets import remove_approved_asset
from files.helpers.config.const import DEFAULT_RATELIMIT_SLOWER, PERMS
from files.helpers.get import get_ID
from files.routes.wrappers import admin_level_required


@app.post("/admin/community-assets/<kind>/<submission_id>/remove-approved")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@admin_level_required(PERMS["SITE_SETTINGS"])
def remove_approved_community_asset(kind, submission_id, v):
	if kind not in {"banner", "sidebar"}:
		abort(404)
	try:
		remove_approved_asset(kind, submission_id, v.username)
	except FileNotFoundError:
		abort(404)
	return redirect(("/sidebar_images" if kind == "sidebar" else "/banners") + "?msg=Community asset removed.")
