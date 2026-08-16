(() => {
	'use strict';

	const state = {
		kind: '',
		price: 0,
		basePrice: 0,
		coins: 0,
		wishbux: 0,
		owned: 0,
		unlimited: false,
		singleton: false,
		currencyLabel: 'Wishcoins/Wishbux',
		emojiName: '',
	};

	let activeTooltip = null;
	let activeTooltipTarget = null;

	function quantityInput() {
		return document.getElementById('award-quantity');
	}

	function giveButton() {
		return document.getElementById('giveaward');
	}

	function summary() {
		return document.getElementById('award-price-summary');
	}

	function emojiWrap() {
		return document.getElementById('award-emoji-wrap');
	}

	function emojiInput() {
		return document.getElementById('award-emoji-input');
	}

	function emojiPreview() {
		return document.getElementById('award-emoji-preview');
	}

	function emojiPicker() {
		return document.getElementById('award-emoji-picker');
	}

	function clampQuantity() {
		const input = quantityInput();
		if (!input) return 1;
		const max = state.singleton ? 1 : 30;
		let value = parseInt(input.value, 10);
		if (!Number.isFinite(value)) value = 1;
		value = Math.max(1, Math.min(max, value));
		input.value = String(value);
		input.max = String(max);
		return value;
	}

	function resetConfirmation() {
		const button = giveButton();
		if (!button) return;
		button.dataset.confirmed = '0';
		button.textContent = 'Give Award';
	}

	function affordablePurchaseCount() {
		if (state.unlimited || state.price <= 0) return 30;
		return Math.floor(state.coins / state.price) + Math.floor(state.wishbux / state.price);
	}

	function money(value) {
		return Number(value || 0).toLocaleString('en-US');
	}

	function clearEmojiChoice() {
		state.emojiName = '';
		const input = emojiInput();
		const preview = emojiPreview();
		const picker = emojiPicker();
		if (input) input.value = '';
		if (preview) {
			preview.removeAttribute('src');
			preview.alt = '';
			preview.classList.add('d-none');
		}
		const label = picker?.querySelector('span');
		if (label) label.textContent = 'Pick an Emoji';
	}

	function updateEmojiSelector() {
		const wrap = emojiWrap();
		if (!wrap) return;
		wrap.classList.toggle('d-none', state.kind !== 'wholesome');
	}

	function updateSummary() {
		const input = quantityInput();
		const button = giveButton();
		const priceSummary = summary();
		if (!input || !button || !priceSummary || !state.kind) return;

		const amount = clampQuantity();
		const inventoryUsed = Math.min(amount, state.owned);
		const purchaseCount = Math.max(0, amount - inventoryUsed);
		const totalPrice = purchaseCount * state.price;
		const totalBasePrice = purchaseCount * state.basePrice;
		const hasDiscount = totalBasePrice > totalPrice;
		const financiallyAllowed = purchaseCount === 0 || state.unlimited || affordablePurchaseCount() >= purchaseCount;
		const needsEmoji = state.kind === 'wholesome' && !state.emojiName;
		const canGive = financiallyAllowed && !needsEmoji;

		button.disabled = !canGive;

		if (needsEmoji) {
			priceSummary.innerHTML = '<span class="award-summary-insufficient">Pick an emoji to continue</span>';
			return;
		}

		if (purchaseCount === 0) {
			priceSummary.innerHTML = `<span class="award-summary-owned">Using ${inventoryUsed} owned award${inventoryUsed === 1 ? '' : 's'} — no charge</span>`;
		} else {
			const ownedPrefix = inventoryUsed
				? `<span class="award-summary-owned">${inventoryUsed} owned</span><span class="award-summary-separator">·</span>`
				: '';
			const countLabel = purchaseCount > 1 ? `${purchaseCount} purchased` : 'Purchase';
			const prices = hasDiscount
				? `<span class="award-summary-original">${money(totalBasePrice)}</span><strong class="award-summary-current">${money(totalPrice)}</strong>`
				: `<strong class="award-summary-current">${money(totalPrice)}</strong>`;

			priceSummary.innerHTML = `${ownedPrefix}<span>${countLabel}</span><span class="award-summary-separator">·</span>${prices}<span>${state.currencyLabel}</span>`;
		}

		if (!financiallyAllowed) {
			priceSummary.insertAdjacentHTML('beforeend', '<span class="award-summary-insufficient">Insufficient balance</span>');
		}
	}

	window.pick = function(kind, price, coins, marseybux, unlimitedSpending = false, currency = 'marseybux', owned = 0) {
		const previousKind = state.kind;
		state.kind = kind;
		state.price = parseInt(price, 10) || 0;
		state.coins = parseInt(coins, 10) || 0;
		state.wishbux = parseInt(marseybux, 10) || 0;
		state.owned = parseInt(owned, 10) || 0;
		state.unlimited = unlimitedSpending === true || unlimitedSpending === 'true';
		state.currencyLabel = kind === 'benefactor' ? 'Wishbux' : 'Wishcoins/Wishbux';
		if (kind !== 'wholesome' || previousKind !== 'wholesome') clearEmojiChoice();
		updateEmojiSelector();

		const selected = document.getElementById(kind);
		state.singleton = !!selected && selected.dataset.singleton === 'true';
		state.basePrice = selected ? (parseInt(selected.dataset.basePrice, 10) || state.price) : state.price;
		document.getElementById('kind').value = kind;

		for (const choice of document.querySelectorAll('#awardModal .award-choice.picked')) {
			choice.classList.remove('picked');
		}
		if (selected) selected.classList.add('picked');

		const input = quantityInput();
		if (input) {
			input.disabled = state.singleton;
			input.max = state.singleton ? '1' : '30';
			if (state.singleton) input.value = '1';
		}

		const label = document.getElementById('notelabel');
		const note = document.getElementById('note');
		if (kind === 'flairlock') {
			label.textContent = 'New flair:';
			note.placeholder = 'Insert new flair here, or leave empty to extend the current flair.';
			note.maxLength = 100;
		} else {
			label.innerHTML = 'Note <span>(optional)</span>';
			note.placeholder = 'Add a message for the recipient...';
			note.maxLength = 200;
		}

		resetConfirmation();
		updateSummary();
	};

	window.pickAwardEmoji = function() {
		if (state.kind !== 'wholesome') return;
		for (const modifier of document.querySelectorAll('#emojiModal .emoji-suffix, #emojiModal .emoji-postfix')) {
			modifier.checked = false;
		}
		const input = emojiInput();
		if (input) {
			input.value = '';
			input.focus();
			try { input.setSelectionRange(0, 0); } catch (_) {}
		}
		if (typeof loadEmojis === 'function') loadEmojis('award-emoji-input');
	};

	function applyEmojiInput() {
		if (state.kind !== 'wholesome') return;
		const input = emojiInput();
		if (!input) return;
		const match = /^:([A-Za-z0-9_-]{1,80}):$/.exec(input.value.trim());
		if (!match) return;

		state.emojiName = match[1];
		const preview = emojiPreview();
		if (preview) {
			preview.src = `/e/${encodeURIComponent(state.emojiName)}.webp`;
			preview.alt = `:${state.emojiName}:`;
			preview.classList.remove('d-none');
		}
		const label = emojiPicker()?.querySelector('span');
		if (label) label.textContent = 'Change Emoji';
		resetConfirmation();
		updateSummary();

		const modal = document.getElementById('emojiModal');
		if (modal && window.bootstrap?.Modal) bootstrap.Modal.getOrCreateInstance(modal).hide();
	}

	function parseResponse(xhr) {
		try {
			return JSON.parse(xhr.responseText || '{}');
		} catch (_) {
			return {};
		}
	}

	function sendAward(url, payload) {
		return new Promise((resolve, reject) => {
			const form = new FormData();
			for (const [key, value] of Object.entries(payload)) form.append(key, value);
			const request = createXhrWithFormKey(url, 'POST', form);
			const xhr = request[0];
			xhr.onload = () => {
				const data = parseResponse(xhr);
				if (xhr.status >= 200 && xhr.status < 300) resolve(data);
				else reject(new Error(data.details || data.error || 'Error, please try again later.'));
			};
			xhr.onerror = () => reject(new Error('Network error, please try again.'));
			xhr.send(request[1]);
		});
	}

	function updateOwnedDisplay(amount) {
		if (!state.kind || state.owned <= 0) return;
		const inventoryUsed = Math.min(amount, state.owned);
		state.owned = Math.max(0, state.owned - inventoryUsed);
		const choice = document.getElementById(state.kind);
		if (!choice) return;

		choice.dataset.owned = String(state.owned);
		const ownedLabel = choice.querySelector('.award-owned-count');
		if (ownedLabel) {
			if (state.owned > 0) ownedLabel.textContent = `${state.owned} owned`;
			else ownedLabel.remove();
		}
	}

	window.giveaward = async function(button) {
		if (!state.kind || button.disabled) return;
		if (state.kind === 'wholesome' && !state.emojiName) {
			showToast(false, 'You need to provide an emoji name!');
			return;
		}
		const amount = clampQuantity();

		if (button.dataset.confirmed !== '1') {
			button.dataset.confirmed = '1';
			button.textContent = 'Are you sure?';
			return;
		}

		button.disabled = true;
		button.textContent = 'Giving...';
		try {
			const result = await sendAward(button.dataset.action, {
				kind: state.kind,
				note: document.getElementById('note').value,
				currency: 'marseybux',
				amount: amount,
				emoji: state.kind === 'wholesome' ? state.emojiName : '',
			});
			updateOwnedDisplay(amount);
			showToast(true, result.message || 'Award given successfully!');
			const modal = document.getElementById('awardModal');
			bootstrap.Modal.getOrCreateInstance(modal).hide();
		} catch (error) {
			showToast(false, error.message);
		} finally {
			resetConfirmation();
			updateSummary();
		}
	};

	function hideAwardTooltip() {
		if (activeTooltip) activeTooltip.remove();
		activeTooltip = null;
		activeTooltipTarget = null;
	}

	function positionAwardTooltip(target, tooltip) {
		const rect = target.getBoundingClientRect();
		const tipRect = tooltip.getBoundingClientRect();
		const edge = 8;
		const gap = 9;
		const targetCenter = rect.left + rect.width / 2;
		let left = targetCenter - tipRect.width / 2;
		left = Math.max(edge, Math.min(left, window.innerWidth - tipRect.width - edge));

		let top = rect.top - tipRect.height - gap;
		let below = false;
		if (top < edge) {
			below = true;
			top = rect.bottom + gap;
		}
		if (top + tipRect.height > window.innerHeight - edge) {
			top = Math.max(edge, window.innerHeight - tipRect.height - edge);
		}

		const arrowLeft = Math.max(12, Math.min(targetCenter - left, tipRect.width - 12));
		tooltip.style.setProperty('--award-tooltip-arrow-left', `${Math.round(arrowLeft)}px`);
		tooltip.classList.toggle('is-below', below);
		tooltip.style.left = `${Math.round(left)}px`;
		tooltip.style.top = `${Math.round(top)}px`;
	}

	function showAwardTooltip(choice) {
		const source = choice.querySelector('.award-inline-tooltip');
		if (!source) return;
		if (activeTooltipTarget === choice && activeTooltip) return;
		hideAwardTooltip();

		const tooltip = document.createElement('div');
		tooltip.className = 'award-floating-tooltip';
		tooltip.setAttribute('role', 'tooltip');
		tooltip.innerHTML = source.innerHTML;
		document.body.appendChild(tooltip);
		activeTooltip = tooltip;
		activeTooltipTarget = choice;
		positionAwardTooltip(choice, tooltip);
	}

	function bindAwardTooltips() {
		for (const choice of document.querySelectorAll('#awardModal .award-choice')) {
			if (choice.dataset.awardTooltipBound === '1') continue;
			choice.dataset.awardTooltipBound = '1';
			choice.addEventListener('mouseenter', () => showAwardTooltip(choice));
			choice.addEventListener('mouseleave', hideAwardTooltip);
			choice.addEventListener('focus', () => showAwardTooltip(choice));
			choice.addEventListener('blur', hideAwardTooltip);
		}
	}

	function init() {
		const input = quantityInput();
		if (input) {
			input.addEventListener('input', () => {
				resetConfirmation();
				updateSummary();
			});
			input.addEventListener('change', () => {
				clampQuantity();
				resetConfirmation();
				updateSummary();
			});
		}

		const note = document.getElementById('note');
		if (note) note.addEventListener('input', resetConfirmation);
		const awardEmojiInput = emojiInput();
		if (awardEmojiInput) awardEmojiInput.addEventListener('input', applyEmojiInput);

		bindAwardTooltips();
		const modal = document.getElementById('awardModal');
		if (modal) {
			modal.addEventListener('show.bs.modal', resetConfirmation);
			modal.addEventListener('shown.bs.modal', bindAwardTooltips);
			modal.addEventListener('hidden.bs.modal', () => {
				hideAwardTooltip();
				clearEmojiChoice();
				state.kind = '';
				updateEmojiSelector();
			});
		}
		window.addEventListener('resize', hideAwardTooltip, {passive: true});
		window.addEventListener('scroll', hideAwardTooltip, {passive: true, capture: true});
	}

	if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init, {once: true});
	else init();
})();
