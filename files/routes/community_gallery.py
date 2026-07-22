import os

from flask import abort, redirect, render_template, request

from files.__main__ import app, cache, limiter
from files.helpers.cloudflare import purge_files_in_cache
from files.helpers.community_assets import (
	COMMUNITY_ASSET_CONFIG,
	active_community_asset_filenames,
	list_approved_assets,
	remove_approved_asset,
)
from files.helpers.config.const import DEFAULT_RATELIMIT, DEFAULT_RATELIMIT_SLOWER, PERMS, SITE_FULL
from files.routes.wrappers import admin_level_required, auth_desired


app.jinja_env.globals["active_community_asset_filenames"] = active_community_asset_filenames


@app.get("/terms")
@auth_desired
def terms_of_service(v):
	return render_template("terms.html", v=v)


@app.get("/privacy")
@auth_desired
def privacy_policy(v):
	return render_template("privacy.html", v=v)


@app.get("/banners")
@app.get("/sidebar_images")
@limiter.limit(DEFAULT_RATELIMIT)
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
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@admin_level_required(PERMS["SITE_SETTINGS_SIDEBARS_BANNERS_BADGES"])
def remove_approved_community_asset(kind, submission_id, v):
	if kind not in {"banner", "sidebar"}:
		abort(404)

	try:
		removed_urls = remove_approved_asset(kind, submission_id, v.username)
	except FileNotFoundError:
		abort(404)

	purge_urls = [f"{SITE_FULL}{url}" for url in removed_urls]
	if kind == "banner":
		# Logged-out pages historically preferred cached.webp before consulting
		# the active-banner list. Remove that generated copy and purge it so a
		# deleted banner cannot return from Redis, Cloudflare, or a redeploy.
		cached_banner = os.path.join(app.root_path, "assets", "images", "Obsession", "cached.webp")
		if os.path.isfile(cached_banner):
			os.remove(cached_banner)
		purge_urls.append(f"{SITE_FULL}/i/Obsession/cached.webp")

	# Cached page HTML can still contain a previously selected asset URL.
	# Clear it immediately so all renders use the persistent removal records.
	cache.clear()
	if purge_urls:
		purge_files_in_cache(purge_urls)

	return redirect(("/sidebar_images" if kind == "sidebar" else "/banners") + "?msg=Community+asset+removed")
