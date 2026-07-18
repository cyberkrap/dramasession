from __future__ import unicode_literals

import os
import glob
import importlib.util
import re
import shutil
from shutil import copyfile
from urllib.parse import parse_qs, urlparse
from uuid import uuid4

import pyotp
import requests
import yt_dlp
from yt_dlp.version import __version__ as YTDLP_VERSION

from files.helpers.actions import *
from files.helpers.alerts import *
from files.helpers.config.const import *
from files.helpers.get import *
from files.helpers.mail import *
from files.helpers.media import process_files, process_image
from files.helpers.regex import *
from files.helpers.sanitize import *
from files.helpers.sanitize import filter_emojis_only
from files.helpers.security import *
from files.helpers.useractions import *
from files.routes.wrappers import *

from .front import frontlist
from files.__main__ import app, cache, limiter


@app.get("/settings")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def settings(v:User):
	return redirect("/settings/personal")

@app.get("/settings/personal")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def settings_personal(v:User):
	return render_template("settings/personal.html", v=v, error=get_error(), msg=get_msg())

@app.delete('/settings/background')
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@auth_required
def remove_background(v):
	if v.background:
		if v.background.startswith('/images/'):
			os.remove(v.background)
		v.background = None
		g.db.add(v)
	return {"message": "Background removed!"}

@app.post('/settings/custom_background')
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@auth_required
def upload_custom_background(v):
	if g.is_tor: abort(403, "Image uploads are not allowed through TOR!")

	if not v.patron:
		abort(403, f"This feature is only available to {patron}s!")

	file = request.files["file"]

	name = f'/images/{time.time()}'.replace('.','') + '.webp'
	file.save(name)
	background = process_image(name, v)

	if background:
		if v.background and v.background.startswith('/images/'):
			os.remove(v.background)
		v.background = background
		g.db.add(v)

	return redirect('/settings/personal')

@app.post('/settings/profile_background')
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@auth_required
def upload_profile_background(v):
	if g.is_tor: abort(403, "Image uploads are not allowed through TOR!")

	file = request.files.get("file")
	if not file or not file.filename:
		abort(400, "Please choose an image to upload.")

	name = f'/images/{time.time()}'.replace('.','') + '.webp'
	file.save(name)
	background = process_image(name, v)

	if background:
		if v.profile_background and path.isfile(v.profile_background):
			os.remove(v.profile_background)
		v.profile_background = background
		g.db.add(v)
		badge_grant(badge_id=193, user=v)
	return redirect(f'/@{v.username}')

@app.delete('/settings/profile_background')
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@auth_required
def delete_profile_background(v):
	if v.profile_background and path.isfile(v.profile_background):
		os.remove(v.profile_background)
	v.profile_background = None
	g.db.add(v)
	return {"message": "Profile background removed!"}

