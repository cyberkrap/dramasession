(() => {
	'use strict';

	function initialize() {
		const modal = document.querySelector('[data-award-purchase-modal]');
		if (!(modal instanceof Element) || modal.dataset.viewportFixed === '1') return;
		modal.dataset.viewportFixed = '1';

		// The original shop script attaches purchase handlers during DOMContentLoaded.
		// Move the modal only after those handlers exist, otherwise the shell lookup
		// cannot find it and every Buy button becomes inert.
		if (modal.parentElement !== document.body) document.body.appendChild(modal);

		const currencyNode = modal.querySelector('[data-award-confirm-currency]');
		const noteNode = modal.querySelector('[data-award-confirm-note]');
		const dialog = modal.querySelector('.obs-purchase-modal__dialog');

		for (const button of document.querySelectorAll('[data-award-buy-url]')) {
			button.addEventListener('click', () => {
				const currency = String(button.dataset.awardCurrency || 'Wishbux or Wishcoins').trim();
				if (currencyNode) currencyNode.textContent = currency;

				if (noteNode) {
					if (currency === 'Wishcoins') {
						noteNode.textContent = 'Wishcoins will be deducted because Wishbux cannot cover this purchase.';
					} else if (currency === 'Wishbux') {
						noteNode.textContent = 'Wishbux will be deducted from your balance.';
					} else {
						noteNode.textContent = 'Wishbux is used first. If it cannot cover the price, Wishcoins are used instead.';
					}
				}

				modal.scrollTop = 0;
				if (dialog instanceof HTMLElement) dialog.scrollTop = 0;
			});
		}
	}

	// Deferred scripts run while readyState is often "interactive", before the
	// DOMContentLoaded event. Waiting for that event preserves listener order:
	// obsession_shop.js initializes first, then this script moves the modal.
	if (document.readyState === 'complete') initialize();
	else document.addEventListener('DOMContentLoaded', initialize, {once: true});
})();