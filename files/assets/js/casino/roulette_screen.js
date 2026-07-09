// Kiss my ass if you're judgin'
const CELL_TO_NUMBER_LOOKUP = {
	1: 3,
	2: 6,
	3: 9,
	4: 12,
	5: 15,
	6: 18,
	7: 21,
	8: 24,
	9: 27,
	10: 30,
	11: 33,
	12: 36,
	13: 2,
	14: 5,
	15: 8,
	16: 11,
	17: 14,
	18: 17,
	19: 20,
	20: 23,
	21: 26,
	22: 29,
	23: 32,
	24: 35,
	25: 1,
	26: 4,
	27: 7,
	28: 10,
	29: 13,
	30: 16,
	31: 19,
	32: 22,
	33: 25,
	34: 28,
	35: 31,
	36: 34
};

function initializeGame() {
	buildRouletteTable();
	updateResult("Rolls occur every five minutes", "success");
	requestRouletteBets();
}

function buildRouletteTable() {
	const table = document.getElementById('roulette-table');
	const reds = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36];

	let html = "";

	// Lines
	html += `
		<div class="roulette-table-row">
			<div style="flex: 1"></div>
			<div id="LINE_BET#1" data-nonce="${nonce}" data-onclick="placeChip('LINE_BET', '1')" class="roulette-table-1to1">Line 1</div>
			<div id="LINE_BET#2" data-nonce="${nonce}" data-onclick="placeChip('LINE_BET', '2')" class="roulette-table-1to1">Line 2</div>
			<div id="LINE_BET#3" data-nonce="${nonce}" data-onclick="placeChip('LINE_BET', '3')" class="roulette-table-1to1">Line 3</div>
			<div id="LINE_BET#4" data-nonce="${nonce}" data-onclick="placeChip('LINE_BET', '4')" class="roulette-table-1to1">Line 4</div>
			<div id="LINE_BET#5" data-nonce="${nonce}" data-onclick="placeChip('LINE_BET', '5')" class="roulette-table-1to1">Line 5</div>
			<div id="LINE_BET#6" data-nonce="${nonce}" data-onclick="placeChip('LINE_BET', '6')" class="roulette-table-1to1">Line 6</div>
			<div style="flex: 1"></div>
		</div>
	`;

	// First Column
	html += "<div class=\"roulette-table-row\">";
	html += `<div id="STRAIGHT_UP_BET#37" data-nonce="${nonce}" data-onclick="placeChip('STRAIGHT_UP_BET', '37')" class="roulette-table-number roulette-table-number__green">00</div>`
	for (let i = 1; i < 13; i++) {
		const correctNumber = CELL_TO_NUMBER_LOOKUP[i];
		const isRed = reds.includes(correctNumber);

		html += `<div
			id="STRAIGHT_UP_BET#${correctNumber}"
			data-nonce="${nonce}"
			data-onclick="placeChip('STRAIGHT_UP_BET', '${correctNumber}')"
			class="roulette-table-number roulette-table-number__${isRed ? 'red' : 'black'}">
			${correctNumber}
		</div>
		`;
	}
	html += `<div id="COLUMN_BET#3" class="roulette-table-column" data-nonce="${nonce}" data-onclick="placeChip('COLUMN_BET', '3')">Col 3</div>`;
	html += "</div>";

	// Second Column
	html += "<div class=\"roulette-table-row\">";
	html += `<div id="roulette-spacer-left-middle" class="roulette-table-number roulette-table-number__green"></div>`
	for (let i = 13; i < 25; i++) {
		const correctNumber = CELL_TO_NUMBER_LOOKUP[i];
		const isRed = reds.includes(correctNumber);

		html += `<div
			id="STRAIGHT_UP_BET#${correctNumber}"
			data-nonce="${nonce}"
			data-onclick="placeChip('STRAIGHT_UP_BET', '${correctNumber}')"
			class="roulette-table-number roulette-table-number__${isRed ? 'red' : 'black'}">
			${correctNumber}
		</div>
		`;
	}
	html += `<div id="COLUMN_BET#2" class="roulette-table-column" data-nonce="${nonce}" data-onclick="placeChip('COLUMN_BET', '2')">Col 2</div>`;
	html += "</div>";

	// Third Column
	html += "<div class=\"roulette-table-row\">";
	html += `<div id="STRAIGHT_UP_BET#0" data-nonce="${nonce}" data-onclick="placeChip('STRAIGHT_UP_BET', '0')" class="roulette-table-number roulette-table-number__green">0</div>`
	for (let i = 25; i < 37; i++) {
		const correctNumber = CELL_TO_NUMBER_LOOKUP[i];
		const isRed = reds.includes(correctNumber);

		html += `<div
			id="STRAIGHT_UP_BET#${correctNumber}"
			data-nonce="${nonce}"
			data-onclick="placeChip('STRAIGHT_UP_BET', '${correctNumber}')"
			class="roulette-table-number roulette-table-number__${isRed ? 'red' : 'black'}">
			${correctNumber}
		</div>
		`;
	}
	html += `<div id="COLUMN_BET#1" class="roulette-table-column" data-nonce="${nonce}" data-onclick="placeChip('COLUMN_BET', '1')">Col 1</div>`;
	html += "</div>";

	// Line Bets and 1:1 Bets
	html += `
		<div class="roulette-table-row">
			<div style="flex: 1"></div>
			<div id="DOZEN_BET#1" class="roulette-table-line" data-nonce="${nonce}" data-onclick="placeChip('DOZEN_BET', '1')">1st12</div>
			<div id="DOZEN_BET#2" class="roulette-table-line" data-nonce="${nonce}" data-onclick="placeChip('DOZEN_BET', '2')">2nd12</div>
			<div id="DOZEN_BET#3" class="roulette-table-line" data-nonce="${nonce}" data-onclick="placeChip('DOZEN_BET', '3')">3rd12</div>
			<div style="flex: 1"></div>
			</div>
			<div class="roulette-table-row">
				<div style="flex: 1"></div>
				<div id="HIGH_LOW_BET#LOW" class="roulette-table-1to1" data-nonce="${nonce}" data-onclick="placeChip('HIGH_LOW_BET', 'LOW')">1:18</div>
				<div id="EVEN_ODD_BET#EVEN" class="roulette-table-1to1" data-nonce="${nonce}" data-onclick="placeChip('EVEN_ODD_BET', 'EVEN')">EVEN</div>
				<div id="RED_BLACK_BET#RED" class="roulette-table-1to1" data-nonce="${nonce}" data-onclick="placeChip('RED_BLACK_BET', 'RED')" style="background-color: red">RED</div>
				<div id="RED_BLACK_BET#BLACK" class="roulette-table-1to1" data-nonce="${nonce}" data-onclick="placeChip('RED_BLACK_BET', 'BLACK')" style="background-color: black">BLACK</div>
				<div id="EVEN_ODD_BET#ODD" class="roulette-table-1to1" data-nonce="${nonce}" data-onclick="placeChip('EVEN_ODD_BET', 'ODD')">ODD</div>
				<div id="HIGH_LOW_BET#HIGH" class="roulette-table-1to1" data-nonce="${nonce}" data-onclick="placeChip('HIGH_LOW_BET', 'HIGH')">19:36</div>
				<div style="flex: 1"></div>
		</div>
	`;

	table.innerHTML = html;
}