@app.post("/settings/personal")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@auth_required
def settings_personal_post(v):
	if v.id == 253 and request.values.get("private"):
		abort(403)
	updated = False

	# begin common selectors #

	def update_flag(column_name:str, request_name:str):
		if not request.values.get(request_name, ''): return False
		request_flag = request.values.get(request_name, '') == 'true'
		if request_flag != getattr(v, column_name):
			setattr(v, column_name, request_flag)
			return True
		return False

	def update_potentially_permanent_flag(column_name:str, request_name:str, friendly_name:str, badge_id:Optional[int]):
		if not request.values.get(request_name): return False
		current_value = getattr(v, column_name)
		if FEATURES['USERS_PERMANENT_WORD_FILTERS'] and current_value > 1:
			abort(403, f"Cannot change the {friendly_name} setting after you've already set it permanently!")
		request_flag = int(request.values.get(request_name, '') == 'true')
		if current_value and request_flag and request.values.get("permanent", '') == 'true' and request.values.get("username") == v.username:
			if v.client: abort(403, f"Cannot set {friendly_name} permanently from the API")
			request_flag = int(time.time())
			setattr(v, column_name, request_flag)
			if badge_id: badge_grant(v, badge_id)
			return render_template("settings/personal.html", v=v, msg=f"You have set the {friendly_name} permanently! Enjoy your new badge!")
		elif current_value != request_flag:
			setattr(v, column_name, request_flag)
			return True
		return False

	def set_selector_option(column_name:str, api_name:str, valid_values:Iterable[str], error_msg:str="value"):
		opt = request.values.get(api_name)
		if opt: opt = opt.strip()
		if not opt: return False
		if opt in valid_values:
			setattr(v, column_name, opt)
			return True
		abort(400, f"'{opt}' is not a valid {error_msg}")

	# end common selectors #

	background = request.values.get("background", v.background)
	if background != v.background and background.endswith(".webp") and len(background) <= 20:
		v.background = '/i/backgrounds/' + request.values.get("background")
		updated = True
	elif request.values.get("reddit", v.reddit) != v.reddit:
		reddit = request.values.get("reddit")
		if reddit in {'old.reddit.com', 'reddit.com', 'i.reddit.com', 'teddit.net', 'libredd.it', 'unddit.com'}:
			updated = True
			v.reddit = reddit
	elif request.values.get("poor", v.poor) != v.poor:
		updated = True
		v.poor = request.values.get("poor", v.poor) == 'true'
		session['poor'] = v.poor

	slur_filter_updated = updated or update_potentially_permanent_flag("slurreplacer", "slurreplacer", "slur replacer", 192)
	if isinstance(slur_filter_updated, bool):
		updated = slur_filter_updated
	else:
		g.db.add(v)
		return slur_filter_updated

	profanity_filter_updated = updated or update_potentially_permanent_flag("profanityreplacer", "profanityreplacer", "profanity replacer", 190)
	if isinstance(profanity_filter_updated, bool):
		updated = profanity_filter_updated
	else:
		g.db.add(v)
		return profanity_filter_updated

	updated = updated or update_flag("hidevotedon", "hidevotedon")
	updated = updated or update_flag("cardview", "cardview")
	updated = updated or update_flag("newtab", "newtab")
	updated = updated or update_flag("newtabexternal", "newtabexternal")
	updated = updated or update_flag("nitter", "nitter")
	updated = updated or update_flag("imginn", "imginn")
	updated = updated or update_flag("controversial", "controversial")
	updated = updated or update_flag("sigs_disabled", "sigs_disabled")
	updated = updated or update_flag("over_18", "over_18")
	updated = updated or update_flag("is_private", "private")

	if not updated and request.values.get("spider", v.spider) != v.spider and v.spider <= 1:
		updated = True
		v.spider = int(request.values.get("spider") == 'true')
		if v.spider: badge_grant(user=v, badge_id=179)
		else:
			badge = v.has_badge(179)
			if badge: g.db.delete(badge)

	elif IS_FISTMAS() and not updated and request.values.get("event_music", v.event_music) != v.event_music and v.can_toggle_event_music:
		updated = True
		v.event_music = not v.event_music

	elif not updated and request.values.get("bio") == "" and not request.files.get('file'):
		v.bio = None
		v.bio_html = None
		g.db.add(v)
		return render_template("settings/personal.html", v=v, msg="Your bio has been updated!")

	elif not updated and request.values.get("sig") == "":
		v.sig = None
		v.sig_html = None
		g.db.add(v)
		return render_template("settings/personal.html", v=v, msg="Your sig has been updated!")

	elif not updated and request.values.get("friends") == "":
		v.friends = None
		v.friends_html = None
		g.db.add(v)
		return render_template("settings/personal.html", v=v, msg="Your friends list has been updated!")

	elif not updated and request.values.get("enemies") == "":
		v.enemies = None
		v.enemies_html = None
		g.db.add(v)
		return render_template("settings/personal.html", v=v, msg="Your enemies list has been updated!")

	elif not updated and v.patron and request.values.get("sig"):
		sig = request.values.get("sig")[:200].replace('\n','').replace('\r','')
		sig_html = sanitize(sig)
		if len(sig_html) > 1000:
			return render_template("settings/personal.html",
								v=v,
								error="Your sig is too long")

		v.sig = sig[:200]
		v.sig_html=sig_html
		g.db.add(v)
		return render_template("settings/personal.html",
							v=v,
							msg="Your sig has been updated.")

	elif not updated and FEATURES['USERS_PROFILE_BODYTEXT'] and request.values.get("friends"):
		friends = request.values.get("friends")[:1000]

		friends_html = sanitize(friends)

		if len(friends_html) > 5000:
			return render_template("settings/personal.html",
								v=v,
								error="Your friends list is too long")

		notify_users = NOTIFY_USERS(friends, v)

		if notify_users:
			cid = notif_comment(f"@{v.username} has added you to their friends list!")
			for x in notify_users:
				add_notif(cid, x)

		v.friends = friends[:1000]
		v.friends_html=friends_html
		g.db.add(v)
		return render_template("settings/personal.html",
							v=v,
							msg="Your friends list has been updated.")


	elif not updated and FEATURES['USERS_PROFILE_BODYTEXT'] and request.values.get("enemies"):
		enemies = request.values.get("enemies")[:1000]

		enemies_html = sanitize(enemies)

		if len(enemies_html) > 5000:
			return render_template("settings/personal.html",
								v=v,
								error="Your enemies list is too long")

		notify_users = NOTIFY_USERS(enemies, v)
		if notify_users:
			cid = notif_comment(f"@{v.username} has added you to their enemies list!")
			for x in notify_users:
				add_notif(cid, x)

		v.enemies = enemies[:1000]
		v.enemies_html=enemies_html
		g.db.add(v)
		return render_template("settings/personal.html",
							v=v,
							msg="Your enemies list has been updated.")


	elif not updated and FEATURES['USERS_PROFILE_BODYTEXT'] and \
			(request.values.get("bio") or request.files.get('file')):
		bio = request.values.get("bio")[:1500]
		bio += process_files(request.files, v)
		bio = bio.strip()
		bio_html = sanitize(bio)

		if len(bio_html) > 10000:
			return render_template("settings/personal.html",
								v=v,
								error="Your bio is too long")

		if len(bio_html) > 10000: abort(400)

		v.bio = bio[:1500]
		v.bio_html=bio_html
		g.db.add(v)
		return render_template("settings/personal.html",
							v=v,
							msg="Your bio has been updated.")


	frontsize = request.values.get("frontsize")
	if frontsize:
		frontsize = int(frontsize)
		if frontsize in PAGE_SIZES:
			v.frontsize = frontsize
			updated = True
			cache.delete_memoized(frontlist)
		else: abort(400)

	updated = updated or set_selector_option("defaultsortingcomments", "defaultsortingcomments", COMMENT_SORTS, "comment sort")
	updated = updated or set_selector_option("defaultsorting", "defaultsorting", SORTS, "post sort")
	updated = updated or set_selector_option("defaulttime", "defaulttime", TIME_FILTERS, "time filter")

	theme = request.values.get("theme")
	if not updated and theme:
		if theme in THEMES:
			if v.theme == "win98": v.themecolor = DEFAULT_COLOR
			v.theme = theme
			if theme == "win98": v.themecolor = "30409f"
			updated = True
		else: abort(400, f"{theme} is not a valid theme")

	house = request.values.get("house")
	if not updated and house and house in HOUSES and FEATURES['HOUSES']:
		if v.bite: abort(403)
		if v.house:
			if v.house.replace(' Founder', '') == house: abort(409, f"You're already in House {house}")
			cost = HOUSE_SWITCH_COST
		else:
			cost = HOUSE_JOIN_COST

		success = v.charge_account('coins', cost)
		if not success:
			success = v.charge_account('marseybux', cost)
		if not success: abort(403)

		if house == "None": house = ''
		v.house = house

		updated = True

	if updated:
		g.db.add(v)
		return {"message": "Your settings have been updated!"}
	else:
		abort(400, "You didn't change anything!")


