(() => {
	'use strict';

	const ASSET_ROOT = '/assets/images/username_effects/';
	const ASSET_VERSION = '3';
	const CYCLE_INTERVAL = 8000;
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
		return `${ASSET_ROOT}${encodeURIComponent(effect)}.webp?v=${ASSET_VERSION}`;
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

	function schedulePreload(effects) {
		const load = () => effects.forEach(preloadEffect);
		if ('requestIdleCallback' in window) requestIdleCallback(load, {timeout: 1800});
		else window.setTimeout(load, 250);
	}

	function isPatronPlate(element) {
		return element instanceof Element && element.classList.contains('patron');
	}

	function unwrapLegacyInnerEffect(element) {
		if (!(element instanceof Element)) return;
		const inner = element.querySelector(':scope > .username-effect, :scope > .username-effect-text');
		if (!inner || isPatronPlate(inner)) return;
		while (inner.firstChild) element.insertBefore(inner.firstChild, inner);
		inner.remove();
	}

	function wrapFirstTextToken(root) {
		if (!(root instanceof Element)) return null;
		const existing = root.querySelector(':scope > [data-profile-username-effect]');
		if (existing) return existing;

		for (const node of Array.from(root.childNodes)) {
			if (node.nodeType !== Node.TEXT_NODE || !node.nodeValue || !node.nodeValue.trim()) continue;
			const match = node.nodeValue.match(/^(\s*)(\S+)([\s\S]*)$/);
			if (!match) continue;
			const target = document.createElement('span');
			target.dataset.profileUsernameEffect = '1';
			target.textContent = match[2];
			const fragment = document.createDocumentFragment();
			if (match[1]) fragment.append(document.createTextNode(match[1]));
			fragment.append(target);
			if (match[3]) fragment.append(document.createTextNode(match[3]));
			node.replaceWith(fragment);
			return target;
		}

		const excluded = '.pronouns, .sub-flair, .badge, [class*="flair"], [class*="pronoun"], i, img, svg, button';
		const candidates = Array.from(root.children).filter(child => {
			if (!(child instanceof Element) || child.matches(excluded)) return false;
			return Boolean(child.textContent && child.textContent.trim());
		});
		return candidates[0] || null;
	}

	function isolateProfileUsername(root) {
		if (!(root instanceof Element)) return null;
		if (isPatronPlate(root)) return root;
		const patron = root.querySelector(':scope > .patron, .patron');
		if (patron) return patron;
		return wrapFirstTextToken(root);
	}

	function resolveTarget(host, fromProfileMarker = false) {
		if (!(host instanceof Element)) return null;
		if (fromProfileMarker || host.id === 'profile--name') return isolateProfileUsername(host);
		if (isPatronPlate(host)) return host;

		if (host.matches('span, strong, b, bdi, h1, h2, h3, h4, h5')) return host;

		const directPatron = host.querySelector(':scope > .patron');
		if (directPatron) return directPatron;

		if (host.matches('.user-name, a')) {
			const candidates = Array.from(host.children).filter(child =>
				child instanceof Element &&
				child.tagName === 'SPAN' &&
				!child.matches('.pronouns, [class*="pronoun"], [class*="flair"]')
			);
			return candidates[candidates.length - 1] || null;
		}

		return null;
	}

	function removeOldInlineOverrides(element) {
		if (!(element instanceof HTMLElement)) return;
		if (element.style.getPropertyValue('color') === 'transparent') element.style.removeProperty('color');
		if (element.style.getPropertyValue('-webkit-text-fill-color') === 'transparent') {
			element.style.removeProperty('-webkit-text-fill-color');
		}
		for (const property of [
			'background-image', 'background-position', 'background-repeat', 'background-size',
			'-webkit-background-clip', 'background-clip'
		]) element.style.removeProperty(property);
	}

	function prepareTarget(element) {
		if (!(element instanceof Element)) return;
		removeOldInlineOverrides(element);
		element.classList.add('username-effect-host');

		if (isPatronPlate(element)) {
			unwrapLegacyInnerEffect(element);
			element.classList.remove('username-effect', 'username-effect-text');
			element.classList.add('username-effect-plate');
		} else {
			element.classList.remove('username-effect-plate');
			element.classList.add('username-effect', 'username-effect-text');
		}
	}

	function clearVisual(element) {
		if (!(element instanceof Element)) return;
		element.classList.remove('username-effect--ready');
		element.style.removeProperty('--username-effect-image');
		delete element.dataset.usernameEffectCurrent;
	}

	async function applyEffect(element, effect) {
		if (!(element instanceof Element) || !effect || !element.isConnected) return;
		if (element.dataset.usernameEffectCurrent === effect && element.classList.contains('username-effect--ready')) return;

		const requestToken = `${effect}:${performance.now()}:${Math.random()}`;
		element.dataset.usernameEffectRequest = requestToken;
		const loaded = await preloadEffect(effect);
		if (!element.isConnected || element.dataset.usernameEffectRequest !== requestToken) return;
		if (!loaded) {
			clearVisual(element);
			return;
		}

		element.style.setProperty('--username-effect-image', effectUrl(effect));
		element.dataset.usernameEffectCurrent = effect;
		element.classList.add('username-effect--ready');
	}

	function isPreview(element) {
		return Boolean(element.closest('.obs-effect-preview, .obs-effect-live-preview'));
	}

	function fitPreview(element) {
		const box = element.closest('.obs-effect-preview, .obs-effect-live-preview');
		if (!box || !box.clientWidth) return;
		element.style.removeProperty('font-size');
		const computed = getComputedStyle(element);
		const baseSize = parseFloat(computed.fontSize) || 24;
		const boxStyle = getComputedStyle(box);
		const available = Math.max(
			44,
			box.clientWidth - (parseFloat(boxStyle.paddingLeft) || 0) - (parseFloat(boxStyle.paddingRight) || 0) - 12,
		);
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
					requestAnimationFrame(() => fitPreview(element));
					applyEffect(element, state.effects[state.index]);
				} else {
					clearVisual(element);
				}
			}
		}, {rootMargin: '120px 0px', threshold: 0.01})
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

	function register(host, userId, effectsValue, options = {}) {
		const effects = cleanEffects(effectsValue);
		if (!effects.length) return;
		const element = resolveTarget(host, Boolean(options.profile));
		if (!element) return;

		const userValue = String(userId || element.dataset.usernameEffectUser || 'anonymous');
		const effectsString = effects.join(',');
		const nextKey = `${userValue}::${effectsString}`;
		const previous = registrations.get(element);
		if (previous && previous.key === nextKey) {
			if (isPreview(element)) requestAnimationFrame(() => fitPreview(element));
			return;
		}

		if (previous) unregister(element);
		prepareTarget(element);
		if (element.dataset.usernameEffectUser !== userValue) element.dataset.usernameEffectUser = userValue;
		if (element.dataset.usernameEffects !== effectsString) element.dataset.usernameEffects = effectsString;

		let state = groups.get(nextKey);
		if (!state) {
			state = {effects, index: 0, elements: new Set()};
			groups.set(nextKey, state);
			if (effects.length > 1) schedulePreload(effects);
		}
		state.elements.add(element);
		registrations.set(element, {key: nextKey});

		if (isPreview(element)) {
			previewElements.add(element);
			requestAnimationFrame(() => fitPreview(element));
			if (previewObserver) previewObserver.observe(element);
			else applyEffect(element, state.effects[state.index]);
			return;
		}

		element.dataset.usernameEffectVisible = '1';
		applyEffect(element, state.effects[state.index]);
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
		register(trigger, data.id, effects.join(','));
	}

	function enhanceMarkers(root = document) {
		const markers = [];
		if (root instanceof Element && root.matches('[data-username-effect-target]')) markers.push(root);
		if (root.querySelectorAll) markers.push(...root.querySelectorAll('[data-username-effect-target]'));

		for (const marker of markers) {
			const selector = marker.dataset.usernameEffectTarget;
			if (!selector) continue;
			const profileMarker = selector.startsWith('#profile--name');
			const target = profileMarker
				? document.querySelector('#profile--name')
				: document.querySelector(selector);
			if (target) register(
				target,
				marker.dataset.usernameEffectUser,
				marker.dataset.usernameEffects,
				{profile: profileMarker},
			);
		}
	}

	function scan(root = document) {
		const hosts = [];
		const triggers = [];
		const selector = '[data-username-effects]:not([data-username-effect-target])';
		if (root instanceof Element) {
			if (root.matches(selector)) hosts.push(root);
			if (root.matches('.user-name[data-pop-info]')) triggers.push(root);
		}
		if (root.querySelectorAll) {
			hosts.push(...root.querySelectorAll(selector));
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
			state.index = (state.index + 1) % state.effects.length;
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
		if (document.fonts && document.fonts.ready) {
			document.fonts.ready.then(() => previewElements.forEach(element => requestAnimationFrame(() => fitPreview(element))));
		}

		const observer = new MutationObserver(mutations => {
			for (const mutation of mutations) {
				for (const node of mutation.addedNodes) {
					if (node instanceof Element) scan(node);
				}
			}
		});
		observer.observe(document.body, {childList: true, subtree: true});

		let resizeFrame = 0;
		window.addEventListener('resize', () => {
			cancelAnimationFrame(resizeFrame);
			resizeFrame = requestAnimationFrame(() => previewElements.forEach(fitPreview));
		}, {passive: true});

		window.setInterval(cycle, CYCLE_INTERVAL);
	});
})();
