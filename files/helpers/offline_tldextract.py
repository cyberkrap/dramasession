def configure_tldextract_offline():
	"""Use tldextract's bundled PSL snapshot and never fetch it during requests."""
	try:
		import tldextract
	except ImportError:
		return

	extractor = tldextract.TLDExtract(
		suffix_list_urls=(),
		fallback_to_snapshot=True,
	)
	tldextract.extract = extractor

	# Keep compatibility with versions that expose the default extractor
	# from the implementation module as well as from the package root.
	try:
		from tldextract import tldextract as implementation
		for name in ("TLD_EXTRACTOR", "_DEFAULT_TLD_EXTRACTOR"):
			if hasattr(implementation, name):
				setattr(implementation, name, extractor)
	except (ImportError, AttributeError):
		pass