@app.post("/settings/filters")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def filters(v:User):
	filters=request.values.get("filters")[:1000].strip()

	if filters == v.custom_filter_list:
		return redirect("/settings/advanced?error=You didn't change anything!")

	v.custom_filter_list=filters
	g.db.add(v)
	return redirect("/settings/advanced?msg=Your custom filters have been updated!")


def set_color(v:User, attr:str, color:Optional[str]):
	current = getattr(v, attr)
	color = color.strip().lower() if color else None
	if color:
		if color.startswith('#'): color = color[1:]
		if not color_regex.fullmatch(color):
			return render_template("settings/personal.html", v=v, error="Invalid color hex code!")
		if color and current != color:
			setattr(v, attr, color)
			g.db.add(v)
	return render_template("settings/personal.html", v=v, msg="Color successfully updated!")


@app.post("/settings/namecolor")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@auth_required
def namecolor(v):
	return set_color(v, "namecolor", request.values.get("namecolor"))

@app.post("/settings/themecolor")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@auth_required
def themecolor(v):
	return set_color(v, "themecolor", request.values.get("themecolor"))

@app.post("/settings/titlecolor")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@auth_required
def titlecolor(v):
	return set_color(v, "titlecolor", request.values.get("titlecolor"))

@app.post("/settings/verifiedcolor")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@auth_required
def verifiedcolor(v):
	if not v.verified: abort(403, "You don't have a checkmark")
	return set_color(v, "verifiedcolor", request.values.get("verifiedcolor"))

