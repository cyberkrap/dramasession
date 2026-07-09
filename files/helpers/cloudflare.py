import json
from typing import List, Optional, Union

import requests

from files.helpers.config.const import CF_HEADERS, CF_ZONE, DEFAULT_CONFIG_VALUE

CLOUDFLARE_API_URL = "https://api.cloudflare.com/client/v4"
CLOUDFLARE_REQUEST_TIMEOUT_SECS = 5

CLOUDFLARE_AVAILABLE = CF_ZONE and CF_ZONE != DEFAULT_CONFIG_VALUE

def _request_from_cloudflare(url:str, method:str, post_data_str) -> bool:
	if not CLOUDFLARE_AVAILABLE: return False
	try:
		res = str(requests.request(method, f"{CLOUDFLARE_API_URL}/zones/{CF_ZONE}/{url}", headers=CF_HEADERS, data=post_data_str, timeout=CLOUDFLARE_REQUEST_TIMEOUT_SECS))
	except:
		return False
	return res == "<Response [200]>"

def get_security_level() -> Optional[str]:
	res = None
	try:
		res = requests.get(f'{CLOUDFLARE_API_URL}/zones/{CF_ZONE}/settings/security_level', headers=CF_HEADERS, timeout=CLOUDFLARE_REQUEST_TIMEOUT_SECS).json()['result']['value']
	except:
		pass
	return res

def set_security_level(under_attack="high") -> bool:
	return _request_from_cloudflare("settings/security_level", "PATCH", f'{{"value":"{under_attack}"}}')

def clear_entire_cache() -> bool:
	return _request_from_cloudflare("purge_cache", "POST", '{"purge_everything":true}')

def purge_files_in_cache(files:Union[List[str],str]) -> bool:
	if not CLOUDFLARE_AVAILABLE: return False
	if isinstance(files, str):
		files = [files]
	post_data = {"files": files}
	res = None
	try:
		res = requests.post(f'{CLOUDFLARE_API_URL}/zones/{CF_ZONE}/purge_cache', headers=CF_HEADERS, data=json.dumps(post_data), timeout=CLOUDFLARE_REQUEST_TIMEOUT_SECS)
	except:
		return False
	return res == "<Response [200]>"
