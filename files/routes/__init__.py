# import constants then...
from files.helpers.config.const import FEATURES

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
	patch_comment_attachment_source,
	patch_youtube_anthem_source,
)
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
from .static import *
from .paypal import *
from .community_gallery import *
from .users import *
from .votes import *
from .feeds import *
if FEATURES['AWARDS']:
	from .awards import *
from .giphy import *
from .subs import *
if FEATURES['GAMBLING']:
	from .lottery import *
	from .casino import *
from .polls import *
from .notifications import *
if FEATURES['HATS']:
	from .hats import *
if FEATURES['ASSET_SUBMISSIONS']:
	from .asset_submissions import *
from .special import *
from .push_notifs import *

from files.classes import User
from files.helpers.ban_hats import install_ban_hat_support
from files.helpers.contribution_badges import install_cumulative_contribution_badges
from files.helpers.default_user_background import install_default_user_background
install_ban_hat_support()
install_cumulative_contribution_badges()
install_default_user_background()
User.ban_notice = User.ban_notice_html