from os import path, rename
from shutil import copyfile, move

from files.classes.marsey import Marsey
from files.classes.hats import Hat, HatDef
from files.classes.mod_logs import ModAction
from files.helpers.cloudflare import purge_files_in_cache
from files.helpers.config.const import *
from files.helpers.get import *
from files.helpers.media import *
from files.helpers.useractions import *
from files.routes.wrappers import *
from files.__main__ import app, cache, limiter

ASSET_TYPES = (Marsey, HatDef)

@app.get("/submit/marseys")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def submit_marseys(v:User):
	if v.admin_level >= PERMS['VIEW_PENDING_SUBMITTED_MARSEYS']:
		marseys = g.db.query(Marsey).filter(Marsey.submitter_id != None)
	else:
		marseys = g.db.query(Marsey).filter(Marsey.submitter_id == v.id)

	marseys = marseys.order_by(Marsey.created_utc.desc()).all()

	for marsey in marseys:
		marsey.author = g.db.query(User.username).filter_by(id=marsey.author_id).one()[0]
		marsey.submitter = g.db.query(User.username).filter_by(id=marsey.submitter_id).one()[0]

	return render_template("submit_marseys.html", v=v, marseys=marseys)


@app.post("/submit/marseys")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def submit_marsey(v:User):
	file = request.files["image"]
	name = request.values.get('name', '').lower().strip()
	tags = request.values.get('tags', '').lower().strip()
	username = request.values.get('author', '').lower().strip()

	def error(error):
		if v.admin_level >= PERMS['VIEW_PENDING_SUBMITTED_MARSEYS']: marseys = g.db.query(Marsey).filter(Marsey.submitter_id != None)
		else: marseys = g.db.query(Marsey).filter(Marsey.submitter_id == v.id)
		marseys = marseys.order_by(Marsey.created_utc.desc()).all()
		for marsey in marseys:
			marsey.author = g.db.query(User.username).filter_by(id=marsey.author_id).one()[0]
			marsey.submitter = g.db.query(User.username).filter_by(id=marsey.submitter_id).one()[0]
		return render_template("submit_marseys.html", v=v, marseys=marseys, error=error, name=name, tags=tags, username=username, file=file), 400

	if g.is_tor:
		return error("Image uploads are not allowed through TOR!")

	if not file or not file.content_type.startswith('image/'):
		return error("You need to submit an image!")

	if not marsey_regex.fullmatch(name):
		return error("Invalid name!")

	existing = g.db.query(Marsey.name).filter_by(name=name).one_or_none()
	if existing:
		return error("Someone already submitted a marsey with this name!")

	if not tags_regex.fullmatch(tags):
		return error("Invalid tags!")

	author = get_user(username, v=v, graceful=True, include_shadowbanned=False)
	if not author:
		return error(f"A user with the name '{username}' was not found!")

	highquality = f'/asset_submissions/marseys/{name}'
	file.save(highquality)

	filename = f'/asset_submissions/marseys/{name}.webp'
	copyfile(highquality, filename)
	process_image(filename, v, resize=200, trim=True)

	marsey = Marsey(name=name, author_id=author.id, tags=tags, count=0, submitter_id=v.id)
	g.db.add(marsey)

	g.db.flush()
	if v.admin_level >= PERMS['VIEW_PENDING_SUBMITTED_MARSEYS']: marseys = g.db.query(Marsey).filter(Marsey.submitter_id != None)
	else: marseys = g.db.query(Marsey).filter(Marsey.submitter_id == v.id)

	marseys = marseys.order_by(Marsey.created_utc.desc()).all()

	for marsey in marseys:
		marsey.author = g.db.query(User.username).filter_by(id=marsey.author_id).one()[0]
		marsey.submitter = g.db.query(User.username).filter_by(id=marsey.submitter_id).one()[0]

	return render_template("submit_marseys.html", v=v, marseys=marseys, msg=f"'{name}' submitted successfully!")

def verify_permissions_and_get_asset(cls, asset_type:str, v:User, name:str, make_lower=False):
	if cls not in ASSET_TYPES: raise Exception("not a valid asset type")
	name = name.strip()
	if make_lower: name = name.lower()
	asset = None
	if cls == HatDef:
		asset = g.db.query(cls).filter_by(name=name).one_or_none()
	else:
		asset = g.db.get(cls, name)
	if not asset:
		abort(404, f"This {asset} '{name}' doesn't exist!")
	return asset

