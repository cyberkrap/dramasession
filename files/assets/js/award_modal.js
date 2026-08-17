// TODO: Refactor this ugly shit who wrote this lmao
function vote(type, id, dir) {
	const upvotes = document.getElementsByClassName(type + '-' + id + '-up');
	const downvotes = document.getElementsByClassName(type + '-' + id + '-down');
	const scoretexts = document.getElementsByClassName(type + '-score-' + id);

	for (let i=0; i<upvotes.length; i++) {

		const upvote = upvotes[i]
		const downvote = downvotes[i]
		const scoretext = scoretexts[i]
		const score = Number(scoretext.textContent);

		if (dir == "1") {
			if (upvote.classList.contains('active')) {
				upvote.classList.remove('active')
				upvote.classList.remove('active-anim')
				scoretext.textContent = score - 1
				votedirection = "0"
			} else if (downvote.classList.contains('active')) {
				upvote.classList.add('active')
				upvote.classList.add('active-anim')
				downvote.classList.remove('active')
				downvote.classList.remove('active-anim')
				scoretext.textContent = score + 2
				votedirection = "1"
			} else {
				upvote.classList.add('active')
				upvote.classList.add('active-anim')
				scoretext.textContent = score + 1
				votedirection = "1"
			}

			if (upvote.classList.contains('active')) {
				scoretext.classList.add('score-up')
				scoretext.classList.add('score-up-anim')
				scoretext.classList.remove('score-down')
				scoretext.classList.remove('score')
			} else if (downvote.classList.contains('active')) {
				scoretext.classList.add('score-down')
				scoretext.classList.remove('score-up')
				scoretext.classList.remove('score-up-anim');
				scoretext.classList.remove('score')
			} else {
				scoretext.classList.add('score')
				scoretext.classList.remove('score-up')
				scoretext.classList.remove('score-up-anim');
				scoretext.classList.remove('score-down')
			}
		}
		else {
			if (downvote.classList.contains('active')) {
				downvote.classList.remove('active')
				downvote.classList.remove('active-anim')
				scoretext.textContent = score + 1
				votedirection = "0"
			} else if (upvote.classList.contains('active')) {
				downvote.classList.add('active')
				downvote.classList.add('active-anim')
				upvote.classList.remove('active')
				upvote.classList.remove('active-anim')
				scoretext.textContent = score - 2
				votedirection = "-1"
			} else {
				downvote.classList.add('active')
				downvote.classList.add('active-anim')
				scoretext.textContent = score - 1
				votedirection = "-1"
			}

			if (upvote.classList.contains('active')) {
				scoretext.classList.add('score-up')
				scoretext.classList.add('score-up-anim')
				scoretext.classList.remove('score-down')
				scoretext.classList.remove('score')
			} else if (downvote.classList.contains('active')) {
				scoretext.classList.add('score-down')
				scoretext.classList.remove('score-up-anim')
				scoretext.classList.remove('score-up')
				scoretext.classList.remove('score')
			} else {
				scoretext.classList.add('score')
				scoretext.classList.remove('score-up')
				scoretext.classList.remove('score-down')
				scoretext.classList.remove('score-up-anim')
			}
		}
	}

	const xhr = createXhrWithFormKey("/vote/" + type.replace('-mobile','') + "/" + id + "/" + votedirection);
	xhr[0].onload = function() {
		if (xhr[0].status < 200 || xhr[0].status >= 300) return;
		let result = {};
		try { result = JSON.parse(xhr[0].responseText || "{}"); } catch (e) {}
		const delta = Number(result.xp_delta || 0);
		if (!delta) return;
		showVoteXp(delta);

	};
	xhr[0].send(xhr[1]);
}

let selectedAwardCurrency = "marseybux";
let selectedAwardOwned = 0;
let selectedAwardPrice = 0;

function validAwardAction(action) {
	return /^\/award\/(?:post|comment)\/\d+$/.test(String(action || ''));
}

