(() => {
	'use strict';

	const ASSET_ROOT = '/assets/images/username_effects/';
	const ASSET_VERSION = '11';
	const CYCLE_INTERVAL = 40000;
	const states = new Map();
	const pendingIds = new Set();
	const imageCache = new Map();
	let fetchTimer = 0;
	let cycleTimer = 0;

	function cleanEffects(value) {
		const seen = new Set();
		const source = Array.isArray(value) ? value : String(value || '').split(',');
		return source
			.map(item => String(item || '').trim().toLowerCase())
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

	function preload(effect) {
		if (imageCache.has(effect)) return imageCache.get(effect);
		const promise = new Promise(resolve => {
			const image = new Image();
			image.decoding = 'async';
			image.addEventListener('load', () => resolve(true), {once: true});
			image.addEventListener('error', () => resolve(false), {once: true});
			image.src = assetUrl(effect);
		});
		imageCache.set(effect, promise);
		return promise;
	}

	function popoverData(element) {
		try {
			return JSON.parse(element.dataset.popInfo || '{}');
		} catch (_) {
			return {};
		}
	}

	function identifyHost(host) {
		if (!(host instanceof Element)) return null;
		if (host.dataset.usernameEffectUser) {
			return {userId: String(host.dataset.usernameEffectUser), host};
		}
		if (host.matches('.user-name[data-pop-info]')) {
			const data = popoverData(host);
			if (data.id) return {userId: String(data.id), host};
		}
		return null;
	}

	function resolveTarget(host) {
		if (!(host instanceof Element)) return null;
		if (host.dataset.usernameEffectUser && host.matches('span, strong, b, bdi, h1, h2, h3, h4, h5')) {
			return host;
		}
		const direct = host.querySelector(':scope > [data-username-effect-user]');
		if (direct) return direct;
		const patron = host.querySelector(':scope > .patron');
		if (patron) return patron;
		const spans = Array.from(host.children).filter(child =>
			child instanceof Element && child.tagName === 'SPAN' &&
			!child.matches('.pronouns, [class*="pronoun"], [class*="flair"]')
		);
		return spans[spans.length - 1] || null;
	}

	function currentIndex(length) {
		return length > 1 ? Math.floor(Date.now() / CYCLE_INTERVAL) % length : 0;
	}

	function prepareTarget(target, color) {
		const patron = target.classList.contains('patron');
		target.classList.add('username-effect-host');
		if (patron) {
			target.classList.remove('username-effect', 'username-effect-text');
			target.classList.add('username-effect-plate');
			target.style.setProperty('--username-effect-text-color', `#${cleanColor(color)}`);
		} else {
			target.classList.remove('username-effect-plate');
			target.classList.add('username-effect', 'username-effect-text');
			target.style.removeProperty('--username-effect-text-color');
		}
	}

	function clearTarget(target) {
		if (!(target instanceof Element)) return;
		target.classList.remove('username-effect--ready');
		target.style.removeProperty('--username-effect-image');
		delete target.dataset.usernameEffectCurrent;
	}

	async function applyTarget(target, effect, color) {
		if (!(target instanceof Element) || !target.isConnected || !effect) return;
		prepareTarget(target, color);
		const patron = target.classList.contains('patron');
		const asset = effect === 'siren' && patron ? 'siren_patron' : effect;
		if (target.dataset.usernameEffectCurrent === asset && target.classList.contains('username-effect--ready')) return;
		const requestToken = `${asset}:${performance.now()}:${Math.random()}`;
		target.dataset.usernameEffectHydrationRequest = requestToken;
		const loaded = await preload(asset);
		if (!target.isConnected || target.dataset.usernameEffectHydrationRequest !== requestToken) return;
		if (!loaded) {
			clearTarget(target);
			return;
		}
		target.style.setProperty('--username-effect-image', `url("${assetUrl(asset)}")`);
		target.dataset.usernameEffectCurrent = asset;
		target.classList.add('username-effect--ready');
	}

	function applyState(state) {
		for (const target of Array.from(state.elements)) {
			if (!target.isConnected) state.elements.delete(target);
		}
		if (!state.effects.length) {
			state.elements.forEach(clearTarget);
			return;
		}
		state.index = currentIndex(state.effects.length);
		const effect = state.effects[state.index];
		state.elements.forEach(target => applyTarget(target, effect, state.color));
	}

	function embeddedState(host, target) {
		const popover = host.matches?.('.user-name[data-pop-info]') ? popoverData(host) : {};
		const effects = cleanEffects(
			target.dataset.usernameEffects ||
			host.dataset.usernameEffects ||
			popover.username_effects ||
			[]
		);
		const color = cleanColor(
			target.dataset.usernameEffectColor ||
			host.dataset.usernameEffectColor ||
			popover.username_effect_color
		);
		return {effects, color};
	}

	function track(host) {
		const identity = identifyHost(host);
		if (!identity || !/^\d+$/.test(identity.userId)) return;
		const target = resolveTarget(identity.host);
		if (!target) return;

		let state = states.get(identity.userId);
		if (!state) {
			state = {effects: [], color: 'ffffff', index: 0, elements: new Set()};
			states.set(identity.userId, state);
		}

		const embedded = embeddedState(identity.host, target);
		if (embedded.effects.length) {
			state.effects = embedded.effects;
			state.color = embedded.color;
			state.effects.forEach(preload);
		}

		state.elements.add(target);
		if (state.effects.length) applyState(state);
		pendingIds.add(identity.userId);
		scheduleFetch();
	}

	function scan(root = document) {
		const selector = '[data-username-effect-user], .user-name[data-pop-info]';
		if (root instanceof Element && root.matches(selector)) track(root);
		root.querySelectorAll?.(selector).forEach(track);
	}

	async function fetchChunk(ids) {
		const response = await fetch(`/api/username-effects?ids=${encodeURIComponent(ids.join(','))}`, {
			credentials: 'same-origin',
			cache: 'no-store',
			headers: {'Accept': 'application/json'},
		});
		if (!response.ok) throw new Error(`Username effect hydration failed: ${response.status}`);
		const payload = await response.json();
		const users = payload && payload.users ? payload.users : {};
		ids.forEach(userId => {
			const user = users[userId] || {};
			const state = states.get(userId);
			if (!state) return;
			state.effects = cleanEffects(user.effects || []);
			state.color = cleanColor(user.color);
			state.effects.forEach(preload);
			applyState(state);
		});
	}

	async function flushFetch() {
		fetchTimer = 0;
		const ids = Array.from(pendingIds);
		pendingIds.clear();
		for (let offset = 0; offset < ids.length; offset += 100) {
			const chunk = ids.slice(offset, offset + 100);
			try {
				await fetchChunk(chunk);
			} catch (_) {
				chunk.forEach(id => pendingIds.add(id));
				window.setTimeout(scheduleFetch, 3000);
			}
		}
	}

	function scheduleFetch() {
		if (fetchTimer || !pendingIds.size) return;
		fetchTimer = window.setTimeout(flushFetch, 40);
	}

	function cycleAll() {
		states.forEach(state => applyState(state));
	}

	function scheduleCycle() {
		window.clearTimeout(cycleTimer);
		const delay = CYCLE_INTERVAL - (Date.now() % CYCLE_INTERVAL) + 180;
		cycleTimer = window.setTimeout(() => {
			cycleAll();
			scheduleCycle();
		}, delay);
	}

	function initialize() {
		scan(document);
		const observer = new MutationObserver(mutations => {
			mutations.forEach(mutation => mutation.addedNodes.forEach(node => {
				if (node instanceof Element) scan(node);
			}));
		});
		observer.observe(document.body, {childList: true, subtree: true});
		scheduleCycle();
	}

	document.addEventListener('visibilitychange', () => {
		if (!document.hidden) {
			scan(document);
			cycleAll();
		}
	});
	window.addEventListener('pageshow', () => scan(document));
	window.addEventListener('popstate', () => window.setTimeout(() => scan(document), 0));

	if (document.readyState === 'loading') {
		document.addEventListener('DOMContentLoaded', initialize, {once: true});
	} else {
		initialize();
	}
})();
