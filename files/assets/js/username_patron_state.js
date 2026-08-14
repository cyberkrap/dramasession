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
		if (trigger.matches('[data-username-effect-user]')) return trigger;
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

	function syncDirectTarget(target) {
		if (!(target instanceof HTMLElement)) return;
		if (target.dataset.usernameEffectPatron !== '0') return;
		clearExpiredPlate(target);
	}

	function syncTrigger(trigger) {
		const data = popoverData(trigger);
		if (data.active_patron !== false) return;
		const target = usernameTarget(trigger);
		if (target) clearExpiredPlate(target);
	}

	function scan(root = document) {
		const triggerSelector = '.user-name[data-pop-info]';
		const directSelector = '[data-username-effect-patron="0"]';
		if (root instanceof Element) {
			if (root.matches(triggerSelector)) syncTrigger(root);
			if (root.matches(directSelector)) syncDirectTarget(root);
		}
		root.querySelectorAll?.(triggerSelector).forEach(syncTrigger);
		root.querySelectorAll?.(directSelector).forEach(syncDirectTarget);
	}

	function initialize() {
		scan(document);
		new MutationObserver(mutations => {
			for (const mutation of mutations) {
				if (mutation.type === 'attributes') {
					const target = mutation.target;
					if (target instanceof Element && target.matches('[data-username-effect-patron="0"]')) {
						syncDirectTarget(target);
					}
					continue;
				}
				mutation.addedNodes.forEach(node => {
					if (node instanceof Element) scan(node);
				});
			}
		}).observe(document.body, {
			childList: true,
			subtree: true,
			attributes: true,
			attributeFilter: ['class'],
		});
	}

	if (document.readyState === 'loading') {
		document.addEventListener('DOMContentLoaded', initialize, {once: true});
	} else {
		initialize();
	}
})();
