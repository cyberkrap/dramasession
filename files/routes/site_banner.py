import os
import random

from flask import make_response, send_file

from files.__main__ import app
from files.helpers.community_assets import active_community_asset_filenames, approved_directory
from files.helpers.config.const import SITE_NAME
from files.helpers.login_activity_ui import install_login_activity_home_link


@app.get('/site-banner')
def site_banner():
	"""Serve only banners that are currently active in the admin gallery.

	This endpoint avoids stale HTML, the legacy cached.webp file, and repository
	fallback banners that an administrator already removed.
	"""
	filenames = active_community_asset_filenames('banner') if SITE_NAME == 'Obsession' else []
	if filenames:
		path = os.path.join(approved_directory('banner'), random.choice(filenames))
	else:
		path = os.path.join(app.root_path, 'assets', 'images', SITE_NAME, 'banner.webp')

	response = make_response(send_file(path, conditional=False, max_age=0))
	response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
	response.headers['Pragma'] = 'no-cache'
	response.headers['Expires'] = '0'
	return response


# Register persistent account activity after normal authentication routes exist.
# login_activity records explicit login/signup events; login_visit_activity adds
# daily page visits for members whose long-lived session is already authenticated.
from .login_activity import *  # noqa: E402,F401,F403
from .login_visit_activity import *  # noqa: E402,F401,F403
install_login_activity_home_link()
