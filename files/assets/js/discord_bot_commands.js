(() => {
	"use strict";

	const copyText = async (text) => {
		if (navigator.clipboard && window.isSecureContext) {
			await navigator.clipboard.writeText(text);
			return;
		}

		const textarea = document.createElement("textarea");
		textarea.value = text;
		textarea.setAttribute("readonly", "");
		textarea.style.position = "fixed";
		textarea.style.opacity = "0";
		document.body.appendChild(textarea);
		textarea.select();
		const copied = document.execCommand("copy");
		textarea.remove();
		if (!copied) throw new Error("Copy command failed");
	};

	document.querySelectorAll("[data-copy-command]").forEach((button) => {
		button.addEventListener("click", async () => {
			const syntax = button.dataset.copyCommand || "";
			if (!syntax) return;

			const label = button.querySelector("span");
			const originalLabel = label ? label.textContent : "";
			button.disabled = true;

			try {
				await copyText(syntax);
				if (label) label.textContent = "Copied";
			} catch (error) {
				console.error("Could not copy command syntax:", error);
				if (label) label.textContent = "Failed";
			} finally {
				window.setTimeout(() => {
					if (label) label.textContent = originalLabel;
					button.disabled = false;
				}, 1200);
			}
		});
	});

	const search = document.querySelector("#discord-command-filter");
	const cards = Array.from(document.querySelectorAll("[data-command-card]"));
	const empty = document.querySelector("[data-command-js-empty]");
	if (!search || cards.length === 0) return;

	const filter = () => {
		const needle = search.value.trim().toLocaleLowerCase();
		let visible = 0;

		cards.forEach((card) => {
			const haystack = (card.dataset.commandText || "").toLocaleLowerCase();
			const matches = !needle || haystack.includes(needle);
			card.hidden = !matches;
			if (matches) visible += 1;
		});

		if (empty) empty.hidden = visible !== 0;
	};

	search.addEventListener("input", filter);
})();
