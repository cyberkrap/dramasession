(() => {
	'use strict';

	const ASSET_ROOT = '/assets/images/username_effects/';
	const ASSET_VERSION = '14';
	const CYCLE_INTERVAL = 40000;
	const groups = new Map();
	const registrations = new WeakMap();
	const assetCache = new Map();
	const previewElements = new Set();
	const pendingRoots = new Set();
	let cycleTimer = 0;
	let scanFrame = 0;

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

	function cleanColor(value) {
		const color = String(value || '').trim().toLowerCase().replace(/^#/, '');
		return /^[0-9a-f]{6}$/.test(color) ? color : 'ffffff';
	}

	function assetUrl(effect) {
		return `${ASSET_ROOT}${encodeURIComponent(effect)}.webp?v=${ASSET_VERSION}`;
	}

	function preloadEffect(effect) {
		if (assetCache.has(effect)) return assetCache.get(effect);
		const promise = new Promise(resolve => {
			const image = new Image();
			image.decoding = 'async';
			image.addEventListener('load', () => resolve(true), {once: true});
			image.addEventListener('error', () => resolve(false), {once: true});
			image.src = assetUrl(effect);
		});
		assetCache.set(effect, promise);
		return promise;
	}

	function isPatronPlate(element) {
		return element instanceof Element && element.classList.contains('patron');
	}

	function isDistinguished(host, element) {
		return Boolean(
			(host instanceof Element && host.matches('.mod, .mod-rdrama')) ||
			(element instanceof Element && element.matches('.mod, .mod-rdrama'))
		);
	}

	function renderedAsset(effect, element) {
		return effect === 'siren' && isPatronPlate(element) ? 'siren_patron' : effect;
	}

	function wrapFirstTextToken(root) {
		if (!(root instanceof Element)) return null;
		const existing = root.querySelector(':scope > [data-profile-username-effect]');
		if (existing) return existing;

		for (const node of Array.from(root.childNodes)) {
			if (node.nodeType !== Node.TEXT_NODE || !node.nodeValue?.trim()) continue;
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
		return Array.from(root.children).find(child =>
			child instanceof Element && !child.matches(excluded) && child.textContent?.trim()
		) || null;
	}

	function resolveTarget(host, profile = false) {
		if (!(host instanceof Element)) return null;
		if (profile || host.id === 'profile--name') {
			if (isPatronPlate(host)) return host;
			return host.querySelector(':scope > .patron, .patron') || wrapFirstTextToken(host);
		}
		if (isPatronPlate(host)) return host;
		if (host.matches('span, strong, b, bdi, h1, h2, h3, h4, h5')) return host;
		const patron = host.querySelector(':scope > .patron');
		if (patron) return patron;
		if (host.matches('.user-name, a')) {
			const spans = Array.from(host.children).filter(child =>
				child instanceof Element && child.tagName === 'SPAN' &&
				!child.matches('.pronouns, [class*="pronoun"], [class*="flair"]')
			);
			return spans[spans.length - 1] || null;
		}
		return null;
	}

	function prepareTarget(element, color) {
		if (!(element instanceof HTMLElement)) return;
		element.classList.add('username-effect-host');
		if (isPatronPlate(element)) {
			element.classList.remove('username-effect', 'username-effect-text');
			element.classList.add('username-effect-plate');
			element.style.setProperty('--username-effect-text-color', `#${cleanColor(color)}`);
		} else {
			element.classList.remove('username-effect-plate');
			element.classList.add('username-effect', 'username-effect-text');
			element.style.removeProperty('--username-effect-text-color');
		}
	}

	function clearVisual(element, removeClasses = false) {
		if (!(element instanceof Element)) return;
		element.classList.remove('username-effect--ready');
		element.style.removeProperty('--username-effect-image');
		element.style.removeProperty('background-image');
		delete element.dataset.usernameEffectCurrent;
		delete element.dataset.usernameEffectRequest;
		if (removeClasses) {
			element.classList.remove(
				'username-effect-host',
				'username-effect',
				'username-effect-text',
				'username-effect-plate'
			);
			element.style.removeProperty('--username-effect-text-color');
		}
	}

	async function applyEffect(element, effect) {
		if (!(element instanceof Element) || !effect || !element.isConnected) return;
		if (isDistinguished(element, element)) {
			unregister(element);
			clearVisual(element, true);
			return;
		}
		const asset = renderedAsset(effect, element);
		const expectedUrl = assetUrl(asset);
		const currentImage = element.style.getPropertyValue('background-image');
		if (
			element.dataset.usernameEffectCurrent === asset &&
			element.classList.contains('username-effect--ready') &&
			currentImage.includes(expectedUrl)
		) return;
		const token = `${asset}:${performance.now()}:${Math.random()}`;
		element.dataset.usernameEffectRequest = token;
		const loaded = await preloadEffect(asset);
		if (!element.isConnected || element.dataset.usernameEffectRequest !== token) return;
		if (!loaded) {
			clearVisual(element);
			return;
		}
		const image = `url("${expectedUrl}")`;
		element.style.setProperty('--username-effect-image', image);
		// Post and comment styles use background shorthands. Applying only the CSS
		// variable lets those rules overwrite the texture, so pin the image itself.
		element.style.setProperty('background-image', image, 'important');
		element.dataset.usernameEffectCurrent = asset;
		element.classList.add('username-effect--ready');
	}

	function currentIndex(length) {
		return length > 1 ? Math.floor(Date.now() / CYCLE_INTERVAL) % length : 0;
	}

	function fitPreview(element) {
		const box = element.closest('.obs-effect-preview, .obs-effect-live-preview');
		if (!box || !box.clientWidth) return;
		element.style.removeProperty('font-size');
		const baseSize = parseFloat(getComputedStyle(element).fontSize) || 24;
		const boxStyle = getComputedStyle(box);
		const available = Math.max(44, box.clientWidth -
			(parseFloat(boxStyle.paddingLeft) || 0) -
			(parseFloat(boxStyle.paddingRight) || 0) - 12);
		const naturalWidth = Math.max(element.scrollWidth, element.getBoundingClientRect().width);
		if (naturalWidth > available) {
			element.style.setProperty('font-size', `${Math.max(9, baseSize * (available / naturalWidth))}px`, 'important');
		}
	}

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
		const element = resolveTarget(host, Boolean(options.profile));
		if (!element) return;
		if (isDistinguished(host, element)) {
			unregister(element);
			clearVisual(element, true);
			return;
		}

		const effects = cleanEffects(effectsValue);
		if (!effects.length) {
			unregister(element);
			clearVisual(element, true);
			return;
		}

		const userValue = String(userId || element.dataset.usernameEffectUser || 'anonymous');
		const effectsString = effects.join(',');
		const color = cleanColor(options.color || element.dataset.usernameEffectColor);
		const key = `${userValue}::${effectsString}::${color}`;
		const previous = registrations.get(element);
		if (previous?.key === key) return;
		if (previous) unregister(element);

		prepareTarget(element, color);
		element.dataset.usernameEffectUser = userValue;
		element.dataset.usernameEffects = effectsString;
		element.dataset.usernameEffectColor = color;

		let state = groups.get(key);
		if (!state) {
			state = {effects, index: currentIndex(effects.length), elements: new Set()};
			groups.set(key, state);
			effects.forEach(preloadEffect);
		}
		state.elements.add(element);
		registrations.set(element, {key});
		if (element.closest('.obs-effect-preview, .obs-effect-live-preview')) {
			previewElements.add(element);
			requestAnimationFrame(() => fitPreview(element));
		}
		applyEffect(element, state.effects[state.index]);
	}

	function popoverData(trigger) {
		try {
			return JSON.parse(trigger.dataset.popInfo || '{}');
		} catch (_) {
			return {};
		}
	}

	function enhanceTrigger(trigger) {
		const data = popoverData(trigger);
		const effects = cleanEffects(data.username_effects);
		if (effects.length) register(trigger, data.id, effects.join(','), {color: data.username_effect_color});
	}

	function enhanceMarkers(root = document) {
		const markers = [];
		if (root instanceof Element && root.matches('[data-username-effect-target]')) markers.push(root);
		root.querySelectorAll?.('[data-username-effect-target]').forEach(marker => markers.push(marker));
		markers.forEach(marker => {
			const selector = marker.dataset.usernameEffectTarget;
			if (!selector) return;
			const profile = selector.startsWith('#profile--name');
			const target = document.querySelector(profile ? '#profile--name' : selector);
			if (target) register(target, marker.dataset.usernameEffectUser, marker.dataset.usernameEffects, {
				profile,
				color: marker.dataset.usernameEffectColor,
			});
		});
	}

	function scan(root = document) {
		const hosts = [];
		const triggers = [];
		const selector = '[data-username-effects]:not([data-username-effect-target])';
		if (root instanceof Element) {
			if (root.matches(selector)) hosts.push(root);
			if (root.matches('.user-name[data-pop-info]')) triggers.push(root);
		}
		root.querySelectorAll?.(selector).forEach(host => hosts.push(host));
		root.querySelectorAll?.('.user-name[data-pop-info]').forEach(trigger => triggers.push(trigger));
		hosts.forEach(host => register(host, host.dataset.usernameEffectUser, host.dataset.usernameEffects, {
			color: host.dataset.usernameEffectColor,
		}));
		triggers.forEach(enhanceTrigger);
		enhanceMarkers(root);
	}

	function queueScan(root) {
		if (!(root instanceof Element)) return;
		pendingRoots.add(root);
		if (scanFrame) return;
		scanFrame = requestAnimationFrame(() => {
			scanFrame = 0;
			const roots = Array.from(pendingRoots);
			pendingRoots.clear();
			roots.forEach(scan);
		});
	}

	function cycleAll() {
		for (const [key, state] of groups) {
			for (const element of Array.from(state.elements)) {
				if (!element.isConnected || element.matches('.mod, .mod-rdrama')) {
					unregister(element);
					if (element.matches?.('.mod, .mod-rdrama')) clearVisual(element, true);
				}
			}
			if (!state.elements.size) {
				groups.delete(key);
				continue;
			}
			const next = currentIndex(state.effects.length);
			if (next === state.index) continue;
			state.index = next;
			state.elements.forEach(element => applyEffect(element, state.effects[state.index]));
		}
	}

	function scheduleCycle() {
		window.clearTimeout(cycleTimer);
		const delay = CYCLE_INTERVAL - (Date.now() % CYCLE_INTERVAL) + 25;
		cycleTimer = window.setTimeout(() => {
			cycleAll();
			scheduleCycle();
		}, delay);
	}

	function initialize() {
		scan(document);
		const observer = new MutationObserver(mutations => {
			for (const mutation of mutations) {
				for (const node of mutation.addedNodes) queueScan(node);
			}
		});
		// Child insertion only. Never observe class/style attributes because this
		// renderer changes those itself and would otherwise create a feedback loop.
		observer.observe(document.body, {childList: true, subtree: true});
		scheduleCycle();
	}

	document.addEventListener('shown.bs.popover', event => {
		const trigger = event.target;
		if (!(trigger instanceof Element) || !trigger.matches('.user-name[data-pop-info]')) return;
		const data = popoverData(trigger);
		const effects = cleanEffects(data.username_effects);
		if (!effects.length) return;
		requestAnimationFrame(() => {
			const popover = trigger.getAttribute('aria-describedby')
				? document.getElementById(trigger.getAttribute('aria-describedby'))
				: null;
			const host = popover?.querySelector('.pop-username');
			if (host) register(host, data.id, effects.join(','), {color: data.username_effect_color});
		});
	});

	document.addEventListener('visibilitychange', () => {
		if (!document.hidden) cycleAll();
	});
	window.addEventListener('resize', () => previewElements.forEach(fitPreview), {passive: true});
	window.ObsessionUsernameEffects = {scan, register};

	if (document.readyState === 'loading') {
		document.addEventListener('DOMContentLoaded', initialize, {once: true});
	} else {
		initialize();
	}
})();
