(() => {
	'use strict';

	const rendered = new WeakMap();
	const visualKinds = ['furry', 'shit', 'truthnuke', 'truthnova', 'lovebomb'];
	const assetBase = '/assets/images/awards/';

	function isStandaloneThread() {
		return document.body && document.body.id === 'thread';
	}

	function targetForIcon(icon) {
		if (!isStandaloneThread()) return null;

		// A .comment-body owns both the current comment and every nested reply.
		// Effects must bind to the exact comment content node or they leak into
		// descendants when replies are added dynamically.
		const comment = icon.closest('.comment-anchor');
		if (comment) return comment;

		return icon.closest('#post-root > .card');
	}

	function countFor(target, kind) {
		return Array.from(target.querySelectorAll(`.award-kind-${kind}`))
			.filter((icon) => targetForIcon(icon) === target).length;
	}

	function countsFor(target) {
		const counts = {};
		for (const kind of visualKinds) counts[kind] = countFor(target, kind);
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

	function ensureLayer(target) {
		let layer = Array.from(target.children).find((child) => child.classList?.contains('requested-award-effects'));
		if (!layer) {
			layer = document.createElement('div');
			layer.className = 'requested-award-effects';
			layer.setAttribute('aria-hidden', 'true');
			target.appendChild(layer);
		}
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
		// Keep the rDrama-style roaming dancers, but cap density so the content
		// remains readable even when several Furry awards are stacked.
		const total = Math.min(6, Math.max(3, count * 2));
		const roamers = [];
		for (let i = 0; i < total; i++) {
			const roamer = document.createElement('span');
			roamer.className = 'award-furry-roamer';
			const image = document.createElement('img');
			image.loading = 'lazy';
			image.alt = '';
			image.className = 'award-furry-dancer';
			image.src = `${assetBase}furry${(i % 3) + 1}.webp?v=20260817`;
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
		], {
			duration,
			delay: -Math.random() * duration,
			iterations: Infinity,
			direction: 'alternate',
			easing: 'ease-in-out',
		});
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
			image.src = `${assetBase}fly-sprite.webp?v=20260817`;
			image.addEventListener('error', () => image.remove(), {once: true});
			fly.appendChild(image);
			layer.appendChild(fly);
			animateFly(fly);
		}
	}

	function addImpact(layer, kind, count) {
		const wrap = document.createElement('div');
		wrap.className = `award-impact award-impact-${kind}`;
		wrap.dataset.stack = String(Math.min(30, count));
		const image = document.createElement('img');
		image.loading = 'lazy';
		image.alt = '';
		image.src = kind === 'truthnova'
			? `${assetBase}truthnova.gif?v=20260817`
			: `${assetBase}truthnuke.webp?v=20260817`;
		image.addEventListener('error', () => wrap.remove(), {once: true});
		wrap.appendChild(image);
		layer.appendChild(wrap);
	}

	function addLoveBomb(layer, count) {
		const hearts = document.createElement('div');
		hearts.className = 'award-lovebomb-pattern';
		hearts.style.setProperty('--love-opacity', String(Math.min(.58, .28 + count * .045)));
		layer.appendChild(hearts);
	}

	function renderTarget(target) {
		if (!(target instanceof HTMLElement) || !isStandaloneThread()) return;
		const counts = countsFor(target);
		const signature = fingerprint(counts);
		if (rendered.get(target) === signature) return;
		rendered.set(target, signature);

		const oldLayer = Array.from(target.children).find((child) => child.classList?.contains('requested-award-effects'));
		if (oldLayer) oldLayer.remove();
		if (!visualKinds.some((kind) => counts[kind])) return;

		target.classList.add('award-effect-target');
		const layer = ensureLayer(target);
		if (counts.lovebomb) addLoveBomb(layer, counts.lovebomb);
		if (counts.truthnuke) addImpact(layer, 'truthnuke', counts.truthnuke);
		if (counts.truthnova) addImpact(layer, 'truthnova', counts.truthnova);
		if (counts.shit) addShitFlies(layer, counts.shit);
		if (counts.furry) addFurries(layer, counts.furry);
	}

	function scan(root = document) {
		if (!isStandaloneThread()) return;
		const icons = [];
		if (root instanceof HTMLElement && /(^|\s)award-kind-/.test(root.className || '')) icons.push(root);
		root.querySelectorAll?.('[class*="award-kind-"]').forEach((icon) => icons.push(icon));
		const targets = new Set();
		for (const icon of icons) {
			const target = targetForIcon(icon);
			if (target) targets.add(target);
		}
		targets.forEach(renderTarget);
	}

	function init() {
		if (!isStandaloneThread()) return;
		scan(document);
		const observer = new MutationObserver((mutations) => {
			for (const mutation of mutations) {
				for (const node of mutation.addedNodes) {
					if (node instanceof HTMLElement && !node.classList.contains('requested-award-effects')) scan(node);
				}
			}
		});
		observer.observe(document.body, {childList: true, subtree: true});
	}

	if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init, {once: true});
	else init();
})();
