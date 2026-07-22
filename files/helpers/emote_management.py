import json
import os
import re
import shutil
from pathlib import Path

from files.helpers.persistent_site_content import get_site_content, set_site_content

EMOTE_ROOT = Path('/asset_submissions/marseys')
EMOTE_PENDING_DIR = EMOTE_ROOT / 'pending'
EMOTE_APPROVED_DIR = EMOTE_ROOT / 'approved'
EMOTE_ORIGINAL_DIR = EMOTE_ROOT / 'original'
DEFAULT_EMOTE_CATEGORIES = ['Community Emotes', 'Community Classics', 'Misc']
_CATEGORY_KEY = 'emote_categories:v1'
_CATEGORY_MAP_KEY = 'emote_category_map:v1'
_SAFE_CATEGORY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9 '&+._-]{0,39}$")


def ensure_emote_directories():
	for directory in (EMOTE_ROOT, EMOTE_PENDING_DIR, EMOTE_APPROVED_DIR, EMOTE_ORIGINAL_DIR):
		directory.mkdir(parents=True, exist_ok=True)


def get_emote_categories():
	try: stored = json.loads(get_site_content(_CATEGORY_KEY, '[]') or '[]')
	except Exception: stored = []
	categories = []
	for category in DEFAULT_EMOTE_CATEGORIES + list(stored):
		category = str(category).strip()
		if category and category not in categories: categories.append(category)
	return categories


def save_emote_categories(categories, actor=None):
	clean = []
	for category in categories:
		category = str(category).strip()
		if category in DEFAULT_EMOTE_CATEGORIES: continue
		if not _SAFE_CATEGORY.fullmatch(category): raise ValueError('Invalid category name.')
		if category not in clean: clean.append(category)
	set_site_content(_CATEGORY_KEY, json.dumps(clean), actor)


def get_emote_category_map():
	try:
		data = json.loads(get_site_content(_CATEGORY_MAP_KEY, '{}') or '{}')
		return data if isinstance(data, dict) else {}
	except Exception: return {}


def save_emote_category_map(mapping, actor=None):
	set_site_content(_CATEGORY_MAP_KEY, json.dumps(mapping, sort_keys=True), actor)


def category_for_emote(name):
	category = get_emote_category_map().get(name, 'Community Emotes')
	return category if category in get_emote_categories() else 'Community Emotes'


def set_emote_category(name, category, actor=None):
	if category not in get_emote_categories(): raise ValueError('Unknown category.')
	mapping = get_emote_category_map(); mapping[name] = category
	save_emote_category_map(mapping, actor)


def pending_raw_path(name): return EMOTE_PENDING_DIR / name
def pending_webp_path(name): return EMOTE_PENDING_DIR / f'{name}.webp'
def approved_webp_path(name): return EMOTE_APPROVED_DIR / f'{name}.webp'
def legacy_raw_path(name): return EMOTE_ROOT / name
def legacy_webp_path(name): return EMOTE_ROOT / f'{name}.webp'


def find_pending_raw(name):
	for candidate in (pending_raw_path(name), legacy_raw_path(name)):
		if candidate.is_file(): return candidate


def find_pending_webp(name):
	for candidate in (pending_webp_path(name), legacy_webp_path(name)):
		if candidate.is_file(): return candidate


def custom_emote_exists(name): return approved_webp_path(name).is_file()
def custom_emote_url(name): return f'/community-emote/{name}.webp'


def remove_emote_files(name):
	ensure_emote_directories()
	for candidate in (pending_raw_path(name), pending_webp_path(name), approved_webp_path(name), legacy_raw_path(name), legacy_webp_path(name)):
		try: candidate.unlink()
		except FileNotFoundError: pass
	for candidate in EMOTE_ORIGINAL_DIR.glob(f'{name}.*'):
		try: candidate.unlink()
		except FileNotFoundError: pass


def rename_emote_files(old_name, new_name):
	ensure_emote_directories()
	for old, new in ((pending_raw_path(old_name), pending_raw_path(new_name)), (pending_webp_path(old_name), pending_webp_path(new_name)), (approved_webp_path(old_name), approved_webp_path(new_name)), (legacy_raw_path(old_name), legacy_raw_path(new_name)), (legacy_webp_path(old_name), legacy_webp_path(new_name))):
		if old.is_file(): os.replace(old, new)
	for old in EMOTE_ORIGINAL_DIR.glob(f'{old_name}.*'): os.replace(old, old.with_name(new_name + old.suffix.lower()))
	mapping = get_emote_category_map()
	if old_name in mapping:
		mapping[new_name] = mapping.pop(old_name); save_emote_category_map(mapping)


def approve_emote_files(name):
	ensure_emote_directories()
	processed = find_pending_webp(name)
	if not processed: raise FileNotFoundError
	shutil.copyfile(processed, approved_webp_path(name))
	for candidate in (pending_raw_path(name), pending_webp_path(name), legacy_raw_path(name), legacy_webp_path(name)):
		try: candidate.unlink()
		except FileNotFoundError: pass


def install_custom_emote_rendering():
	from files.helpers import sanitize as sanitize_module
	original = sanitize_module.render_emoji
	if getattr(original, '_persistent_custom_emotes', False): return
	def wrapped(html, regexp, golden, marseys_used, b=False):
		html = original(html, regexp, golden, marseys_used, b=b)
		for match in list(regexp.finditer(html)):
			old = match.group(1).lower()
			name = old.replace('!', '').replace('#', '')
			if name.endswith('pat') or not custom_emote_exists(name): continue
			attrs = ' b' if b else ''
			replacement = f'<img loading="lazy" data-bs-toggle="tooltip" alt=":{old}:" title=":{old}:" src="{custom_emote_url(name)}"{attrs}>'
			html = re.sub(f'(?<!"){match.group(0)}(?![^<]*</(code|pre|a)>)', replacement, html)
			marseys_used.add(name)
		return html
	wrapped._persistent_custom_emotes = True
	sanitize_module.render_emoji = wrapped