@app.post("/settings/security")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@auth_required
def settings_security_post(v):
	if request.values.get("new_password"):
		if request.values.get("new_password") != request.values.get("cnf_password"):
			return render_template("settings/security.html", v=v, error="Passwords do not match!")

		if not valid_password_regex.fullmatch(request.values.get("new_password")):
			return render_template("settings/security.html", v=v, error="Password must be between 8 and 100 characters!")

		if not v.verifyPass(request.values.get("old_password")):
			return render_template("settings/security.html", v=v, error="Incorrect password")

		v.passhash = hash_password(request.values.get("new_password"))

		g.db.add(v)
		return render_template("settings/security.html", v=v, msg="Your password has been changed!")

	if request.values.get("new_email"):
		if not v.verifyPass(request.values.get('password')):
			return render_template("settings/security.html", v=v, error="Invalid password!")

		new_email = request.values.get("new_email","").strip().lower()

		if new_email == v.email:
			return render_template("settings/security.html", v=v, error="This email is already yours!")

		url = f"{SITE_FULL}/activate"

		now = int(time.time())

		token = generate_hash(f"{new_email}+{v.id}+{now}")
		params = f"?email={quote(new_email)}&id={v.id}&time={now}&token={token}"

		link = url + params

		send_mail(to_address=new_email,
				subject="Verify your email address.",
				html=render_template("email/email_change.html",
									action_url=link,
									v=v)
				)

		return render_template("settings/security.html", v=v, msg="We have sent you an email, click the verification link inside it to complete the email change. Check your spam folder if you can't find it!")

	if request.values.get("2fa_token"):
		if not v.verifyPass(request.values.get('password')):
			return render_template("settings/security.html", v=v, error="Invalid password!")

		secret = request.values.get("2fa_secret")
		x = pyotp.TOTP(secret)
		if not x.verify(request.values.get("2fa_token"), valid_window=1):
			return render_template("settings/security.html", v=v, error="Invalid token!")

		v.mfa_secret = secret
		g.db.add(v)
		return render_template("settings/security.html", v=v, msg="Two-factor authentication enabled!")

	if request.values.get("2fa_remove"):
		if not v.verifyPass(request.values.get('password')):
			return render_template("settings/security.html", v=v, error="Invalid password!")

		token = request.values.get("2fa_remove")

		if not token or not v.validate_2fa(token):
			return render_template("settings/security.html", v=v, error="Invalid token!")

		v.mfa_secret = None
		g.db.add(v)
		g.db.commit()
		return render_template("settings/security.html", v=v, msg="Two-factor authentication disabled!")

@app.post("/settings/log_out_all_others")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@auth_required
def settings_log_out_others(v):
	submitted_password = request.values.get("password", "").strip()
	if not v.verifyPass(submitted_password):
		return redirect("/settings/security?error=Incorrect password!")

	v.login_nonce += 1
	session["login_nonce"] = v.login_nonce
	g.db.add(v)

	return redirect("/settings/security?msg=All other devices have been logged out!")


@app.post("/settings/images/profile")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@auth_required
def settings_images_profile(v):
	if g.is_tor: abort(403, "Image uploads are not allowed through TOR!")

	file = request.files["profile"]

	name = f'/images/{time.time()}'.replace('.','') + '.webp'
	file.save(name)
	highres = process_image(name, v)

	if not highres: abort(400)

	name2 = name.replace('.webp', 'r.webp')
	copyfile(name, name2)
	imageurl = process_image(name2, v, resize=100)

	if not imageurl: abort(400)

	if v.highres and v.highres.startswith('/images/') and os.path.isfile(v.highres):
		os.remove(v.highres)

	if v.profileurl and v.profileurl.startswith('/images/') and os.path.isfile(v.profileurl):
		os.remove(v.profileurl)
	v.highres = highres
	v.profileurl = imageurl
	g.db.add(v)

	cache.delete_memoized(get_profile_picture, v.id)
	cache.delete_memoized(get_profile_picture, v.username)
	cache.delete_memoized(get_profile_picture, v.original_username)

	return redirect("/settings/personal?msg=Profile picture successfully updated!")


