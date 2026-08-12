(() => {
	'use strict';

	function numeric(card, key) {
		const value = Number(card.dataset[key]);
		return Number.isFinite(value) ? value : 0;
	}

	function text(card, key) {
		return String(card.dataset[key] || '').trim().toLowerCase();
	}

	function initializeHatSort(select) {
		const shell = select.closest('.obs-shop-shell');
		const catalog = shell && shell.querySelector('[data-shop-catalog]');
		if (!catalog) return;

		const cards = Array.from(catalog.querySelectorAll('[data-shop-card]'));
		if (!cards.length) return;
		const container = cards[0].parentElement;
		if (!container) return;

		const originalOrder = new Map(cards.map((card, index) => [card, index]));

		function fallback(left, right) {
			return (originalOrder.get(left) || 0) - (originalOrder.get(right) || 0);
		}

		function compare(left, right, mode) {
			let result = 0;
			switch (mode) {
				case 'price-desc':
					result = numeric(right, 'sortPrice') - numeric(left, 'sortPrice');
					break;
				case 'price-asc':
					result = numeric(left, 'sortPrice') - numeric(right, 'sortPrice');
					break;
				case 'newest':
					result = numeric(right, 'sortCreated') - numeric(left, 'sortCreated');
					break;
				case 'oldest':
					result = numeric(left, 'sortCreated') - numeric(right, 'sortCreated');
					break;
				case 'owners':
					result = numeric(right, 'sortOwners') - numeric(left, 'sortOwners');
					break;
				case 'obtained':
					result = numeric(right, 'sortObtained') - numeric(left, 'sortObtained');
					break;
				case 'name':
					result = text(left, 'sortName').localeCompare(text(right, 'sortName'));
					break;
				default:
					return fallback(left, right);
			}
			return result || fallback(left, right);
		}

		function sortCards() {
			const mode = String(select.value || 'default').trim().toLowerCase();
			const ordered = cards.slice().sort((left, right) => compare(left, right, mode));
			for (const card of ordered) container.appendChild(card);
		}

		select.addEventListener('change', sortCards);
		sortCards();
	}

	document.addEventListener('DOMContentLoaded', () => {
		document.querySelectorAll('[data-shop-sort]').forEach(initializeHatSort);
	});
})();
