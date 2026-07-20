from flask import render_template, request

from files.__main__ import app, limiter
from files.helpers.community_assets import COMMUNITY_ASSET_CONFIG, list_approved_assets
from files.helpers.config.const import DEFAULT_RATELIMIT
from files.helpers.get import get_ID
from files.routes.wrappers import auth_required


@app.get("/banners")
@app.get("/sidebar_images")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def community_asset_gallery(v):
	kind = "sidebar" if request.path == "/sidebar_images" else "banner"
	config = COMMUNITY_ASSET_CONFIG[kind]
	title = "Sidebar Images" if kind == "sidebar" else "Banners"
	submit_url = "/submit/sidebar-art" if kind == "sidebar" else "/submit/banner"
	return render_template(
		"view_art.html",
		v=v,
		kind=kind,
		title=title,
		label=config["label"],
		submit_url=submit_url,
		assets=list_approved_assets(kind),
	)
