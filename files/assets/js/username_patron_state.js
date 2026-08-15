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
		target.style.removeProperty('--username-effect-text-color');
		if (target.classList.contains('username-effect-host')) {
			target.classList.add('username-effect', 'username-effect-text');
		}
	}

	function ensureFreeloaderTextTarget(target, data = {}) {
		if (!(target instanceof HTMLElement)) return null;
		clearExpiredPlate(target);

		if (target.dataset.usernameEffectFreeloaderText === '1') {
			target.dataset.usernameEffectPatron = '0';
			return target;
		}

		target.classList.add('username-effect-text-container');
		target.dataset.usernameEffectPatron = '0';

		let inner = target.querySelector(':scope > [data-username-effect-freeloader-text="1"]');
		if (!inner) {
			inner = document.createElement('span');
			inner.dataset.usernameEffectFreeloaderText = '1';
			while (target.firstChild) inner.append(target.firstChild);
			target.append(inner);
		}

		const userId = target.dataset.usernameEffectUser || data.id;
		const effects = target.dataset.usernameEffects || (Array.isArray(data.username_effects) ? data.username_effects.join(',') : data.username_effects);
		const color = target.dataset.usernameEffectColor || data.username_effect_color;

		if (userId) inner.dataset.usernameEffectUser = String(userId);
		if (effects) inner.dataset.usernameEffects = String(effects);
		if (color) inner.dataset.usernameEffectColor = String(color);
		inner.dataset.usernameEffectPatron = '0';

		// Keep layout/popover behavior on the outer username element. The effect
		// itself belongs only to this inner glyph span, exactly like the working
		// profile-page name renderer.
		target.removeAttribute('data-username-effects');
		target.removeAttribute('data-username-effect-color');
		return inner;
	}

	function setPatronState(target, active, data = {}) {
		if (!(target instanceof HTMLElement)) return;
		target.dataset.usernameEffectPatron = active ? '1' : '0';
		if (!active) ensureFreeloaderTextTarget(target, data);
	}

	function syncDirectTarget(target) {
		if (!(target instanceof HTMLElement)) return;
		if (target.dataset.usernameEffectPatron === '0') ensureFreeloaderTextTarget(target);
	}

	function syncTrigger(trigger) {
		const data = popoverData(trigger);
		if (typeof data.active_patron !== 'boolean') return;
		const target = usernameTarget(trigger);
		if (target) setPatronState(target, data.active_patron, data);
	}

	function scan(root = document) {
		const triggerSelector = '.user-name[data-pop-info]';
		const directSelector = '[data-username-effect-patron]';
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