@app.post("/admin/approve/marsey/<name>")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@admin_level_required(PERMS['MODERATE_PENDING_SUBMITTED_ASSETS'])
def approve_marsey(v, name):
	marsey = verify_permissions_and_get_asset(Marsey, "marsey", v, name, True)
	tags = request.values.get('tags').lower().strip()
	if not tags:
		abort(400, "You need to include tags!")

	new_name = request.values.get('name').lower().strip()
	if not new_name:
		abort(400, "You need to include name!")


	if not marsey_regex.fullmatch(new_name):
		abort(400, "Invalid name!")
	if not tags_regex.fullmatch(tags):
		abort(400, "Invalid tags!")


	marsey.name = new_name
	marsey.tags = tags
	g.db.add(marsey)

	author = get_account(marsey.author_id)
	all_by_author = g.db.query(Marsey).filter_by(author_id=author.id).count()

	if all_by_author >= 99:
		badge_grant(badge_id=143, user=author)
	elif all_by_author >= 9:
		badge_grant(badge_id=16, user=author)
	else:
		badge_grant(badge_id=17, user=author)
	purge_files_in_cache(f"https://{SITE}/e/{marsey.name}/webp")
	cache.delete(EMOJIS_CACHE_KEY)
	cache.delete(MARSEYS_CACHE_KEY)
	move(f"/asset_submissions/marseys/{name}.webp", f"files/assets/images/emojis/{marsey.name}.webp")

	highquality = f"/asset_submissions/marseys/{name}"
	with Image.open(highquality) as i:
		new_path = f'/asset_submissions/marseys/original/{name}.{i.format.lower()}'
	rename(highquality, new_path)

	author.pay_account('coins', 250)
	g.db.add(author)

	if v.id != author.id:
		msg = f"@{v.username} (a site admin) has approved a marsey you made: :{marsey.name}:\nYou have received 250 coins as a reward!"
		send_repeatable_notification(author.id, msg)

	if v.id != marsey.submitter_id and author.id != marsey.submitter_id:
		msg = f"@{v.username} (a site admin) has approved a marsey you submitted: :{marsey.name}:"
		send_repeatable_notification(marsey.submitter_id, msg)

	marsey.submitter_id = None

	return {"message": f"'{marsey.name}' approved!"}

def remove_asset(cls, type_name:str, v:User, name:str) -> dict[str, str]:
	if cls not in ASSET_TYPES: raise Exception("not a valid asset type")
	should_make_lower = cls == Marsey
	if should_make_lower: name = name.lower()
	name = name.strip()
	if not name:
		abort(400, f"You need to specify a {type_name}!")
	asset = None
	if cls == HatDef:
		asset = g.db.query(cls).filter_by(name=name).one_or_none()
	else:
		asset = g.db.get(cls, name)
	if not asset:
		abort(404, f"This {type_name} '{name}' doesn't exist!")
	if v.id != asset.submitter_id and v.admin_level < PERMS['MODERATE_PENDING_SUBMITTED_ASSETS']:
		abort(403)
	name = asset.name
	if v.id != asset.submitter_id:
		msg = f"@{v.username} has rejected a {type_name} you submitted: `'{name}'`"
		send_repeatable_notification(asset.submitter_id, msg)
	g.db.delete(asset)
	os.remove(f"/asset_submissions/{type_name}s/{name}.webp")
	os.remove(f"/asset_submissions/{type_name}s/{name}")
	return {"message": f"'{name}' removed!"}

@app.post("/remove/marsey/<name>")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def remove_marsey(v:User, name):
	return remove_asset(Marsey, "marsey", v, name)

@app.get("/submit/hats")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def submit_hats(v:User):
	if v.admin_level >= PERMS['VIEW_PENDING_SUBMITTED_HATS']: hats = g.db.query(HatDef).filter(HatDef.submitter_id != None)
	else: hats = g.db.query(HatDef).filter(HatDef.submitter_id == v.id)
	hats = hats.order_by(HatDef.created_utc.desc()).all()
	return render_template("submit_hats.html", v=v, hats=hats)


