(() => {
	'use strict';

	const rendered = new WeakMap();
	const visualKinds = ['furry', 'shit', 'truthnuke', 'truthnova', 'lovebomb'];
	const assetBase = '/assets/images/awards/';

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

	function iconsForOwner(owner, kind) {
		return Array.from(owner.querySelectorAll(`.award-kind-${kind}`))
			.filter((icon) => ownerForIcon(icon) === owner);
	}

	function countsFor(owner) {
		const counts = {};
		for (const kind of visualKinds) counts[kind] = iconsForOwner(owner, kind).length;
		return counts;
	}

	function fingerprint(counts) {
		return visualKinds.map((kind) => `${kind}:${counts[kind] || 0}`).join('|');
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

	function addFurries(layer, count) {
		const total = Math.min(6, Math.max(3, count * 2));
		const roamers = [];
		for (let i = 0; i < total; i++) {
			const roamer = document.createElement('span');
			roamer.className = 'award-furry-roamer';
			const image = document.createElement('img');
			image.loading = 'lazy';
			image.alt = '';
			image.className = 'award-furry-dancer';
			image.src = `${assetBase}furry${(i % 3) + 1}.webp?v=20260818`;
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

	function addShitFlies(layer, count) {
		const total = Math.min(26, 7 + count * 4);
		for (let i = 0; i < total; i++) {
			const fly = document.createElement('span');
			fly.className = 'award-shit-fly';
			fly.style.left = randomPercent(2, 95);
			fly.style.top = randomPercent(5, 90);
			const image = document.createElement('img');
			image.loading = 'lazy';
			image.alt = '';
			image.src = `${assetBase}fly-sprite.webp?v=20260818`;
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
			? `${assetBase}truthnova.gif?v=20260818`
			: `${assetBase}truthnuke.webp?v=20260818`;
		image.addEventListener('error', () => wrap.remove(), {once: true});
		wrap.appendChild(image);
		layer.appendChild(wrap);
	}

	function addLoveBomb(layer, count) {
		const wrap = document.createElement('div');
		wrap.className = 'award-lovebomb-single';
		wrap.style.setProperty('--love-opacity', String(Math.min(.62, .38 + Math.max(0, count - 1) * .035)));
		const image = document.createElement('img');
		image.loading = 'lazy';
		image.alt = '';
		image.src = `${assetBase}lovebomb.webp?v=20260818`;
		image.addEventListener('error', () => wrap.remove(), {once: true});
		wrap.appendChild(image);
		layer.appendChild(wrap);
	}

	function renderOwner(owner) {
		if (!(owner instanceof HTMLElement) || !isStandaloneThread()) return;
		const host = visualHostForOwner(owner);
		if (!host) return;
		const counts = countsFor(owner);
		const signature = `${fingerprint(counts)}|host:${host.id || host.className}`;
		if (rendered.get(owner) === signature) return;
		rendered.set(owner, signature);

		owner.querySelectorAll('.requested-award-effects').forEach((layer) => layer.remove());
		if (!visualKinds.some((kind) => counts[kind])) return;

		const layer = ensureLayer(host);
		if (counts.lovebomb) addLoveBomb(layer, counts.lovebomb);
		if (counts.truthnuke) addImpact(layer, 'truthnuke');
		if (counts.truthnova) addImpact(layer, 'truthnova');
		if (counts.shit) addShitFlies(layer, counts.shit);
		if (counts.furry) addFurries(layer, counts.furry);
	}

	function migrateLegacyLayer(layer) {
		if (!(layer instanceof HTMLElement) || !layer.classList.contains('content-award-effects')) return;
		const owner = layer.closest('.comment-anchor') || layer.closest('#post-root > .card');
		if (!owner) return;
		const host = visualHostForOwner(owner);
		if (!host || layer.parentElement === host) return;
		host.classList.add('award-effect-target', 'award-effect-content-host');
		host.appendChild(layer);
	}

	function migrateLegacyLayers(root = document) {
		if (root instanceof HTMLElement && root.classList.contains('content-award-effects')) migrateLegacyLayer(root);
		root.querySelectorAll?.('.content-award-effects').forEach(migrateLegacyLayer);
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
		owners.forEach(renderOwner);
		migrateLegacyLayers(root);
	}

	function pinOwner(pin) {
		return pin.closest('.comment-anchor') || pin.closest('#post-root > .card');
	}

	function awardGiver(owner, kind) {
		if (!owner) return null;
		const icon = Array.from(owner.querySelectorAll(`.award-kind-${kind}`))
			.find((candidate) => ownerForIcon(candidate) === owner);
		if (!icon) return null;
		const title = icon.getAttribute('data-bs-original-title') || icon.getAttribute('title') || '';
		const match = title.match(/given by\s+@([^\s]+)/i);
		return match ? match[1].replace(/[.,;:!?]+$/, '') : null;
	}

	function pinBaseTitle(pin) {
		const existing = pin.getAttribute('title') || pin.getAttribute('data-bs-original-title') || '';
		if (/^Pinned by\s+/i.test(existing)) return existing.replace(/\s+until\s+.*$/i, '');
		const owner = pinOwner(pin);
		const gigaGiver = awardGiver(owner, 'gigapin');
		if (gigaGiver) return `Pinned by @${gigaGiver} (giga pin award)`;
		const pinGiver = awardGiver(owner, 'pin');
		if (pinGiver) return `Pinned by @${pinGiver} (pin award)`;
		return 'Pinned by (a site admin)';
	}

	function fixPinTooltip(pin) {
		if (!(pin instanceof HTMLElement)) return;
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
		if (tooltip?.setContent) tooltip.setContent({'.tooltip-inner': title});
	}

	window.pinned_timestamp = (id) => {
		const pin = document.getElementById(id);
		if (pin) fixPinTooltip(pin);
	};

	function init() {
		if (!isStandaloneThread()) return;
		scan(document);
		document.querySelectorAll('[id^="pinned-"][data-timestamp]').forEach(fixPinTooltip);
		document.addEventListener('mouseover', (event) => {
			const pin = event.target.closest?.('[id^="pinned-"]');
			if (pin) fixPinTooltip(pin);
		}, true);

		const observer = new MutationObserver((mutations) => {
			for (const mutation of mutations) {
				for (const node of mutation.addedNodes) {
					if (!(node instanceof HTMLElement)) continue;
					if (!node.classList.contains('requested-award-effects')) scan(node);
					if (node.matches?.('[id^="pinned-"]')) fixPinTooltip(node);
					node.querySelectorAll?.('[id^="pinned-"]').forEach(fixPinTooltip);
				}
			}
		});
		observer.observe(document.body, {childList: true, subtree: true});
	}

	if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init, {once: true});
	else init();
})();
