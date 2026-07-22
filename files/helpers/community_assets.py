import json
import os
import time
from shutil import copyfile

from flask import current_app

from files.helpers.persistent_site_content import (
	delete_site_content,
	get_site_content_keys,
	set_site_content,
)


COMMUNITY_ASSET_CONFIG = {
	"banner": {
		"label": "Banner Art",
		"folder": "banner_submissions",
		"approved_folder": "banners",
		"max_bytes": 2 * 1024 * 1024,
		"dimensions": (1920, 192),
	},
	"sidebar": {
		"label": "Sidebar Art",
		"folder": "sidebar_submissions",
		"approved_folder": "sidebar",
		"max_bytes": 2 * 1024 * 1024,
		"dimensions": None,
	},
}

APPROVED_IMAGE_EXTENSIONS = {".webp", ".png", ".jpg", ".jpeg", ".gif"}


def _config(kind):
	if kind not in COMMUNITY_ASSET_CONFIG:
		raise ValueError("Unknown community asset type")
	return COMMUNITY_ASSET_CONFIG[kind]


def _safe_submission_id(submission_id):
	submission_id = os.path.basename(str(submission_id or "").strip())
	if not submission_id or submission_id in {".", ".."}:
		raise FileNotFoundError
	return submission_id


def _removed_key(kind, submission_id):
	return f"community_asset_removed:{kind}:{_safe_submission_id(submission_id)}"


def _removed_ids(kind):
	prefix = f"community_asset_removed:{kind}:"
	return {key[len(prefix):] for key in get_site_content_keys(prefix)}


def queue_directory(kind):
	return os.path.join(current_app.root_path, "..", "asset_submissions", _config(kind)["folder"])


def approved_directory(kind):
	return os.path.join(current_app.root_path, "assets", "images", "Obsession", _config(kind)["approved_folder"])


def approved_asset_url(kind, filename):
	return f"/i/Obsession/{_config(kind)['approved_folder']}/{os.path.basename(filename)}"


def ensure_asset_directories(kind):
	os.makedirs(queue_directory(kind), exist_ok=True)
	os.makedirs(approved_directory(kind), exist_ok=True)


def _metadata_path(kind, submission_id):
	return os.path.join(queue_directory(kind), f"{os.path.basename(submission_id)}.json")


def read_submission(kind, submission_id):
	path = _metadata_path(kind, submission_id)
	if not os.path.isfile(path):
		return None
	with open(path, "r", encoding="utf-8") as stream:
		data = json.load(stream)
	data["id"] = os.path.splitext(os.path.basename(path))[0]
	data["kind"] = kind
	data["status"] = data.get("status", "pending")
	data["image_url"] = f"/community-assets/{kind}/{data['id']}"
	return data


def list_submissions(kind, submitter=None, status=None):
	ensure_asset_directories(kind)
	items = []
	for filename in os.listdir(queue_directory(kind)):
		if not filename.endswith(".json"):
			continue
		item = read_submission(kind, filename[:-5])
		if not item:
			continue
		if submitter and item.get("submitter") != submitter:
			continue
		if status and item.get("status") != status:
			continue
		items.append(item)
	return sorted(items, key=lambda item: item.get("submitted_utc", 0), reverse=True)


def active_community_asset_filenames(kind):
	ensure_asset_directories(kind)
	removed = _removed_ids(kind)
	filenames = []
	for filename in os.listdir(approved_directory(kind)):
		full_path = os.path.join(approved_directory(kind), filename)
		stem, extension = os.path.splitext(filename)
		if not os.path.isfile(full_path):
			continue
		if extension.lower() not in APPROVED_IMAGE_EXTENSIONS:
			continue
		if stem in removed:
			continue
		filenames.append(filename)
	return sorted(filenames)


def list_approved_assets(kind):
	metadata = {item["id"]: item for item in list_submissions(kind)}
	items = []
	for filename in active_community_asset_filenames(kind):
		stem, _ = os.path.splitext(filename)
		item = dict(metadata.get(stem) or {})
		item.update({
			"id": stem,
			"kind": kind,
			"filename": filename,
			"status": "approved",
			"approved_url": approved_asset_url(kind, filename),
		})
		items.append(item)
	return sorted(items, key=lambda item: (int(item.get("submitted_utc") or 0), item.get("id", "")), reverse=True)


def write_submission(kind, submission_id, metadata):
	ensure_asset_directories(kind)
	with open(_metadata_path(kind, submission_id), "w", encoding="utf-8") as stream:
		json.dump(metadata, stream, indent=2)


def approve_submission(kind, submission_id, reviewer):
	item = read_submission(kind, submission_id)
	if not item:
		raise FileNotFoundError
	source = os.path.join(queue_directory(kind), item["filename"])
	if not os.path.isfile(source):
		raise FileNotFoundError
	ensure_asset_directories(kind)
	target_name = f"{item['id']}.webp"
	target = os.path.join(approved_directory(kind), target_name)
	copyfile(source, target)
	delete_site_content(_removed_key(kind, item["id"]))
	item.update({
		"status": "approved",
		"reviewed_by": reviewer,
		"reviewed_utc": int(time.time()),
		"approved_url": approved_asset_url(kind, target_name),
	})
	write_submission(kind, item["id"], {key: value for key, value in item.items() if key not in {"id", "image_url"}})
	return item


def reject_submission(kind, submission_id, reviewer):
	item = read_submission(kind, submission_id)
	if not item:
		raise FileNotFoundError
	approved_path = os.path.join(approved_directory(kind), item["id"] + ".webp")
	if os.path.isfile(approved_path):
		os.remove(approved_path)
	set_site_content(_removed_key(kind, item["id"]), "1", reviewer)
	item.update({"status": "rejected", "reviewed_by": reviewer, "reviewed_utc": int(time.time())})
	write_submission(kind, item["id"], {key: value for key, value in item.items() if key not in {"id", "image_url", "approved_url"}})
	return item


def remove_approved_asset(kind, submission_id, reviewer):
	ensure_asset_directories(kind)
	submission_id = _safe_submission_id(submission_id)
	item = read_submission(kind, submission_id)
	removed_urls = []
	for filename in os.listdir(approved_directory(kind)):
		full_path = os.path.join(approved_directory(kind), filename)
		if os.path.isfile(full_path) and os.path.splitext(filename)[0] == submission_id:
			removed_urls.append(approved_asset_url(kind, filename))
			os.remove(full_path)
	if not item and not removed_urls and submission_id in _removed_ids(kind):
		return []
	if not item and not removed_urls:
		raise FileNotFoundError
	set_site_content(_removed_key(kind, submission_id), "1", reviewer)
	if item:
		item.update({"status": "removed", "reviewed_by": reviewer, "reviewed_utc": int(time.time())})
		write_submission(kind, item["id"], {key: value for key, value in item.items() if key not in {"id", "image_url", "approved_url"}})
	return removed_urls
