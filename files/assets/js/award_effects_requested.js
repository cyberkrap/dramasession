(() => {
	'use strict';

	const rendered = new WeakMap();
	const requestedKinds = ['furry', 'shit', 'truthnuke', 'truthnova', 'lovebomb'];
	const legacyKinds = ['fireflies', 'ricardo', 'firework', 'wholesome'];
	const animatedKinds = new Set([...requestedKinds, ...legacyKinds]);
	const assetBase = '/assets/images/awards/';
	const legacySelectors = {
		fireflies: '.award-firefly',
		ricardo: '.award-ricardo-roamer',
		firework: '.award-firework',
		wholesome: '.award-emoji-rain',
	};

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

	function latestAnimatedAward(owner) {
		if (!(owner instanceof HTMLElement)) return null;
		let latest = null;
		let order = 0;
		for (const icon of owner.querySelectorAll('[class*="award-kind-"]')) {
			if (ownerForIcon(icon) !== owner) continue;
			const kind = kindForIcon(icon);
			if (!animatedKinds.has(kind)) continue;
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

	function randomPercent(min = 3, max = 94) {
		return `${min + Math.random() * (max - min)}%`;
	}

	function ensureLayer(host) {
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

	function roam(layer, elements, speedMin = .025, speedMax = .07) {
		if (!elements.length) return;
		requestAnimationFrame(() => {
			if (!layer.isConnected) return;
			const sprites = elements.map((element) => ({
				element,
				x: Math.random() * Math.max(0, layer.clientWidth - (element.offsetWidth || 60)),
				y: Math.random() * Math.max(0, layer.clientHeight - (element.offsetHeight || 60)),
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
					const width = sprite.element.offsetWidth || 60;
					const height = sprite.element.offsetHeight || 60;
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
			image.src = `${assetBase}furry${i + 1}.webp?v=20260818b`;
			image.style.animationDelay = `${-Math.random() * 1.8}s`;
			image.addEventListener('error', () => roamer.remove(), {once: true});
			roamer.appendChild(image);
			layer.appendChild(roamer);
			roamers.push(roamer);
		}
		roam(layer, roamers, .02, .05);
	}

	function animateFly(fly) {
		if (typeof fly.animate !== 'function') return;
		const dx = randomSigned(25, 110);
		const dy = randomSigned(18, 75);
		const duration = 900 + Math.random() * 1800;
		fly.animate([
			{transform: 'translate3d(0,0,0) rotate(0deg)'},
			{transform: `translate3d(${dx * .45}px,${dy * -.3}px,0) rotate(${randomSigned(35, 160)}deg)`, offset: .4},
			{transform: `translate3d(${dx}px,${dy}px,0) rotate(${randomSigned(120, 420)}deg)`},
		], {duration, delay: -Math.random() * duration, iterations: Infinity, direction: 'alternate', easing: 'ease-in-out'});
	}

	function addShitFlies(layer) {
		for (let i = 0; i < 11; i++) {
			const fly = document.createElement('span');
			fly.className = 'award-shit-fly';
			fly.style.left = randomPercent(2, 95);
			fly.style.top = randomPercent(5, 90);
			const image = document.createElement('img');
			image.loading = 'lazy';
			image.alt = '';
			image.src = `${assetBase}fly-sprite.webp?v=20260818b`;
			image.addEventListener('error', () => image.remove(), {once: true});
			fly.appendChild(image);
			layer.appendChild(fly);
			animateFly(fly);
		}
	}

	function addImpact(layer, kind) {
		const wrap = document.createElement('div');
		wrap.className = `award-impact award-impact-${kind}`;
		const image = document.createElement('img');
		image.loading = 'lazy';
		image.alt = '';
		image.src = kind === 'truthnova'
			? `${assetBase}truthnova.gif?v=20260818b`
			: `${assetBase}truthnuke.webp?v=20260818b`;
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
		image.src = `${assetBase}lovebomb.webp?v=20260818b`;
		image.addEventListener('error', () => wrap.remove(), {once: true});
		wrap.appendChild(image);
		layer.appendChild(wrap);
	}

	function moveLegacyLayer(layer, owner) {
		if (!(layer instanceof HTMLElement) || !owner) return null;
		const host = visualHostForOwner(owner);
		if (!host) return null;
		host.classList.add('award-effect-target', 'award-effect-content-host');
		if (layer.parentElement !== host) host.appendChild(layer);
		return layer;
	}

	function reconcileLegacyEffects(owner, latest) {
		if (!(owner instanceof HTMLElement)) return;
		const layers = Array.from(owner.querySelectorAll('.content-award-effects'));
		for (const originalLayer of layers) {
			const layer = moveLegacyLayer(originalLayer, owner);
			if (!layer) continue;
			if (!latest || requestedKinds.includes(latest.kind) || !legacyKinds.includes(latest.kind)) {
				layer.remove();
				continue;
			}
			const selector = legacySelectors[latest.kind];
			for (const child of Array.from(layer.children)) {
				if (!child.matches(selector)) child.remove();
			}
			// Emoji awards are one-sprite effects. If several historical Emoji
			// awards exist, keep only the sprite belonging to the newest award.
			if (latest.kind === 'wholesome') {
				let emojiName = null;
				for (const token of latest.icon.classList) {
					if (token.startsWith('award-emoji-name-')) emojiName = token.slice('award-emoji-name-'.length);
				}
				const sprites = Array.from(layer.querySelectorAll('.award-emoji-rain'));
				let kept = false;
				for (let i = sprites.length - 1; i >= 0; i--) {
					const sprite = sprites[i];
					const matches = !emojiName || decodeURIComponent(sprite.src).includes(`/e/${emojiName}.webp`);
					if (matches && !kept) kept = true;
					else sprite.remove();
				}
			}
		}
	}

	function renderOwner(owner) {
		if (!(owner instanceof HTMLElement) || !isStandaloneThread()) return;
		const host = visualHostForOwner(owner);
		if (!host) return;
		const latest = latestAnimatedAward(owner);
		const signature = latest ? `${latest.kind}:${latest.timestamp}:${latest.order}` : 'none';

		reconcileLegacyEffects(owner, latest);
		owner.querySelectorAll('.requested-award-effects').forEach((layer) => layer.remove());
		if (rendered.get(owner) === signature && (!latest || legacyKinds.includes(latest.kind))) return;
		rendered.set(owner, signature);
		if (!latest || !requestedKinds.includes(latest.kind)) return;

		const layer = ensureLayer(host);
		switch (latest.kind) {
			case 'lovebomb': addLoveBomb(layer); break;
			case 'truthnuke': addImpact(layer, 'truthnuke'); break;
			case 'truthnova': addImpact(layer, 'truthnova'); break;
			case 'shit': addShitFlies(layer); break;
			case 'furry': addFurries(layer); break;
		}
	}

	function scan(root = document) {
		if (!isStandaloneThread()) return;
		const icons = [];
		if (root instanceof HTMLElement && /(^|\s)award-kind-/.test(root.className || '')) icons.push(root);
		root.querySelectorAll?.('[class*="award-kind-"]').forEach((icon) => icons.push(icon));
		const owners = new Set();
		for (const icon of icons) {
			const owner = ownerForIcon(icon);
			if (owner) owners.add(owner);
		}
		// A legacy effect layer can be the only newly inserted node, so also
		// recover its owner even when no award icon is inside the mutation root.
		if (root instanceof HTMLElement && root.classList.contains('content-award-effects')) {
			const owner = root.closest('.comment-anchor') || root.closest('#post-root > .card');
			if (owner) owners.add(owner);
		}
		owners.forEach(renderOwner);
	}

	function pinOwner(pin) {
		return pin.closest('.comment-anchor') || pin.closest('.actual-post') || pin.closest('.card');
	}

	function awardGiver(owner, kind) {
		if (!owner) return null;
		const icons = Array.from(owner.querySelectorAll(`.award-kind-${kind}`));
		const icon = icons[icons.length - 1];
		if (!icon) return null;
		const title = icon.getAttribute('data-bs-original-title') || icon.getAttribute('title') || '';
		const match = title.match(/given by\s+@([^\s]+)/i);
		return match ? match[1].replace(/[.,;:!?]+$/, '') : null;
	}

	function pinBaseTitle(pin) {
		if (pin.dataset.tocPinBase) return pin.dataset.tocPinBase;
		const existing = pin.getAttribute('title') || pin.getAttribute('data-bs-original-title') || '';
		if (/^Pinned by\s+/i.test(existing)) {
			const base = existing.replace(/\s+until\s+.*$/i, '');
			pin.dataset.tocPinBase = base;
			return base;
		}
		const owner = pinOwner(pin);
		const gigaGiver = awardGiver(owner, 'gigapin');
		const pinGiver = awardGiver(owner, 'pin');
		const base = gigaGiver
			? `Pinned by @${gigaGiver} (giga pin award)`
			: pinGiver
				? `Pinned by @${pinGiver} (pin award)`
				: 'Pinned by (a site admin)';
		pin.dataset.tocPinBase = base;
		return base;
	}

	function fixPinTooltip(pin) {
		if (!(pin instanceof HTMLElement)) return;
		// Disable the legacy hover-time mutator. The complete tooltip is prepared
		// before Bootstrap sees the first hover, so it never alternates between
		// source-only and date-only strings.
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
		// Pin tooltips occur on listings as well as standalone threads.
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
					if (isStandaloneThread() && !node.classList.contains('requested-award-effects')) scan(node);
				}
			}
		});
		observer.observe(document.body, {childList: true, subtree: true});
	}

	if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init, {once: true});
	else init();
})();
