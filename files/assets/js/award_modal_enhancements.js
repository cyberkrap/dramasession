(() => {
	'use strict';

	const state = {
		kind: '',
		price: 0,
		coins: 0,
		wishbux: 0,
		owned: 0,
		unlimited: false,
		singleton: false,
	};

	function quantityInput() {
		return document.getElementById('award-quantity');
	}

	function giveButton() {
		return document.getElementById('giveaward');
	}

	function summary() {
		return document.getElementById('award-price-summary');
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

	function updateSummary() {
		const input = quantityInput();
		const button = giveButton();
		const priceSummary = summary();
		if (!input || !button || !priceSummary || !state.kind) return;

		const amount = clampQuantity();
		const inventoryUsed = Math.min(amount, state.owned);
		const purchaseCount = Math.max(0, amount - inventoryUsed);
		const totalPrice = purchaseCount * state.price;
		const canGive = purchaseCount === 0 || state.unlimited || affordablePurchaseCount() >= purchaseCount;

		button.disabled = !canGive;
		if (inventoryUsed && purchaseCount) {
			priceSummary.textContent = `Uses ${inventoryUsed} owned · Price: ${totalPrice.toLocaleString('en-US')} Wishcoins/Wishbux`;
		} else if (inventoryUsed) {
			priceSummary.textContent = `Uses ${inventoryUsed} owned award${inventoryUsed === 1 ? '' : 's'}`;
		} else {
			priceSummary.textContent = `Price: ${totalPrice.toLocaleString('en-US')} Wishcoins/Wishbux`;
		}

		if (!canGive) priceSummary.textContent += ' · insufficient balance';
	}

	window.pick = function(kind, price, coins, marseybux, unlimitedSpending = false, currency = 'marseybux', owned = 0) {
		state.kind = kind;
		state.price = parseInt(price, 10) || 0;
		state.coins = parseInt(coins, 10) || 0;
		state.wishbux = parseInt(marseybux, 10) || 0;
		state.owned = parseInt(owned, 10) || 0;
		state.unlimited = unlimitedSpending === true || unlimitedSpending === 'true';

		const selected = document.getElementById(kind);
		state.singleton = !!selected && selected.dataset.singleton === 'true';
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
			label.textContent = 'Note (optional):';
			note.placeholder = 'Note to include in award notification...';
			note.maxLength = 200;
		}

		resetConfirmation();
		updateSummary();
	};

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
		const label = choice.querySelector('.award-price');
		if (label) label.textContent = state.owned > 0 ? `${state.owned} owned` : `Price: ${state.price.toLocaleString('en-US')}`;
	}

	window.giveaward = async function(button) {
		if (!state.kind || button.disabled) return;
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

		const modal = document.getElementById('awardModal');
		if (modal) modal.addEventListener('show.bs.modal', resetConfirmation);
	}

	if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init, {once: true});
	else init();
})();
