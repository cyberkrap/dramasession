(() => {
	'use strict';

	if (!window.location.pathname.startsWith('/casino')) return;

	const isCurrencyImage = (image) => {
		const source = String(image.currentSrc || image.getAttribute('src') || '').toLowerCase();
		const alt = String(image.getAttribute('alt') || '').toLowerCase();
		const title = String(image.getAttribute('title') || '').toLowerCase();
		return source.includes('wishcoin')
			|| source.includes('coins.webp')
			|| source.includes('marseybux')
			|| alt.includes('wishcoin')
			|| alt.includes('wishbux')
			|| title.includes('wishcoin')
			|| title.includes('wishbux');
	};

	const hasAssociatedRadio = (choice) => {
		if (!choice) return false;
		if (choice.matches('input[type="radio"]')) return true;
		if (choice.querySelector('input[type="radio"]')) return true;

		if (choice.tagName === 'LABEL' && choice.htmlFor) {
			const input = document.getElementById(choice.htmlFor);
			if (input && input.matches('input[type="radio"]')) return true;
		}

		const previous = choice.previousElementSibling;
		if (previous && previous.matches('input[type="radio"]')) return true;

		return Boolean(choice.closest('[role="radiogroup"], .btn-group, .currency, [class*="currency"]'));
	};

	const cleanCurrencyChoices = (root = document) => {
		root.querySelectorAll('img').forEach((image) => {
			if (!isCurrencyImage(image)) return;

			const choice = image.closest('label, button, .btn, [role="radio"]');
			if (!choice || !hasAssociatedRadio(choice)) return;

			choice.classList.add('casino-currency-choice-clean');
		});
	};

	const start = () => {
		cleanCurrencyChoices();

		const observer = new MutationObserver((mutations) => {
			for (const mutation of mutations) {
				for (const node of mutation.addedNodes) {
					if (!(node instanceof Element)) continue;
					if (node.matches('img') && isCurrencyImage(node)) {
						cleanCurrencyChoices(node.parentElement || document);
					} else if (node.querySelector('img')) {
						cleanCurrencyChoices(node);
					}
				}
			}
		});

		observer.observe(document.body, { childList: true, subtree: true });
	};

	if (document.readyState === 'loading') {
		document.addEventListener('DOMContentLoaded', start, { once: true });
	} else {
		start();
	}
})();
