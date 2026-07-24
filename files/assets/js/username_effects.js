(() => {
	'use strict';

	const ASSET_ROOT = '/assets/images/username_effects/';
	const CYCLE_INTERVAL = 6500;
	const groups = new Map();
	const registrations = new WeakMap();
	const assetCache = new Map();
	const previewElements = new Set();
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

	function assetUrl(effect) {
		return `${ASSET_ROOT}${encodeURIComponent(effect)}.webp?v=1`;
	}

	function effectUrl(effect) {
		return `url("${assetUrl(effect)}")`;
	}

	function preloadEffect(effect) {
		if (assetCache.has(effect)) return assetCache.get(effect).promise;
		const image = new Image();
		image.decoding = 'async';
		const promise = new Promise(resolve => {
			image.addEventListener('load', () => resolve(true), {once: true});
			image.addEventListener('error', () => resolve(false), {once: true});
		});
		image.src = assetUrl(effect);
		assetCache.set(effect, {image, promise});
		return promise;
	}

	function usableColor(element) {
		if (element.dataset.usernameEffectFallback) return element.dataset.usernameEffectFallback;
		let node = element;
		while (node instanceof Element) {
			const color = getComputedStyle(node).color;
			if (color && color !== 'transparent' && !/^rgba\([^)]*,\s*0(?:\.0+)?\)$/.test(color)) {
				element.dataset.usernameEffectFallback = color;
				return color;
			}
			node = node.parentElement;
		}
		element.dataset.usernameEffectFallback = '#f5f5f5';
		return '#f5f5f5';
	}

	function unwrapOldInnerEffect(element) {
		const inner = element.querySelector(':scope > .username-effect');
		if (!inner) return;
		while (inner.firstChild) element.insertBefore(inner.firstChild, inner);
		inner.remove();
	}

	function isPatronPlate(element) {
		return element instanceof Element && element.classList.contains('patron');
	}

	function resolveTarget(host) {
		if (!(host instanceof Element)) return null;
		if (isPatronPlate(host)) return host;
		const directPatron = host.querySelector(':scope > .patron');
		if (directPatron) return directPatron;
		if (isPatronPlate(host.parentElement)) return host.parentElement;
		if (host.matches('span, strong, b, bdi, h1, h2, h3, h4, h5')) return host;
		const textSpans = Array.from(host.children).filter(
			child => child.tagName === 'SPAN' && !child.classList.contains('pronouns')
		);
		return textSpans[textSpans.length - 1] || host;
	}

	function prepareTarget(element) {
		const plate = isPatronPlate(element);
		if (plate) {
			unwrapOldInnerEffect(element);
			element.classList.remove('username-effect');
			element.classList.add('username-effect-plate');
			element.style.removeProperty('color');
			element.style.removeProperty('-webkit-text-fill-color');
			element.style.removeProperty('-webkit-background-clip');
			element.style.removeProperty('background-clip');
		} else {
			element.classList.remove('username-effect-plate');
			element.classList.add('username-effect');
			element.style.setProperty('--username-effect-fallback', usableColor(element));
		}
	}

	function clearVisual(element) {
		if (!(element instanceof Element)) return;
		element.classList.remove('username-effect--ready');
		element.style.removeProperty('background-image');
		element.style.removeProperty('--username-effect-image');
		delete element.dataset.usernameEffectCurrent;
	}

	async function applyEffect(element, effect) {
		if (!(element instanceof Element) || !effect || !element.isConnected) return;
		if (element.dataset.usernameEffectCurrent === effect && element.classList.contains('username-effect--ready')) return;
		const requestToken = `${effect}:${Date.now()}:${Math.random()}`;
		element.dataset.usernameEffectRequest = requestToken;
		const loaded = await preloadEffect(effect);
		if (!element.isConnected || element.dataset.usernameEffectRequest !== requestToken) return;
		if (!loaded) {
			clearVisual(element);
			return;
		}
		const image = effectUrl(effect);
		element.style.setProperty('--username-effect-image', image);
		element.style.setProperty('background-image', image, 'important');
		element.dataset.usernameEffectCurrent = effect;
		element.classList.add('username-effect--ready');
	}

	function groupKey(element, effects) {
		return `${element.dataset.usernameEffectUser || 'anonymous'}::${effects.join(',')}`;
	}

	function isPreview(element) {
		return Boolean(element.closest('.obs-effect-preview, .obs-effect-live-preview'));
	}

	function fitPreview(element) {
		const box = element.closest('.obs-effect-preview, .obs-effect-live-preview');
		if (!box || !box.clientWidth) return;
		element.style.removeProperty('font-size');
		const baseSize = parseFloat(getComputedStyle(element).fontSize) || 24;
		const boxStyle = getComputedStyle(box);
		const available = Math.max(40, box.clientWidth - parseFloat(boxStyle.paddingLeft || 0) - parseFloat(boxStyle.paddingRight || 0) - 8);
		const naturalWidth = Math.max(element.scrollWidth, element.getBoundingClientRect().width);
		if (naturalWidth > available) {
			const fitted = Math.max(9, baseSize * (available / naturalWidth));
			element.style.setProperty('font-size', `${fitted}px`, 'important');
		}
	}

	const previewObserver = 'IntersectionObserver' in window
		? new IntersectionObserver(entries => {
			for (const entry of entries) {
				const element = entry.target;
				element.dataset.usernameEffectVisible = entry.isIntersecting ? '1' : '0';
				const registration = registrations.get(element);
				const state = registration && groups.get(registration.key);
				if (!state) continue;
				if (entry.isIntersecting) {
					fitPreview(element);
					applyEffect(element, state.effects[state.index]);
				} else {
					clearVisual(element);
				}
			}
		}, {rootMargin: '180px 0px', threshold: 0.01})
		: null;

	const previewResizeObserver = 'ResizeObserver' in window
		? new ResizeObserver(entries => {
			for (const entry of entries) requestAnimationFrame(() => fitPreview(entry.target));
		})
		: null;

	function unregister(element) {
		const previous = registrations.get(element);
		if (!previous) return;
		const state = groups.get(previous.key);
		if (state) {
			state.elements.delete(element);
			if (!state.elements.size) groups.delete(previous.key);
		}
		registrations.delete(element);
	}

	function register(host, userId, effectsValue) {
		const effects = cleanEffects(effectsValue);
		if (!effects.length) return;
		const element = resolveTarget(host);
		if (!element) return;
		prepareTarget(element);
		element.dataset.usernameEffectUser = String(userId || element.dataset.usernameEffectUser || 'anonymous');
		element.dataset.usernameEffects = effects.join(',');
		const key = groupKey(element, effects);
		const previous = registrations.get(element);
		if (previous && previous.key !== key) unregister(element);
		let state = groups.get(key);
		if (!state) {
			state = {effects, index: Math.floor(Math.random() * effects.length), elements: new Set()};
			groups.set(key, state);
		}
		state.elements.add(element);
		registrations.set(element, {key});
		if (isPreview(element)) {
			previewElements.add(element);
			fitPreview(element);
			if (previewObserver) previewObserver.observe(element);
			else applyEffect(element, state.effects[state.index]);
			if (previewResizeObserver) previewResizeObserver.observe(element);
		} else {
			element.dataset.usernameEffectVisible = '1';
			applyEffect(element, state.effects[state.index]);
		}
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
		if (host) register(host, data.id, effects.join(','));
	}

	function enhanceMarkers(root=document) {
		const markers = [];
		if (root instanceof Element && root.matches('[data-username-effect-target]')) markers.push(root);
		if (root.querySelectorAll) markers.push(...root.querySelectorAll('[data-username-effect-target]'));
		for (const marker of markers) {
			const selector = marker.dataset.usernameEffectTarget;
			let target = selector ? document.querySelector(selector) : null;
			if (!target && selector && selector.endsWith(' > span')) target = document.querySelector(selector.slice(0, -7));
			if (target) register(target, marker.dataset.usernameEffectUser, marker.dataset.usernameEffects);
		}
	}

	function scan(root=document) {
		const hosts = [];
		const triggers = [];
		const hostSelector = '[data-username-effects]:not([data-username-effect-target])';
		if (root instanceof Element) {
			if (root.matches(hostSelector)) hosts.push(root);
			if (root.matches('.user-name[data-pop-info]')) triggers.push(root);
		}
		if (root.querySelectorAll) {
			hosts.push(...root.querySelectorAll(hostSelector));
			triggers.push(...root.querySelectorAll('.user-name[data-pop-info]'));
		}
		hosts.forEach(host => register(host, host.dataset.usernameEffectUser, host.dataset.usernameEffects));
		triggers.forEach(enhanceTrigger);
		enhanceMarkers(root);
	}

	function cycle() {
		if (reducedMotion.matches || document.hidden) return;
		for (const [key, state] of groups) {
			for (const element of Array.from(state.elements)) {
				if (!element.isConnected) {
					state.elements.delete(element);
					registrations.delete(element);
				}
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
			state.elements.forEach(element => {
				if (element.dataset.usernameEffectVisible !== '0') applyEffect(element, effect);
			});
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
			if (host) register(host, data.id, effects.join(','));
		});
	});

	document.addEventListener('DOMContentLoaded', () => {
		scan(document);
		if (document.fonts && document.fonts.ready) document.fonts.ready.then(() => previewElements.forEach(fitPreview));
		const observer = new MutationObserver(mutations => {
			for (const mutation of mutations) {
				if (mutation.type === 'attributes' && mutation.target instanceof Element) scan(mutation.target);
				for (const node of mutation.addedNodes || []) if (node instanceof Element) scan(node);
			}
		});
		observer.observe(document.body, {
			childList: true,
			subtree: true,
			attributes: true,
			attributeFilter: ['class', 'data-username-effects'],
		});
		window.setInterval(cycle, CYCLE_INTERVAL);
	});
})();