function pick(kind, price, coins, marseybux, unlimitedSpending = false, currency = "marseybux", owned = 0) {
	price = parseInt(price, 10) || 0;
	coins = parseInt(coins, 10) || 0;
	marseybux = parseInt(marseybux, 10) || 0;
	owned = parseInt(owned, 10) || 0;
	unlimitedSpending = unlimitedSpending === true || unlimitedSpending === 'true';
	selectedAwardCurrency = currency;
	selectedAwardOwned = owned;
	selectedAwardPrice = price;
	document.getElementById('kind').value = kind;
	for (const choice of document.querySelectorAll('.award-choice.picked')) choice.classList.remove('picked');
	const choice = document.getElementById(kind);
	choice.classList.add('picked');
	const balance = currency === 'marseybux' ? marseybux : coins;
	const usesInventory = owned > 0;
	const canGive = usesInventory || unlimitedSpending || balance >= price;
	const button = document.getElementById('giveaward');
	button.disabled = !canGive;
	button.textContent = usesInventory
		? 'Give Award'
		: `Give Award - ${price.toLocaleString('en-GB')} ${currency === 'marseybux' ? 'Wishbux' : 'Wishcoins'}`;
	document.getElementById('award-price-summary').textContent = usesInventory
		? `Uses 1 owned award · x${owned} available`
		: (canGive ? 'Ready to purchase and apply' : `Needs ${price.toLocaleString('en-GB')} ${currency === 'marseybux' ? 'Wishbux' : 'Wishcoins'}`);
	if (kind === "flairlock") {
		document.getElementById('notelabel').textContent = "New flair:";
		document.getElementById('note').placeholder = "Insert new flair here, or leave empty to extend the current flair.";
		document.getElementById('note').maxLength = 100;
	} else {
		document.getElementById('notelabel').textContent = "Gift message (optional):";
		document.getElementById('note').placeholder = "Add a message explaining why you're giving this award...";
		document.getElementById('note').maxLength = 200;
	}
}

function updateOwnedAwardDisplay(kind) {
	if (selectedAwardOwned <= 0) return;
	const choice = document.getElementById(kind);
	if (!choice) return;
	selectedAwardOwned = Math.max(0, selectedAwardOwned - 1);
	choice.dataset.owned = String(selectedAwardOwned);
	const label = choice.querySelector('.award-price');
	if (label) {
		label.textContent = selectedAwardOwned > 0
			? `x${selectedAwardOwned} owned`
			: `Price: ${selectedAwardPrice.toLocaleString('en-GB')}`;
	}
}

function giveaward(t) {
	const action = String(t.dataset.action || '');
	if (!validAwardAction(action)) {
		showToast(false, 'Could not determine which post/comment to award. Close the award picker and try again.');
		return;
	}
	const kind = document.getElementById('kind').value;
	const usedOwnedAward = selectedAwardOwned > 0;
	postToast(t, action, {
		kind: kind,
		note: document.getElementById('note').value,
		currency: selectedAwardCurrency
	}, () => {
		if (usedOwnedAward) updateOwnedAwardDisplay(kind);
		document.getElementById('award-price-summary').textContent = usedOwnedAward ? 'Owned award used' : 'Award purchased and applied';
	});
}

function setAwardActionFromTrigger(trigger) {
	if (!(trigger instanceof HTMLElement)) return false;
	if (!trigger.matches('[data-bs-target="#awardModal"][data-url]')) return false;
	if (trigger.dataset.nonce != nonce) {
		console.log("Nonce check failed!");
		return false;
	}
	const button = document.getElementById('giveaward');
	if (!button) return false;
	const action = String(trigger.dataset.url || '');
	if (!validAwardAction(action)) {
		button.dataset.action = '';
		return false;
	}
	button.dataset.action = action;
	return true;
}

// Comment replies are inserted over XHR, so a one-time querySelectorAll binding
// misses their Give Award buttons. Delegate the click and also use Bootstrap's
// relatedTarget on modal open; both work for comments added without a refresh.
document.addEventListener('click', (event) => {
	const trigger = event.target.closest?.('[data-bs-target="#awardModal"][data-url]');
	if (trigger) {
		setAwardActionFromTrigger(trigger);
		return;
	}

	// Never let either the legacy or enhanced award submitter POST to a relative
	// "undefined" URL if a dynamically inserted trigger somehow failed to bind.
	const submit = event.target.closest?.('#giveaward');
	if (!submit || validAwardAction(submit.dataset.action)) return;
	event.preventDefault();
	event.stopImmediatePropagation();
	submit.dataset.confirmed = '0';
	showToast(false, 'Could not determine which post/comment to award. Close the award picker and try again.');
}, true);

const awardModalElement = document.getElementById('awardModal');
if (awardModalElement) {
	awardModalElement.addEventListener('show.bs.modal', (event) => {
		setAwardActionFromTrigger(event.relatedTarget);
	});
}

document.querySelectorAll('[data-award-tab]').forEach(tab => {
	tab.addEventListener('click', () => {
		document.querySelectorAll('[data-award-tab]').forEach(item => item.classList.toggle('active', item === tab));
		document.querySelectorAll('[data-award-panel]').forEach(panel => panel.classList.toggle('d-none', panel.dataset.awardPanel !== tab.dataset.awardTab));
	});
});

for (const element of document.querySelectorAll('.award-choice[data-bs-toggle="tooltip"]')) {
	if (!bootstrap.Tooltip.getInstance(element)) {
		new bootstrap.Tooltip(element, {container: 'body', trigger: 'hover focus'});
	}
}
