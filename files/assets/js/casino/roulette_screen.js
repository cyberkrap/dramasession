const ROULETTE_REDS = new Set([1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]);
const CELL_TO_NUMBER_LOOKUP = {
	1: 3, 2: 6, 3: 9, 4: 12, 5: 15, 6: 18,
	7: 21, 8: 24, 9: 27, 10: 30, 11: 33, 12: 36,
	13: 2, 14: 5, 15: 8, 16: 11, 17: 14, 18: 17,
	19: 20, 20: 23, 21: 26, 22: 29, 23: 32, 24: 35,
	25: 1, 26: 4, 27: 7, 28: 10, 29: 13, 30: 16,
	31: 19, 32: 22, 33: 25, 34: 28, 35: 31, 36: 34,
};

function escapeRouletteHtml(value) {
	return String(value ?? "")
		.replaceAll("&", "&amp;")
		.replaceAll("<", "&lt;")
		.replaceAll(">", "&gt;")
		.replaceAll('"', "&quot;")
		.replaceAll("'", "&#039;");
}

function rouletteFormatNumber(value) {
	return typeof formatNumber === "function"
		? formatNumber(value)
		: Number(value || 0).toLocaleString();
}

function getWager() {
	const amount = Number.parseInt(document.getElementById("wagerAmount").value, 10);
	const selected = document.querySelector('input[name="wagerCurrency"]:checked');
	const currency = selected?.value === "marseybux" ? "marseybux" : "coins";
	return {
		amount: Number.isFinite(amount) ? amount : 0,
		currency,
		localCurrency: currency === "coins" ? "Wishcoins" : "Wishbux",
	};
}

function updatePlayerCurrencies(updated = {}) {
	if (updated.coins !== undefined) {
		const coins = document.getElementById("user-coins-amount");
		if (coins) coins.innerText = rouletteFormatNumber(updated.coins);
	}
	if (updated.marseybux !== undefined) {
		const bux = document.getElementById("user-bux-amount");
		if (bux) bux.innerText = rouletteFormatNumber(updated.marseybux);
	}
}

function clearResult() {
	const result = document.getElementById("casinoGameResult");
	if (!result) return;
	result.classList.remove("alert-success", "alert-danger", "alert-warning");
}

function updateResult(text, className = "success") {
	const result = document.getElementById("casinoGameResult");
	if (!result) return;
	clearResult();
	result.classList.add(`alert-${className}`);
	result.textContent = text;
}

function rouletteCell({ id, bet, which, className, label, style = "" }) {
	return `<div id="${id}" data-bet="${bet}" data-which="${which}" class="${className}"${style ? ` style="${style}"` : ""}>${label}</div>`;
}

function buildRouletteTable() {
	const table = document.getElementById("roulette-table");
	if (!table) return;

	let html = '<div class="roulette-table-row roulette-lines-row"><div class="roulette-table-spacer"></div>';
	for (let line = 1; line <= 6; line += 1) {
		html += rouletteCell({
			id: `LINE_BET#${line}`,
			bet: "LINE_BET",
			which: line,
			className: "roulette-table-1to1",
			label: `Line ${line}`,
		});
	}
	html += '<div class="roulette-table-spacer"></div></div>';

	const buildNumberRow = (start, end, zeroCell, column) => {
		let row = '<div class="roulette-table-row">';
		row += zeroCell;
		for (let index = start; index < end; index += 1) {
			const number = CELL_TO_NUMBER_LOOKUP[index];
			const color = ROULETTE_REDS.has(number) ? "red" : "black";
			row += rouletteCell({
				id: `STRAIGHT_UP_BET#${number}`,
				bet: "STRAIGHT_UP_BET",
				which: number,
				className: `roulette-table-number roulette-table-number__${color}`,
				label: number,
			});
		}
		row += rouletteCell({
			id: `COLUMN_BET#${column}`,
			bet: "COLUMN_BET",
			which: column,
			className: "roulette-table-column",
			label: `Col ${column}`,
		});
		return `${row}</div>`;
	};

	html += buildNumberRow(
		1,
		13,
		rouletteCell({ id: "STRAIGHT_UP_BET#37", bet: "STRAIGHT_UP_BET", which: 37, className: "roulette-table-number roulette-table-number__green", label: "00" }),
		3,
	);
	html += buildNumberRow(13, 25, '<div id="roulette-spacer-left-middle" class="roulette-table-number roulette-table-number__green roulette-table-zero-spacer"></div>', 2);
	html += buildNumberRow(
		25,
		37,
		rouletteCell({ id: "STRAIGHT_UP_BET#0", bet: "STRAIGHT_UP_BET", which: 0, className: "roulette-table-number roulette-table-number__green", label: "0" }),
		1,
	);

	html += '<div class="roulette-table-row roulette-dozens-row"><div class="roulette-table-spacer"></div>';
	for (let dozen = 1; dozen <= 3; dozen += 1) {
		html += rouletteCell({
			id: `DOZEN_BET#${dozen}`,
			bet: "DOZEN_BET",
			which: dozen,
			className: "roulette-table-line",
			label: `${dozen}${dozen === 1 ? "st" : dozen === 2 ? "nd" : "rd"}12`,
		});
	}
	html += '<div class="roulette-table-spacer"></div></div>';

	html += '<div class="roulette-table-row roulette-outside-row"><div class="roulette-table-spacer"></div>';
	[
		["HIGH_LOW_BET", "LOW", "1:18", ""],
		["EVEN_ODD_BET", "EVEN", "EVEN", ""],
		["RED_BLACK_BET", "RED", "RED", "background:#ed1717"],
		["RED_BLACK_BET", "BLACK", "BLACK", "background:#090909"],
		["EVEN_ODD_BET", "ODD", "ODD", ""],
		["HIGH_LOW_BET", "HIGH", "19:36", ""],
	].forEach(([bet, which, label, style]) => {
		html += rouletteCell({ id: `${bet}#${which}`, bet, which, className: "roulette-table-1to1", label, style });
	});
	html += '<div class="roulette-table-spacer"></div></div>';

	table.innerHTML = html;
	table.addEventListener("click", (event) => {
		const cell = event.target.closest("[data-bet][data-which]");
		if (!cell || !table.contains(cell)) return;
		placeChip(cell.dataset.bet, cell.dataset.which);
	});
}

