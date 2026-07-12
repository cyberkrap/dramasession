function toggleElement(id, id2) {
	for (const el of document.getElementsByClassName('toggleable')) {
		if (el.id !== id) el.classList.add('d-none');
	}
	const panel = document.getElementById(id);
	const input = document.getElementById(id2);
	if (panel) panel.classList.toggle('d-none');
	if (input) input.focus();
}

const TRANSFER_TAX = Number(document.getElementById('tax')?.textContent || 0);

function updateTax() {
	const amount = parseInt(document.getElementById('coin-transfer-amount')?.value || 0);
	const output = document.getElementById('coins-transfer-taxed');
	if (output && amount > 0) output.innerText = amount - Math.ceil(amount * TRANSFER_TAX);
}

function updateBux() {
	const amount = parseInt(document.getElementById('bux-transfer-amount')?.value || 0);
	const output = document.getElementById('bux-transfer-taxed');
	if (output && amount > 0) output.innerText = amount;
}

function transferCoins(t) {
	for (const el of document.getElementsByClassName('toggleable')) el.classList.add('d-none');
	const amountInput = document.getElementById('coin-transfer-amount');
	const reasonInput = document.getElementById('coin-transfer-reason');
	const amount = parseInt(amountInput?.value || 0);
	const transferred = amount - Math.ceil(amount * TRANSFER_TAX);
	const username = document.getElementById('username').innerHTML;

	t.disabled = true;
	postToast(t, `/@${username}/transfer_coins`, {
		amount: amountInput.value,
		reason: reasonInput.value
	}, () => {
		const ownBalance = document.getElementById('user-coins-amount');
		const profileBalance = document.getElementById('profile-coins-amount');
		if (ownBalance) ownBalance.innerText = parseInt(ownBalance.innerText) - amount;
		if (profileBalance) profileBalance.innerText = parseInt(profileBalance.innerText) + transferred;
	});
	setTimeout(() => t.disabled = false, 2000);
}

function transferBux(t) {
	for (const el of document.getElementsByClassName('toggleable')) el.classList.add('d-none');
	const amountInput = document.getElementById('bux-transfer-amount');
	const reasonInput = document.getElementById('bux-transfer-reason');
	const amount = parseInt(amountInput?.value || 0);
	const username = document.getElementById('username').innerHTML;

	t.disabled = true;
	postToast(t, `/@${username}/transfer_bux`, {
		amount: amountInput.value,
		reason: reasonInput.value
	}, () => {
		const ownBalance = document.getElementById('user-bux-amount');
		const profileBalance = document.getElementById('profile-bux-amount');
		if (ownBalance) ownBalance.innerText = parseInt(ownBalance.innerText) - amount;
		if (profileBalance) profileBalance.innerText = parseInt(profileBalance.innerText) + amount;
	});
	setTimeout(() => t.disabled = false, 2000);
}

function sendMessage(form) {
	const message = document.getElementById('message');
	const preview = document.getElementById('message-preview');
	if (message) message.classList.add('d-none');
	if (preview) preview.classList.add('d-none');
	sendFormXHR(form, () => {
		const input = document.getElementById('input-message');
		if (input) input.value = '';
	});
}
