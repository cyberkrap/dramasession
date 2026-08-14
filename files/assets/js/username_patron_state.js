(() => {
	'use strict';

	function popoverData(trigger) {
		try {
			return JSON.parse(trigger.dataset.popInfo || '{}');
		} catch (_) {
			return {};
		}
	}

	function usernameTarget(trigger) {
		if (!(trigger instanceof Element)) return null;
		const explicit = trigger.querySelector(':scope > [data-username-effect-user]');
		if (explicit) return explicit;
		const spans = Array.from(trigger.children).filter(child =>
			child instanceof Element && child.tagName === 'SPAN' &&
			!child.matches('.pronouns, [class*="pronoun"], [class*="flair"], .mod, .mod-rdrama')
		);
		return spans[spans.length - 1] || null;
	}

	function clearExpiredPlate(target) {
		if (!(target instanceof HTMLElement)) return;
		target.classList.remove('patron', 'username-effect-plate');
		target.style.removeProperty('background-color');
		target.style.removeProperty('color');
		target.style.removeProperty('-webkit-text-fill-color');
		target.style.removeProperty('-webkit-background-clip');
		target.style.removeProperty('background-clip');
		target.style.removeProperty('--username-effect-text-color');
		if (target.classList.contains('username-effect-host')) {
			target.classList.add('username-effect', 'username-effect-text');
		}
	}

	function syncTrigger(trigger) {
		const data = popoverData(trigger);
		if (data.active_patron !== false) return;
		const target = usernameTarget(trigger);
		if (!target) return;
		if (target.classList.contains('patron') || target.classList.contains('username-effect-plate')) {
			clearExpiredPlate(target);
		}
	}

	function scan(root = document) {
		const selector = '.user-name[data-pop-info]';
		if (root instanceof Element && root.matches(selector)) syncTrigger(root);
		root.querySelectorAll?.(selector).forEach(syncTrigger);
	}

	function initialize() {
		scan(document);
		new MutationObserver(mutations => {
			for (const mutation of mutations) {
				mutation.addedNodes.forEach(node => {
					if (node instanceof Element) scan(node);
				});
			}
		}).observe(document.body, {childList: true, subtree: true});
	}

	if (document.readyState === 'loading') {
		document.addEventListener('DOMContentLoaded', initialize, {once: true});
	} else {
		initialize();
	}
})();