@app.post("/settings/images/banner")
@feature_required('USERS_PROFILE_BANNER')
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@auth_required
def settings_images_banner(v):
	if g.is_tor: abort(403, "Image uploads are not allowed through TOR!")

	file = request.files["banner"]

	name = f'/images/{time.time()}'.replace('.','') + '.webp'
	file.save(name)
	bannerurl = process_image(name, v)

	if bannerurl:
		if v.bannerurl and '/images/' in v.bannerurl and path.isfile(v.bannerurl):
			os.remove(v.bannerurl)
		v.bannerurl = bannerurl
		g.db.add(v)

	return redirect("/settings/personal?msg=Banner successfully updated!")

@app.get("/settings/css")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def settings_css_get(v:User):
	return render_template("settings/css.html", v=v, msg=get_msg(), profilecss=v.profilecss)

@app.post("/settings/css")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@auth_required
def settings_css(v):
	if v.agendaposter: abort(400, "Agendapostered users can't edit CSS!")
	css = request.values.get("css", v.css).strip().replace('\\', '').strip()[:CSS_LENGTH_LIMIT]
	v.css = css
	g.db.add(v)

	return render_template("settings/css.html", v=v, msg="Custom CSS successfully updated!", profilecss=v.profilecss)

@app.post("/settings/profilecss")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@auth_required
def settings_profilecss(v):
	profilecss = request.values.get("profilecss", v.profilecss).strip().replace('\\', '').strip()[:CSS_LENGTH_LIMIT]
	valid, error = validate_css(profilecss)
	if not valid:
		return render_template("settings/css.html", error=error, v=v, profilecss=profilecss)
	v.profilecss = profilecss
	g.db.add(v)
	return redirect("/settings/css?msg=Profile CSS successfully updated!")

@app.get("/settings/security")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def settings_security(v:User):
	return render_template("settings/security.html",
						v=v,
						mfa_secret=pyotp.random_base32() if not v.mfa_secret else None,
						now=int(time.time()),
						error=get_error(),
						msg=get_msg()
						)

@app.post("/settings/block")
@limiter.limit("1/second;20/day")
@limiter.limit("1/second;20/day", key_func=get_ID)
@auth_required
def settings_block_user(v):
	user = get_user(request.values.get("username"), graceful=True)
	if not user: abort(404, "This user doesn't exist!")

	if user.unblockable:
		if not v.shadowbanned:
			send_notification(user.id, f"@{v.username} has tried to block you and failed because of your unblockable status!")
		abort(403, f"@{user.username} is unblockable!")

	if user.id == v.id: abort(400, "You can't block yourself")
	if user.id == AUTOJANNY_ID: abort(403, f"You can't block @{user.username}")
	if v.has_blocked(user): abort(409, f"You have already blocked @{user.username}")

	new_block = UserBlock(user_id=v.id, target_id=user.id)
	g.db.add(new_block)

	if user.admin_level >= PERMS['USER_BLOCKS_VISIBLE']:
		send_notification(user.id, f"@{v.username} has blocked you!")

	cache.delete_memoized(frontlist)
	return {"message": f"@{user.username} blocked!"}


@app.post("/settings/unblock")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@auth_required
def settings_unblock_user(v):
	user = get_user(request.values.get("username"))
	x = v.has_blocked(user)
	if not x: abort(409, "You can't unblock someone you haven't blocked")
	g.db.delete(x)
	if not v.shadowbanned and user.admin_level >= PERMS['USER_BLOCKS_VISIBLE']:
		send_notification(user.id, f"@{v.username} has unblocked you!")
	cache.delete_memoized(frontlist)
	return {"message": f"@{user.username} unblocked successfully!"}

@app.get("/settings/apps")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def settings_apps(v:User):
	return render_template("settings/apps.html", v=v)

