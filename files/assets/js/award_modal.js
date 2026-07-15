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

let selectedAwardCurrency = "coins";

function pick(kind, price, coins, marseybux, unlimitedSpending = false, currency = "coins") {
	price = parseInt(price);
	coins = parseInt(coins);
	marseybux = parseInt(marseybux);
	selectedAwardCurrency = currency;
	document.getElementById('kind').value = kind;
	for (const choice of document.querySelectorAll('.award-choice.picked')) choice.classList.remove('picked');
	document.getElementById(kind).classList.add('picked');
	const balance = currency === 'marseybux' ? marseybux : coins;
	const canGive = unlimitedSpending || balance >= price;
	const button = document.getElementById('giveaward');
	button.disabled = !canGive;
	button.textContent = `Give Award - ${price.toLocaleString()} ${currency === 'marseybux' ? 'Wishbux' : 'Wishcoins'}`;
	document.getElementById('award-price-summary').textContent = canGive ? 'Ready to apply' : `Needs ${price.toLocaleString()} ${currency === 'marseybux' ? 'Wishbux' : 'Wishcoins'}`;
	if (kind === "flairlock") {
		document.getElementById('notelabel').textContent = "New flair:";
		document.getElementById('note').placeholder = "Insert new flair here, or leave empty to extend the current flair.";
		document.getElementById('note').maxLength = 100;
	} else {
		document.getElementById('notelabel').textContent = "Note (optional):";
		document.getElementById('note').placeholder = "Note to include in award notification...";
		document.getElementById('note').maxLength = 200;
	}
}

function giveaward(t) {
	const kind = document.getElementById('kind').value;
	postToast(t, t.dataset.action, {
		kind: kind,
		note: document.getElementById('note').value
	}, () => {
		document.getElementById('award-price-summary').textContent = 'Award applied';
	});
}
const data_url = document.querySelectorAll('[data-url]');
for (const element of data_url) {
	if (element.dataset.nonce != nonce) {
		console.log("Nonce check failed!")
		continue
	}
	element.addEventListener('click', () => {
		document.getElementById('giveaward').dataset.action = element.dataset.url
	});
}

document.querySelectorAll('[data-award-tab]').forEach(tab => {
	tab.addEventListener('click', () => {
		document.querySelectorAll('[data-award-tab]').forEach(item => item.classList.toggle('active', item === tab));
		document.querySelectorAll('[data-award-panel]').forEach(panel => panel.classList.toggle('d-none', panel.dataset.awardPanel !== tab.dataset.awardTab));
	});
});