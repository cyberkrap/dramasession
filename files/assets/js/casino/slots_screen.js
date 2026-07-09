function pullSlots() {
	const { amount, currency } = getWager();

	console.log({amount, currency})

	disableWager();
	clearResult();
	document.getElementById("casinoSlotsPull").disabled = true;

	const xhr = new XMLHttpRequest();
	xhr.open("post", "/casino/slots");
	xhr.setRequestHeader('xhr', 'xhr');
	xhr.onload = handleSlotsResponse.bind(null, xhr);

	const form = new FormData();
	form.append("formkey", formkey());
	form.append("wager", amount);
	form.append("currency", currency);

	xhr.send(form);
}

function handleSlotsResponse(xhr) {
	let response;

	try {
		response = JSON.parse(xhr.response);
	} catch (error) {
		console.error(error);
	}

	const succeeded =
		xhr.status >= 200 && xhr.status < 300 && response && !response.error;

	if (succeeded) {
		const { game_state, gambler } = response;
		const state = JSON.parse(game_state);
		const reels = Array.from(document.querySelectorAll(".slots_reel"));
		const symbols = state.symbols.split(",");

		for (let i = 0; i < 3; i++) {
			reels[i].innerHTML = symbols[i];
		}

		let className;

		if (state.text.includes("Jackpot")) {
			className = "warning";
		} else if (state.text.includes("Won")) {
			className = "success";
		} else if (state.text.includes("Lost")) {
			className = "danger";
		} else {
			className = "success";
		}

		updateResult(state.text, className);
		updatePlayerCurrencies(gambler);
		reloadFeed()
	} else {
		updateResult(response.error, "danger");
		console.error(response.error);
	}

	enableWager();
	document.getElementById("casinoSlotsPull").disabled = false;
}
