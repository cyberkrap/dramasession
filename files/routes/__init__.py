# import constants then...
from files.helpers.config.const import FEATURES

# Never block a request while tldextract tries to download the Public Suffix List.
from files.helpers.offline_tldextract import configure_tldextract_offline
configure_tldextract_offline()

# import flask then...
from flask import g, request, render_template, make_response, redirect, send_file

# import our app then...
from files.__main__ import app

# import route helpers then...
from files.routes.routehelpers import *

# import wrappers then...
from files.routes.wrappers import *

# import jinja2 then... (lmao this was in feeds.py before wtf)
from files.routes.jinja2 import *

# Repair legacy route source before the affected modules are imported.
from files.helpers.runtime_source_fixes import (
	patch_award_currency_source,
	patch_badge_gift_message_source,
	patch_comment_attachment_source,
	patch_youtube_anthem_source,
)
from files.helpers.final_ui_source_fixes import (
	patch_admin_emote_link_source,
	patch_asset_submission_directories_source,
	patch_asset_submission_removal_source,
	patch_badge_gift_note_source,
	patch_custom_emote_sources,
	patch_live_banner_source,
	patch_marseys_source,
)
try:
	patch_award_currency_source()
	patch_badge_gift_message_source()
except RuntimeError:
	pass
try:
	patch_admin_emote_link_source()
	patch_asset_submission_directories_source()
	patch_asset_submission_removal_source()
	patch_badge_gift_note_source()
	patch_custom_emote_sources()
	patch_live_banner_source()
	patch_marseys_source()
except RuntimeError:
	pass
patch_comment_attachment_source()
patch_youtube_anthem_source()

# import routes :)
from .admin import *
from .comments import *
from .errors import *
from .reporting import *
from .front import *
from .login import *
from .mail import *
from .oauth import *
from .posts import *
from .inline_images import *
from .search import *
from .settings import *
from .connections import *
from .static import *
from .site_banner import *
from .paypal import *
from .community_gallery import *
from .users import *
from .profile_enhancements import *
from .lifetime_contributions import *
from .votes import *
from .feeds import *
if FEATURES['AWARDS']:
	from .awards import *
from .username_effects import *
from .giphy import *
from .subs import *
if FEATURES['GAMBLING']:
	from .lottery import *
	from .casino import *
from .polls import *
from .notifications import *
from .relationship_counts import *
if FEATURES['HATS']:
	from .hats import *
if FEATURES['ASSET_SUBMISSIONS']:
	from .asset_submissions import *
	from .emote_admin import *
	from .emote_admin_tools import *
from .report_fixes import *
from .special import *
from .push_notifs import *

# Patch connection identity hydration after connection routes are registered.
from files.helpers.connection_repairs import install_connection_repairs
install_connection_repairs()

# Replace the legacy alt handlers only after the original endpoints exist.
from .alt_link_fixes import install_alt_link_fixes
install_alt_link_fixes()

from files.classes import User
from files.__main__ import engine
from files.helpers.badge_branding import install_badge_branding
from files.helpers.ban_hats import install_ban_hat_support
from files.helpers.board_branding import install_board_branding
from files.helpers.contribution_badges import install_cumulative_contribution_badges
from files.helpers.default_follow import install_default_following
from files.helpers.default_user_background import install_default_user_background
from files.helpers.patron_branding import install_patron_branding
from files.helpers.persistent_site_content import install_persistent_site_content
from files.helpers.username_effects import install_username_effects
from files.helpers.wishcoin_asset import install_wishcoin_asset
install_badge_branding(engine)
install_ban_hat_support()
install_board_branding(app)
install_cumulative_contribution_badges()
install_default_following(app, engine)
install_default_user_background()
install_patron_branding()
install_persistent_site_content()
install_username_effects(engine, User)
install_wishcoin_asset(app)
if FEATURES['ASSET_SUBMISSIONS']:
	from files.helpers.emote_management import ensure_emote_directories, install_custom_emote_rendering
	ensure_emote_directories()
	install_emote_management()
install_report_fixes()
User.ban_notice = User.ban_notice_html