function formatFlatBets(bets) {
	let flatBets = [];

	for (const betCollection of Object.values(bets)) {
		flatBets = flatBets.concat(betCollection)
	}

	return flatBets;
}

function formatNormalizedBets(bets) {
	const normalizedBets = {
		gamblers: [],
		gamblersByName: {}
	};
	const flatBets = formatFlatBets(bets);

	for (const bet of flatBets) {
		if (!normalizedBets.gamblers.includes(bet.gambler_username)) {
			normalizedBets.gamblers.push(bet.gambler_username);
		}

		if (!normalizedBets.gamblersByName[bet.gambler_username]) {
			normalizedBets.gamblersByName[bet.gambler_username] = {
				name: bet.gambler_username,
				avatar: bet.gambler_profile_url,
				profile: `/@${bet.gambler_username}`,
				wagerTotal: {
					coins: 0,
					marseybux: 0
				},
				wagers: []
			}
		}

		const entry = normalizedBets.gamblersByName[bet.gambler_username];

		entry.wagerTotal[bet.wager.currency] += bet.wager.amount;

		const existingWager = entry.wagers.find(wager => wager.bet === bet.bet && wager.which === bet.which);

		if (existingWager) {
			existingWager.amounts[bet.wager.currency] += bet.wager.amount;
		} else {
			const newEntry = {
				bet: bet.bet,
				which: bet.which,
				amounts: {
					coins: 0,
					marseybux: 0
				},
			};
			newEntry.amounts[bet.wager.currency] += bet.wager.amount;

			entry.wagers.push(newEntry);
		}
	}

	return normalizedBets;
}

