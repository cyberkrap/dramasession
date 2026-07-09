import os
import zlib
from collections import defaultdict

import gevent
import gevent_inotifyx as inotify

from files.helpers.config.const import IS_FISTMAS

ASSET_DIR = 'files/assets'
ASSET_SUBDIRS = ['/css', '/js', '/js/vendor']
ASSET_URL = '/assets/'
ASSET_CACHE = defaultdict(lambda: None)

if IS_FISTMAS():
	ASSET_SUBDIRS.extend(['/fistmas/css', '/fistmas/css/themes', '/fistmas/js', '/fistmas/js/vendor'])

def assetcache_build(asset_dir, subdirs):
	for subdir in subdirs:
		for root, dirs, files in os.walk(asset_dir + subdir):
			for fname in files:
				fpath = root + '/' + fname
				relpath = fpath[len(asset_dir) + 1:].replace('\\', '/')
				with open(fpath, 'rb') as f:
					fhash = zlib.crc32(f.read())
					ASSET_CACHE[relpath] = '%x' % fhash

def assetcache_hash(asset_path):
	return ASSET_CACHE[asset_path]

def assetcache_path(asset_path):
	cachehash = assetcache_hash(asset_path)

	url = ASSET_URL + asset_path
	if cachehash:
		url += '?v=' + cachehash

	return url

def assetcache_watch_directories(asset_dir, subdirs):
	fd = inotify.init()
	try:
		for sd in subdirs:
			inotify.add_watch(fd, asset_dir + sd, inotify.IN_CLOSE_WRITE)
		while True:
			for event in inotify.get_events(fd, 0):
				print("Rebuilding assetcache: " + event.name, flush=True)
				assetcache_build(asset_dir, subdirs)
				break
			gevent.sleep(0.5)
	finally:
		os.close(fd)

assetcache_build(ASSET_DIR, ASSET_SUBDIRS)
gevent.spawn(assetcache_watch_directories, ASSET_DIR, ASSET_SUBDIRS)
