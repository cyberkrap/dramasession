(() => {
	'use strict';

	// TOC renders all visual award effects in award_effects_requested.js.
	// Keep this legacy asset as a no-op because html_head still loads it first.
	// A single renderer prevents competing observers from moving/deleting each
	// other's animation nodes and breaking Furry/Emoji/Ricardo/Fireworks.
	window.__tocLegacyAwardEffectsDisabled = true;
})();
