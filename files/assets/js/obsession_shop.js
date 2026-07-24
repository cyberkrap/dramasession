(() => {
	'use strict';

	function normalize(value) {
		return String(value || '').trim().toLowerCase();
	}

	function initializeCatalog(catalog) {
		if (!(catalog instanceof Element) || catalog.dataset.shopReady === '1') return;
		catalog.dataset.shopReady = '1';

		const shell = catalog.closest('.obs-shop-shell') || document;
		const search = shell.querySelector('[data-shop-search]');
		const filter = shell.querySelector('[data-shop-filter]');
		const counter = shell.querySelector('[data-shop-count]');
		const empty = catalog.querySelector('[data-shop-empty]');
		const cards = Array.from(catalog.querySelectorAll('[data-shop-card]'));

		function update() {
			const query = normalize(search && search.value);
			const selected = normalize(filter && filter.value) || 'all';
			let visible = 0;

			for (const card of cards) {
				const haystack = normalize(card.dataset.search);
				const state = normalize(card.dataset.state);
				const category = normalize(card.dataset.category);
				const matchesSearch = !query || haystack.includes(query);
				const matchesFilter =
					selected === 'all' ||
					selected === state ||
					(selected === 'owned' && (state === 'owned' || state === 'active' || state === 'equipped')) ||
					(selected === 'equipped' && (state === 'equipped' || state === 'active')) ||
					selected === category;
				const show = matchesSearch && matchesFilter;
				card.hidden = !show;
				if (show) visible += 1;
			}

			if (counter) counter.textContent = `${visible} shown`;
			if (empty) empty.hidden = visible !== 0;
		}

		if (search) search.addEventListener('input', update);
		if (filter) filter.addEventListener('change', update);
		update();
	}

	document.addEventListener('DOMContentLoaded', () => {
		document.querySelectorAll('[data-shop-catalog]').forEach(initializeCatalog);
	});
})();