@app.post("/submit/hats")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def submit_hat(v:User):
	name = request.values.get('name', '').strip()
	description = request.values.get('description', '').strip()
	username = request.values.get('author', '').strip()

	def error(error):
		if v.admin_level >= PERMS['VIEW_PENDING_SUBMITTED_HATS']: hats = g.db.query(HatDef).filter(HatDef.submitter_id != None)
		else: hats = g.db.query(HatDef).filter(HatDef.submitter_id == v.id)
		hats = hats.order_by(HatDef.created_utc.desc()).all()
		return render_template("submit_hats.html", v=v, hats=hats, error=error, name=name, description=description, username=username), 400

	if g.is_tor:
		return error("Image uploads are not allowed through TOR!")

	file = request.files["image"]
	if not file or not file.content_type.startswith('image/'):
		return error("You need to submit an image!")

	if not hat_regex.fullmatch(name):
		return error("Invalid name!")

	existing = g.db.query(HatDef.name).filter_by(name=name).one_or_none()
	if existing:
		return error("A hat with this name already exists!")

	if not description_regex.fullmatch(description):
		return error("Invalid description!")

	author = get_user(username, v=v, graceful=True, include_shadowbanned=False)
	if not author:
		return error(f"A user with the name '{username}' was not found!")

	highquality = f'/asset_submissions/hats/{name}'
	file.save(highquality)

	with Image.open(highquality) as i:
		if i.width > 100 or i.height > 130:
			os.remove(highquality)
			return error("Images must be 100x130")

		if len(list(Iterator(i))) > 1: price = 1000
		else: price = 500

	filename = f'/asset_submissions/hats/{name}.webp'
	copyfile(highquality, filename)
	process_image(filename, v, resize=100)

	hat = HatDef(name=name, author_id=author.id, description=description, price=price, submitter_id=v.id)
	g.db.add(hat)
	g.db.commit()

	if v.admin_level >= PERMS['VIEW_PENDING_SUBMITTED_HATS']: hats = g.db.query(HatDef).filter(HatDef.submitter_id != None)
	else: hats = g.db.query(HatDef).filter(HatDef.submitter_id == v.id)

	hats = hats.order_by(HatDef.created_utc.desc()).all()

	return render_template("submit_hats.html", v=v, hats=hats, msg=f"'{name}' submitted successfully!")


@app.post("/admin/approve/hat/<name>")
@limiter.limit("3/second;120/minute;200/hour;1000/day")
@limiter.limit("3/second;120/minute;200/hour;1000/day", key_func=get_ID)
@admin_level_required(PERMS['MODERATE_PENDING_SUBMITTED_ASSETS'])
def approve_hat(v, name):
	hat = verify_permissions_and_get_asset(HatDef, "hat", v, name, False)
	description = request.values.get('description').strip()
	if not description: abort(400, "You need to include a description!")

	new_name = request.values.get('name').strip()
	if not new_name: abort(400, "You need to include a name!")
	if not hat_regex.fullmatch(new_name): abort(400, "Invalid name!")
	if not description_regex.fullmatch(description): abort(400, "Invalid description!")

	try:
		hat.price = int(request.values.get('price'))
		if hat.price < 0: raise ValueError("Invalid hat price")
	except:
		abort(400, "Invalid hat price")
	hat.name = new_name
	hat.description = description
	g.db.add(hat)


	g.db.flush()
	author = hat.author

	all_by_author = g.db.query(HatDef).filter_by(author_id=author.id).count()

	if all_by_author >= 250:
		badge_grant(badge_id=166, user=author)
	elif all_by_author >= 100:
		badge_grant(badge_id=165, user=author)
	elif all_by_author >= 50:
		badge_grant(badge_id=164, user=author)
	elif all_by_author >= 10:
		badge_grant(badge_id=163, user=author)

	hat_copy = Hat(
		user_id=author.id,
		hat_id=hat.id
	)
	g.db.add(hat_copy)


	if v.id != author.id:
		msg = f"@{v.username} (a site admin) has approved a hat you made: '{hat.name}'"
		send_repeatable_notification(author.id, msg)

	if v.id != hat.submitter_id and author.id != hat.submitter_id:
		msg = f"@{v.username} (a site admin) has approved a hat you submitted: '{hat.name}'"
		send_repeatable_notification(hat.submitter_id, msg)

	hat.submitter_id = None

	move(f"/asset_submissions/hats/{name}.webp", f"files/assets/images/hats/{hat.name}.webp")

	highquality = f"/asset_submissions/hats/{name}"
	with Image.open(highquality) as i:
		new_path = f'/asset_submissions/hats/original/{name}.{i.format.lower()}'
	rename(highquality, new_path)

	return {"message": f"'{hat.name}' approved!"}

@app.post("/remove/hat/<name>")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def remove_hat(v:User, name):
	return remove_asset(HatDef, 'hat', v, name)

