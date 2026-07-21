import copy
import os

import yt_dlp


_CLIENT_ATTEMPTS = (
	("mweb-po-token", ["mweb"]),
	("default", None),
	("android_vr", ["android_vr"]),
	("web_safari", ["web_safari"]),
)


def download_youtube_audio(video_id, base_options):
	"""Download anthem audio with PO-token support, retries, and optional proxying."""
	errors = []
	proxy = os.environ.get("YOUTUBE_PROXY", "").strip()
	impersonate = os.environ.get("YOUTUBE_IMPERSONATE", "").strip()

	for label, player_clients in _CLIENT_ATTEMPTS:
		options = copy.deepcopy(base_options)
		options.update({
			"retries": 3,
			"fragment_retries": 3,
			"extractor_retries": 3,
			"socket_timeout": 30,
			"overwrites": True,
		})
		if player_clients:
			extractor_args = copy.deepcopy(options.get("extractor_args") or {})
			youtube_args = copy.deepcopy(extractor_args.get("youtube") or {})
			youtube_args["player_client"] = player_clients
			extractor_args["youtube"] = youtube_args
			options["extractor_args"] = extractor_args
		if proxy:
			options["proxy"] = proxy
		if impersonate:
			options["impersonate"] = impersonate

		try:
			with yt_dlp.YoutubeDL(options) as ydl:
				ydl.download([f"https://www.youtube.com/watch?v={video_id}"])
			return label
		except Exception as exc:
			errors.append(f"{label}: {type(exc).__name__}: {str(exc)[:300]}")

	raise RuntimeError("All YouTube extraction clients failed. " + " | ".join(errors))