function buildPokerChip(avatar) {
	return `
		<div class="roulette-poker-chip">
			<img loading="lazy" src="/i/pokerchip.webp" width="40" height="40">
			<img loading="lazy" src="${avatar}" width="40" height="40">
		</div>
	`;
}

function buildRouletteBets(bets) {
	const betArea = document.getElementById("roulette-bets");
	const flatBets = formatFlatBets(bets);
	const normalizedBets = formatNormalizedBets(bets);
	const coinImgHtml = `
		<img
			src="/i/rDrama/coins.webp?v=3009"
			alt="coin"
			width="32"
			data-bs-toggle="tooltip"
			data-bs-placement="bottom"
			data-bs-original-title="Coin">
	`;
	const marseybuxImgHtml = `
		<img
			src="/i/marseybux.webp?v=2000"
			alt="marseybux"
			data-bs-toggle="tooltip"
			data-bs-placement="bottom"
			width="32" class="mr-1 ml-1"
			data-bs-original-title="Marseybux">
	`;
	const { participants, coin, marseybux } = flatBets.reduce((prev, next) => {
		if (!prev.participants.includes(next.gambler_username)) {
			prev.participants.push(next.gambler_username);
		}

		if (next.wager.currency == 'coins') {
			prev.coin += next.wager.amount;
		} else {
			prev.marseybux += next.wager.amount;
		}

		return prev;
	}, { participants: [], coin: 0, marseybux: 0 });
	const coinText = `${coin} ${coinImgHtml}`;
	const marseybuxText = `${marseybux} ${marseybuxImgHtml}`;
	const playerText = participants.length > 1 ? `${participants.length} players are` : `1 player is`;
	const totalText = coin && marseybux ? `${coinText} and ${marseybuxText}` : coin ? coinText : marseybuxText;
	const fullTotalText = participants.length === 0 ? "No one has placed a bet" : `${playerText} betting a total of ${totalText}`;

	let betHtml = `
		<small class="roulette-total-bets">${fullTotalText}</small>
		<hr>
	`;

	for (player of normalizedBets.gamblers) {
		const { name, avatar, wagerTotal, wagers } = normalizedBets.gamblersByName[player];

		betHtml += `<div class="roulette-bet-summary">`;
		// Heading
		betHtml += `  <div class="roulette-bet-summary--heading">`;
		betHtml += buildPokerChip(avatar);
		const coinText = wagerTotal.coins > 0 ? `${wagerTotal.coins} ${coinImgHtml}` : "";
		const procoinText = wagerTotal.marseybux > 0 ? `${wagerTotal.marseybux} ${marseybuxImgHtml}` : "";
		const bettingText = coinText && procoinText ? `${coinText} and ${procoinText}` : coinText || procoinText;
		betHtml += `<p>${name} is betting ${bettingText}:</p>`;
		betHtml += ` </div>`;

		// Individual bets
		betHtml += `<ul class="roulette-bet-summary--list">`;
		for (const individualBet of wagers) {
			const coinText = individualBet.amounts.coins > 0 ? `${individualBet.amounts.coins} ${coinImgHtml}` : "";
			const procoinText = individualBet.amounts.marseybux > 0 ? `${individualBet.amounts.marseybux} ${marseybuxImgHtml}` : "";
			const straightUpWhich = (individualBet.which == 37) ? "00" : individualBet.which;
			const details = {
				STRAIGHT_UP_BET: `that the number will be ${straightUpWhich}`,
				LINE_BET: `that the number will be within line ${individualBet.which}`,
				COLUMN_BET: `that the number will be within column ${individualBet.which}`,
				DOZEN_BET: `that the number will be within dozen ${individualBet.which}`,
				EVEN_ODD_BET: `that the number will be ${individualBet.which.toLowerCase()}`,
				RED_BLACK_BET: `that the color of the number will be ${individualBet.which.toLowerCase()}`,
				HIGH_LOW_BET: `that the number will be ${individualBet.which === "HIGH" ? "higher than 18" : "lower than 19"}`
			}
			const betText = coinText && procoinText ? `${coinText} and ${procoinText}` : coinText || procoinText;

			betHtml += `<li>${betText} ${details[individualBet.bet]}</li>`;
		}
		betHtml += `</ul>`;
		betHtml += `</div>`;
	}

	betArea.innerHTML = betHtml;
}