function formatFlatBets(bets = {}) {
	return Object.values(bets).flatMap((collection) => Array.isArray(collection) ? collection : []);
}

function formatNormalizedBets(bets) {
	const normalized = { gamblers: [], gamblersByName: {} };
	for (const bet of formatFlatBets(bets)) {
		const username = bet.gambler_username;
		if (!normalized.gamblersByName[username]) {
			normalized.gamblers.push(username);
			normalized.gamblersByName[username] = {
				name: username,
				avatar: bet.gambler_profile_url,
				wagerTotal: { coins: 0, marseybux: 0 },
				wagers: [],
			};
		}

		const entry = normalized.gamblersByName[username];
		entry.wagerTotal[bet.wager.currency] += bet.wager.amount;
		let wager = entry.wagers.find((item) => item.bet === bet.bet && item.which === bet.which);
		if (!wager) {
			wager = { bet: bet.bet, which: bet.which, amounts: { coins: 0, marseybux: 0 } };
			entry.wagers.push(wager);
		}
		wager.amounts[bet.wager.currency] += bet.wager.amount;
	}
	return normalized;
}

function rouletteAsset(currency) {
	const id = currency === "coins" ? "rouletteWishcoinAsset" : "rouletteWishbuxAsset";
	return document.getElementById(id)?.src || (currency === "coins" ? "/i/coins.webp" : "/i/marseybux.webp?v=2000");
}

function rouletteCurrencyHtml(currency, amount) {
	if (!amount) return "";
	const label = currency === "coins" ? "Wishcoin" : "Wishbux";
	return `${rouletteFormatNumber(amount)} <img class="roulette-currency-icon" src="${escapeRouletteHtml(rouletteAsset(currency))}" alt="${label}" title="${label}" width="24" height="24">`;
}

function buildPokerChip(avatar, tableChip = false) {
	return `<span class="roulette-poker-chip${tableChip ? " roulette-poker-chip--table" : ""}">
		<img class="roulette-poker-chip__ring" loading="lazy" src="/i/pokerchip.webp" alt="" width="34" height="34">
		<img class="roulette-poker-chip__avatar" loading="lazy" src="${escapeRouletteHtml(avatar)}" alt="" width="34" height="34">
	</span>`;
}

function rouletteBetDescription(bet, which) {
	const straight = String(which) === "37" ? "00" : which;
	return {
		STRAIGHT_UP_BET: `that the number will be ${straight}`,
		LINE_BET: `that the number will be within line ${which}`,
		COLUMN_BET: `that the number will be within column ${which}`,
		DOZEN_BET: `that the number will be within dozen ${which}`,
		EVEN_ODD_BET: `that the number will be ${String(which).toLowerCase()}`,
		RED_BLACK_BET: `that the color of the number will be ${String(which).toLowerCase()}`,
		HIGH_LOW_BET: `that the number will be ${which === "HIGH" ? "higher than 18" : "lower than 19"}`,
	}[bet] || "";
}

function combinedCurrencyHtml(amounts) {
	const coin = rouletteCurrencyHtml("coins", amounts.coins);
	const bux = rouletteCurrencyHtml("marseybux", amounts.marseybux);
	return coin && bux ? `${coin} and ${bux}` : coin || bux;
}

