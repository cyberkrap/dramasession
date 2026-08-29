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

# Register the core request lifecycle before feature-specific before_request
# hooks. In particular, this guarantees g.db exists before the age gate reads
# submissions or comments.
from files.routes.allroutes import *

# import jinja2 then... (lmao this was in feeds.py before wtf)
from files.routes.jinja2 import *

# Repair legacy route source before the affected modules are imported.
from files.helpers.background_source_fix import patch_background_validation_source
from files.helpers.runtime_source_fixes import (
	patch_award_currency_source,
	patch_badge_gift_message_source,
	patch_comment_attachment_source,
	patch_youtube_anthem_source,
)
from files.helpers.award_system_fixes import (
	disable_retired_awards,
	patch_award_batch_source,
	patch_award_templates_source,
)
from files.helpers.requested_awards import (
	install_requested_awards,
	patch_requested_awards_pre_batch_source,
	patch_requested_award_templates_source,
)
from files.helpers.pin_award_stack_fixes import patch_stackable_pin_award_source
from files.helpers.requested_awards_postfix import patch_requested_awards_post_batch_source_v2
from files.helpers.final_ui_source_fixes import (
	patch_admin_emote_link_source,
	patch_asset_submission_directories_source,
	patch_asset_submission_removal_source,
	patch_badge_gift_note_source,
	patch_custom_emote_sources,
	patch_live_banner_source,
	patch_marseys_source,
)
from files.helpers.hat_submission_fixes import patch_hat_submission_source
from files.helpers.username_effect_template_fixes import patch_comment_username_effects_source
from files.helpers.transfer_currency_format_fixes import (
	install_transfer_currency_format_fix,
	patch_transfer_currency_source,
)
from files.helpers.toc_ui_fixes import install_toc_ui_fixes
from files.helpers.house_system import install_house_system

install_toc_ui_fixes()
disable_retired_awards()
install_requested_awards(app)
try:
	patch_requested_awards_pre_batch_source()
except RuntimeError:
	pass
try:
	patch_stackable_pin_award_source()
except RuntimeError:
	pass
try:
	patch_award_currency_source()
	patch_badge_gift_message_source()
except RuntimeError:
	pass
try:
	patch_award_batch_source()
except RuntimeError:
	pass
try:
	patch_requested_awards_post_batch_source_v2()
except RuntimeError:
	pass
try:
	patch_award_templates_source()
except RuntimeError:
	pass
try:
	patch_requested_award_templates_source()
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
try:
	patch_hat_submission_source()
except RuntimeError:
	pass
try:
	patch_comment_username_effects_source()
except RuntimeError:
	pass
patch_comment_attachment_source()
patch_youtube_anthem_source()
patch_background_validation_source()
patch_transfer_currency_source()
install_transfer_currency_format_fix(app)

# House award access is the final award-catalog/source normalization step. Run
# it after the other award patchers so the route imported below always sees the
# canonical TOC mapping (Furry/OwOify, Femboy/Rainbow, Racist/Early Life).
install_house_system()

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
from .snatchy import *
from .inline_images import *
from .search import *
from .settings import *
from .short_username_perk import *
from .connections import *
from .signup_rewards import *
from .static import *
from .discord_bot import *
# These modules intentionally load after static.py: site_stats replaces the
# legacy /stats endpoint, while house_pages registers the dynamic house views.
from .site_stats import *
from .house_pages import *
from .profile_moderation_fixes import *
from .site_banner import *
from .paypal import *
from .community_gallery import *
from .users import *
from .leaderboard_fixes import *
from .profile_view_history import *
from .profile_enhancements import *
from .bank_statement import *
from .lifetime_contributions import *
from .votes import *
from .feeds import *
if FEATURES['AWARDS']:
	from .awards import *
from .username_effects import *
from .username_effect_hydration import *
from .giphy import *
from .subs import *
if FEATURES['GAMBLING']:
	from .lottery import *
	from .casino import *
	from .roulette_bet_fixes import *
	from .roulette_rounds import *
