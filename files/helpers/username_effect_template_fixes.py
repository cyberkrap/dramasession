import os
import tempfile
from pathlib import Path


_COMMENTS_TEMPLATE = Path("files/templates/comments.html")


def _atomic_write(path, content):
	path = Path(path)
	fd, temp_path = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
	try:
		with os.fdopen(fd, "w", encoding="utf-8") as stream:
			stream.write(content)
		os.replace(temp_path, path)
	finally:
		try:
			os.unlink(temp_path)
		except FileNotFoundError:
			pass


def patch_comment_username_effects_source():
	"""Put effect metadata on the exact comment username element.

	The popover JSON remains available for profile popovers, but animated username
	effects must not depend on parsing that larger attribute. Direct metadata also
	lets dynamically inserted comments initialize immediately through the existing
	MutationObserver.
	"""
	source = _COMMENTS_TEMPLATE.read_text(encoding="utf-8")
	original = source

	malformed = "data-pop-info='{{c.author.json_popover(v) | tojson}}'' data-bs-placement="
	fixed = "data-pop-info='{{c.author.json_popover(v) | tojson}}' data-bs-placement="
	if malformed in source:
		source = source.replace(malformed, fixed, 1)

	old_span = '''\t\t\t\t\t\t<span {% if c.author.active_patron and not c.distinguish_level %}class="patron" style="background-color:#{{c.author.name_color}};"{% elif c.distinguish_level %}class="mod {% if SITE_NAME == 'rDrama' %}mod-rdrama{% endif %}"{% endif %}>{{c.author_name}}</span>'''
	new_span = '''\t\t\t\t\t\t<span data-username-effect-user="{{c.author.id}}" data-username-effects="{{c.author.active_username_effects|join(',')}}" data-username-effect-color="{{c.author.username_effect_text_color}}" {% if c.author.active_patron and not c.distinguish_level %}class="patron" style="background-color:#{{c.author.name_color}};"{% elif c.distinguish_level %}class="mod {% if SITE_NAME == 'rDrama' %}mod-rdrama{% endif %}"{% endif %}>{{c.author_name}}</span>'''
	if old_span in source:
		source = source.replace(old_span, new_span, 1)
	elif new_span not in source:
		raise RuntimeError("Could not locate the comment username span")

	if source != original:
		_atomic_write(_COMMENTS_TEMPLATE, source)
	return True
