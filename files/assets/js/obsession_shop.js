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

	function initializeEffectActions(shell) {
		if (!(shell instanceof Element) || shell.dataset.effectActionsReady === '1') return;
		shell.dataset.effectActionsReady = '1';

		const colorButtons = Array.from(shell.querySelectorAll('[data-effect-color-button]'));
		if (colorButtons.length) {
			const picker = document.createElement('input');
			picker.type = 'color';
			picker.className = 'obs-effect-color-input';
			picker.value = `#${String(shell.dataset.effectShopColor || 'ffffff').replace(/^#/, '')}`;
			picker.setAttribute('aria-label', 'Effect username text colour');
			shell.append(picker);

			let sourceButton = colorButtons[0];
			for (const button of colorButtons) {
				button.addEventListener('click', () => {
					sourceButton = button;
					picker.click();
				});
			}

			picker.addEventListener('change', () => {
				const color = picker.value.replace(/^#/, '');
				postToast(sourceButton, '/shop/effects/color', {color}, () => location.reload());
			});
		}

		for (const button of shell.querySelectorAll('[data-effect-gift-url]')) {
			button.addEventListener('click', () => {
				const entered = window.prompt('Gift this effect to which username?');
				if (entered === null) return;
				const username = entered.trim().replace(/^@/, '');
				if (!username) {
					showToast(false, 'Enter a username to receive the gift.');
					return;
				}
				postToast(button, button.dataset.effectGiftUrl, {username}, () => location.reload());
			});
		}
	}

	document.addEventListener('DOMContentLoaded', () => {
		document.querySelectorAll('[data-shop-catalog]').forEach(initializeCatalog);
		document.querySelectorAll('.obs-shop-shell').forEach(initializeEffectActions);
	});
})();
