import html
import re
import time

from flask import g

from files.classes import AwardRelationship, Comment, ModAction, Submission, User
from files.helpers.config.const import SITE_NAME
from files.helpers.lazy import lazy


BAN_HAT_PATHS = {
	"grass": "/i/Obsession/ban-hats/grass.webp",
	"award": "/i/Obsession/ban-hats/award.webp",
	"underage": "/i/Obsession/ban-hats/underage.webp",
	"temporary": "/i/Obsession