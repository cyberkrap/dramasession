import json
import os
import time
from shutil import copyfile

from flask import current_app

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


def _config(kind):
	if kind not in COMMUNITY_ASSET_CONFIG:
		raise ValueError("Unknown community asset type")
	return COMMUNITY_ASSET_CONFIG[kind]


def queue_directory(kind):
	return os.path.join(current_app.root_path, "..", "asset_submissions", _config(kind)["folder"])


def approved_directory(kind):
	return os.path.join(current_app.root_path, "assets", "images", "Obsession", _config(kind)["approved_folder"])


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
	target = os.path.join(approved_directory(kind), f"{item['id']}.webp")
	copyfile(source, target)
	item.update({"status": "approved", "reviewed_by": reviewer, "reviewed_utc": int(time.time()), "approved_url": f"/i/Obsession/{_config(kind)['approved_folder']}/{item['id']}.webp"})
	write_submission(kind, item["id"], {key: value for key, value in item.items() if key not in {"id", "image_url"}})
	return item


def reject_submission(kind, submission_id, reviewer):
	item = read_submission(kind, submission_id)
	if not item:
		raise FileNotFoundError
	approved_path = os.path.join(approved_directory(kind), item["id"] + ".webp")
	if os.path.isfile(approved_path):
		os.remove(approved_path)
	item.update({"status": "rejected", "reviewed_by": reviewer, "reviewed_utc": int(time.time())})
	write_submission(kind, item["id"], {key: value for key, value in item.items() if key not in {"id", "image_url"}})
	return item
