(() => {
	function installRouletteRoundEnhancements() {
		if (window.__rouletteRoundsInstalled) return;

		const baseHandleResponse = window.handleRouletteResponse;
		if (typeof baseHandleResponse !== "function") {
			window.setTimeout(installRouletteRoundEnhancements, 25);
			return;
		}
		window.__rouletteRoundsInstalled = true;

		let nextSpinUtc = null;
		let errorVisibleUntil = 0;
		let landingVisibleUntil = 0;
		let latestLanding = null;
		let lastSeenRoundId = null;
		let pollInFlight = false;

		function formatCountdown(seconds) {
			const minutes = Math.floor(seconds / 60);
			const remainder = String(seconds % 60).padStart(2, "0");
			return `${minutes}:${remainder}`;
		}

		function setRoundStatus(label, value, tone = "success") {
			const result = document.getElementById("casinoGameResult");
			if (!result) return;
			result.classList.remove("alert-success", "alert-danger", "alert-warning");
			result.classList.add(`alert-${tone}`, "roulette-round-status");
			result.replaceChildren();

			const labelNode = document.createElement("span");
			labelNode.className = "roulette-round-status__label";
			labelNode.textContent = label;

			const valueNode = document.createElement("strong");
			valueNode.className = "roulette-round-status__value";
			valueNode.textContent = value;
			result.append(labelNode, valueNode);
		}

		function renderRoundStatus() {
			const nowMs = Date.now();
			if (nowMs < errorVisibleUntil) return;

			if (latestLanding && nowMs < landingVisibleUntil) {
				setRoundStatus(
					"Ball landed on",
					`${latestLanding.number} (${String(latestLanding.color).toUpperCase()})`,
					latestLanding.color === "red" ? "danger" : "success",
				);
				return;
			}

			if (!nextSpinUtc) {
				setRoundStatus("Next spin in", "--:--");
				return;
			}

			const remaining = Math.max(0, nextSpinUtc - Math.floor(Date.now() / 1000));
			if (remaining === 0) {
				setRoundStatus("Spinning", "0:00", "warning");
				return;
			}
			setRoundStatus("Next spin in", formatCountdown(remaining));
		}

		function highlightWinningNumber(result) {
			document.querySelectorAll("#roulette-table .roulette-winning-number").forEach((cell) => {
				cell.classList.remove("roulette-winning-number");
			});
			if (!result) return;
			const cell = document.getElementById(`STRAIGHT_UP_BET#${result.number_value}`);
			if (cell) cell.classList.add("roulette-winning-number");
		}

		function renderRecentResults(results) {
			const container = document.getElementById("roulette-recent-results");
			if (!container) return;
			container.replaceChildren();

			if (!Array.isArray(results) || results.length === 0) {
				const empty = document.createElement("span");
				empty.className = "roulette-history-empty";
				empty.textContent = "No recorded landings yet.";
				container.appendChild(empty);
				return;
			}

			results.forEach((result, index) => {
				const landing = document.createElement("span");
				landing.className = `roulette-history-ball roulette-history-ball--${result.color}`;
				if (index === 0) landing.classList.add("roulette-history-ball--latest");
				landing.textContent = result.number;
				landing.title = `${result.number} (${result.color})`;
				container.appendChild(landing);
			});
		}

		function processRound(round) {
			if (!round) return;
			nextSpinUtc = round.next_spin_utc || null;

			const results = Array.isArray(round.recent_results) ? round.recent_results : [];
			renderRecentResults(results);
			const newest = round.result || results[0] || null;
			if (newest) {
				highlightWinningNumber(newest);
				const isNewLanding = lastSeenRoundId !== null && newest.round_id !== lastSeenRoundId;
				if (round.rolled || isNewLanding) {
					latestLanding = newest;
					landingVisibleUntil = Date.now() + 8000;
				}
				lastSeenRoundId = newest.round_id;
			}
			renderRoundStatus();
		}

		function responseError(response, xhr) {
			return response?.details
				|| response?.description
				|| response?.error
				|| (xhr.status === 0
					? "The request could not reach the server."
					: `Roulette request failed with status ${xhr.status}.`);
		}

		window.handleRouletteResponse = function handleRouletteRoundResponse(xhr) {
			let response = null;
			try {
				response = JSON.parse(xhr.response);
			} catch (error) {
				console.error("Roulette returned invalid JSON", error);
			}

			const succeeded = xhr.status >= 200 && xhr.status < 300 && response && !response.error;
			baseHandleResponse(xhr);

			if (!succeeded) {
				errorVisibleUntil = Date.now() + 10000;
				setRoundStatus(
					(xhr.responseURL || "").includes("/place-bet") ? "Bet rejected" : "Roulette error",
					responseError(response, xhr),
					"danger",
				);
				return;
			}

			errorVisibleUntil = 0;
			processRound(response.round);
		};

		function pollRouletteBets() {
			if (pollInFlight || document.hidden) return;
			pollInFlight = true;

			const xhr = new XMLHttpRequest();
			xhr.open("GET", "/casino/roulette/bets");
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

		renderRoundStatus();
		window.setInterval(renderRoundStatus, 1000);
		window.setInterval(pollRouletteBets, 2500);
		document.addEventListener("visibilitychange", () => {
			if (!document.hidden) pollRouletteBets();
		});
		pollRouletteBets();
	}

	installRouletteRoundEnhancements();
})();
