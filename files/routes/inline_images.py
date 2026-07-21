import ipaddress
import os
import socket
import time
from urllib.parse import urljoin, urlparse

import requests
from flask import abort, g, request

from files.__main__ import app, limiter
from files.helpers.config.const import *
from files.helpers.media import media_ratelimit, process_image
from files.helpers.support import patron_limit
from files.routes.wrappers import auth_required


MAX_REMOTE_REDIRECTS = 4
REMOTE_CHUNK_SIZE = 64 * 1024


def _new_image_path():
	return f"/images/{time.time_ns()}.webp"


def _public_image_url(path):
	if path.startswith("http://") or path.startswith("https://"):
		return path
	return f"{SITE_FULL.rstrip('/')}/{path.lstrip('/')}"


def _validate_remote_url(url):
	try:
		parsed = urlparse(url.strip())
	except (TypeError, ValueError):
		abort(400, "That image URL is invalid.")

	if parsed.scheme not in {"http", "https"} or not parsed.hostname:
		abort(400, "Image URLs must use http or https.")
	if parsed.username or parsed.password:
		abort(400, "Image URLs cannot contain login credentials.")

	try:
		addresses = socket.getaddrinfo(
			parsed.hostname,
			parsed.port or (443 if parsed.scheme == "https" else 80),
			type=socket.SOCK_STREAM,
		)
	except socket.gaierror:
		abort(400, "The image host could not be resolved.")

	for address in addresses:
		ip = ipaddress.ip_address(address[4][0])
		if not ip.is_global:
			abort(400, "That image host is not allowed.")

	return parsed.geturl()


def _download_remote_image(url, max_bytes):
	current_url = url.strip()
	headers = {
		"Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
		"User-Agent": "Mozilla/5.0 (compatible; ObsessionImageImporter/1.0)",
	}

	for _ in range(MAX_REMOTE_REDIRECTS + 1):
		current_url = _validate_remote_url(current_url)
		try:
			response = requests.get(
				current_url,
				headers=headers,
				stream=True,
				allow_redirects=False,
				timeout=(5, 15),
				proxies=proxies,
			)
		except requests.RequestException:
			abort(400, "The image host could not be reached.")

		if response.is_redirect or response.is_permanent_redirect:
			location = response.headers.get("Location")
			response.close()
			if not location:
				abort(400, "The image host returned an invalid redirect.")
			current_url = urljoin(current_url, location)
			continue

		if response.status_code != 200:
			response.close()
			abort(400, f"The image host returned HTTP {response.status_code}.")

		content_type = response.headers.get("Content-Type", "").split(";", 1)[0].lower()
		if not content_type.startswith("image/") or content_type == "image/svg+xml":
			response.close()
			abort(415, "That URL does not point to a supported image.")

		content_length = response.headers.get("Content-Length")
		if content_length:
			try:
				if int(content_length) > max_bytes:
					response.close()
					abort(413, "That remote image is too large.")
			except ValueError:
				pass

		filename = _new_image_path()
		downloaded = 0
		try:
			with open(filename, "wb") as output:
				for chunk in response.iter_content(REMOTE_CHUNK_SIZE):
					if not chunk:
						continue
					downloaded += len(chunk)
					if downloaded > max_bytes:
						raise OverflowError
					output.write(chunk)
		except OverflowError:
			if os.path.exists(filename):
				os.remove(filename)
			abort(413, "That remote image is too large.")
		except OSError:
			if os.path.exists(filename):
				os.remove(filename)
			abort(500, "The server could not store that image.")
		finally:
			response.close()

		return filename

	abort(400, "The image URL redirected too many times.")


@app.post("/api/images/inline")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@auth_required
def upload_inline_images(v):
	if g.is_tor:
		abort(403, "Image uploads are not allowed through TOR!")

	uploads = [item for item in request.files.getlist("file") if item and item.filename]
	remote_urls = [item.strip() for item in request.form.getlist("url") if item.strip()]
	total_items = len(uploads) + len(remote_urls)
	if not total_items:
		abort(400, "Choose an image or provide an image URL.")

	max_files = patron_limit(v, "attachment_count")
	if total_items > max_files:
		abort(413, f"You can upload up to {max_files} images at a time.")

	media_ratelimit(v)
	max_bytes = patron_limit(v, "image_audio_mb") * 1024 * 1024
	stored_urls = []

	for upload in uploads:
		if not (upload.content_type or "").startswith("image/"):
			abort(415, "Only images can be inserted into the post editor.")
		filename = _new_image_path()
		upload.save(filename)
		stored_path = process_image(filename, v)
		if stored_path:
			stored_urls.append(_public_image_url(stored_path))

	for remote_url in remote_urls:
		filename = _download_remote_image(remote_url, max_bytes)
		stored_path = process_image(filename, v)
		if stored_path:
			stored_urls.append(_public_image_url(stored_path))

	if not stored_urls:
		abort(422, "No images could be processed.")

	return {
		"urls": stored_urls,
		"markdown": "\n\n".join(f"![]({url})" for url in stored_urls),
	}, 201
