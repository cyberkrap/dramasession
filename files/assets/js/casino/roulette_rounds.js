(() => {
	const legacyHandleResponse = window.handleRouletteResponse;
	if (typeof legacyHandleResponse !== "function") return;

	let roundStateKnown = false;
	let roundActive = false;
	let nextSpinUtc = null;
	let recentlySettledUntil = 0;
	let pollInFlight = false;

	function formatCountdown(seconds) {
		const minutes = String(Math.floor(seconds / 60)).padStart(2, "0");
		const remainder = String(seconds % 60).padStart(2, "0");
		return `${minutes}:${remainder}`;
	}

	function setRoundStatus(label, value, detail, tone = "success") {
		const result = document.getElementById("casinoGameResult");
		if (!result) return;

		result.style.visibility = "visible";
		result.classList.remove("alert-success", "alert-danger", "alert-warning");
		result.classList.add(`alert-${tone}`, "roulette-round-status");
		result.replaceChildren();

		const labelNode = document.createElement("span");
		labelNode.className = "roulette-round-status__label";
		labelNode.textContent = label;

		const valueNode = document.createElement("strong");
		valueNode.className = "roulette-round-status__value";
		valueNode.textContent = value;

		const detailNode = document.createElement("small");
		detailNode.className = "roulette-round-status__detail";
		detailNode.textContent = detail;

		result.append(labelNode, valueNode, detailNode);
	}

	function renderRoundStatus() {
		if (!roundStateKnown) {
			setRoundStatus("ROUND TIMER", "--:--", "Loading the current roulette round...");
			return;
		}

		const justSettled = Date.now() < recentlySettledUntil;
		if (!roundActive || !nextSpinUtc) {
			setRoundStatus(
				justSettled ? "ROUND SETTLED" : "ROUND TIMER",
				"--:--",
				justSettled
					? "The next five-minute round starts when somebody places a bet."
					: "The five-minute timer starts when the first bet is placed."
			);
			return;
		}

		const remaining = Math.max(0, nextSpinUtc - Math.floor(Date.now() / 1000));
		if (remaining === 0) {
			setRoundStatus("ROLLING NOW", "00:00", "Settling bets and choosing the winning number...");
			return;
		}

		setRoundStatus(
			"NEXT ROLL",
			formatCountdown(remaining),
			"The counter updates live. The round settles automatically at zero."
		);
	}

	function normaliseWishcoinTooltips() {
		document.querySelectorAll('img[alt="coin"], img[alt="Wishcoin"]').forEach((image) => {
			image.alt = "Wishcoin";
			image.title = "Wishcoin";
			image.setAttribute("data-bs-original-title", "Wishcoin");
		});
	}

	window.handleRouletteResponse = function handleRouletteRoundResponse(xhr) {
		let response = null;
		try {
			response = JSON.parse(xhr.response);
		} catch (error) {
			// The legacy handler displays the request failure.
		}

		const succeeded = xhr.status >= 200 && xhr.status < 300 && response && !response.error;
		if (succeeded && typeof window.buildRouletteTable === "function") {
			// The legacy handler appends chips. Rebuild first so polling and repeat
			// bets do not duplicate every chip already displayed on the table.
			window.buildRouletteTable();
		}

		legacyHandleResponse(xhr);
		normaliseWishcoinTooltips();

		if (succeeded && response.round) {
			roundStateKnown = true;
			roundActive = Boolean(response.round.active);
			nextSpinUtc = response.round.next_spin_utc || null;
			if (response.round.rolled) recentlySettledUntil = Date.now() + 10000;
			renderRoundStatus();
		}
	};

	function pollRouletteBets() {
		if (pollInFlight || document.hidden) return;
		pollInFlight = true;

		const xhr = new XMLHttpRequest();
		xhr.open("get", "/casino/roulette/bets");
		xhr.setRequestHeader("xhr", "xhr");
		xhr.onload = () => {
			pollInFlight = false;
			window.handleRouletteResponse(xhr);
		};
		xhr.onerror = () => {
			pollInFlight = false;
		};
		xhr.send();
	}

	normaliseWishcoinTooltips();
	renderRoundStatus();
	window.setInterval(renderRoundStatus, 1000);
	window.setInterval(pollRouletteBets, 5000);
	document.addEventListener("visibilitychange", () => {
		if (!document.hidden) pollRouletteBets();
	});
	pollRouletteBets();
})();
