(() => {
	'use strict';

	function initialize() {
		const modal = document.querySelector('[data-award-purchase-modal]');
		if (!(modal instanceof Element) || modal.dataset.viewportFixed === '1') return;
		modal.dataset.viewportFixed = '1';

		// The shop shell uses visual effects that can create a containing block for
		// position: fixed. Keeping the modal directly under body makes it use the
		// actual browser viewport instead of the catalog's bounds.
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

	if (document.readyState === 'loading') {
		document.addEventListener('DOMContentLoaded', initialize, {once: true});
	} else {
		initialize();
	}
})();