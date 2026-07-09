let purchaseQuantity = 1;
const lotteryOnReady = function () {
	checkLotteryStats();

	// Show ticket being pulled.
	const ticketPulled = document.getElementById("lotteryTicketPulled");
	const purchaseTicket = document.getElementById("purchaseTicket");

	purchaseTicket.addEventListener("click", () => {
	ticketPulled.style.display = "block";

	setTimeout(() => {
		ticketPulled.style.display = "none";
		ticketPulled.src =
		"/i/rDrama/lottery_active.webp?v=2000&t=" +
		new Date().getTime();
		purchaseTicket.disabled = false;
	}, 1780);
	});

	// Update the quantity field
	const purchaseQuantityField = document.getElementById(
	"totalQuantityOfTickets"
	);
	const purchaseTotalCostField = document.getElementById("totalCostOfTickets");
	const ticketPurchaseQuantityInput = document.getElementById(
	"ticketPurchaseQuantity"
	);

	ticketPurchaseQuantityInput.addEventListener("change", (event) => {
	const value = Math.max(1, parseInt(event.target.value))
	purchaseQuantity = value
	purchaseQuantityField.innerText = value
	purchaseTotalCostField.innerText = value * 12
	});
};

function purchaseLotteryTicket() {
	return handleLotteryRequest("buy", "POST");
}

function checkLotteryStats() {
	return handleLotteryRequest("active", "GET");
}

// Admin
function ensureIntent() {
	return window.confirm("Are you sure you want to end the current lottery?");
}

function startLotterySession() {
	checkLotteryStats();

	if (ensureIntent()) {
	return handleLotteryRequest("start", "POST", () =>
		location.reload()
	);
	}
}

function endLotterySession() {
	checkLotteryStats();

	if (ensureIntent()) {
	return handleLotteryRequest("end", "POST", () => location.reload());
	}
}

// Composed
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
	const succeeded =
		xhr.status >= 200 && xhr.status < 300 && response && response.message;

	if (succeeded) {
		// Display success.
		const toast = document.getElementById("lottery-post-success");
		const toastMessage = document.getElementById("lottery-post-success-text");

		toastMessage.innerText = response.message;

		bootstrap.Toast.getOrCreateInstance(toast).show();

		callback();
	} else {
		// Display error.
		const toast = document.getElementById("lottery-post-error");
		const toastMessage = document.getElementById("lottery-post-error-text");

		toastMessage.innerText =
		(response && response.error) || "Error, please try again later.";

		bootstrap.Toast.getOrCreateInstance(toast).show();
	}
	}

	if (response && response.stats) {
	lastStats = response.stats;

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
		prizeImage.style.display = "inline";
		prizeField.textContent = lottery.prize;
		timeLeftField.textContent = formatTimeLeft(lottery.timeLeft);

		if (participants) {
		participantsThisSessionField.textContent = participants;
		}

		ticketsSoldThisSessionField.textContent = lottery.ticketsSoldThisSession;
		ticketsHeldCurrentField.textContent = user.ticketsHeld.current;
	} else {
		prizeImage.style.display = "none";
		[
		prizeField,
		timeLeftField,
		ticketsSoldThisSessionField,
		participantsThisSessionField,
		ticketsHeldCurrentField,
		].forEach((e) => (e.textContent = "-"));
		purchaseTicketButton.disabled = true;
	}

	ticketsHeldTotalField.textContent = user.ticketsHeld.total;
	winningsField.textContent = user.winnings;

	const [endButton, startButton] = [
		"endLotterySession",
		"startLotterySession",
	].map((id) => document.getElementById(id));
	if (response.stats.lottery) {
		endButton.style.display = "block";
		startButton.style.display = "none";
	} else {
		endButton.style.display = "none";
		startButton.style.display = "block";
	}
	}
}

function formatTimeLeft(secondsLeft) {
	const minutesLeft = Math.floor(secondsLeft / 60);
	const seconds = secondsLeft % 60;
	const minutes = minutesLeft % 60;
	const hours = Math.floor(minutesLeft / 60);

	return `${hours}h, ${minutes}m, ${seconds}s`;
}

lotteryOnReady();
