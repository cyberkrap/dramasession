(() => {
	'use strict';

	const rendered = new WeakMap();
	const assetBase = '/assets/images/awards/';

	// Only body-covering effects are mutually exclusive. Every smaller
	// decorative effect is independent and may coexist over the exact card.
	const requestedExclusiveKinds = new Set(['truthnuke', 'truthnova', 'lovebomb']);
	const exclusiveKinds = requestedExclusiveKinds;
	const legacyFreeSelectors = [
		'.award-firefly',
		'.award-firework',
		'.award-ricardo-roamer',
		'.award-emoji-rain',
	];

	function isStandaloneThread() {
		return document.body && document.body.id === 'thread';
	}

	function ownerForIcon(icon) {
		if (!isStandaloneThread() || !(icon instanceof HTMLElement)) return null;
		const comment = icon.closest('.comment-anchor');
		if (comment) return comment;
		return icon.closest('#post-root > .card');
	}

	function visualHostForOwner(owner) {
		if (!(owner instanceof HTMLElement)) return null;
		if (owner.classList.contains('comment-anchor')) {
			return Array.from(owner.children).find((child) => child.classList?.contains('comment-text')) || null;
		}
		return owner.querySelector('#post-body') || owner.querySelector('#post-content');
	}

	function kindForIcon(icon) {
		for (const token of icon.classList || []) {
			if (token.startsWith('award-kind-')) return token.slice('award-kind-'.length);
		}
		return null;
	}

	function timestampForIcon(icon) {
		for (const token of icon.classList || []) {
			if (!token.startsWith('award-ts-')) continue;
			const value = Number.parseInt(token.slice('award-ts-'.length), 10);
			if (Number.isFinite(value)) return value;
		}
		return 0;
	}

	function iconsForOwner(owner, selector) {
		return Array.from(owner.querySelectorAll(selector)).filter((icon) => ownerForIcon(icon) === owner);
	}

	function latestExclusiveAward(owner) {
		if (!(owner instanceof HTMLElement)) return null;
		let latest = null;
		let order = 0;
		for (const icon of owner.querySelectorAll('[class*="award-kind-"]')) {
			if (ownerForIcon(icon) !== owner) continue;
			const kind = kindForIcon(icon);
			if (!exclusiveKinds.has(kind)) continue;
			const candidate = {icon, kind, timestamp: timestampForIcon(icon), order: order++};
			if (!latest || candidate.timestamp > latest.timestamp ||
				(candidate.timestamp === latest.timestamp && candidate.order >= latest.order)) {
				latest = candidate;
			}
		}
		return latest;
	}

	function randomSigned(min, max) {
		const n = min + Math.random() * (max - min);
		return Math.random() < .5 ? -n : n;
	}

	function ensureBodyLayer(host) {
		let layer = Array.from(host.children).find((child) => child.classList?.contains('requested-award-effects'));
		if (!layer) {
			layer = document.createElement('div');
			layer.className = 'requested-award-effects';
			layer.setAttribute('aria-hidden', 'true');
			host.appendChild(layer);
		}
		host.classList.add('award-effect-target', 'award-effect-content-host');
		return layer;
	}

	function ensureFreeLayer(owner) {
		let layer = Array.from(owner.children).find((child) => child.classList?.contains('free-award-effects'));
		if (!layer) {
			layer = document.createElement('div');
			layer.className = 'free-award-effects';
			layer.setAttribute('aria-hidden', 'true');
			owner.appendChild(layer);
		}
		owner.classList.add('award-free-effect-host');
		return layer;
	}

	function roam(layer, elements, speedMin = .025, speedMax = .07) {
		if (!elements.length) return;
		requestAnimationFrame(() => {
			if (!layer.isConnected) return;
			const sprites = elements.map((element) => ({
				element,
				x: Math.random() * Math.max(0, layer.clientWidth - (element.offsetWidth || 24)),
				y: Math.random() * Math.max(0, layer.clientHeight - (element.offsetHeight || 24)),
				vx: randomSigned(speedMin, speedMax),
				vy: randomSigned(speedMin, speedMax),
			}));
			let last = performance.now();
			const frame = (now) => {
				if (!layer.isConnected) return;
				const dt = Math.min(40, Math.max(0, now - last));
				last = now;
				for (const sprite of sprites) {
					if (!sprite.element.isConnected) continue;
					const width = sprite.element.offsetWidth || 24;
					const height = sprite.element.offsetHeight || 24;
					const maxX = Math.max(0, layer.clientWidth - width);
					const maxY = Math.max(0, layer.clientHeight - height);
					sprite.x += sprite.vx * dt;
					sprite.y += sprite.vy * dt;
					if (sprite.x <= 0 || sprite.x >= maxX) {
						sprite.x = Math.max(0, Math.min(maxX, sprite.x));
						sprite.vx *= -1;
					}
					if (sprite.y <= 0 || sprite.y >= maxY) {
						sprite.y = Math.max(0, Math.min(maxY, sprite.y));
						sprite.vy *= -1;
					}
					sprite.element.style.transform = `translate3d(${sprite.x}px, ${sprite.y}px, 0)`;
				}
				requestAnimationFrame(frame);
			};
			requestAnimationFrame(frame);
		});
	}

	function addFurries(layer) {
		const roamers = [];
		for (let i = 0; i < 3; i++) {
			const roamer = document.createElement('span');
			roamer.className = 'award-furry-roamer';
			const image = document.createElement('img');
			image.loading = 'lazy';
			image.alt = '';
			image.className = 'award-furry-dancer';
			image.src = `${assetBase}furry${i + 1}.webp?v=20260818f`;
			image.style.animationDelay = `${-Math.random() * 1.8}s`;
			image.addEventListener('error', () => roamer.remove(), {once: true});
			roamer.appendChild(image);
			layer.appendChild(roamer);
			roamers.push(roamer);
		}
		roam(layer, roamers, .02, .05);
	}

	function animateFlySprite(flies) {
		if (!flies.length) return;
		const states = flies.map((fly) => ({
			fly,
			frame: Math.floor(Math.random() * 20),
			next: performance.now() + Math.random() * 90,
			period: 55 + Math.random() * 35,
		}));
		const draw = (state) => {
			const col = state.frame % 5;
			const row = Math.floor(state.frame / 5);
			state.fly.style.backgroundPosition = `${col * 25}% ${row * (100 / 3)}%`;
		};
		states.forEach(draw);
		const tick = (now) => {
			let active = false;
			for (const state of states) {
				if (!state.fly.isConnected) continue;
				active = true;
				if (now >= state.next) {
					state.frame = (state.frame + 1) % 20;
					state.next = now + state.period;
					draw(state);
				}
			}
			if (active) requestAnimationFrame(tick);
		};
		requestAnimationFrame(tick);
	}

	function addShitFlies(layer, count) {
		const total = Math.min(20, 10 + Math.max(1, count) * 2);
		const flies = [];
		for (let i = 0; i < total; i++) {
			const fly = document.createElement('span');
			fly.className = 'award-shit-fly';
			layer.appendChild(fly);
			flies.push(fly);
		}
		animateFlySprite(flies);
		roam(layer, flies, .045, .12);
	}

	function addImpact(layer, kind) {
		const wrap = document.createElement('div');
		wrap.className = `award-impact award-impact-${kind}`;
		const image = document.createElement('img');
		image.loading = 'lazy';
		image.alt = '';
		image.src = kind === 'truthnova'
			? `${assetBase}truthnova.gif?v=20260818f`
			: `${assetBase}truthnuke.webp?v=20260818f`;
		image.addEventListener('error', () => wrap.remove(), {once: true});
		wrap.appendChild(image);
		layer.appendChild(wrap);
	}

	function addLoveBomb(layer) {
		const wrap = document.createElement('div');
		wrap.className = 'award-lovebomb-single';
		const image = document.createElement('img');
		image.loading = 'lazy';
		image.alt = '';
		image.src = `${assetBase}lovebomb.webp?v=20260818f`;
		image.addEventListener('error', () => wrap.remove(), {once: true});
		wrap.appendChild(image);
		layer.appendChild(wrap);
	}

	function reconcileLegacyEffects(owner) {
		if (!(owner instanceof HTMLElement)) return;
		const freeLayer = ensureFreeLayer(owner);
		const layers = Array.from(owner.querySelectorAll('.content-award-effects'));
		const movedRicardos = [];

		// A legacy refresh rebuilds all of these nodes at once. Replace the old
		// copy of each kind in the free layer, then move the fresh nodes over.
		for (const selector of legacyFreeSelectors) {
			if (layers.some((layer) => layer.querySelector(`:scope > ${selector}`))) {
				freeLayer.querySelectorAll(`:scope > ${selector}`).forEach((item) => item.remove());
			}
		}

		for (const originalLayer of layers) {
			for (const selector of legacyFreeSelectors) {
				for (const item of Array.from(originalLayer.querySelectorAll(`:scope > ${selector}`))) {
					freeLayer.appendChild(item);
					if (item.classList.contains('award-ricardo-roamer')) movedRicardos.push(item);
				}
			}

			// Confetti is CSS-driven and every DOM-based legacy effect we still
			// support was extracted above. Leftovers are stale duplicate nodes.
			for (const child of Array.from(originalLayer.children)) child.remove();
			originalLayer.remove();
		}

		// The old Ricardo mover captures the legacy layer in its animation loop.
		// Once we move the dancers out, that loop intentionally dies, so restart
		// their roaming against the persistent full-card layer.
		if (movedRicardos.length) roam(freeLayer, movedRicardos, .035, .085);
	}

	function renderOwner(owner) {
		if (!(owner instanceof HTMLElement) || !isStandaloneThread()) return;
		const host = visualHostForOwner(owner);
		if (!host) return;

		const latestExclusive = latestExclusiveAward(owner);
		const furryCount = iconsForOwner(owner, '.award-kind-furry').length;
		const shitCount = iconsForOwner(owner, '.award-kind-shit').length;
		const signature = `${latestExclusive ? `${latestExclusive.kind}:${latestExclusive.timestamp}:${latestExclusive.order}` : 'none'}|furry:${furryCount}|shit:${shitCount}`;

		// All small/decorative legacy effects roam over the exact awarded card.
		// Only Nuke/Nova/Love Bomb stay in the body-only exclusive layer.
		reconcileLegacyEffects(owner);
		if (rendered.get(owner) === signature) return;
		rendered.set(owner, signature);

		const freeLayer = ensureFreeLayer(owner);
		freeLayer.querySelectorAll(':scope > .award-furry-roamer').forEach((item) => item.remove());
		if (furryCount) addFurries(freeLayer);

		freeLayer.querySelectorAll(':scope > .award-shit-fly').forEach((item) => item.remove());
		if (shitCount) addShitFlies(freeLayer, shitCount);

		owner.querySelectorAll('.requested-award-effects').forEach((layer) => layer.remove());
		if (!latestExclusive || !requestedExclusiveKinds.has(latestExclusive.kind)) return;

		const bodyLayer = ensureBodyLayer(host);
		switch (latestExclusive.kind) {
			case 'lovebomb': addLoveBomb(bodyLayer); break;
			case 'truthnuke': addImpact(bodyLayer, 'truthnuke'); break;
			case 'truthnova': addImpact(bodyLayer, 'truthnova'); break;
		}
	}

	function scan(root = document) {
		if (!isStandaloneThread()) return;
		const owners = new Set();
		const icons = [];
		if (root instanceof HTMLElement && /(^|\s)award-kind-/.test(root.className || '')) icons.push(root);
		root.querySelectorAll?.('[class*="award-kind-"]').forEach((icon) => icons.push(icon));
		for (const icon of icons) {
			const owner = ownerForIcon(icon);
			if (owner) owners.add(owner);
		}
		if (root instanceof HTMLElement && root.classList.contains('content-award-effects')) {
			const owner = root.closest('.comment-anchor') || root.closest('#post-root > .card');
			if (owner) owners.add(owner);
		}
		owners.forEach(renderOwner);
	}

	function pinOwner(pin) {
		return pin.closest('.comment-anchor') || pin.closest('.actual-post') || pin.closest('.card');
	}

	function tooltipText(element) {
		if (!(element instanceof HTMLElement)) return '';
		const direct = element.getAttribute('title') || element.getAttribute('data-bs-original-title') || element.getAttribute('aria-label');
		if (direct) return direct;
		const instance = window.bootstrap?.Tooltip?.getInstance(element);
		return typeof instance?._config?.title === 'string' ? instance._config.title : '';
	}

	function decodeAwardGiver(icon) {
		if (!(icon instanceof HTMLElement)) return null;
		for (const token of icon.classList) {
			if (!token.startsWith('award-user-b64-')) continue;
			const raw = token.slice('award-user-b64-'.length);
			try {
				const padded = raw + '='.repeat((4 - raw.length % 4) % 4);
				const binary = atob(padded.replace(/-/g, '+').replace(/_/g, '/'));
				const bytes = Uint8Array.from(binary, (char) => char.charCodeAt(0));
				return new TextDecoder().decode(bytes);
			}
			catch (_) {}
		}
		return null;
	}

	function awardGiverFromIcon(icon) {
		if (!(icon instanceof HTMLElement)) return null;
		const encoded = decodeAwardGiver(icon);
		if (encoded) return encoded;
		const match = tooltipText(icon).match(/given by\s+@([^\s]+)/i);
		return match ? match[1].replace(/[.,;:!?]+$/, '') : null;
	}

	function latestPinAward(owner) {
		if (!owner) return null;
		let latest = null;
		let order = 0;
		for (const icon of owner.querySelectorAll('.award-kind-pin, .award-kind-gigapin')) {
			const kind = icon.classList.contains('award-kind-gigapin') ? 'gigapin' : 'pin';
			const giver = awardGiverFromIcon(icon);
			if (!giver) continue;
			const candidate = {kind, giver, timestamp: timestampForIcon(icon), order: order++};
			if (!latest || candidate.timestamp > latest.timestamp ||
				(candidate.timestamp === latest.timestamp && candidate.order >= latest.order)) {
				latest = candidate;
			}
		}
		return latest;
	}

	function pinBaseTitle(pin) {
		const awardSource = latestPinAward(pinOwner(pin));
		if (awardSource) {
			return `Pinned by @${awardSource.giver} (${awardSource.kind === 'gigapin' ? 'Giga pin award' : 'Pin award'})`;
		}

		const existing = tooltipText(pin).replace(/\s+until\s+.*$/i, '').trim();
		if (/^Pinned by\s+/i.test(existing)) return existing;
		return 'Pinned by (a site admin)';
	}

	function fixPinTooltip(pin) {
		if (!(pin instanceof HTMLElement)) return;
		pin.removeAttribute('data-onmouseover');
		pin.onmouseover = null;

		const base = pinBaseTitle(pin);
		let title = base;
		const timestamp = Number.parseInt(pin.dataset.timestamp || '', 10);
		if (Number.isFinite(timestamp)) {
			const date = new Date(timestamp * 1000);
			const formatted = typeof window.formatDate === 'function' ? window.formatDate(date) : date.toLocaleString();
			title = `${base} until ${formatted}`;
		}
		pin.setAttribute('title', title);
		pin.setAttribute('data-bs-original-title', title);
		pin.removeAttribute('data-toc-pin-base');
		const tooltip = window.bootstrap?.Tooltip?.getInstance(pin);
		if (tooltip) {
			if (tooltip._config) tooltip._config.title = title;
			if (tooltip.setContent) tooltip.setContent({'.tooltip-inner': title});
		}
	}

	function preparePins(root = document) {
		if (root instanceof HTMLElement && root.matches?.('[id^="pinned-"]')) fixPinTooltip(root);
		root.querySelectorAll?.('[id^="pinned-"]').forEach(fixPinTooltip);
	}

	window.pinned_timestamp = (id) => {
		const pin = document.getElementById(id);
		if (pin) fixPinTooltip(pin);
	};

	function init() {
		preparePins(document);
		document.addEventListener('mouseover', (event) => {
			const pin = event.target.closest?.('[id^="pinned-"]');
			if (pin) fixPinTooltip(pin);
		}, true);

		if (isStandaloneThread()) scan(document);

		const observer = new MutationObserver((mutations) => {
			for (const mutation of mutations) {
				for (const node of mutation.addedNodes) {
					if (!(node instanceof HTMLElement)) continue;
					preparePins(node);
					if (node.matches?.('.award-kind-pin, .award-kind-gigapin') || node.querySelector?.('.award-kind-pin, .award-kind-gigapin')) {
						preparePins(document);
					}
					if (isStandaloneThread() &&
						!node.classList.contains('requested-award-effects') &&
						!node.classList.contains('small-award-effects') &&
						!node.classList.contains('free-award-effects')) scan(node);
				}
			}
		});
		observer.observe(document.body, {childList: true, subtree: true});
	}

	if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init, {once: true});
	else init();
})();