function buildRouletteBets(bets) {
	const betArea = document.getElementById("roulette-bets");
	if (!betArea) return;

	const flat = formatFlatBets(bets);
	const normalized = formatNormalizedBets(bets);
	const participants = [...new Set(flat.map((bet) => bet.gambler_username))];
	const totals = flat.reduce((sum, bet) => {
		sum[bet.wager.currency] += bet.wager.amount;
		return sum;
	}, { coins: 0, marseybux: 0 });

	const totalText = participants.length === 0
		? "No one has placed a bet"
		: `${participants.length} player${participants.length === 1 ? " is" : "s are"} betting a total of ${combinedCurrencyHtml(totals)}`;

	let html = `<small class="roulette-total-bets">${totalText}</small>`;
	for (const username of normalized.gamblers) {
		const player = normalized.gamblersByName[username];
		html += `<article class="roulette-bet-summary">
			<div class="roulette-bet-summary--heading">
				${buildPokerChip(player.avatar)}
				<p><a href="/@${encodeURIComponent(player.name)}">${escapeRouletteHtml(player.name)}</a> is betting ${combinedCurrencyHtml(player.wagerTotal)}:</p>
			</div>
			<ul class="roulette-bet-summary--list">`;
		for (const wager of player.wagers) {
			html += `<li>${combinedCurrencyHtml(wager.amounts)} ${escapeRouletteHtml(rouletteBetDescription(wager.bet, wager.which))}</li>`;
		}
		html += "</ul></article>";
	}
	betArea.innerHTML = html;
}

function clearTableChips() {
	document.querySelectorAll("#roulette-table .roulette-cell-chip-stack").forEach((stack) => stack.remove());
}

function addChipsToTable(bets) {
	clearTableChips();
	const grouped = new Map();
	for (const bet of formatFlatBets(bets)) {
		const key = `${bet.bet}#${bet.which}`;
		if (!grouped.has(key)) grouped.set(key, []);
		grouped.get(key).push(bet.gambler_profile_url);
	}

	for (const [key, avatars] of grouped.entries()) {
		const cell = document.getElementById(key);
		if (!cell) continue;
		const stack = document.createElement("span");
		stack.className = "roulette-cell-chip-stack";
		avatars.slice(0, 3).forEach((avatar) => stack.insertAdjacentHTML("beforeend", buildPokerChip(avatar, true)));
		if (avatars.length > 3) {
			const more = document.createElement("span");
			more.className = "roulette-cell-chip-more";
			more.textContent = `+${avatars.length - 3}`;
			stack.appendChild(more);
		}
		cell.appendChild(stack);
	}
}

function placeChip(bet, which) {
	const { amount, currency, localCurrency } = getWager();
	if (amount < 5) {
		updateResult(`Minimum roulette wager is 5 ${localCurrency}.`, "danger");
		return;
	}

	const whichNice = String(which) === "37" ? "00" : which;
	const multiplier = {
		STRAIGHT_UP_BET: 35,
		LINE_BET: 5,
		COLUMN_BET: 2,
		DOZEN_BET: 2,
		EVEN_ODD_BET: 1,
		RED_BLACK_BET: 1,
		HIGH_LOW_BET: 1,
	}[bet] || 0;
	const description = rouletteBetDescription(bet, which).replace(/^that /, "");
	if (!window.confirm(`Bet ${amount} ${localCurrency} ${description || `on ${whichNice}`}?\nYou could win ${amount * multiplier} ${localCurrency}.`)) return;

	const xhr = new XMLHttpRequest();
	xhr.open("POST", "/casino/roulette/place-bet");
	xhr.setRequestHeader("xhr", "xhr");
	xhr.onload = () => handleRouletteResponse(xhr);

	const form = new FormData();
	form.append("formkey", formkey());
	form.append("bet", bet);
	form.append("which", which);
	form.append("wager", amount);
	form.append("currency", currency);
	xhr.send(form);
}

function requestRouletteBets() {
	const xhr = new XMLHttpRequest();
	xhr.open("GET", "/casino/roulette/bets");
	xhr.setRequestHeader("xhr", "xhr");
	xhr.onload = () => handleRouletteResponse(xhr);
	xhr.send();
}

function handleRouletteResponse(xhr) {
	let response = null;
	try {
		response = JSON.parse(xhr.response);
	} catch (error) {
		console.error("Roulette returned invalid JSON", error);
	}

	const succeeded = xhr.status >= 200 && xhr.status < 300 && response && !response.error;
	if (!succeeded) {
		updateResult(response?.description || response?.error || "Unable to place that bet.", "danger");
		return;
	}

	buildRouletteBets(response.bets || {});
	addChipsToTable(response.bets || {});
	updatePlayerCurrencies(response.gambler || {});
}

function initializeRoulette() {
	buildRouletteTable();
	requestRouletteBets();
}

initializeRoulette();