function placeChip(bet, which) {
	const { amount, currency: safeCurrency, localCurrency: currency } = getWager();
	const whichNice = which == 37 ? "00" : which;
	const texts = {
		STRAIGHT_UP_BET: `Bet ${amount} ${currency} on ${whichNice}?\nYou could win ${amount * 35} ${currency}.`,
		LINE_BET: `Bet ${amount} ${currency} on line ${which}?\nYou could win ${amount * 5} ${currency}.`,
		COLUMN_BET: `Bet ${amount} ${currency} column ${which}?\nYou could win ${amount * 2} ${currency}.`,
		DOZEN_BET: `Bet ${amount} ${currency} dozen ${which}?\nYou could win ${amount * 2} ${currency}.`,
		EVEN_ODD_BET: `Bet ${amount} ${currency} that the number will be ${which.toLowerCase()}?\nYou could win ${amount} ${currency}.`,
		RED_BLACK_BET: `Bet ${amount} ${currency} that the number will be ${which.toLowerCase()}?\nYou could win ${amount} ${currency}.`,
		HIGH_LOW_BET: `Bet ${amount} ${currency} that the number will be ${which === "HIGH" ? "higher than 18" : "lower than 19"}?\nYou could win ${amount} ${currency}.`,
	}
	const text = texts[bet] || "";
	const confirmed = window.confirm(text);

	if (confirmed) {
		const xhr = new XMLHttpRequest();
		xhr.open("post", "/casino/roulette/place-bet");
		xhr.setRequestHeader('xhr', 'xhr');
		xhr.onload = handleRouletteResponse.bind(null, xhr);

		const form = new FormData();
		form.append("formkey", formkey());
		form.append("bet", bet);
		form.append("which", which);
		form.append("wager", amount);
		form.append("currency", safeCurrency);

		xhr.send(form);
	}
}

function addChipsToTable(bets) {
	const flatBets = formatFlatBets(bets);

	for (const bet of flatBets) {
		const tableElement = document.getElementById(`${bet.bet}#${bet.which}`);
		tableElement.style.position = 'relative';
		const count = tableElement.dataset.count ? parseInt(tableElement.dataset.count) + 1 : 1;
		tableElement.dataset.count = count;

		const chip = buildPokerChip(bet.gambler_profile_url)
		tableElement.innerHTML = `${tableElement.innerHTML}<div style="position: absolute; bottom: ${count + 2}px; left: -${count + 2}px; transform: scale(0.5);">${chip}</div>`;
	}
}

function requestRouletteBets() {
	const xhr = new XMLHttpRequest();
	xhr.open("get", "/casino/roulette/bets");
	xhr.setRequestHeader('xhr', 'xhr');
	xhr.onload = handleRouletteResponse.bind(null, xhr);
	xhr.send();
}

function handleRouletteResponse(xhr) {
	let response;

	try {
		response = JSON.parse(xhr.response);
	} catch (error) {
		console.error(error);
	}

	const succeeded =
		xhr.status >= 200 && xhr.status < 300 && response && !response.error;

	if (succeeded) {
		buildRouletteBets(response.bets);
		addChipsToTable(response.bets);
		updatePlayerCurrencies(response.gambler);
		updateResult("Rolls occur every five minutes", "success");
	} else {
		updateResult("Unable to place that bet.", "danger");
	}
}

initializeGame();
