(() => {
	const legacyHandleResponse = window.handleRouletteResponse;
	if (typeof legacyHandleResponse !== "function") return;

	let roundStateKnown = false;
	let roundActive = false;
	let nextSpinUtc = null;
	let recentlySettledUntil = 0;
	let pollInFlight = false;

	function formatCountdown(seconds) {
		const minutes = Math.floor(seconds / 60);
		const remainder = String(seconds % 60).padStart(2, "0");
		return `${minutes}:${remainder}`;
	}

	function renderRoundStatus() {
		if (!roundStateKnown) return;

		const settledPrefix = Date.now() < recentlySettledUntil ? "Previous round settled. " : "";
		if (!roundActive || !nextSpinUtc) {
			updateResult(`${settledPrefix}The five-minute timer starts when the first bet is placed.`, "success");
			return;
		}

		const remaining = Math.max(0, nextSpinUtc - Math.floor(Date.now() / 1000));
		if (remaining === 0) {
			updateResult("Settling roulette round...", "success");
			return;
		}

		updateResult(`${settledPrefix}Next roll in ${formatCountdown(remaining)}`, "success");
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

	window.setInterval(renderRoundStatus, 1000);
	window.setInterval(pollRouletteBets, 5000);
	document.addEventListener("visibilitychange", () => {
		if (!document.hidden) pollRouletteBets();
	});
	pollRouletteBets();
})();
