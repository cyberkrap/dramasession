from flask import abort, redirect, render_template, request

from files.__main__ import app, limiter
from files.helpers.cloudflare import purge_files_in_cache
from files.helpers.community_assets import (
	COMMUNITY_ASSET_CONFIG,
	list_approved_assets,
	remove_approved_asset,
)
from files.helpers.config.const import DEFAULT_RATELIMIT, DEFAULT_RATELIMIT_SLOWER, PERMS, SITE_FULL
from files.helpers.get import get_ID
from files.routes.wrappers import admin_level_required, auth_desired


@app.get("/banners")
@app.get("/sidebar_images")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_desired
def community_asset_gallery(v):
	kind = "sidebar" if request.path == "/sidebar_images" else "banner"
	config = COMMUNITY_ASSET_CONFIG[kind]
	return render_template(
		"view_art.html",
		v=v,
		kind=kind,
		title="Sidebar Images" if kind == "sidebar" else "Banners",
		label=config["label"],
		submit_url="/submit/sidebar-art" if kind == "sidebar" else "/submit/banner",
		assets=list_approved_assets(kind),
	)


@app.post("/admin/community-assets/<kind>/<submission_id>/remove-approved")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@admin_level_required(PERMS["SITE_SETTINGS_SIDEBARS_BANNERS_BADGES"])
def remove_approved_community_asset(kind, submission_id, v):
	if kind not in {"banner", "sidebar"}:
		abort(404)

	try:
		removed_urls = remove_approved_asset(kind, submission_id, v.username)
	except FileNotFoundError:
		abort(404)

	if removed_urls:
		purge_files_in_cache([f"{SITE_FULL}{url}" for url in removed_urls])

	return redirect(("/sidebar_images" if kind == "sidebar" else "/banners") + "?msg=Community+asset+removed")
