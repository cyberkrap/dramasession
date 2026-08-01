(() => {
	const root = document.getElementById("roulette-leaders");
	if (!root) return;

	const list = root.querySelector(".roulette-leader-list");
	if (!list) return;

	let leaderboard;
	try {
		leaderboard = JSON.parse(root.dataset.leaderboard || "{}");
	} catch (error) {
		console.error("Unable to parse roulette leaderboard", error);
		list.textContent = "Roulette records are temporarily unavailable.";
		return;
	}

	const records = [
		{
			label: "Biggest Winner (Last 24h)",
			entry: leaderboard?.last_24h?.biggest_win,
			tone: "winner",
			icon: "fa-trophy",
		},
		{
			label: "Biggest Winner (All Time)",
			entry: leaderboard?.all_time?.biggest_win,
			tone: "winner",
			icon: "fa-crown",
		},
		{
			label: "Biggest Loser (Last 24h)",
			entry: leaderboard?.last_24h?.biggest_loss,
			tone: "loser",
			icon: "fa-arrow-down",
		},
		{
			label: "Biggest Loser (All Time)",
			entry: leaderboard?.all_time?.biggest_loss,
			tone: "loser",
			icon: "fa-skull",
		},
	];

	function formatAmount(value) {
		const amount = Number(value || 0);
		return typeof formatNumber === "function"
			? formatNumber(amount)
			: amount.toLocaleString();
	}

	function currencyName(currency, amount) {
		if (currency === "marseybux") return "Wishbux";
		return Number(amount) === 1 ? "Wishcoin" : "Wishcoins";
	}

	function buildRecord(record) {
		const article = document.createElement("article");
		article.className = `roulette-leader roulette-leader--${record.tone}`;

		const icon = document.createElement("span");
		icon.className = "roulette-leader-icon";
		icon.setAttribute("aria-hidden", "true");
		const iconGlyph = document.createElement("i");
		iconGlyph.className = `fas ${record.icon}`;
		icon.appendChild(iconGlyph);

		const details = document.createElement("div");
		details.className = "roulette-leader-details";

		const label = document.createElement("small");
		label.className = "roulette-leader-label";
		label.textContent = record.label;
		details.appendChild(label);

		const entry = record.entry || {};
		if (!entry.user) {
			const empty = document.createElement("strong");
			empty.className = "roulette-leader-empty";
			empty.textContent = "No record yet";
			details.appendChild(empty);
		} else {
			const user = document.createElement("a");
			user.className = "roulette-leader-user";
			user.href = `/@${encodeURIComponent(entry.user)}`;
			user.textContent = entry.user;
			details.appendChild(user);

			const amount = document.createElement("span");
			amount.className = "roulette-leader-amount";
			amount.textContent = `${formatAmount(entry.amount)} ${currencyName(entry.currency, entry.amount)}`;
			details.appendChild(amount);
		}

		article.append(icon, details);
		return article;
	}

	list.replaceChildren(...records.map(buildRecord));
})();