@app.get("/settings/advanced")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def settings_advanced_get(v:User):
	return render_template("settings/advanced.html", v=v, msg=get_msg(), error=get_error())

@app.post("/settings/name_change")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@is_not_permabanned
def settings_name_change(v):
	new_name=request.values.get("name").strip()

	if new_name==v.username:
		return render_template("settings/personal.html",
						v=v,
						error="You didn't change anything")

	if not valid_username_regex.fullmatch(new_name):
		return render_template("settings/personal.html",
						v=v,
						error="This isn't a valid username.")

	search_name = new_name.replace('\\', '').replace('_','\_').replace('%','')

	x = g.db.query(User).filter(
		or_(
			User.username.ilike(search_name),
			User.original_username.ilike(search_name)
			)
		).one_or_none()

	if x and x.id != v.id:
		return render_template("settings/personal.html",
						v=v,
						error=f"Username `{new_name}` is already in use.")

	v=get_account(v.id)
	v.username=new_name
	v.name_changed_utc=int(time.time())
	g.db.add(v)

	return redirect("/settings/personal?msg=Name successfully changed!")

@app.post("/settings/song_change_mp3")
@feature_required('USERS_PROFILE_SONG')
@limiter.limit("1/second;10/day")
@limiter.limit("1/second;10/day", key_func=get_ID)
@auth_required
def settings_song_change_mp3(v):
	file = request.files.get('file')
	content_type = (file.content_type or '').lower() if file else ''
	filename = (file.filename or '').lower() if file else ''
	allowed_types = {'audio/mpeg', 'audio/mp3', 'audio/x-mpeg', 'application/octet-stream'}
	if not file or not filename.endswith('.mp3') or content_type not in allowed_types:
		return redirect("/settings/personal?error=Please upload a valid MP3 file."), 400

	song = str(time.time()).replace('.','')
	name = f'/songs/{song}.mp3'
	os.makedirs('/songs', exist_ok=True)
	try:
		file.save(name)
		size = os.stat(name).st_size
	except OSError:
		if path.isfile(name): os.remove(name)
		return redirect("/settings/personal?error=The anthem storage service is unavailable. Please try again."), 503

	if size > 8 * 1024 * 1024:
		os.remove(name)
		return redirect("/settings/personal?error=MP3 file must be smaller than 8MB"), 413

	if v.song and path.isfile(f"/songs/{v.song}.mp3") and g.db.query(User).filter_by(song=v.song).count() == 1:
		os.remove(f"/songs/{v.song}.mp3")

	v.song = song
	g.db.add(v)

	return redirect("/settings/personal?msg=Profile Anthem successfully updated!")

