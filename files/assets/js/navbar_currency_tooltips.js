(() => {
	'use strict';

	const descriptions = {
		Wishcoins: 'Wishcoins - Earned from votes on your posts and comments.',
		Wishbux: 'Wishbux - Earned by supporting Obsession.',
	};

	function installTooltip(row, text) {
		if (!(row instanceof Element)) return;
		row.setAttribute('title', text);
		row.setAttribute('aria-label', text);
		row.dataset.bsToggle = 'tooltip';
		row.dataset.bsPlacement = 'bottom';
		row.style.cursor = 'help';

		row.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(child => {
			if (child === row) return;
			if (window.bootstrap?.Tooltip) {
				window.bootstrap.Tooltip.getInstance(child)?.dispose();
			}
			child.removeAttribute('data-bs-toggle');
			child.removeAttribute('data-bs-original-title');
			child.removeAttribute('title');
		});

		if (window.bootstrap?.Tooltip) {
			window.bootstrap.Tooltip.getInstance(row)?.dispose();
			window.bootstrap.Tooltip.getOrCreateInstance(row, {
				container: 'body',
				placement: 'bottom',
				fallbackPlacements: [],
				boundary: 'viewport',
				offset: [0, 6],
			});
		}
	}

	function enhanceCurrencyTooltips() {
		document.querySelectorAll('.header--currency img[alt]').forEach(icon => {
			const text = descriptions[icon.alt];
			if (text) installTooltip(icon.closest('.header--currency'), text);
		});

		document.querySelectorAll('.mobile-drawer-balance span').forEach(item => {
			const icon = item.querySelector('img[alt]');
			const text = icon && descriptions[icon.alt];
			if (!text) return;
			item.setAttribute('title', text);
			item.setAttribute('aria-label', text);
		});
	}

	if (document.readyState === 'loading') {
		document.addEventListener('DOMContentLoaded', enhanceCurrencyTooltips, {once: true});
	} else {
		enhanceCurrencyTooltips();
	}
})();
