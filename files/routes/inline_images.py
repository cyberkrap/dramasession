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
from files.routes.wrappers import auth_required, get_ID


MAX_REMOTE