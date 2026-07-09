function makeBlackjackRequest(action) {
	const xhr = new XMLHttpRequest();
	xhr.open("post", `/casino/twentyone/${action}`);
	xhr.setRequestHeader('xhr', 'xhr');
	xhr.onload = handleBlackjackResponse.bind(null, xhr);
	xhr.blackjackAction = action;
	return xhr;
}

function handleBlackjackResponse(xhr) {
	let status;
	try {
		const response = JSON.parse(xhr.response);
		const succeeded = xhr.status >= 200 &&
			xhr.status < 300 &&
			response &&
			!response.error;

		clearResult();
		status = xhr.status;

		if (status == 429) {
			throw new Error(response["details"]);
		}

		if (succeeded) {
			updateBlackjackTable(response.state);
			updateFeed(response.feed);
			updatePlayerCurrencies(response.gambler);
		} else {
			console.error("Error: ", response.error);
			throw new Error("Error")
		}
	} catch (error) {
		const results = {
			deal: "Unable to deal a new hand. Is one in progress?",
			hit: "Unable to hit.",
			stay: "Unable to stay.",
			"double-down": "Unable to double down.",
			"buy-insurance": "Unable to buy insurance."
		};
		result = results[xhr.blackjackAction];

		if (status == 429) {
			result = error.message;
		}

		updateResult(result, "danger");
	}
}

function updateBlackjackActions(state) {
	const actions = Array.from(document.querySelectorAll('.twentyone-btn'));

	// Hide all actions.
	actions.forEach(action => action.style.display = 'none');

	if (state) {
		// Show the correct ones.
		state.actions.forEach(action => document.getElementById(`twentyone-${action}`).style.display = 'inline-block');
	} else {
		const dealButton = document.getElementById(`twentyone-DEAL`);

		setTimeout(() => {
			const dealButton = document.getElementById(`twentyone-DEAL`);
		})

		if (dealButton) {
			dealButton.style.display = 'inline-block'
		}
	}
}

function updateBlackjackTable(state) {
	const table = document.getElementById('blackjack-table');
	const charactersToRanks = {
		X: "10"
	};
	const charactersToSuits = {
		S: "♠️",
		H: "♥️",
		C: "♣️",
		D: "♦️",
	};
	const makeCardset = (from, who, value) => `
		<div class="blackjack-cardset">
			<div class="blackjack-cardset-value">
				${value === -1 ? `${who} went bust` : `${who} has ${value}`}
			</div>
			${from
			.filter(card => card !== "?")
			.map(([rankCharacter, suitCharacter]) => {
				const rank = charactersToRanks[rankCharacter] || rankCharacter;
				const suit = charactersToSuits[suitCharacter] || suitCharacter;
				return buildPlayingCard(rank, suit);
			})
			.join('')}
		</div>
	`;
	const dealerCards = makeCardset(state.dealer, 'Dealer', state.dealer_value);
	const playerCards = makeCardset(state.player, 'Player', state.player_value);

	updateBlackjackActions(state);

	table.innerHTML = `
		<div style="position: relative;">
			${dealerCards}
		</div>
		${playerCards}
	`;

	const currency = state.wager.currency === 'coins' ? 'coins' : 'marseybux';

	switch (state.status) {
		case 'BLACKJACK':
			updateResult(`Blackjack: Received ${state.payout} ${currency}`, "warning");
			break;
		case 'WON':
			updateResult(`Won: Received ${state.payout} ${currency}`, "success");
			break;
		case 'PUSHED':
			updateResult(`Pushed: Received ${state.wager.amount} ${currency}`, "success");
			break;
		case 'LOST':
			updateResult(`Lost ${state.wager.amount} ${currency}`, "danger");
			break;
		default:
			break;
	}

	updateCardsetBackgrounds(state);

	if (state.status === 'PLAYING') {
		updateResult(`${state.wager.amount} ${currency} are at stake`, "success");
	} else {
		enableWager();
	}
}

function updateCardsetBackgrounds(state) {
	const cardsets = Array.from(document.querySelectorAll('.blackjack-cardset'));

	for (const cardset of cardsets) {
		['PLAYING', 'LOST', 'PUSHED', 'WON', 'BLACKJACK'].forEach(status => cardset.classList.remove(`blackjack-cardset__${status}`));
		cardset.classList.add(`blackjack-cardset__${state.status}`)
	}
}

function deal() {
	const request = makeBlackjackRequest('deal');
	const { amount, currency } = getWager();
	const form = new FormData();

	form.append("formkey", formkey());
	form.append("wager", amount);
	form.append("currency", currency);

	request.send(form);

	clearResult();
	disableWager();
	drawFromDeck();
}

function hit() {
	const request = makeBlackjackRequest('hit');
	const form = new FormData();
	form.append("formkey", formkey());
	request.send(form);

	drawFromDeck();
}

function stay() {
	const request = makeBlackjackRequest('stay');
	const form = new FormData();
	form.append("formkey", formkey());
	request.send(form);
}

function doubleDown() {
	const request = makeBlackjackRequest('double-down');
	const form = new FormData();
	form.append("formkey", formkey());
	request.send(form);

	drawFromDeck();
}

function buyInsurance() {
	const request = makeBlackjackRequest('buy-insurance');
	const form = new FormData();
	form.append("formkey", formkey());
	request.send(form);
}

function buildBlackjackDeck() {
	document.getElementById('blackjack-table-deck').innerHTML = `
		<div style="position: absolute; top: 150px; left: -100px;">
			${buildPlayingCardDeck()}
		</div>
	`;
}

function initializeBlackjack() {
	buildBlackjackDeck();

	try {
		const passed = document.getElementById('blackjack-table').dataset.state;
		const state = JSON.parse(passed);
		updateBlackjackTable(state);
	} catch (error) {
		updateBlackjackActions();
	}
}

initializeBlackjack();
