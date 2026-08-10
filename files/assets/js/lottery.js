let purchaseQuantity = 1;
let lotteryCountdownSeconds = null;
let lotteryCountdownTimer = null;
let lotteryResyncTimer = null;
let lotteryRolloverCheckPending = false;

const lotteryOnReady = function () {
	checkLotteryStats();
	startLotteryCountdownClock();

	const ticketPulled = document.getElementById("lotteryTicketPulled");
	const purchaseTicket = document.getElementById("purchaseTicket");

	if (purchaseTicket && ticketPulled) {
		purchaseTicket.addEventListener("click", () => {
			ticketPulled.style.display = "flex";
			setTimeout(() => {
				ticketPulled.style.display = "none";
				purchaseTicket.disabled = false;
			}, 1780);
		});
	}

	const purchaseQuantityField = document.getElementById("totalQuantityOfTickets");
	const purchaseTotalCostField = document.getElementById("totalCostOfTickets");
	const ticketPurchaseQuantityInput = document.getElementById("ticketPurchaseQuantity");

	if (ticketPurchaseQuantityInput) {
		ticketPurchaseQuantityInput.addEventListener("change", (event) => {
			const parsed = parseInt(event.target.value, 10);
			const value = Number.isFinite(parsed) ? Math.max(1, parsed) : 1;
			event.target.value = value;
			purchaseQuantity = value;
			purchaseQuantityField.innerText = value;
			purchaseTotalCostField.innerText = formatNumber(value * 12);
		});
	}

	// Browsers throttle background tabs. Resync immediately when the user comes
	// back so the displayed countdown never drifts after tab suspension.
	document.addEventListener("visibilitychange", () => {
		if (!document.hidden) checkLotteryStats();
	});
};

function purchaseLotteryTicket() {
	return handleLotteryRequest("buy", "POST");
}

function checkLotteryStats() {
	return handleLotteryRequest("active", "GET");
}

function ensureIntent() {
	return window.confirm("Are you sure you want to override the current lottery session?");
}

function startLotterySession() {
	checkLotteryStats();
	if (ensureIntent()) {
		return handleLotteryRequest("start", "POST", () => location.reload());
	}
}

function endLotterySession() {
	checkLotteryStats();
	if (ensureIntent()) {
		return handleLotteryRequest("end", "POST", () => location.reload());
	}
}

function handleLotteryRequest(uri, method, callback = () => {}) {
	const form = new FormData();
	form.append("formkey", formkey());
	form.append("quantity", purchaseQuantity);
	const xhr = createXhrWithFormKey(`/lottery/${uri}`, method, form);
	xhr[0].onload = handleLotteryResponse.bind(null, xhr[0], method, callback);
	xhr[0].send(xhr[1]);
}

