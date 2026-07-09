import re

from owoify.structures.word import Word
from owoify.utility.interleave_arrays import interleave_arrays
from owoify.utility.presets import *

import files.helpers.regex as help_re
import files.helpers.sanitize as sanitize

# Includes, excerpts, and modifies some functions from:
# https://github.com/deadshot465/owoify-py @ owoify/owoify.py

OWO_WORD_REGEX = re.compile(r'[^\s]+')
OWO_SPACE_REGEX = re.compile(r'\s+')

OWO_EXCLUDE_PATTERNS = [
	re.compile(r'\]\('), # links []() and images ![]()
		# NB: May not be effective when URL part contains literal spaces vs %20
		# Also relies on owoify replacements currently not affecting symbols.
	sanitize.url_re, # bare links
	re.compile(r':[!#@a-z0-9_\-]+:', flags=re.I|re.A), # emoji
	help_re.mention_regex, # mentions
	help_re.poll_regex, # polls
	help_re.choice_regex,
	help_re.command_regex, # markup commands
	re.compile(r'\bthe\b', flags=re.I|re.A), # exclude: 'the' ↦ 'teh'
]

def owoify(source: str) -> str:
	word_matches = OWO_WORD_REGEX.findall(source)
	space_matches = OWO_SPACE_REGEX.findall(source)

	words = [Word(s) for s in word_matches]
	spaces = [Word(s) for s in space_matches]

	words = list(map(lambda w: owoify_map_token_custom(w), words))

	result = interleave_arrays(words, spaces)
	result_strings = list(map(lambda w: str(w), result))
	return ''.join(result_strings)

def owoify_map_token_custom(token):
	for pattern in OWO_EXCLUDE_PATTERNS:
		# if pattern appears anywhere in token, do not owoify.
		if pattern.search(token.word):
			return token

	# Original Owoification Logic (sans cases for higher owo levels)
	for func in SPECIFIC_WORD_MAPPING_LIST:
		token = func(token)

	for func in OWO_MAPPING_LIST:
		token = func(token)
	# End Original Owoification Logic

	return token