@app.post("/settings/song_change")
@feature_required('USERS_PROFILE_SONG')
@limiter.limit("3/second;10/day")
@limiter.limit("3/second;10/day", key_func=get_ID)
@auth_required
def settings_song_change(v):
    song = (request.values.get("song") or "").strip()

    def render_song_error(message):
        return render_template("settings/personal.html", v=v, error=message), 400

    if song == "" and v.song:
        if path.isfile(f"/songs/{v.song}.mp3") and g.db.query(User).filter_by(song=v.song).count() == 1:
            os.remove(f"/songs/{v.song}.mp3")
        v.song = None
        g.db.add(v)
        return redirect("/settings/personal?msg=Profile Anthem successfully removed!")

    try:
        parsed = urlparse(song)
        host = (parsed.hostname or "").lower().rstrip(".")
    except ValueError:
        return render_song_error("Not a valid YouTube video link.")

    video_id = None
    if parsed.scheme == "https" and host == "youtu.be":
        video_id = parsed.path.strip("/").split("/", 1)[0]
    elif parsed.scheme == "https" and host in {
        "www.youtube.com",
        "youtube.com",
        "m.youtube.com",
        "music.youtube.com",
    } and parsed.path == "/watch":
        video_id = parse_qs(parsed.query).get("v", [None])[0]

    if not video_id or not yt_id_regex.fullmatch(video_id):
        return render_song_error("Not a valid YouTube video link.")

    final_path = f"/songs/{video_id}.mp3"
    if path.isfile(final_path) and path.getsize(final_path) > 0:
        v.song = video_id
        g.db.add(v)
        return redirect("/settings/personal?msg=Profile Anthem successfully updated!")

    try:
        req_response = requests.get(
            "https://www.googleapis.com/youtube/v3/videos",
            params={"id": video_id, "key": YOUTUBE_KEY, "part": "contentDetails"},
            timeout=5,
        )
        req_response.raise_for_status()
        req = req_response.json()
        duration = req["items"][0]["contentDetails"]["duration"]
    except requests.exceptions.Timeout:
        return render_song_error("YouTube took too long to respond. Please try again.")
    except (requests.RequestException, KeyError, IndexError, TypeError, ValueError):
        return render_song_error("This YouTube video is unavailable.")

    if duration == "P0D":
        return render_song_error("Can't use a live youtube video!")

    duration_match = re.fullmatch(
        r"PT(?:(?P<hours>\d+)H)?(?:(?P<minutes>\d+)M)?(?:(?P<seconds>\d+)S)?",
        duration,
    )
    if not duration_match:
        return render_song_error("The audio could not be retrieved from this YouTube video.")

    duration_seconds = (
        (int(duration_match.group("hours") or 0) * 3600)
        + (int(duration_match.group("minutes") or 0) * 60)
        + int(duration_match.group("seconds") or 0)
    )
    if duration_seconds > 15 * 60:
        return render_song_error("Duration of the video must not exceed 15 minutes!")

    temp_dir = "/songs/tmp"
    temp_stem = f"{video_id}-{uuid4().hex}"
    temp_template = os.path.join(temp_dir, f"{temp_stem}.%(ext)s")
    temp_mp3 = os.path.join(temp_dir, f"{temp_stem}.mp3")

    def cleanup_temp_files():
        for temp_file in glob.glob(os.path.join(temp_dir, f"{temp_stem}.*")):
            try:
                if os.path.isfile(temp_file):
                    os.remove(temp_file)
            except OSError:
                pass

    os.makedirs(temp_dir, exist_ok=True)
    ydl_opts = {
        "outtmpl": temp_template,
        "format": "bestaudio/best",
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
    }
    if YOUTUBE_COOKIES_FILE and os.path.isfile(YOUTUBE_COOKIES_FILE):
        ydl_opts["cookiefile"] = YOUTUBE_COOKIES_FILE

    deno_path = shutil.which("deno")
    if deno_path:
        ydl_opts["js_runtimes"] = {"deno": {"path": deno_path}}

    runtime_names = [name for name in ("deno", "node", "bun", "qjs") if shutil.which(name)]
    po_provider_detected = bool(importlib.util.find_spec("yt_dlp_plugins"))
    print(
        "yt-dlp runtime diagnostics: "
        f"version={YTDLP_VERSION} "
        f"js_runtimes={','.join(runtime_names) or 'none'} "
        f"po_token_provider={'detected' if po_provider_detected else 'not-detected'}",
        flush=True,
    )

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([f"https://www.youtube.com/watch?v={video_id}"])

        if not os.path.isfile(temp_mp3) or os.path.getsize(temp_mp3) == 0:
            raise RuntimeError("yt-dlp completed without a non-empty MP3 file")

        os.replace(temp_mp3, final_path)
        if not os.path.isfile(final_path) or os.path.getsize(final_path) == 0:
            if os.path.isfile(final_path):
                os.remove(final_path)
            raise RuntimeError("final MP3 file was empty after atomic move")
    except Exception as e:
        cleanup_temp_files()
        safe_error = str(e)
        if YOUTUBE_KEY:
            safe_error = safe_error.replace(YOUTUBE_KEY, "[redacted]")
        if YOUTUBE_COOKIES_FILE:
            safe_error = safe_error.replace(YOUTUBE_COOKIES_FILE, "[redacted]")
        print(
            f"yt-dlp anthem download failed: {type(e).__name__}: {safe_error[:500]}",
            flush=True,
        )
        error_text = safe_error.lower()
        if any(term in error_text for term in (
            "confirm you're not a bot",
            "confirm you’re not a bot",
            "automated queries",
            "unusual traffic",
            "verification required",
            "botguard",
            "sign in to confirm",
        )):
            failure_category = "bot-challenge"
        elif any(term in error_text for term in ("timed out", "timeout", "time out")):
            failure_category = "timeout"
        elif any(term in error_text for term in (
            "private video",
            "video unavailable",
            "has been removed",
            "does not exist",
        )):
            failure_category = "unavailable"
        else:
            failure_category = "extraction"
        print(f"yt-dlp anthem failure category: {failure_category}", flush=True)
        if any(term in error_text for term in (
            "confirm you're not a bot",
            "confirm you’re not a bot",
            "automated queries",
            "unusual traffic",
            "verification required",
            "login required",
            "botguard",
            "sign in to confirm",
        )):
            message = "YouTube blocked the server from accessing this video. Please try another video."
        elif any(term in error_text for term in (
            "age-restricted",
            "age restricted",
            "confirm your age",
            "requires authentication",
            "authentication required",
        )):
            message = "This video requires YouTube authentication and cannot currently be used."
        elif any(term in error_text for term in (
            "private video",
            "video unavailable",
            "video is unavailable",
            "has been removed",
            "does not exist",
            "not available",
        )):
            message = "This YouTube video is unavailable."
        elif "unsupported url" in error_text or "unsupported url" in type(e).__name__.lower():
            message = "Not a valid YouTube video link."
        elif any(term in error_text for term in ("timed out", "timeout", "time out")):
            message = "YouTube took too long to respond. Please try again."
        else:
            message = "The audio could not be retrieved from this YouTube video."
        return render_song_error(message)
    finally:
        cleanup_temp_files()

    if v.song and v.song != video_id and path.isfile(f"/songs/{v.song}.mp3") and g.db.query(User).filter_by(song=v.song).count() == 1:
        os.remove(f"/songs/{v.song}.mp3")

    v.song = video_id
    g.db.add(v)
    return redirect("/settings/personal?msg=Profile Anthem successfully updated!")

