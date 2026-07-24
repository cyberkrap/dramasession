(() => {
	'use strict';

	const ASSET_ROOT = '/assets/images/username_effects/';
	const CYCLE_INTERVAL = 4200;
	const groups = new Map();
	const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

	function cleanEffects(value) {
		const seen = new Set();
		return String(value || '')
			.split(',')
			.map(item => item.trim().toLowerCase())
			.filter(item => /^[a-z0-9_]+$/.test(item))
			.filter(item => {
				if (seen.has(item)) return false;
				seen.add(item);
				return true;
			});
	}

	function effectUrl(effect) {
		return `url("${ASSET_ROOT}${encodeURIComponent(effect)}.webp?v=1")`;
	}

	function applyEffect(element, effect) {
		if (!element || !effect) return;
		element.classList.add('username-effect');
		element.dataset.usernameEffectCurrent = effect;
		element.style.setProperty('--username-effect-image', effectUrl(effect));
		element.style.setProperty('background-image', effectUrl(effect), 'important');
		element.style.setProperty('color', 'transparent', 'important');
		element.style.setProperty('-webkit-text-fill-color', 'transparent', 'important');
		element.style.setProperty('-webkit-background-clip', 'text', 'important');
		element.style.setProperty('background-clip', 'text', 'important');
	}

	function groupKey(element, effects) {
		return `${element.dataset.usernameEffectUser || 'anonymous'}::${effects.join(',')}`;
	}

	function register(element) {
		if (!(element instanceof Element)) return;
		const effects = cleanEffects(element.dataset.usernameEffects);
		if (!effects.length) return;

		const key = groupKey(element, effects);
		let state = groups.get(key);
		if (!state) {
			state = {
				effects,
				index: Math.floor(Math.random() * effects.length),
				elements: new Set(),
			};
			groups.set(key, state);
			effects.forEach(effect => {
				const image = new Image();
				image.decoding = 'async';
				image.src = `${ASSET_ROOT}${encodeURIComponent(effect)}.webp?v=1`;
			});
		}
		state.elements.add(element);
		applyEffect(element, state.effects[state.index]);
	}

	function ensureInnerEffect(host, userId, effectsValue) {
		if (!(host instanceof Element)) return;
		const effects = cleanEffects(effectsValue);
		if (!effects.length) return;

		let effect = host.querySelector(':scope > .username-effect');
		if (!effect) {
			effect = document.createElement('span');
			effect.className = 'username-effect';
			while (host.firstChild) effect.append(host.firstChild);
			host.append(effect);
		}
		effect.dataset.usernameEffectUser = String(userId || 'anonymous');
		effect.dataset.usernameEffects = effects.join(',');
		register(effect);
	}

	function dataForTrigger(trigger) {
		try {
			return JSON.parse(trigger.dataset.popInfo || '{}');
		} catch (_) {
			return {};
		}
	}

	function enhanceTrigger(trigger) {
		if (!(trigger instanceof Element)) return;
		const data = dataForTrigger(trigger);
		const effects = cleanEffects(data.username_effects);
		if (!effects.length) return;

		const candidates = Array.from(trigger.children).filter(
			child => child.tagName === 'SPAN' && !child.classList.contains('pronouns')
		);
		const host = candidates[candidates.length - 1];
		if (host) ensureInnerEffect(host, data.id, effects.join(','));
	}

	function enhanceMarkers(root=document) {
		const markers = [];
		if (root instanceof Element && root.matches('[data-username-effect-target]')) markers.push(root);
		if (root.querySelectorAll) markers.push(...root.querySelectorAll('[data-username-effect-target]'));
		for (const marker of markers) {
			const target = document.querySelector(marker.dataset.usernameEffectTarget);
			if (target) ensureInnerEffect(
				target,
				marker.dataset.usernameEffectUser,
				marker.dataset.usernameEffects,
			);
		}
	}

	function scan(root=document) {
		const direct = [];
		const hosts = [];
		const triggers = [];
		const hostSelector = '[data-username-effects]:not(.username-effect):not([data-username-effect-target])';
		if (root instanceof Element) {
			if (root.matches('.username-effect[data-username-effects]')) direct.push(root);
			if (root.matches(hostSelector)) hosts.push(root);
			if (root.matches('.user-name[data-pop-info]')) triggers.push(root);
		}
		if (root.querySelectorAll) {
			direct.push(...root.querySelectorAll('.username-effect[data-username-effects]'));
			hosts.push(...root.querySelectorAll(hostSelector));
			triggers.push(...root.querySelectorAll('.user-name[data-pop-info]'));
		}
		direct.forEach(register);
		hosts.forEach(host => ensureInnerEffect(
			host,
			host.dataset.usernameEffectUser,
			host.dataset.usernameEffects,
		));
		triggers.forEach(enhanceTrigger);
		enhanceMarkers(root);
	}

	function cycle() {
		if (reducedMotion.matches) return;
		for (const [key, state] of groups) {
			for (const element of Array.from(state.elements)) {
				if (!element.isConnected) state.elements.delete(element);
			}
			if (!state.elements.size) {
				groups.delete(key);
				continue;
			}
			if (state.effects.length < 2) continue;
			let next = state.index;
			while (next === state.index) next = Math.floor(Math.random() * state.effects.length);
			state.index = next;
			const effect = state.effects[state.index];
			state.elements.forEach(element => applyEffect(element, effect));
		}
	}

	document.addEventListener('shown.bs.popover', event => {
		const trigger = event.target;
		if (!(trigger instanceof Element) || !trigger.matches('.user-name[data-pop-info]')) return;
		const data = dataForTrigger(trigger);
		const effects = cleanEffects(data.username_effects);
		if (!effects.length) return;

		requestAnimationFrame(() => {
			const popoverId = trigger.getAttribute('aria-describedby');
			const popover = popoverId ? document.getElementById(popoverId) : null;
			const host = popover && popover.querySelector('.pop-username');
			if (host) ensureInnerEffect(host, data.id, effects.join(','));
		});
	});

	document.addEventListener('DOMContentLoaded', () => {
		scan(document);
		const observer = new MutationObserver(mutations => {
			for (const mutation of mutations) {
				for (const node of mutation.addedNodes) {
					if (node instanceof Element) scan(node);
				}
			}
		});
		observer.observe(document.body, {childList: true, subtree: true});
		window.setInterval(cycle, CYCLE_INTERVAL);
	});
})();
