import os
import shutil
import subprocess
import time
import requests
from shutil import copyfile
from typing import Optional

import gevent
import imagehash
from flask import abort, g, has_request_context, request
from werkzeug.utils import secure_filename
from PIL import Image
from PIL import UnidentifiedImageError
from PIL.ImageSequence import Iterator
from sqlalchemy.orm.session import Session

from files.classes.media import *
from files.helpers.cloudflare import purge_files_in_cache
from files.helpers.settings import get_setting
from files.helpers.support import patron_limit

from .config.const import *


IMAGE_CONVERTER = shutil.which("magick") or shutil.which("convert")


def _remove_failed_image(filename):
	try:
		if os.path.exists(filename):
			os.remove(filename)
	except OSError:
		pass


def _log_image_conversion_failure(error):
	print(f"Image conversion failed ({type(error).__name__})")


def media_ratelimit(v):
	t = time.time() - 86400
	count = g.db.query(Media).filter(Media.user_id == v.id, Media.created_utc > t).count()
	if count > 50: abort(500)

def process_files(files, v):
	body = ''
	if g.is_tor or not files.get("file"): return body
	max_files = patron_limit(v, "attachment_count")
	files = files.getlist('file')
	if len(files) > max_files:
		abort(413, f"You can upload up to {max_files} files at a time.")
	
	if files:
		media_ratelimit(v)

	for file in files:
		if file.content_type.startswith('image/'):
			name = f'/images/{time.time()}'.replace('.','') + '.webp'
			file.save(name)
			url = process_image(name, v)
			body += f"\n\n![]({url})"
		elif file.content_type.startswith('video/'):
			body += f"\n\n{process_video(file, v)}"
		elif file.content_type.startswith('audio/'):
			body += f"\n\n{process_audio(file, v)}"
		else:
			abort(415, "The uploaded file is not a valid image.")
	return body


def process_audio(file, v):
	name = f'/audio/{time.time()}'.replace('.','')

	name_original = secure_filename(file.filename)
	extension = name_original.split('.')[-1].lower()
	name = name + '.' + extension
	file.save(name)

	size = os.stat(name).st_size
	if size > patron_limit(v, "image_audio_mb") * 1024 * 1024:
		os.remove(name)
		abort(413, f"Max image/audio size is {MAX_IMAGE_AUDIO_SIZE_MB} MB ({MAX_IMAGE_AUDIO_SIZE_MB_PATRON} MB for {patron.lower()}s)")

	media = g.db.query(Media).filter_by(filename=name, kind='audio').one_or_none()
	if media: g.db.delete(media)
	
	media = Media(
		kind='audio',
		filename=name,
		user_id=v.id,
		size=size
	)
	g.db.add(media)

	return name


def webm_to_mp4(old, new, vid, db):
	tmp = new.replace('.mp4', '-t.mp4')
	subprocess.run(["ffmpeg", "-y", "-loglevel", "warning", "-nostats", "-threads:v", "1", "-i", old, "-map_metadata", "-1", tmp], check=True, stderr=subprocess.STDOUT)
	os.replace(tmp, new)
	os.remove(old)

	media = db.query(Media).filter_by(filename=new, kind='video').one_or_none()
	if media: db.delete(media)

	media = Media(
		kind='video',
		filename=new,
		user_id=vid,
		size=os.stat(new).st_size
	)
	db.add(media)
	db.commit()
	db.close()

	purge_files_in_cache(f"{SITE_FULL}{new}")



def process_video(file, v):
	old = f'/videos/{time.time()}'.replace('.','')
	file.save(old)

	size = os.stat(old).st_size
	if size > patron_limit(v, "video_mb") * 1024 * 1024:
		os.remove(old)
		abort(413, f"Max video size is {MAX_VIDEO_SIZE_MB} MB ({MAX_VIDEO_SIZE_MB_PATRON} MB for paypigs)")

	name_original = secure_filename(file.filename)
	extension = name_original.split('.')[-1].lower()
	new = old + '.' + extension

	if extension == 'webm':
		new = new.replace('.webm', '.mp4')
		copyfile(old, new)
		db = Session(bind=g.db.get_bind(), autoflush=False)
		gevent.spawn(webm_to_mp4, old, new, v.id, db)
	else:
		subprocess.run(["ffmpeg", "-y", "-loglevel", "warning", "-nostats", "-i", old, "-map_metadata", "-1", "-c:v", "copy", "-c:a", "copy", new], check=True)
		os.remove(old)

		media = g.db.query(Media).filter_by(filename=new, kind='video').one_or_none()
		if media: g.db.delete(media)

		media = Media(
			kind='video',
			filename=new,
			user_id=v.id,
			size=os.stat(new).st_size
		)
		g.db.add(media)

	return new