@app.get("/admin/update/marseys")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@admin_level_required(PERMS['UPDATE_ASSETS'])
def update_marseys(v):
	name = request.values.get('name')
	tags = None
	error = None
	if name:
		marsey = g.db.get(Marsey, name)
		if marsey:
			tags = marsey.tags or ''
		else:
			name = ''
			tags = ''
			error = "A marsey with this name doesn't exist!"
	return render_template("update_assets.html", v=v, error=error, name=name, tags=tags, type="Marsey")


@app.post("/admin/update/marseys")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@admin_level_required(PERMS['UPDATE_ASSETS'])
def update_marsey(v):
	file = request.files["image"]
	name = request.values.get('name', '').lower().strip()
	tags = request.values.get('tags', '').lower().strip()

	def error(error):
		return render_template("update_assets.html", v=v, error=error, name=name, tags=tags, type="Marsey")

	existing = g.db.get(Marsey, name)
	if not existing:
		return error("A marsey with this name doesn't exist!")

	if file:
		if g.is_tor:
			return error("Image uploads are not allowed through TOR!")
		if not file.content_type.startswith('image/'):
			return error("You need to submit an image!")

		for x in IMAGE_FORMATS:
			if path.isfile(f'/asset_submissions/marseys/original/{name}.{x}'):
				os.remove(f'/asset_submissions/marseys/original/{name}.{x}')

		highquality = f"/asset_submissions/marseys/{name}"
		file.save(highquality)
		with Image.open(highquality) as i:
			format = i.format.lower()
		new_path = f'/asset_submissions/marseys/original/{name}.{format}'
		rename(highquality, new_path)

		filename = f"files/assets/images/emojis/{name}.webp"
		copyfile(new_path, filename)
		process_image(filename, v, resize=200, trim=True)
		purge_files_in_cache([f"https://{SITE}/e/{name}.webp", f"https://{SITE}/assets/images/emojis/{name}.webp", f"https://{SITE}/asset_submissions/marseys/original/{name}.{format}"])

	if tags and existing.tags != tags and tags != "none":
		existing.tags = tags
		g.db.add(existing)
	elif not file:
		return error("You need to actually update something!")

	ma = ModAction(
		kind="update_marsey",
		user_id=v.id,
		_note=f'<a href="/e/{name}.webp">{name}</a>'
	)
	g.db.add(ma)
	return render_template("update_assets.html", v=v, msg=f"'{name}' updated successfully!", name=name, tags=tags, type="Marsey")

@app.get("/admin/update/hats")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@admin_level_required(PERMS['UPDATE_ASSETS'])
def update_hats(v):
	return render_template("update_assets.html", v=v, type="Hat")


@app.post("/admin/update/hats")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@admin_level_required(PERMS['UPDATE_ASSETS'])
def update_hat(v):
	file = request.files["image"]
	name = request.values.get('name', '').strip()

	def error(error):
		return render_template("update_assets.html", v=v, error=error, type="Hat")

	if g.is_tor:
		return error("Image uploads are not allowed through TOR!")

	if not file or not file.content_type.startswith('image/'):
		return error("You need to submit an image!")

	if not hat_regex.fullmatch(name):
		return error("Invalid name!")

	existing = g.db.query(HatDef.name).filter_by(name=name).one_or_none()
	if not existing:
		return error("A hat with this name doesn't exist!")

	highquality = f"/asset_submissions/hats/{name}"
	file.save(highquality)

	with Image.open(highquality) as i:
		if i.width > 100 or i.height > 130:
			os.remove(highquality)
			return error("Images must be 100x130")

		format = i.format.lower()
	new_path = f'/asset_submissions/hats/original/{name}.{format}'

	for x in IMAGE_FORMATS:
		if path.isfile(f'/asset_submissions/hats/original/{name}.{x}'):
			os.remove(f'/asset_submissions/hats/original/{name}.{x}')

	rename(highquality, new_path)

	filename = f"files/assets/images/hats/{name}.webp"
	copyfile(new_path, filename)
	process_image(filename, v, resize=100)
	purge_files_in_cache([f"https://{SITE}/i/hats/{name}.webp", f"https://{SITE}/assets/images/hats/{name}.webp", f"https://{SITE}/asset_submissions/hats/original/{name}.{format}"])
	ma = ModAction(
		kind="update_hat",
		user_id=v.id,
		_note=f'<a href="/i/hats/{name}.webp">{name}</a>'
	)
	g.db.add(ma)
	return render_template("update_assets.html", v=v, msg=f"'{name}' updated successfully!", type="Hat")
