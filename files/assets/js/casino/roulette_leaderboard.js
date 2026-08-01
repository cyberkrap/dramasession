(() => {
	const ICONS = {
		trophy: `
			<svg viewBox="0 0 24 24" role="img" aria-hidden="true">
				<path d="M7 4h10v4.5c0 3.1-2.1 5.7-5 6.5-2.9-.8-5-3.4-5-6.5V4Z"/>
				<path d="M7 6H4v1.5c0 2.4 1.7 4.4 4 4.9M17 6h3v1.5c0 2.4-1.7 4.4-4 4.9M12 15v4M8.5 20h7"/>
			</svg>`,
		crown: `
			<svg viewBox="0 0 24 24" role="img" aria-hidden="true">
				<path d="m4 8 4 3 4-6 4 6 4-3-1.5 10h-13L4 8Z"/>
				<path d="M6 21h12"/>
			</svg>`,
		down: `
			<svg viewBox="0 0 24 24" role="img" aria-hidden="true">
				<path d="M12 4v13M6.5 12.5 12 18l5.5-5.5"/>
				<path d="M5 21h14"/>
			</svg>`,
		skull: `
			<svg viewBox="0 0 24 24" role="img" aria-hidden="true">
				<path d="M5 10a7 7 0 1 1 14 0c0 2.7-1.5 4.8-3.8 5.9V19H8.8v-3.1A6.5 6.5 0 0 1 5 10Z"/>
				<circle cx="9" cy="10.5" r="1.2"/><circle cx="15" cy="10.5" r="1.2"/>
				<path d="m10 15 2-1.5 2 1.5M10 19v2M14 19v2"/>
			</svg>`,
	};

	const RECORDS = [
		{
			label: "Biggest Winner (Last 24h)",
			path: ["last_24h", "biggest_win"],
			tone: "winner",
			icon: "trophy",
		},
		{
			label: "Biggest Winner (All Time)",
			path: ["all_time", "biggest_win"],
			tone: "winner",
			icon: "crown",
		},
		{
			label: "Biggest Loser (Last 24h)",
			path: ["last_24h", "biggest_loss"],
			tone: "loser",
			icon: "down",
		},
		{
			label: "Biggest Loser (All Time)",
			path: ["all_time", "biggest_loss"],
			tone: "loser",
			icon: "skull",
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

	function getEntry(leaderboard, path) {
		return path.reduce((value, key) => value?.[key], leaderboard) || {};
	}

	function buildRecord(record, leaderboard) {
		const article = document.createElement("article");
		article.className = `roulette-leader roulette-leader--${record.tone}`;

		const icon = document.createElement("span");
		icon.className = "roulette-leader-icon";
		icon.setAttribute("aria-hidden", "true");
		icon.innerHTML = ICONS[record.icon];

		const details = document.createElement("div");
		details.className = "roulette-leader-details";

		const label = document.createElement("small");
		label.className = "roulette-leader-label";
		label.textContent = record.label;
		details.appendChild(label);

		const entry = getEntry(leaderboard, record.path);
		if (!entry.user || Number(entry.amount || 0) <= 0) {
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

	function renderCasinoLeaderboard(root) {
		if (!root) return;
		const list = root.querySelector(".roulette-leader-list");
		if (!list) return;

		let leaderboard;
		try {
			leaderboard = JSON.parse(root.dataset.leaderboard || "{}");
		} catch (error) {
			console.error("Unable to parse casino leaderboard", error);
			list.textContent = "Casino records are temporarily unavailable.";
			return;
		}

		list.replaceChildren(...RECORDS.map((record) => buildRecord(record, leaderboard)));
	}

	window.renderCasinoLeaderboard = renderCasinoLeaderboard;
	document.querySelectorAll("#roulette-leaders, #gameLeaderboard").forEach(renderCasinoLeaderboard);
})();