@app.post("/settings/title_change")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@auth_required
def settings_title_change(v):
	if v.flairchanged: abort(403)

	customtitleplain = sanitize_settings_text(request.values.get("title"), 100)

	if len(customtitleplain) > 100:
		return redirect("/settings/personal?error=Flair too long!")

	if customtitleplain == v.customtitleplain:
		return redirect("/settings/personal?error=You didn't change anything!")

	customtitle = filter_emojis_only(customtitleplain)
	customtitle = censor_slurs(customtitle, None)

	if len(customtitle) > 1000:
		return redirect("/settings/personal?error=Flair too long!")

	v.customtitleplain = customtitleplain
	v.customtitle = customtitle
	g.db.add(v)

	return redirect("/settings/personal?msg=Flair successfully updated!")


@app.post("/settings/pronouns_change")
@feature_required('PRONOUNS')
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@auth_required
def settings_pronouns_change(v):
	pronouns = sanitize_settings_text(request.values.get("pronouns"))

	if len(pronouns) > 11:
		return redirect("/settings/personal?error=Your pronouns exceed the character limit (11 characters)")

	if pronouns == v.pronouns:
		return redirect("/settings/personal?error=You didn't change anything!")

	if not pronouns_regex.fullmatch(pronouns):
		return redirect("/settings/personal?error=The pronouns you entered don't match the required format!")

	bare_pronouns = pronouns.lower().replace('/', '')
	if 'nig' in bare_pronouns: pronouns = 'BI/POC'
	elif 'fag' in bare_pronouns: pronouns = 'cute/twink'

	v.pronouns = pronouns
	g.db.add(v)

	return redirect("/settings/personal?msg=Pronouns successfully updated!")


@app.post("/settings/checkmark_text")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@limiter.limit(DEFAULT_RATELIMIT_SLOWER, key_func=get_ID)
@auth_required
def settings_checkmark_text(v):
	if not v.verified: abort(403)
	new_name = sanitize_settings_text(request.values.get("checkmark-text"), 100)
	if not new_name: abort(400)
	if new_name == v.verified: return redirect("/settings/personal?error=You didn't change anything!")
	v.verified = new_name
	g.db.add(v)
	return redirect("/settings/personal?msg=Checkmark Text successfully updated!")

if IS_FISTMAS():
	@app.post("/events/fistmas2022/darkmode")
	@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
	@auth_required
	def event_darkmode(v):
		v.event_darkmode = not v.event_darkmode
		g.db.add(v)
		return {"message": "Dark mode toggled successfully!"}