def process_image(filename:str, v, resize=0, trim=False, uploader_id:Optional[int]=None, db=None):
	# Thumbnail processing can run without a request context, so failures must
	# be cleaned up and returned to the caller instead of crashing a worker.
	has_request = has_request_context()
	size = os.stat(filename).st_size
	if size > patron_limit(v, "image_audio_mb") * 1024 * 1024:
		os.remove(filename)
		if has_request:
			abort(413, f"Max image/audio size is {MAX_IMAGE_AUDIO_SIZE_MB} MB ({MAX_IMAGE_AUDIO_SIZE_MB_PATRON} MB for paypigs)")
		return None

	needs_conversion = True
	try:
		with Image.open(filename) as i:
			# Upload routes save every incoming image to a .webp destination before
			# process_image runs. If the upload is already a valid WebP and no resize
			# or trim is requested, converting WebP -> WebP again is pointless and can
			# fail on deployments whose ImageMagick build lacks a WebP decoder even
			# though Pillow can read the file just fine. Keep the validated WebP as-is.
			needs_conversion = not (i.format == 'WEBP' and not resize and not trim)
			if needs_conversion:
				if not IMAGE_CONVERTER:
					_remove_failed_image(filename)
					if has_request:
						abort(422, "Image conversion is temporarily unavailable. Please try again later.")
					return None
				params = [IMAGE_CONVERTER]
				if resize == 99: params.append(f"{filename}[0]")
				else: params.append(filename)
				params.extend(["-coalesce", "-quality", "88", "-strip", "-auto-orient"])
				if trim and len(list(Iterator(i))) == 1:
					params.append("-trim")
				if resize and i.width > resize:
					params.extend(["-resize", f"{resize}>"])
	except (UnidentifiedImageError, OSError) as e:
		print(f"Couldn't identify an image for {filename}; deleting... (user {v.id if v else '-no user-'})")
		try:
			os.remove(filename)
		except: pass
		if has_request:
			abort(415, "The uploaded file is not a valid image.")
		return None

	if needs_conversion:
		params.append(filename)
		try:
			subprocess.run(
				params,
				timeout=MAX_IMAGE_CONVERSION_TIMEOUT,
				check=True,
				stdout=subprocess.PIPE,
				stderr=subprocess.PIPE,
			)
		except (subprocess.TimeoutExpired, subprocess.CalledProcessError, OSError) as error:
			_log_image_conversion_failure(error)
			_remove_failed_image(filename)
			if isinstance(error, subprocess.TimeoutExpired):
				if has_request:
					abort(413, ("An uploaded image took too long to convert to WEBP. "
							"Please convert it to WEBP elsewhere then upload it again."))
				return None
			if has_request:
				abort(422, "That image could not be converted. Please try another image.")
			return None

	if resize:
		if os.stat(filename).st_size > MAX_IMAGE_SIZE_BANNER_RESIZED_MB * 1024 * 1024:
			os.remove(filename)
			if has_request:
				abort(413, f"Max size for site assets is {MAX_IMAGE_SIZE_BANNER_RESIZED_MB} MB")
			return None

		if filename.startswith('files/assets/images/'):
			path = filename.rsplit('/', 1)[0]
			kind = path.split('/')[-1]

			if kind in {'banners','sidebar'}:
				hashes = {}

				for img in os.listdir(path):
					if resize == 400 and img in {'256.webp','585.webp'}: continue
					img_path = f'{path}/{img}'
					if img_path == filename: continue

					with Image.open(img_path) as i:
						i_hash = str(imagehash.phash(i))

					if i_hash in hashes.keys():
						print(hashes[i_hash], flush=True)
						print(img_path, flush=True)
					else: hashes[i_hash] = img_path

				with Image.open(filename) as i:
					i_hash = str(imagehash.phash(i))

				if i_hash in hashes.keys():
					os.remove(filename)
					if has_request:
						abort(409, "Image already exists!")
					return None

	db = db or g.db

	media = db.query(Media).filter_by(filename=filename, kind='image').one_or_none()
	if media: db.delete(media)

	media = Media(
		kind='image',
		filename=filename,
		user_id=uploader_id or v.id,
		size=os.stat(filename).st_size
	)
	db.add(media)

	return filename


def process_dm_images(v, user):
	if not request.files.get("file") or g.is_tor or not get_setting("dm_images"):
		return ''

	body = ''
	max_files = patron_limit(v, "attachment_count")
	files = request.files.getlist('file')
	if len(files) > max_files:
		abort(413, f"You can upload up to {max_files} files at a time.")

	for file in files:
		if not file.content_type or not file.content_type.startswith('image/'):
			abort(415, "The uploaded file is not a valid image.")

		filename = f'/dm_images/{time.time()}'.replace('.','') + '.webp'
		try:
			file.save(filename)
			url = process_image(filename, v)
		except Exception:
			_remove_failed_image(filename)
			raise

		if not url:
			_remove_failed_image(filename)
			abort(422, "That image could not be processed. Please try another image.")

		body += f'\n\n{SITE_FULL}{url}\n\n'

	if body:
		with open(f"{LOG_DIRECTORY}/dm_images.log", "a+", encoding="utf-8") as f:
			if user:
				f.write(f'{body.strip()}, {v.username}, {v.id}, {user.username}, {user.id}\n')
			else:
				f.write(f'{body.strip()}, {v.username}, {v.id}, Modmail, Modmail\n')
	return body