from .polls import *
from .notifications import *
from .relationship_counts import *
if FEATURES['HATS']:
	from .hats import *
if FEATURES['ASSET_SUBMISSIONS']:
	from .asset_submissions import *
	from .emote_admin import *
	from .emote_admin_tools import *
	if FEATURES['HATS']:
		from .hat_admin_tools import *
from .report_fixes import *
from .special import *
from .push_notifs import *
from .age_verification import *

# Keep Didit API failures on the branded page so Cloudflare does not replace
# the useful upstream error message with its generic 502 interstitial.
from files.helpers.age_verification_response import install_age_verification_response_fix
install_age_verification_response_fix()

# Patch connection identity hydration after connection routes are registered.
from files.helpers.connection_repairs import install_connection_repairs
install_connection_repairs()

# Replace the legacy alt handlers only after the original endpoints exist.
from .alt_link_fixes import install_alt_link_fixes
install_alt_link_fixes()

from files.classes import User
from files.__main__ import engine
from files.helpers.admin_patron_rewards import install_admin_patron_rewards
from files.helpers import admin_permission_management as admin_permission_management
from files.helpers.admin_permission_management import install_admin_permission_management
from files.helpers.award_batch_runtime import repair_existing_award_batches
from files.helpers.badge_branding import install_badge_branding
from files.helpers.ban_hats import install_ban_hat_support
from files.helpers.bank_statement_noise_fixes import install_bank_statement_noise_fixes
from files.helpers.board_branding import install_board_branding
from files.helpers.chat_admin_modaction_types import install_chat_admin_modaction_types
from files.helpers.contribution_badges import install_cumulative_contribution_badges
from files.helpers.default_follow import install_default_following
from files.helpers.default_user_background import install_default_user_background
from files.helpers.dm_image_audit import install_dm_image_audit
from files.helpers.economy_ledger import install_economy_ledger
from files.helpers.economy_ledger_flush import install_economy_ledger_flush_fix
from files.helpers.gift_ledger_enrichment import install_gift_ledger_enrichment
from files.helpers.patron_branding import install_patron_branding
from files.helpers.persistent_site_content import install_persistent_site_content
from files.helpers.private_economy_modactions import install_private_economy_modactions
from files.helpers.signup_rewards import install_signup_rewards
from files.helpers.support_badge_removal_fix import install_support_badge_removal_fix
from files.helpers.user_activity_defaults import install_user_activity_defaults
from files.helpers.username_effects import install_username_effects
from files.helpers.wishcoin_asset import install_wishcoin_asset
install_badge_branding(engine)
install_ban_hat_support()
install_board_branding(app)
install_cumulative_contribution_badges()
install_support_badge_removal_fix()
install_default_following(app, engine)
install_default_user_background()
install_economy_ledger(app, engine)
install_bank_statement_noise_fixes(engine)
install_admin_patron_rewards()
install_chat_admin_modaction_types()
install_gift_ledger_enrichment()
install_economy_ledger_flush_fix()
repair_existing_award_batches(engine)
install_patron_branding()
install_persistent_site_content()
if not FEATURES['ASSET_SUBMISSIONS']:
	admin_permission_management._TOC_HIDDEN_PERMISSIONS.update({
		'MODERATE_PENDING_SUBMITTED_ASSETS',
		'UPDATE_ASSETS',
		'VIEW_PENDING_SUBMITTED_HATS',
		'VIEW_PENDING_SUBMITTED_MARSEYS',
	})
install_admin_permission_management()
install_dm_image_audit()
install_private_economy_modactions(engine)
install_user_activity_defaults(engine, User)
install_signup_rewards(engine)
install_signup_reward_signup_hook()
install_username_effects(engine, User)
install_wishcoin_asset(app)
if FEATURES['ASSET_SUBMISSIONS']:
	from files.helpers.emote_management import ensure_emote_directories, install_custom_emote_rendering
	ensure_emote_directories()
	install_emote_management()
install_report_fixes()
User.ban_notice = User.ban_notice_html