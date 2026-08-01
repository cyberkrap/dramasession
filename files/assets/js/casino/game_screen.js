/**
 * This script block contains generic helper function usable across casino games:
 * - Wagers
 * - Feed
 * - Leaderboard
 */

function initializeGame() {
	updateFeed();
	updateLeaderboard();
}

function updatePlayerCurrencies(updated) {
	if (updated.coins) {
		document.getElementById("user-coins-amount").innerText = formatNumber(updated.coins);
	}

	if (updated.marseybux) {
		document.getElementById("user-bux-amount").innerText = formatNumber(updated.marseybux);
	}
}

function getWager() {
	const amount = document.getElementById("wagerAmount").value;
	const currency = document.querySelector(
		'input[name="wagerCurrency"]:checked'
	).value;
	const genericCurrency = currency == 'marseybux' ? 'marseybux' : 'coins';

	return { amount, currency: genericCurrency, localCurrency: currency };
}

function disableWager() {
	document.getElementById("wagerAmount").disabled = true;
	document.getElementById("wagerCoins").disabled = true;
	document.getElementById("wagerMarseybux").disabled = true;
}

function enableWager() {
	document.getElementById("wagerAmount").disabled = false;
	document.getElementById("wagerCoins").disabled = false;
	document.getElementById("wagerMarseybux").disabled = false;
}

function updateResult(text, className) {
	clearResult();
	const result = document.getElementById("casinoGameResult");
	result.style.visibility = "visible";
	result.innerText = text;
	result.classList.add(`alert-${className}`);
}

function clearResult() {
	const result = document.getElementById("casinoGameResult");
	result.style.visibility = "hidden";
	result.innerText = "N/A";
	result.classList.remove("alert-success", "alert-danger", "alert-warning");
}

function updateFeed(newFeed) {
	let feed;

	if (newFeed) {
		feed = newFeed;
	} else {
		const gameFeed = document.getElementById("casinoGameFeed");
		feed = gameFeed.dataset.feed;
		feed = JSON.parse(feed);
		gameFeed.dataset.feed = "";
	}

	const feedHtml = feed
		.map(
			(entry) =>
				`
		<li
			style="display: flex; align-items: center; justify-content: space-between;"
			class="${entry.won_or_lost === "won" ? "text-success" : "text-danger"}">
			<div>
				<a href="/@${entry.user}">@${entry.user}</a> ${entry.won_or_lost} ${formatNumber(entry.amount)} ${entry.currency}
			</div>
		</li>
	`
		)
		.join("");

	document.getElementById("casinoGameFeedList").innerHTML = feedHtml;
}

function reloadFeed() {
	const game = document.getElementById('casino-game-wrapper').dataset.game;
	const xhr = new XMLHttpRequest();
	xhr.open("get", `/casino/${game}/feed`);
	xhr.setRequestHeader('xhr', 'xhr');
	xhr.onload = handleFeedResponse.bind(null, xhr);
	xhr.send();
}

function handleFeedResponse(xhr) {
	let response;

	try {
		response = JSON.parse(xhr.response);
	} catch (error) {
		console.error(error);
	}

	const succeeded =
		xhr.status >= 200 && xhr.status < 300 && response && !response.error;

	if (succeeded) {
		document.getElementById("casinoGameFeed").dataset.feed = JSON.stringify(response.feed);
		updateFeed();
	} else {
		console.error("error");
	}
}

function updateLeaderboard() {
	const leaderboardContainer = document.getElementById("gameLeaderboard");
	if (!leaderboardContainer) return;

	if (typeof window.renderCasinoLeaderboard === "function") {
		window.renderCasinoLeaderboard(leaderboardContainer);
		return;
	}

	const list = leaderboardContainer.querySelector(".roulette-leader-list");
	if (list) list.textContent = "Casino records are temporarily unavailable.";
}

function getRandomInt(min, max) {
	min = Math.ceil(min);
	max = Math.floor(max);
	return Math.floor(Math.random() * (max - min + 1)) + min;
}

function getRandomCardAngle() {
	const skew = 10
	return getRandomInt(-skew, skew);
}

function buildPlayingCard(rank, suit) {
	return `
		<div
			style="--card-angle: ${getRandomCardAngle()}deg"
			class="playing-card playing-card_${["♥️", "♦️"].includes(suit) ? 'red' : 'black'}">
			<div class="playing-card_small playing-card_topright">${rank}${suit}</div>
			<div class="playing-card_large">${rank}${suit}</div>
			<div class="playing-card_small playing-card_bottomleft">${rank}${suit}</div>
		</div>
	`;
}

function buildPlayingCardDeck(size = 14) {
	const cards = Array.from({ length: size }, (_, index) => `
		<div
			style="bottom: ${index}px; left: ${-index}px"
			class="flipped-playing-card"></div>
	`).join('\n');

	return `
		<div id="playingCardDeck" class="playing-card-deck">
			${cards}
		</div>
	`;
}

function drawFromDeck() {
	try {
		const [topCard] = Array.from(document.querySelectorAll("#playingCardDeck > *")).reverse();

		topCard.classList.add('drawing-a-card');

		setTimeout(() => {
			topCard.classList.remove('drawing-a-card');
		}, 600);
	} catch { }
}

initializeGame();
