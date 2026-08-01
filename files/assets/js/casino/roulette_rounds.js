(() => {
	function installRouletteRoundEnhancements() {
		if (window.__rouletteRoundsInstalled) return;

		const legacyHandleResponse = window.handleRouletteResponse;
		if (typeof legacyHandleResponse !== "function") {
			window.setTimeout(installRouletteRoundEnhancements, 25);
			return;
		}

		window.__rouletteRoundsInstalled = true;

		let roundStateKnown = false;
		let roundActive = false;
		let nextSpinUtc = null;
		let recentlySettledUntil = 0;
		let errorVisibleUntil = 0;
		let pollInFlight = false;

		function formatCountdown(seconds) {
			const minutes = String(Math.floor(seconds / 60)).padStart(1, "0");
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
			if (Date.now() < errorVisibleUntil) return;

			if (!roundStateKnown || !nextSpinUtc) {
				setRoundStatus("NEXT SPIN IN", "--:--", "Loading the roulette clock...");
				return;
			}

			const remaining = Math.max(0, nextSpinUtc - Math.floor(Date.now() / 1000));
			if (remaining === 0) {
				setRoundStatus("SPINNING", "0:00", "Settling the current clock round...");
				return;
			}

			const justSettled = Date.now() < recentlySettledUntil;
			setRoundStatus(
				justSettled ? "NEXT SPIN IN" : "NEXT SPIN IN",
				formatCountdown(remaining),
				roundActive
					? "Bets close when the real-world five-minute clock reaches zero."
					: "Spins are aligned to :00, :05, :10, :15 and every five minutes after."
			);
		}

		function normaliseCurrencyAssets() {
			const wishcoinSource = document.querySelector('label[for="wagerCoins"] img')?.src;
			const wishbuxSource = document.querySelector('label[for="wagerMarseybux"] img')?.src;

			document.querySelectorAll('img[alt="coin"], img[alt="Wishcoin"]').forEach((image) => {
				if (wishcoinSource) image.src = wishcoinSource;
				image.alt = "Wishcoin";
				image.title = "Wishcoin";
				image.setAttribute("data-bs-original-title", "Wishcoin");
				image.classList.add("roulette-currency-icon");
			});

			document.querySelectorAll('img[alt="marseybux"], img[alt="Wishbux"]').forEach((image) => {
				if (wishbuxSource) image.src = wishbuxSource;
				image.alt = "Wishbux";
				image.title = "Wishbux";
				image.setAttribute("data-bs-original-title", "Wishbux");
				image.classList.add("roulette-currency-icon");
			});
		}

		function clearRenderedRouletteChips() {
			const table = document.getElementById("roulette-table");
			if (!table) return;

			table.querySelectorAll(".roulette-poker-chip").forEach((chip) => {
				const wrapper = chip.parentElement;
				if (wrapper && wrapper.parentElement && wrapper.parentElement.closest("#roulette-table")) {
					wrapper.remove();
				} else {
					chip.remove();
				}
			});

			table.querySelectorAll("[data-count]").forEach((cell) => {
				cell.removeAttribute("data-count");
			});
		}

		function getResponseError(response, xhr) {
			if (response) {
				return response.details || response.description || response.error || "The roulette request was rejected.";
			}
			if (xhr.status === 0) return "The request could not reach the server. Check your connection and try again.";
			return `Roulette request failed with status ${xhr.status}.`;
		}

		window.handleRouletteResponse = function handleRouletteRoundResponse(xhr) {
			let response = null;
			try {
				response = JSON.parse(xhr.response);
			} catch (error) {
				// A readable fallback is shown below when the response is not JSON.
			}

			const succeeded = xhr.status >= 200 && xhr.status < 300 && response && !response.error;
			if (succeeded) clearRenderedRouletteChips();

			legacyHandleResponse(xhr);
			normaliseCurrencyAssets();

			if (!succeeded) {
				const isBetRequest = (xhr.responseURL || "").includes("/casino/roulette/place-bet");
				errorVisibleUntil = Date.now() + 10000;
				setRoundStatus(
					isBetRequest ? "BET REJECTED" : "ROULETTE ERROR",
					"×",
					getResponseError(response, xhr),
					"danger"
				);
				return;
			}

			if ((xhr.responseURL || "").includes("/casino/roulette/place-bet")) {
				errorVisibleUntil = 0;
			}

			if (response.round) {
				roundStateKnown = true;
				roundActive = Boolean(response.round.active);
				nextSpinUtc = response.round.next_spin_utc || null;
				if (response.round.rolled) recentlySettledUntil = Date.now() + 8000;
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

		normaliseCurrencyAssets();
		renderRoundStatus();
		window.setInterval(renderRoundStatus, 1000);
		window.setInterval(pollRouletteBets, 5000);
		document.addEventListener("visibilitychange", () => {
			if (!document.hidden) pollRouletteBets();
		});
		pollRouletteBets();
	}

	installRouletteRoundEnhancements();
})();
