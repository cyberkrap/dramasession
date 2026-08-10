let purchaseQuantity = 1;

const lotteryOnReady = function () {
	checkLotteryStats();

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
			if (timeLeftField) timeLeftField.textContent = formatTimeLeft(lottery.timeLeft);
			if (participantsThisSessionField) participantsThisSessionField.textContent = formatNumber(participants || 0);
			if (ticketsSoldThisSessionField) ticketsSoldThisSessionField.textContent = formatNumber(lottery.ticketsSoldThisSession);
			if (ticketsHeldCurrentField) ticketsHeldCurrentField.textContent = formatNumber(user.ticketsHeld.current);
			if (purchaseTicketButton) purchaseTicketButton.disabled = false;
		} else {
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

function formatTimeLeft(secondsLeft) {
	const total = Math.max(0, Number(secondsLeft) || 0);
	const days = Math.floor(total / 86400);
	const hours = Math.floor((total % 86400) / 3600);
	const minutes = Math.floor((total % 3600) / 60);
	const seconds = total % 60;

	if (days > 0) return `${days}d, ${hours}h, ${minutes}m, ${seconds}s`;
	return `${hours}h, ${minutes}m, ${seconds}s`;
}

lotteryOnReady();
