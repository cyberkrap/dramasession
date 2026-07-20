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
		"folder