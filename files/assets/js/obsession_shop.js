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

	function initializeAwardPurchases(shell) {
		if (!(shell instanceof Element) || shell.dataset.awardPurchasesReady === '1') return;
		shell.dataset.awardPurchasesReady = '1';

		for (const button of shell.querySelectorAll('[data-award-buy-url]')) {
			button.addEventListener('click', () => {
				if (button.disabled || button.dataset.purchasePending === '1') return;

				const title = String(button.dataset.awardTitle || 'this award').trim();
				const price = String(button.dataset.awardPrice || '').trim();
				const priceText = price ? ` for ${price} Wishbux` : '';
				if (!window.confirm(`Are you sure you want to buy ${title}${priceText}?`)) return;

				const url = String(button.dataset.awardBuyUrl || '').trim();
				if (!url || typeof postToastReload !== 'function') {
					showToast(false, 'This award cannot be purchased right now.');
					return;
				}

				button.dataset.purchasePending = '1';
				postToastReload(button, url);
			});
		}
	}

	function initializeEffectActions(shell) {
		if (!(shell instanceof Element) || shell.dataset.effectActionsReady === '1') return;
		shell.dataset.effectActionsReady = '1';

		let activeModal = null;
		let lastFocused = null;

		function closeModal(modal = activeModal) {
			if (!(modal instanceof Element)) return;
			modal.hidden = true;
			modal.setAttribute('aria-hidden', 'true');
			document.body.classList.remove('obs-effect-modal-open');
			if (activeModal === modal) activeModal = null;
			if (lastFocused instanceof HTMLElement && lastFocused.isConnected) lastFocused.focus();
			lastFocused = null;
		}

		function openModal(modal, focusTarget) {
			if (!(modal instanceof Element)) return;
			if (activeModal && activeModal !== modal) closeModal(activeModal);
			lastFocused = document.activeElement instanceof HTMLElement ? document.activeElement : null;
			activeModal = modal;
			modal.hidden = false;
			modal.setAttribute('aria-hidden', 'false');
			document.body.classList.add('obs-effect-modal-open');
			window.requestAnimationFrame(() => {
				const target = focusTarget || modal.querySelector('input, button, select, textarea');
				if (target instanceof HTMLElement) target.focus();
			});
		}

		for (const closeButton of shell.querySelectorAll('[data-effect-modal-close]')) {
			closeButton.addEventListener('click', () => closeModal(closeButton.closest('.obs-effect-modal')));
		}

		document.addEventListener('keydown', event => {
			if (event.key === 'Escape' && activeModal) {
				event.preventDefault();
				closeModal(activeModal);
			}
		});

		const colorModal = shell.querySelector('[data-effect-color-modal]');
		const colorForm = shell.querySelector('[data-effect-color-form]');
		const colorInput = shell.querySelector('#effect-color-hex');
		const colorSave = shell.querySelector('[data-effect-color-save]');
		const colorSwatches = Array.from(shell.querySelectorAll('[data-effect-color]'));

		function cleanColor(value) {
			return String(value || '').trim().replace(/^#/, '').toLowerCase();
		}

		function selectColor(value) {
			const color = cleanColor(value);
			if (colorInput instanceof HTMLInputElement) colorInput.value = color;
			for (const swatch of colorSwatches) {
				const selected = cleanColor(swatch.dataset.effectColor) === color;
				swatch.classList.toggle('is-selected', selected);
				swatch.setAttribute('aria-pressed', selected ? 'true' : 'false');
			}
		}

		if (colorModal && colorForm && colorInput && colorSave) {
			selectColor(shell.dataset.effectShopColor || colorInput.value);

			for (const button of shell.querySelectorAll('[data-effect-color-button]')) {
				button.addEventListener('click', () => {
					selectColor(shell.dataset.effectShopColor || colorInput.value);
					openModal(colorModal, colorInput);
				});
			}

			for (const swatch of colorSwatches) {
				swatch.addEventListener('click', () => {
					selectColor(swatch.dataset.effectColor);
					colorInput.focus();
				});
			}

			colorInput.addEventListener('input', () => selectColor(colorInput.value));

			colorForm.addEventListener('submit', event => {
				event.preventDefault();
				const color = cleanColor(colorInput.value);
				if (!/^[0-9a-f]{6}$/.test(color)) {
					showToast(false, 'Enter a valid six-digit color hex code.');
					colorInput.focus();
					return;
				}
				postToast(colorSave, '/shop/effects/color', {color}, () => location.reload());
			});
		}

		const giftModal = shell.querySelector('[data-effect-gift-modal]');
		const giftForm = shell.querySelector('[data-effect-gift-form]');
		const giftInput = shell.querySelector('#effect-gift-username');
		const giftName = shell.querySelector('[data-effect-gift-name]');
		const giftSave = shell.querySelector('[data-effect-gift-save]');

		if (giftModal && giftForm && giftInput && giftSave) {
			for (const button of shell.querySelectorAll('[data-effect-gift-url]')) {
				button.addEventListener('click', () => {
					giftForm.dataset.action = button.dataset.effectGiftUrl || '';
					giftInput.value = '';
					if (giftName) giftName.textContent = button.dataset.effectTitle || 'this effect';
					openModal(giftModal, giftInput);
				});
			}

			giftForm.addEventListener('submit', event => {
				event.preventDefault();
				const username = String(giftInput.value || '').trim().replace(/^@/, '');
				const action = giftForm.dataset.action || '';
				if (!action) {
					showToast(false, 'This effect cannot be gifted right now.');
					return;
				}
				if (!username) {
					showToast(false, 'Enter a username to receive the gift.');
					giftInput.focus();
					return;
				}
				postToast(giftSave, action, {username}, () => location.reload());
			});
		}
	}

	document.addEventListener('DOMContentLoaded', () => {
		document.querySelectorAll('[data-shop-catalog]').forEach(initializeCatalog);
		document.querySelectorAll('.obs-shop-shell').forEach(shell => {
			initializeAwardPurchases(shell);
			initializeEffectActions(shell);
		});
	});
})();