function handleLotteryResponse(xhr, method, callback) {
	let response;

	try {
		response = JSON.parse(xhr.response);
	} catch (error) {
		console.error(error);
	}

	if (method === "POST") {
		const succeeded = xhr.status >= 200 && xhr.status < 300 && response && response.message;

		if (succeeded) {
			const toast = document.getElementById("lottery-post-success");
			const toastMessage = document.getElementById("lottery-post-success-text");
			if (toast && toastMessage) {
				toastMessage.innerText = response.message;
				bootstrap.Toast.getOrCreateInstance(toast).show();
			}
			callback();
		} else {
			const toast = document.getElementById("lottery-post-error");
			const toastMessage = document.getElementById("lottery-post-error-text");
			if (toast && toastMessage) {
				toastMessage.innerText = (response && response.error) || "Error, please try again later.";
				bootstrap.Toast.getOrCreateInstance(toast).show();
			}
		}
	}

	if (response && response.stats) {
		const { user, lottery, participants } = response.stats;
		const [
			prizeImage,
			prizeField,
			timeLeftField,
			ticketsSoldThisSessionField,
			participantsThisSessionField,
			ticketsHeldCurrentField,
			ticketsHeldTotalField,
			winningsField,
			purchaseTicketButton,
		] = [
			"prize-image",
			"prize",
			"timeLeft",
			"ticketsSoldThisSession",
			"participantsThisSession",
			"ticketsHeldCurrent",
			"ticketsHeldTotal",
			"winnings",
			"purchaseTicket",
		].map((id) => document.getElementById(id));

		if (lottery) {
			if (prizeImage) prizeImage.style.display = "inline";
			if (prizeField) prizeField.textContent = formatNumber(lottery.prize);
			setLotteryCountdown(lottery.timeLeft);
			if (timeLeftField) timeLeftField.textContent = formatTimeLeft(lotteryCountdownSeconds);
			if (participantsThisSessionField) participantsThisSessionField.textContent = formatNumber(participants || 0);
			if (ticketsSoldThisSessionField) ticketsSoldThisSessionField.textContent = formatNumber(lottery.ticketsSoldThisSession);
			if (ticketsHeldCurrentField) ticketsHeldCurrentField.textContent = formatNumber(user.ticketsHeld.current);
			if (purchaseTicketButton) purchaseTicketButton.disabled = false;
			lotteryRolloverCheckPending = false;
		} else {
			lotteryCountdownSeconds = null;
			if (prizeImage) prizeImage.style.display = "none";
			[prizeField, timeLeftField, ticketsSoldThisSessionField, participantsThisSessionField, ticketsHeldCurrentField]
				.filter(Boolean)
				.forEach((element) => (element.textContent = "-"));
			if (purchaseTicketButton) purchaseTicketButton.disabled = true;
		}

		if (ticketsHeldTotalField) ticketsHeldTotalField.textContent = formatNumber(user.ticketsHeld.total);
		if (winningsField) winningsField.textContent = formatNumber(user.winnings);

		const endButton = document.getElementById("endLotterySession");
		const startButton = document.getElementById("startLotterySession");
		if (endButton && startButton) {
			if (lottery) {
				endButton.style.display = "block";
				startButton.style.display = "none";
			} else {
				endButton.style.display = "none";
				startButton.style.display = "block";
			}
		}
	}
}

function setLotteryCountdown(secondsLeft) {
	lotteryCountdownSeconds = Math.max(0, Math.floor(Number(secondsLeft) || 0));
}

function startLotteryCountdownClock() {
	if (lotteryCountdownTimer) clearInterval(lotteryCountdownTimer);
	if (lotteryResyncTimer) clearInterval(lotteryResyncTimer);

	lotteryCountdownTimer = window.setInterval(() => {
		if (lotteryCountdownSeconds === null) return;

		lotteryCountdownSeconds = Math.max(0, lotteryCountdownSeconds - 1);
		const timeLeftField = document.getElementById("timeLeft");
		if (timeLeftField) timeLeftField.textContent = formatTimeLeft(lotteryCountdownSeconds);

		// Once the timer reaches zero, ask the server for the newly rolled-over
		// weekly session exactly once rather than leaving 0s on screen forever.
		if (lotteryCountdownSeconds === 0 && !lotteryRolloverCheckPending) {
			lotteryRolloverCheckPending = true;
			window.setTimeout(() => checkLotteryStats(), 1200);
		}
	}, 1000);

	// Correct any clock drift without making a request every second.
	lotteryResyncTimer = window.setInterval(() => {
		if (!document.hidden) checkLotteryStats();
	}, 60000);
}

function formatTimeLeft(secondsLeft) {
	const total = Math.max(0, Math.floor(Number(secondsLeft) || 0));
	const days = Math.floor(total / 86400);
	const hours = Math.floor((total % 86400) / 3600);
	const minutes = Math.floor((total % 3600) / 60);
	const seconds = total % 60;

	if (days > 0) return `${days}d, ${hours}h, ${minutes}m, ${seconds}s`;
	return `${hours}h, ${minutes}m, ${seconds}s`;
}

lotteryOnReady();
